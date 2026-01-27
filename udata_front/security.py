import logging
import re
import html
from lxml import etree
import defusedxml.lxml as safe_lxml

log = logging.getLogger(__name__)

# Limite de tamanho para SVG (5MB) - proteção contra DoS
MAX_SVG_SIZE = 5 * 1024 * 1024

# Namespaces SVG válidos
SVG_NAMESPACES = {"{http://www.w3.org/2000/svg}svg", "svg"}

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

# URIs perigosos - melhorado para cobrir encoding e HTML entities
DANGEROUS_URI_PATTERNS = [
    re.compile(r"^\s*(javascript|vbscript|data):", re.IGNORECASE),
    re.compile(r"^\s*&#", re.IGNORECASE),  # HTML entities
    re.compile(r"^\s*%[0-9a-f]{2}", re.IGNORECASE),  # URL encoding
]


def _normalize_uri(uri: str) -> str:
    """
    Normaliza URI para detectar ofuscação.
    Remove whitespace, newlines, e decodifica HTML entities.
    """
    if not uri:
        return ""

    # Remove whitespace e newlines
    normalized = uri.strip().replace("\n", "").replace("\r", "").replace("\t", "")

    # Decodifica HTML entities (ex: &#106;avascript:)
    try:
        normalized = html.unescape(normalized)
    except Exception:
        pass

    return normalized


def _is_dangerous_uri(uri: str) -> bool:
    """
    Verifica se URI contém vetores perigosos.
    """
    normalized = _normalize_uri(uri)

    for pattern in DANGEROUS_URI_PATTERNS:
        if pattern.match(normalized):
            return True

    # Verifica também a versão lowercase
    if any(
        dangerous in normalized.lower()
        for dangerous in ["javascript:", "vbscript:", "data:"]
    ):
        return True

    return False


def sanitize_svg(content: bytes) -> bytes:
    """
    Remove scripts, eventos e outros vetores de XSS de ficheiros SVG.
    Utiliza defusedxml para parse seguro contra XML Bombs e XXE.

    Args:
        content: Conteúdo do ficheiro SVG em bytes

    Returns:
        Conteúdo sanitizado em bytes

    Raises:
        ValueError: Se o ficheiro for inválido ou demasiado grande
    """
    if not content:
        return content

    # Verificar tamanho do ficheiro
    if len(content) > MAX_SVG_SIZE:
        log.warning(
            f"SVG rejeitado: tamanho {len(content)} bytes excede limite de {MAX_SVG_SIZE} bytes"
        )
        raise ValueError(
            f"Ficheiro SVG demasiado grande (máximo {MAX_SVG_SIZE // 1024 // 1024}MB)"
        )

    try:
        # Parsear XML de forma segura
        try:
            tree = safe_lxml.fromstring(content)
        except etree.XMLSyntaxError as e:
            # Se não for XML válido, rejeitamos por segurança.
            # SVGs servidos como image/svg+xml devem ser bem formados.
            log.warning(f"Rejeitando SVG inválido: {e}")
            raise ValueError("Ficheiro SVG inválido (XML malformado)") from e

        # Validar que é realmente um SVG
        if tree.tag not in SVG_NAMESPACES:
            log.warning(f"Rejeitando ficheiro: elemento raiz '{tree.tag}' não é SVG")
            raise ValueError(
                "Ficheiro não é um SVG válido (elemento raiz deve ser <svg>)"
            )

        # Coletar elementos a remover (evita modificar durante iteração)
        elements_to_remove = []

        for element in tree.iter():
            # 1. Verificar Tag
            # lxml usa {namespace}tag format
            tag_name = (
                element.tag.split("}")[-1]
                if "}" in str(element.tag)
                else str(element.tag)
            )

            if element.tag in FORBIDDEN_TAGS or tag_name in FORBIDDEN_TAGS:
                elements_to_remove.append(element)
                continue

            # 2. Verificar Atributos
            attrs_to_remove = []
            for attr_name, attr_value in element.attrib.items():
                # Normaliza nome do atributo (remove namespace se houver)
                clean_attr_name = attr_name.split("}")[-1].lower()

                # a) Atributos de evento (onload, onclick, etc)
                if EVENT_ATTRIBUTES_REGEX.match(clean_attr_name):
                    attrs_to_remove.append(attr_name)
                    log.debug(f"Removendo atributo de evento: {attr_name}")
                    continue

                # b) Atributos href/src com javascript: ou outros URIs perigosos
                if clean_attr_name in (
                    "href",
                    "xlink:href",
                    "src",
                    "action",
                    "formaction",
                ):
                    if _is_dangerous_uri(attr_value):
                        attrs_to_remove.append(attr_name)
                        log.debug(
                            f"Removendo URI perigoso: {attr_name}={attr_value[:50]}"
                        )

            # Remover atributos perigosos
            for attr in attrs_to_remove:
                del element.attrib[attr]

        # Remover elementos perigosos
        for element in elements_to_remove:
            parent = element.getparent()
            if parent is not None:
                parent.remove(element)
                log.debug(f"Removendo elemento perigoso: {element.tag}")

        # Serializa de volta para bytes
        return etree.tostring(tree, encoding="utf-8", xml_declaration=True)

    except ValueError:
        # Re-raise ValueError (já são erros esperados)
        raise
    except Exception as e:
        log.error(f"Erro ao sanitizar SVG: {e}")
        # Fail-closed: rejeitar em caso de erro inesperado
        raise ValueError("Falha na sanitização do SVG") from e
