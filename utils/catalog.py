#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Catalog Fetcher Tool - A utility for extracting, processing, and saving catalog data from various sources.
This tool supports extracting catalog data from multiple environments, filtering by tags,
and exporting in XML, JSON, TXT, or TTL formats.
"""

import os
import requests
import xml.etree.ElementTree as ET
import time
import sys
import logging
import json
import re
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

# Configure logging and error tracking
error_log_path = os.path.join(os.getcwd(), "error.log")
http_errors: List[Tuple[int, str, Optional[str]]] = []
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s', 
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("catalog_fetcher")

# Available data sources - each with a name and URL
SOURCES = {
    "1": {"name": "Production", "url": "https://dados.gov.pt/api/1/site/catalog.xml"},
    "2": {"name": "Preprod", "url": "https://preprod.dados.gov.pt/api/1/site/catalog.xml"},
    "3": {"name": "Test", "url": "https://10.55.37.38/api/1/site/catalog.xml"},
    "4": {"name": "Development", "url": "https://172.31.204.12/api/1/site/catalog.xml"},
    "5": {"name": "Local", "url": "http://localhost:7000/api/1/site/catalog.xml"}
}

# Supported output formats
SUPPORTED_FORMATS = ["xml", "json", "txt", "ttl"]

# UI helper functions
def clear_screen():
    """Clear the terminal screen based on the operating system."""
    os.system('cls' if os.name == 'nt' else 'clear')

def display_header():
    """Display the application header/title."""
    clear_screen()
    print("=" * 60)
    print("FERRAMENTA DE EXTRAÇÃO DE CATÁLOGO DE DADOS".center(60))
    print("=" * 60)
    print()

def get_user_source() -> str:
    """
    Present available data sources to the user and get their selection.
    
    Returns:
        str: The URL of the selected data source
    """
    while True:
        print("\nFONTES DE DADOS DISPONÍVEIS:")
        for key, value in SOURCES.items():
            print(f"  [{key}] - {value['name']} ({value['url']})")
            
        source_choice = input("\nDigite o número da fonte desejada (ou 'q' para sair): ").strip().lower()
        
        if source_choice == 'q':
            sys.exit("Programa encerrado pelo usuário.")
            
        if source_choice in SOURCES:
            return SOURCES[source_choice]["url"]
            
        print("\n❌ Opção inválida. Por favor, tente novamente.")

def get_tag_filter() -> Optional[str]:
    """
    Ask the user if they want to filter results by a specific tag.
    
    Returns:
        Optional[str]: The tag to filter by, or None if no filtering is desired
    """
    while True:
        add_tag = input("\nDeseja adicionar uma tag à consulta? (s/n): ").strip().lower()
        
        if add_tag == "n":
            return None
            
        if add_tag == "s":
            tag = input("Digite a tag desejada: ").strip()
            return tag if tag else print("❌ A tag não pode estar vazia.") or None
            
        print("❌ Por favor, digite 's' para sim ou 'n' para não.")

def get_output_format() -> str:
    """
    Present available output formats and get the user's selection.
    
    Returns:
        str: The selected output format (xml, json, txt, or ttl)
    """
    while True:
        print("\nFORMATOS DE SAÍDA DISPONÍVEIS:")
        for i, fmt in enumerate(SUPPORTED_FORMATS, 1):
            format_description = {
                "xml": "XML - Extensible Markup Language",
                "json": "JSON - JavaScript Object Notation", 
                "txt": "TXT - Plain Text",
                "ttl": "TTL - Turtle RDF Format"
            }
            print(f"  [{i}] - {format_description.get(fmt, fmt.upper())}")
            
        format_choice = input("\nEscolha o formato do arquivo de saída (1-{}): ".format(len(SUPPORTED_FORMATS))).strip()
        
        try:
            index = int(format_choice) - 1
            if 0 <= index < len(SUPPORTED_FORMATS):
                return SUPPORTED_FORMATS[index]
        except ValueError:
            pass
            
        print("❌ Formato inválido. Por favor, escolha uma das opções listadas.")

def get_output_path(output_format: str) -> str:
    """
    Get the output file path from the user, or use a default path.
    Creates directories if they don't exist.
    
    Args:
        output_format: The file extension to use
        
    Returns:
        str: The full path where the output will be saved
    """
    default_path = os.path.join(os.getcwd(), f"catalog.{output_format}")
    print(f"\nCaminho de saída padrão: {default_path}")
    custom_path = input("Digite um caminho personalizado ou pressione ENTER para usar o padrão: ").strip()
    
    if not custom_path:
        return default_path
        
    # Ensure directory exists
    directory = os.path.dirname(custom_path) or os.getcwd()
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
            logger.info(f"Diretório criado: {directory}")
        except OSError as e:
            logger.error(f"Não foi possível criar o diretório: {e}")
            return default_path
            
    # Ensure filename has correct extension
    return custom_path if custom_path.endswith(f".{output_format}") else f"{custom_path}.{output_format}"

# URL and data processing functions
def add_url_params(url: str, params: Dict[str, str]) -> str:
    """
    Add query parameters to a URL.
    
    Args:
        url: The base URL
        params: Dictionary of parameters to add
        
    Returns:
        str: The URL with parameters added
    """
    parsed_url = urlparse(url)
    query_dict = parse_qs(parsed_url.query)
    query_dict.update(params)
    return urlunparse(parsed_url._replace(query=urlencode(query_dict, doseq=True)))

def find_element_with_namespace(element: ET.Element, tag_name: str) -> Optional[ET.Element]:
    """
    Find an XML element by tag name, accounting for namespaces.
    
    Args:
        element: The parent element to search within
        tag_name: The tag name to find
        
    Returns:
        Optional[ET.Element]: The found element or None
    """
    # Try direct find first
    if result := element.find(tag_name):
        return result
        
    # Search through children for tag with or without namespace
    for child in element:
        # Check for namespace in tag (format: {namespace}tag)
        local_name = child.tag.split('}', 1)[-1]
        if local_name == tag_name:
            return child
            
        # Check for namespace prefix (format: prefix:tag)
        if ':' in child.tag and child.tag.split(':', 1)[1] == tag_name:
            return child
            
    return None

def extract_dataset_ids(response_text: str) -> List[str]:
    """
    Extract dataset IDs from XML response text, using various methods to handle different formats.
    
    Args:
        response_text: The XML response as a string
        
    Returns:
        List[str]: List of extracted dataset IDs
    """
    try:
        # Try parsing as XML first
        root = ET.fromstring(response_text)
        ids = []
        
        for record in root:
            # Try to find identifier element with namespace
            identifier = next((c.text for c in record if c.tag.endswith('identifier') or ':identifier' in c.tag), None)
            
            # If not found, try common ID tag names
            if not identifier:
                for tag in ['id', 'identifier', 'datasetId', 'uri', 'guid', 'uuid']:
                    if elem := find_element_with_namespace(record, tag):
                        identifier = elem.text
                        break
                        
            # Try to find ID in attributes
            if not identifier:
                identifier = record.attrib.get('identifier') or record.attrib.get('id')
                
            # Last resort: use first child's value
            if not identifier and len(record) > 0 and record[0].text:
                identifier = f"{record[0].tag}:{record[0].text[:30]}"
                
            ids.append(identifier if identifier else f"unknown_id_{len(ids)}")
            
        # Filter to keep only 24-character IDs without hyphens or http
        return [i for i in ids if i and len(i) == 24 and '-' not in i and 'http' not in i]
        
    except ET.ParseError:
        # If XML parsing fails, try regex-based extraction
        try:
            # Try to find identifier tags with namespaces
            ids1 = [i for i in re.findall(r'<ns\d*:identifier[^>]*>(.*?)</ns\d*:identifier>', response_text) 
                   if len(i) == 24 and '-' not in i and 'http' not in i]
            
            # Try to find identifier tags without namespaces
            ids2 = [i for i in re.findall(r'<identifier[^>]*>(.*?)</identifier>', response_text) 
                   if len(i) == 24 and '-' not in i and 'http' not in i]
            
            return ids1 or ids2
            
        except Exception:
            return []
            
    return []

def fetch_page(url: str, page: int, tag: Optional[str], max_retries: int = 3) -> Tuple[bool, Optional[List]]:
    """
    Fetch a single page of results from the API.
    
    Args:
        url: The base API URL
        page: The page number to fetch
        tag: Optional tag to filter results
        max_retries: Maximum number of retry attempts
        
    Returns:
        Tuple[bool, Optional[List]]: Success status and list of records (if any)
    """
    # Prepare URL parameters
    params = {"page": str(page)}
    if tag:
        params["tag"] = tag
    full_url = add_url_params(url, params)
    
    # Attempt to fetch with retries
    for retry in range(max_retries):
        try:
            logger.info(f"Buscando: {full_url} (Tentativa {retry + 1})")
            response = requests.get(full_url, verify=False, timeout=30)
            
            # Handle 404 or empty response as end of results
            if response.status_code == 404 or not response.text.strip():
                logger.info(f"Fim dos dados na página {page}.")
                return True, []
                
            # Handle HTTP errors
            if response.status_code != 200:
                dataset_ids = []
                
                # For server errors, try to extract dataset IDs for better error reporting
                if response.status_code >= 500:
                    try:
                        if response.text:
                            dataset_ids = extract_dataset_ids(response.text)
                            
                        # If no IDs found, try a separate request for just identifiers
                        if not dataset_ids:
                            id_params = params.copy()
                            id_params["fields"] = "identifier"
                            id_url = add_url_params(url, id_params)
                            id_response = requests.get(id_url, verify=False, timeout=5)
                            if id_response.status_code == 200:
                                dataset_ids = extract_dataset_ids(id_response.text)
                                
                    except Exception as e:
                        logger.debug(f"Tentativa de recuperar IDs falhou: {e}")
                
                # Log errors with dataset IDs if available
                if not dataset_ids:
                    logger.warning(f"Erro HTTP {response.status_code} na página {page}.")
                    http_errors.append((page, f"Erro HTTP {response.status_code}", None))
                else:
                    for ds_id in dataset_ids:
                        logger.warning(f"Erro HTTP {response.status_code} na página {page}, dataset: {ds_id}")
                        http_errors.append((page, f"Erro HTTP {response.status_code}", ds_id))
                
                time.sleep(2)  # Backoff before retry
                continue
                
            # Process successful response
            try:
                root = ET.fromstring(response.text)
                if not root:
                    logger.info(f"Página {page} não contém registros.")
                    return True, []
                    
                # Debug: log IDs found in this page
                try:
                    logger.debug(f"IDs encontrados na página {page}: {extract_dataset_ids(response.text)}")
                except Exception as e:
                    logger.debug(f"Não foi possível extrair IDs da página {page}: {e}")
                    
                return True, list(root)
                
            except ET.ParseError as e:
                # Handle XML parsing errors
                dataset_ids = extract_dataset_ids(response.text)
                if dataset_ids:
                    for ds_id in dataset_ids:
                        logger.error(f"Erro ao processar XML: {e} na página {page}, dataset: {ds_id}")
                        http_errors.append((page, f"Erro ao processar XML: {e}", ds_id))
                else:
                    logger.error(f"Erro ao processar XML: {e} da página {page}")
                    http_errors.append((page, f"Erro ao processar XML: {e}", None))
                    
                time.sleep(1)  # Short backoff before retry
                continue
                
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout ao conectar: {e} na página {page}")
            http_errors.append((page, f"Timeout ao conectar: {e}", None))
            time.sleep(3)  # Longer backoff for timeout
            
        except requests.RequestException as e:
            logger.error(f"Erro de conexão: {e} na página {page}")
            http_errors.append((page, f"Erro de conexão: {e}", None))
            time.sleep(2)  # Medium backoff for connection errors
    
    # All retries failed
    logger.error(f"Falha após {max_retries} tentativas na página {page}.")
    return False, None

def fetch_all_data(base_url: str, tag: Optional[str] = None, max_retries: int = 3) -> List:
    """
    Fetch all pages of data from the API.
    
    Args:
        base_url: The base API URL
        tag: Optional tag to filter results
        max_retries: Maximum number of retry attempts per page
        
    Returns:
        List: All fetched records
    """
    page = 1
    all_records = []
    
    print("\nIniciando a extração de dados...")
    print("Pressione CTRL+C a qualquer momento para interromper.")
    
    try:
        # Continue fetching until we reach the end or encounter an error
        while True:
            success, records = fetch_page(base_url, page, tag, max_retries)
            
            # Skip to next page on failure
            if not success:
                logger.warning(f"Pulando para a próxima página após falha na página {page}.")
                page += 1
                continue
                
            # End of results
            if not records:
                break
                
            # Add records to result set
            all_records.extend(records)
            logger.info(f"Página {page}: {len(records)} registros obtidos.")
            page += 1
            
    except KeyboardInterrupt:
        print("\nExtração interrompida pelo usuário.")
        
    logger.info(f"Total de registros obtidos: {len(all_records)}")
    return all_records

def xml_element_to_ttl(element: ET.Element, base_uri: str = "http://example.org/") -> str:
    """
    Convert an XML element to TTL (Turtle) format.
    
    Args:
        element: XML element to convert
        base_uri: Base URI for the RDF resources
        
    Returns:
        str: TTL representation of the element
    """
    ttl_lines = []
    
    # Create a subject URI based on element tag and attributes
    element_id = element.attrib.get('id') or element.attrib.get('identifier', f"item_{id(element)}")
    subject = f"<{base_uri}{element.tag}/{element_id}>"
    
    # Add type information
    ttl_lines.append(f"{subject} a <{base_uri}types/{element.tag}> ;")
    
    # Process child elements
    for child in element:
        predicate = f"<{base_uri}properties/{child.tag.split('}')[-1]}>"
        
        if child.text and child.text.strip():
            # Escape quotes in text
            text_value = child.text.strip().replace('"', '\\"')
            ttl_lines.append(f"    {predicate} \"{text_value}\" ;")
        
        # Process child attributes
        for attr_name, attr_value in child.attrib.items():
            attr_predicate = f"<{base_uri}attributes/{attr_name}>"
            attr_value_escaped = attr_value.replace('"', '\\"')
            ttl_lines.append(f"    {attr_predicate} \"{attr_value_escaped}\" ;")
    
    # Process element attributes
    for attr_name, attr_value in element.attrib.items():
        attr_predicate = f"<{base_uri}attributes/{attr_name}>"
        attr_value_escaped = attr_value.replace('"', '\\"')
        ttl_lines.append(f"    {attr_predicate} \"{attr_value_escaped}\" ;")
    
    # Remove the last semicolon and add a period
    if ttl_lines:
        ttl_lines[-1] = ttl_lines[-1].rstrip(' ;') + ' .'
    
    return '\n'.join(ttl_lines)

def save_results(records: List, output_format: str, output_path: str) -> bool:
    """
    Save fetched records to a file in the specified format.
    
    Args:
        records: List of XML elements to save
        output_format: Format to save in (xml, json, txt, ttl)
        output_path: Path to save the file
        
    Returns:
        bool: True if save was successful, False otherwise
    """
    if not records:
        logger.warning("Nenhum dado para salvar.")
        return False
        
    # Create a root element to contain all records
    root_element = ET.Element("catalog")
    root_element.extend(records)
    
    try:
        if output_format == "xml":
            # Save as XML file
            ET.ElementTree(root_element).write(output_path, encoding="utf-8")
            return True
            
        elif output_format == "json":
            # Convert to JSON and save
            data = {"catalog": [{elem.tag: elem.text for elem in record} for record in records]}
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return True
            
        elif output_format == "ttl":
            # Convert to TTL (Turtle) format and save
            with open(output_path, "w", encoding="utf-8") as f:
                # Write TTL prefixes
                f.write("@prefix : <http://dados.gov.pt/catalog/> .\n")
                f.write("@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n")
                f.write("@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n")
                f.write("@prefix dcat: <http://www.w3.org/ns/dcat#> .\n")
                f.write("@prefix dc: <http://purl.org/dc/elements/1.1/> .\n")
                f.write("@prefix dcterms: <http://purl.org/dc/terms/> .\n\n")
                
                # Convert each record to TTL
                for i, record in enumerate(records):
                    ttl_content = xml_element_to_ttl(record, "http://dados.gov.pt/catalog/")
                    f.write(ttl_content)
                    f.write("\n\n")
                    
            return True
            
        else:  # txt format
            # Save as plain text (serialized XML)
            with open(output_path, "w", encoding="utf-8") as file:
                file.write(ET.tostring(root_element, encoding="utf-8").decode("utf-8"))
            return True
            
    except Exception as e:
        logger.error(f"Erro ao salvar resultados: {e}")
        return False

def save_error_log(errors: List[Tuple[int, str, Optional[str]]]) -> bool:
    """
    Save encountered errors to log files (text and JSON formats).
    
    Args:
        errors: List of tuples (page, error_message, dataset_id)
        
    Returns:
        bool: True if logs were saved successfully, False otherwise
    """
    try:
        # Save text log
        with open(error_log_path, "w", encoding="utf-8") as f:
            for page, msg, dataset_id in errors:
                f.write(f"Página {page} - Erro: {msg} {'(Dataset: ' + dataset_id + ')' if dataset_id else ''}\n")
        
        # Save JSON log
        json_log_path = error_log_path.replace(".log", ".json")
        with open(json_log_path, "w", encoding="utf-8") as f:
            json.dump([{"page": p, "error": m, "dataset_id": did} for p, m, did in errors], f, indent=2)
            
        return True
        
    except Exception as e:
        logger.error(f"Falha ao salvar o log de erros: {e}")
        return False

def display_summary(start_time: float, records_count: int, output_path: str, output_format: str) -> None:
    """
    Display a summary of the operation, including timing, record count, and errors.
    
    Args:
        start_time: The time the operation started
        records_count: Number of records fetched
        output_path: Path where the results were saved
        output_format: Format of the saved file
    """
    elapsed_time = time.time() - start_time
    
    print("\n" + "=" * 60)
    print("RESUMO DA OPERAÇÃO".center(60))
    print("=" * 60)
    
    print(f"• Tempo total: {elapsed_time:.2f} segundos")
    print(f"• Registros obtidos: {records_count}")
    print(f"• Formato de saída: {output_format.upper()}")
    print(f"• Arquivo salvo em: {output_path}")
    
    # Display error summary if any errors occurred
    if http_errors:
        print(f"• Total de erros HTTP: {len(http_errors)}")
        
        # Group errors by page
        errors_by_page = {}
        for page, msg, dataset_id in http_errors:
            errors_by_page.setdefault(page, []).append(
                f"{msg} (Dataset: {dataset_id})" if dataset_id else msg
            )
            
        print("• Erros por página:")
        for i, (page, errors) in enumerate(sorted(errors_by_page.items())):
            # Limit displayed pages to 5
            if i >= 5:
                print(f"  ... e mais {len(errors_by_page) - 5} páginas com erro (veja o arquivo de log)")
                break
                
            print(f"  - Página {page}:")
            # Limit displayed errors per page to 3
            for j, error in enumerate(errors[:3]):
                print(f"    • {error}")
                
            if len(errors) > 3:
                print(f"    • ... e mais {len(errors) - 3} erros")
                
        # Save errors to log files
        if save_error_log(http_errors):
            print(f"• Log de erros detalhado salvo em: {error_log_path}")
            print(f"• Log JSON salvo em: {error_log_path.replace('.log', '.json')}")
        else:
            print(f"❌ Falha ao salvar o log de erros")
    else:
        print("• Nenhum erro HTTP registrado.")
        
    print("=" * 60)

def main():
    """
    Main function that orchestrates the catalog extraction process.
    """
    # Disable SSL warnings for internal/development environments
    import warnings
    warnings.filterwarnings("ignore", message="Unverified HTTPS request")
    
    display_header()
    
    try:
        # Get user inputs
        base_url = get_user_source()
        tag = get_tag_filter()
        output_format = get_output_format()
        output_path = get_output_path(output_format)
        
        # Display and confirm configuration
        print("\nCONFIGURAÇÕES:")
        print(f"• URL: {base_url}")
        print(f"• Tag: {tag or 'Nenhuma'}")
        print(f"• Formato: {output_format.upper()}")
        print(f"• Saída: {output_path}")
        
        if input("\nConfirmar e iniciar a extração? (s/n): ").strip().lower() != "s":
            sys.exit("Operação cancelada pelo usuário.")
            
        # Start data extraction
        start_time = time.time()
        records = fetch_all_data(base_url, tag)
        
        # Save results if any were fetched
        if records:
            if save_results(records, output_format, output_path):
                logger.info(f"Dados salvos com sucesso em: {output_path}")
            else:
                logger.error("Falha ao salvar os dados.")
        else:
            logger.warning("Nenhum dado foi coletado. Nenhum arquivo será gerado.")
            
        # Display operation summary
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