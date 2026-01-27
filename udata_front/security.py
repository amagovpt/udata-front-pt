import logging
import re
from lxml import etree
import defusedxml.lxml as safe_lxml

log = logging.getLogger(__name__)

# Tags proibidas que permitem execução de scripts ou carregamento de recursos externos
FORBIDDEN_TAGS = {
    "{http://www.w3.org/2000/svg}script",
    "script",
    "{http://www.w3.org/2000/svg}foreignObject",
    "foreignObject",
    "{http://www.w3.org/2000/svg}iframe",
    "iframe",
    "{http://www.w3.org/2000/svg}object",
    "object",
    "{http://www.w3.org/2000/svg}embed",
    "embed",
    "{http://www.w3.org/2000/svg}applet",
    "applet",
    "{http://www.w3.org/2000/svg}meta",
    "meta",
    "{http://www.w3.org/2000/svg}link",
    "link",
}

# Atributos de eventos que executam JS
EVENT_ATTRIBUTES_REGEX = re.compile(r"^on[a-z]+", re.IGNORECASE)

# URIs perigosos (ex: javascript:alert(1))
DANGEROUS_URI_REGEX = re.compile(r"^\s*(javascript|vbscript|data):", re.IGNORECASE)


def sanitize_svg(content: bytes) -> bytes:
    """
    Remove scripts, eventos e outros vetores de XSS de ficheiros SVG.
    Utiliza defusedxml para parse seguro contra XML Bombs e XXE.
    """
    if not content:
        return content

    try:
        # Pagar XML de forma segura
        try:
            # defusedxml.lxml.fromstring parses securely
            tree = safe_lxml.fromstring(content)
        except etree.XMLSyntaxError as e:
            # Se não for XML válido, rejeitamos por segurança.
            # SVGs servidos como image/svg+xml devem ser bem formados.
            log.warning(f"Rejeitando SVG inválido: {e}")
            raise ValueError("Ficheiro SVG inválido (XML malformado)") from e

        # Limpeza iterativa
        # Usamos iter() para percorrer todos os elementos
        for element in tree.iter():
            # 1. Verificar Tag
            # lxml usa {namespace}tag format
            if (
                element.tag in FORBIDDEN_TAGS
                or element.tag.split("}")[-1] in FORBIDDEN_TAGS
            ):
                # Remove o elemento da árvore
                parent = element.getparent()
                if parent is not None:
                    parent.remove(element)
                continue

            # 2. Verificar Atributos
            # Listamos atributos para remover para evitar modificar o dicionário durante a iteração
            attrs_to_remove = []
            for attr_name, attr_value in element.attrib.items():
                # Normaliza nome do atributo (remove namespace se houver)
                clean_attr_name = attr_name.split("}")[-1].lower()

                # a) Atributos de evento (onload, onclick, etc)
                if EVENT_ATTRIBUTES_REGEX.match(clean_attr_name):
                    attrs_to_remove.append(attr_name)
                    continue

                # b) Atributos href/src com javascript:
                if clean_attr_name in ("href", "xlink:href", "src"):
                    if DANGEROUS_URI_REGEX.match(attr_value):
                        attrs_to_remove.append(attr_name)

            for attr in attrs_to_remove:
                del element.attrib[attr]

            # 3. Remover conteúdo de script dentro de CDATA ou texto se escapou da verificação de tag
            # (Geralmente coberto pelo #1, mas sanitização de texto extra pode ser útil se necessário)

        # Serializa de volta para bytes
        return etree.tostring(tree, encoding="utf-8", xml_declaration=True)

    except Exception as e:
        log.error(f"Erro ao sanitizar SVG: {e}")
        # Em caso de erro crítico na sanitização, é mais seguro rejeitar o upload ou retornar
        # o conteúdo, mas como fallback de segurança podemos retornar o conteúdo original
        # mas alertando. Idealmente, falha-se fechado (raise error).
        # Para este script, vamos rejeitar silentemente retornando vazio ou lançar exceção.
        raise ValueError("Falha na sanitização do SVG") from e
