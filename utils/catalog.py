import os
import requests
import xml.etree.ElementTree as ET
import csv
import time
import sys
from typing import Dict, List, Optional, Tuple, Union
import logging
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("catalog_fetcher")

# Definição de fontes de dados
SOURCES = {
    "1": {"name": "Production", "url": "https://dados.gov.pt/api/1/site/catalog.xml"},
    "2": {"name": "Preprod", "url": "https://preprod.dados.gov.pt/api/1/site/catalog.xml"},
    "3": {"name": "Test", "url": "https://10.55.37.38/api/1/site/catalog.xml"},
    "4": {"name": "Development", "url": "https://172.31.204.12/api/1/site/catalog.xml"},
    "5": {"name": "Local", "url": "http://localhost:7000/api/1/site/catalog.xml"}
}

# Formatos de saída suportados
SUPPORTED_FORMATS = ["xml", "csv", "json", "txt"]


def clear_screen():
    """Limpa a tela do terminal para melhor visibilidade."""
    os.system('cls' if os.name == 'nt' else 'clear')


def display_header():
    """Exibe o cabeçalho do programa."""
    clear_screen()
    print("=" * 60)
    print("FERRAMENTA DE EXTRAÇÃO DE CATÁLOGO DE DADOS".center(60))
    print("=" * 60)
    print()


def get_user_source() -> str:
    """Solicita e valida a escolha da fonte de dados pelo usuário."""
    while True:
        print("\nFONTES DE DADOS DISPONÍVEIS:")
        for key, value in SOURCES.items():
            print(f"  [{key}] - {value['name']} ({value['url']})")
        
        source_choice = input("\nDigite o número da fonte desejada (ou 'q' para sair): ").strip()
        
        if source_choice.lower() == 'q':
            sys.exit("Programa encerrado pelo usuário.")
            
        if source_choice in SOURCES:
            return SOURCES[source_choice]["url"]
        
        print("\n❌ Opção inválida. Por favor, tente novamente.")


def get_tag_filter() -> Optional[str]:
    """Solicita e valida a tag de filtro opcional."""
    while True:
        add_tag = input("\nDeseja adicionar uma tag à consulta? (s/n): ").strip().lower()
        
        if add_tag == "n":
            return None
        elif add_tag == "s":
            tag = input("Digite a tag desejada: ").strip()
            if tag:
                return tag
            print("❌ A tag não pode estar vazia.")
        else:
            print("❌ Por favor, digite 's' para sim ou 'n' para não.")


def get_output_format() -> str:
    """Solicita e valida o formato de saída desejado."""
    while True:
        print("\nFORMATOS DE SAÍDA DISPONÍVEIS:")
        for i, fmt in enumerate(SUPPORTED_FORMATS, 1):
            print(f"  [{i}] - {fmt.upper()}")
            
        format_choice = input("\nEscolha o formato do arquivo de saída (1-4): ").strip()
        
        try:
            index = int(format_choice) - 1
            if 0 <= index < len(SUPPORTED_FORMATS):
                return SUPPORTED_FORMATS[index]
        except ValueError:
            pass
            
        print("❌ Formato inválido. Por favor, escolha uma das opções listadas.")


def get_output_path(output_format: str) -> str:
    """Solicita e valida o caminho de saída do arquivo."""
    default_path = os.path.join(os.getcwd(), f"catalog.{output_format}")
    
    print(f"\nCaminho de saída padrão: {default_path}")
    custom_path = input("Digite um caminho personalizado ou pressione ENTER para usar o padrão: ").strip()
    
    if not custom_path:
        return default_path
    
    # Verificar se o diretório existe
    directory = os.path.dirname(custom_path) or os.getcwd()
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
            logger.info(f"Diretório criado: {directory}")
        except OSError as e:
            logger.error(f"Não foi possível criar o diretório: {e}")
            return default_path
    
    # Adicionar extensão se não estiver presente
    if not custom_path.endswith(f".{output_format}"):
        custom_path = f"{custom_path}.{output_format}"
    
    return custom_path


def add_url_params(url: str, params: Dict[str, str]) -> str:
    """Adiciona parâmetros a uma URL, respeitando os parâmetros existentes."""
    parsed_url = urlparse(url)
    query_dict = parse_qs(parsed_url.query)
    
    # Adicionar novos parâmetros
    for key, value in params.items():
        query_dict[key] = [value]
    
    # Reconstruir a query string
    new_query = urlencode(query_dict, doseq=True)
    
    # Substituir a query string na URL
    parsed_url = parsed_url._replace(query=new_query)
    
    return urlunparse(parsed_url)


def fetch_page(url: str, page: int, tag: Optional[str], max_retries: int = 3) -> Tuple[bool, Optional[List]]:
    """
    Busca uma página de dados do catálogo.
    
    Args:
        url: URL base para busca
        page: Número da página atual
        tag: Tag opcional para filtrar resultados
        max_retries: Número máximo de tentativas em caso de erro
        
    Returns:
        Tupla (sucesso, registros)
    """
    params = {"page": str(page)}
    if tag:
        params["tag"] = tag
    
    full_url = add_url_params(url, params)
    
    retry_count = 0
    while retry_count < max_retries:
        try:
            logger.info(f"Buscando: {full_url} (Tentativa {retry_count + 1})")
            
            response = requests.get(full_url, verify=False, timeout=10)
            
            # Verificar se chegamos ao fim dos dados
            if response.status_code == 404 or not response.text.strip():
                logger.info(f"Fim dos dados na página {page}.")
                return True, []
            
            # Verificar erro no status code
            if response.status_code != 200:
                logger.warning(f"Erro HTTP {response.status_code} na página {page}.")
                retry_count += 1
                time.sleep(1)
                continue
            
            # Tentar processar o XML
            try:
                root = ET.fromstring(response.text)
                
                # Verificar se a página está vazia
                if len(root) == 0:
                    logger.info(f"Página {page} não contém registros.")
                    return True, []
                
                return True, list(root)
                
            except ET.ParseError as e:
                logger.error(f"Erro ao processar XML da página {page}: {e}")
                retry_count += 1
                time.sleep(1)
                continue
                
        except requests.RequestException as e:
            logger.error(f"Erro de conexão: {e}")
            retry_count += 1
            time.sleep(2)
            continue
    
    # Se chegou aqui, é porque todas as tentativas falharam
    logger.error(f"Falha após {max_retries} tentativas na página {page}.")
    return False, None


def fetch_all_data(base_url: str, tag: Optional[str] = None, max_retries: int = 3) -> List:
    """
    Busca todos os dados do catálogo, paginando automaticamente.
    
    Args:
        base_url: URL base para busca
        tag: Tag opcional para filtrar resultados
        max_retries: Número máximo de tentativas por página
        
    Returns:
        Lista de registros XML
    """
    page = 1
    all_records = []
    
    print("\nIniciando a extração de dados...")
    print("Pressione CTRL+C a qualquer momento para interromper.")
    
    try:
        while True:
            success, records = fetch_page(base_url, page, tag, max_retries)
            
            if not success:
                logger.warning(f"Pulando para a próxima página após falha na página {page}.")
                page += 1
                continue
            
            if not records:
                break
            
            all_records.extend(records)
            logger.info(f"Página {page}: {len(records)} registros obtidos.")
            page += 1
            
    except KeyboardInterrupt:
        print("\nExtração interrompida pelo usuário.")
    
    logger.info(f"Total de registros obtidos: {len(all_records)}")
    return all_records


def xml_to_csv(root_element: ET.Element, output_path: str) -> bool:
    """
    Converte dados XML para CSV.
    
    Args:
        root_element: Elemento raiz contendo todos os registros XML
        output_path: Caminho do arquivo CSV de saída
        
    Returns:
        True se bem-sucedido, False caso contrário
    """
    try:
        # Se não há registros, não podemos obter os cabeçalhos
        if len(root_element) == 0:
            logger.error("Sem registros para converter para CSV.")
            return False
        
        # Obter todos os possíveis cabeçalhos de todos os registros
        all_tags = set()
        for record in root_element:
            for elem in record:
                all_tags.add(elem.tag)
        
        headers = sorted(list(all_tags))
        
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(headers)
            
            for record in root_element:
                row = []
                for header in headers:
                    elem = record.find(header)
                    row.append(elem.text if elem is not None and elem.text else '')
                csvwriter.writerow(row)
                
        return True
        
    except Exception as e:
        logger.error(f"Erro ao converter para CSV: {e}")
        return False


def save_results(records: List, output_format: str, output_path: str) -> bool:
    """
    Salva os resultados no formato especificado.
    
    Args:
        records: Lista de registros XML
        output_format: Formato de saída (xml, csv, etc.)
        output_path: Caminho do arquivo de saída
        
    Returns:
        True se bem-sucedido, False caso contrário
    """
    if not records:
        logger.warning("Nenhum dado para salvar.")
        return False
    
    try:
        # Criar elemento raiz para conter todos os registros
        root_element = ET.Element("catalog")
        root_element.extend(records)
        
        if output_format == "csv":
            return xml_to_csv(root_element, output_path)
        elif output_format == "xml":
            with open(output_path, "wb") as file:
                file.write(ET.tostring(root_element, encoding="utf-8"))
            return True
        elif output_format == "json":
            # Implementação simplificada - idealmente usaria json.dumps
            with open(output_path, "w", encoding="utf-8") as file:
                file.write("{\n  \"catalog\": [\n")
                for i, record in enumerate(records):
                    file.write("    {\n")
                    for j, elem in enumerate(record):
                        file.write(f'      "{elem.tag}": "{elem.text or ""}"')
                        if j < len(record) - 1:
                            file.write(",\n")
                        else:
                            file.write("\n")
                    file.write("    }")
                    if i < len(records) - 1:
                        file.write(",\n")
                    else:
                        file.write("\n")
                file.write("  ]\n}")
            return True
        else:  # txt ou outro formato
            with open(output_path, "w", encoding="utf-8") as file:
                file.write(ET.tostring(root_element, encoding="utf-8").decode("utf-8"))
            return True
            
    except Exception as e:
        logger.error(f"Erro ao salvar resultados: {e}")
        return False


def display_summary(start_time: float, records_count: int, output_path: str, output_format: str) -> None:
    """Exibe um resumo da operação realizada."""
    elapsed_time = time.time() - start_time
    
    print("\n" + "=" * 60)
    print("RESUMO DA OPERAÇÃO".center(60))
    print("=" * 60)
    print(f"• Tempo total: {elapsed_time:.2f} segundos")
    print(f"• Registros obtidos: {records_count}")
    print(f"• Formato de saída: {output_format.upper()}")
    print(f"• Arquivo salvo em: {output_path}")
    
    if os.path.exists(output_path):
        size_kb = os.path.getsize(output_path) / 1024
        print(f"• Tamanho do arquivo: {size_kb:.2f} KB")
    else:
        print("❌ ATENÇÃO: O arquivo de saída não foi criado!")
    
    print("=" * 60)


def main():
    """Função principal do programa."""
    # Desativar avisos de certificado SSL
    import warnings
    warnings.filterwarnings("ignore", message="Unverified HTTPS request")
    
    display_header()
    
    try:
        # Obter configurações do usuário
        base_url = get_user_source()
        tag = get_tag_filter()
        output_format = get_output_format()
        output_path = get_output_path(output_format)
        
        # Mostrar resumo das configurações
        print("\nCONFIGURAÇÕES:")
        print(f"• URL: {base_url}")
        print(f"• Tag: {tag or 'Nenhuma'}")
        print(f"• Formato: {output_format.upper()}")
        print(f"• Saída: {output_path}")
        
        # Confirmar operação
        confirm = input("\nConfirmar e iniciar a extração? (s/n): ").strip().lower()
        if confirm != "s":
            sys.exit("Operação cancelada pelo usuário.")
        
        # Iniciar contagem de tempo
        start_time = time.time()
        
        # Buscar todos os dados
        records = fetch_all_data(base_url, tag)
        
        # Salvar resultados
        if records:
            success = save_results(records, output_format, output_path)
            if success:
                logger.info(f"Dados salvos com sucesso em: {output_path}")
            else:
                logger.error("Falha ao salvar os dados.")
        else:
            logger.warning("Nenhum dado foi coletado. Nenhum arquivo será gerado.")
        
        # Exibir resumo
        display_summary(start_time, len(records), output_path, output_format)
        
    except KeyboardInterrupt:
        print("\nPrograma interrompido pelo usuário.")
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
        print(f"\n❌ Ocorreu um erro inesperado: {e}")
    finally:
        print("\nPrograma finalizado.")


if __name__ == "__main__":
    main()