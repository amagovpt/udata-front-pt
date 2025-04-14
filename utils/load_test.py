import requests
import concurrent.futures
import time
import random
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import collections
import sys

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("load_test.log"),
        logging.StreamHandler()
    ]
)

def get_valid_url(prompt_text):
    """Solicita e valida uma URL do usuário"""
    while True:
        url = input(prompt_text).strip()
        
        if not url:
            print("URL não pode estar vazia. Tente novamente.")
            continue
            
        # Adiciona o protocolo se não for fornecido
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        try:
            # Verifica se a URL é válida tentando analisá-la
            parsed = urlparse(url)
            if not parsed.netloc:
                print("URL inválida. Tente novamente.")
                continue
            return url
        except Exception as e:
            print(f"URL inválida: {str(e)}. Tente novamente.")

# Definição de headers comuns de navegadores
BROWSER_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'pt-PT,pt;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Cache-Control': 'max-age=0',
}

# Solicita as informações ao usuário
print("\n===== CONFIGURAÇÃO DO TESTE DE CARGA =====")
BASE_URL = get_valid_url("Digite o IP ou nome do site para teste (ex: exemplo.com ou 10.0.0.1): ")

# Para a página específica, oferece a opção de inserir ou usar a raiz
use_specific = input("Deseja testar uma página específica além da página principal? (s/n): ").lower() == 's'
if use_specific:
    SPECIFIC_PAGE = get_valid_url("Digite a URL completa da página específica: ")
else:
    SPECIFIC_PAGE = BASE_URL

# Configurações do teste
NUM_WORKERS = int(input("Número de acessos simultâneos (padrão: 100): ") or "100")
TIMEOUT = int(input("Timeout para requisições em segundos (padrão: 30): ") or "30")
MAX_URLS_TO_CRAWL = int(input("Máximo de URLs para descobrir (padrão: 30): ") or "30")

# Pergunta se quer usar headers de navegador
use_browser_headers = input("Deseja simular um navegador real? (recomendado) (s/n): ").lower() == 's'

# Lista para armazenar todas as URLs encontradas
all_urls = [SPECIFIC_PAGE]  # Inicia com a URL específica
crawled_urls = set()  # URLs já analisadas
session = requests.Session()

# Configura headers do navegador se solicitado
if use_browser_headers:
    session.headers.update(BROWSER_HEADERS)
    logging.info("Headers de navegador configurados")

# Pergunta sobre a verificação SSL
disable_ssl = input("Deseja desabilitar a verificação SSL? Recomendado para IPs ou certificados autoassinados (s/n): ").lower() == 's'
if disable_ssl:
    session.verify = False
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    logging.info("Verificação SSL desabilitada")

def get_domain(url):
    """Extrai o domínio da URL"""
    parsed_url = urlparse(url)
    return parsed_url.netloc

def is_valid_url(url):
    """Verifica se a URL pertence ao mesmo domínio e não é um recurso estático"""
    if not url:
        return False
    
    # Verifica se é do mesmo domínio
    if get_domain(url) != get_domain(BASE_URL):
        return False
    
    # Ignora recursos estáticos comuns
    extensions = ['.css', '.js', '.jpg', '.jpeg', '.png', '.gif', '.svg', '.ico', '.pdf']
    if any(url.lower().endswith(ext) for ext in extensions):
        return False
        
    return True

def crawl_page(url):
    """Encontra links em uma página"""
    if url in crawled_urls or len(all_urls) >= MAX_URLS_TO_CRAWL:
        return
    
    logging.info(f"Crawling: {url}")
    crawled_urls.add(url)
    
    try:
        response = session.get(url, timeout=TIMEOUT)
        status = response.status_code
        
        if status == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link.get('href')
                full_url = urljoin(url, href)
                
                if is_valid_url(full_url) and full_url not in all_urls:
                    all_urls.append(full_url)
                    logging.debug(f"Added URL: {full_url}")
                    
                    if len(all_urls) >= MAX_URLS_TO_CRAWL:
                        logging.info(f"Reached maximum number of URLs: {MAX_URLS_TO_CRAWL}")
                        return
        else:
            logging.warning(f"Failed to crawl {url}, status code: {status}")
            if status == 500:
                logging.error(f"Erro 500 detectado em: {url}")
                # Tenta extrair o ID de erro se estiver disponível
                try:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    error_text = soup.text
                    if "identificador de erro" in error_text.lower():
                        error_id = error_text.split("identificador de erro é")[1].strip() if "identificador de erro é" in error_text else "Não encontrado"
                        logging.error(f"ID do erro 500: {error_id}")
                except Exception as parse_error:
                    logging.error(f"Não foi possível analisar o conteúdo do erro: {str(parse_error)}")
    except Exception as e:
        logging.error(f"Error crawling {url}: {str(e)}")

def access_url(url, worker_id):
    """Função para acessar uma URL e medir o tempo de resposta"""
    start_time = time.time()
    try:
        response = session.get(url, timeout=TIMEOUT)
        elapsed_time = time.time() - start_time
        status = response.status_code
        
        # Informações de log específicas para diferentes tipos de status
        if 200 <= status < 300:
            logging.info(f"Worker {worker_id}: {url} - Status: {status} (OK) - Time: {elapsed_time:.2f}s")
        elif status == 500:
            logging.error(f"Worker {worker_id}: {url} - Status: {status} (Erro Interno) - Time: {elapsed_time:.2f}s")
            # Tenta extrair o ID de erro se estiver disponível
            try:
                soup = BeautifulSoup(response.text, 'html.parser')
                error_text = soup.text
                if "identificador de erro" in error_text.lower():
                    error_id = error_text.split("identificador de erro é")[1].strip() if "identificador de erro é" in error_text else "Não encontrado"
                    logging.error(f"ID do erro 500: {error_id}")
            except Exception:
                pass
        elif 400 <= status < 500:
            logging.warning(f"Worker {worker_id}: {url} - Status: {status} (Erro Cliente) - Time: {elapsed_time:.2f}s")
        elif 300 <= status < 400:
            logging.info(f"Worker {worker_id}: {url} - Status: {status} (Redirecionamento) - Time: {elapsed_time:.2f}s")
        else:
            logging.warning(f"Worker {worker_id}: {url} - Status: {status} (Não categorizado) - Time: {elapsed_time:.2f}s")
            
        return {
            'url': url,
            'status': status,
            'time': elapsed_time,
            'worker_id': worker_id,
            'success': 200 <= status < 300,
            'error_500': status == 500,
            'client_error': 400 <= status < 500,
            'redirect': 300 <= status < 400,
            'response_size': len(response.content) if hasattr(response, 'content') else 0,
            'content_type': response.headers.get('Content-Type', 'Desconhecido')
        }
    except requests.exceptions.Timeout:
        elapsed_time = time.time() - start_time
        logging.error(f"Worker {worker_id}: {url} - TIMEOUT após {elapsed_time:.2f}s")
        return {
            'url': url,
            'status': None,
            'time': elapsed_time,
            'worker_id': worker_id,
            'success': False,
            'error': 'Timeout',
            'is_timeout': True
        }
    except requests.exceptions.ConnectionError:
        elapsed_time = time.time() - start_time
        logging.error(f"Worker {worker_id}: {url} - ERRO DE CONEXÃO após {elapsed_time:.2f}s")
        return {
            'url': url,
            'status': None,
            'time': elapsed_time,
            'worker_id': worker_id,
            'success': False,
            'error': 'Erro de Conexão',
            'is_connection_error': True
        }
    except Exception as e:
        elapsed_time = time.time() - start_time
        logging.error(f"Worker {worker_id}: {url} - Error: {str(e)} - Time: {elapsed_time:.2f}s")
        return {
            'url': url,
            'status': None,
            'time': elapsed_time,
            'worker_id': worker_id,
            'success': False,
            'error': str(e)
        }

def print_progress(completed, total):
    """Exibe uma barra de progresso simples"""
    bar_length = 30
    filled_length = int(round(bar_length * completed / float(total)))
    percents = round(100.0 * completed / float(total), 1)
    bar = '=' * filled_length + '-' * (bar_length - filled_length)
    sys.stdout.write(f'\r[{bar}] {percents}% ({completed}/{total} requisições)')
    sys.stdout.flush()

def run_load_test():
    """Executa o teste de carga"""
    # Primeiro, vamos descobrir algumas URLs do site
    logging.info("Iniciando crawling para encontrar URLs...")
    try:
        crawl_page(BASE_URL)
        
        # Se encontramos poucas URLs, tentamos crawlear mais páginas
        for url in list(all_urls)[:5]:  # Limita a 5 páginas para evitar muitos requests
            if len(all_urls) < MAX_URLS_TO_CRAWL:
                crawl_page(url)
    except Exception as e:
        logging.error(f"Erro durante o crawling: {str(e)}")
        print(f"\nErro durante o crawling: {str(e)}")
        print("Continuando o teste apenas com as URLs conhecidas...")
    
    # Garante que temos pelo menos a URL base para testar
    if not all_urls:
        all_urls.append(BASE_URL)
    
    logging.info(f"URLs encontradas: {len(all_urls)}")
    for i, url in enumerate(all_urls):
        logging.info(f"URL {i+1}: {url}")
    
    # Preparar as tarefas para o teste de carga
    tasks = []
    for i in range(NUM_WORKERS):
        # Seleciona uma URL aleatória da lista
        url = random.choice(all_urls)
        tasks.append((url, i))
    
    results = []
    start_time = time.time()
    logging.info(f"Iniciando teste de carga com {NUM_WORKERS} trabalhadores simultâneos...")
    print(f"\nIniciando teste de carga com {NUM_WORKERS} trabalhadores simultâneos...")
    
    # Contador para a barra de progresso
    completed_tasks = 0
    
    # Executa as requisições em paralelo
    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
        future_to_url = {executor.submit(access_url, url, worker_id): (url, worker_id) 
                         for url, worker_id in tasks}
        
        for future in concurrent.futures.as_completed(future_to_url):
            url, worker_id = future_to_url[future]
            try:
                result = future.result()
                results.append(result)
                
                # Atualiza a barra de progresso
                completed_tasks += 1
                print_progress(completed_tasks, NUM_WORKERS)
                
            except Exception as e:
                logging.error(f"Worker {worker_id} gerou uma exceção: {str(e)}")
    
    total_time = time.time() - start_time
    print("\n")  # Nova linha após a barra de progresso
    
    # Gera estatísticas
    successful_requests = [r for r in results if r.get('success', False)]
    failed_requests = [r for r in results if not r.get('success', False)]
    error_500_requests = [r for r in results if r.get('error_500', False)]
    client_error_requests = [r for r in results if r.get('client_error', False)]
    redirect_requests = [r for r in results if r.get('redirect', False)]
    timeout_requests = [r for r in results if r.get('is_timeout', False)]
    connection_error_requests = [r for r in results if r.get('is_connection_error', False)]
    
    # Conta os tipos específicos de status code
    status_codes = [r.get('status') for r in results if r.get('status') is not None]
    status_counter = collections.Counter(status_codes)
    
    if results:
        avg_response_time = sum(r['time'] for r in results) / len(results)
        if successful_requests:
            avg_success_time = sum(r['time'] for r in successful_requests) / len(successful_requests)
        else:
            avg_success_time = 0
            
        max_time = max(r['time'] for r in results)
        min_time = min(r['time'] for r in results)
        
        # Calcula o tempo médio para erros 500 se houver
        if error_500_requests:
            avg_500_time = sum(r['time'] for r in error_500_requests) / len(error_500_requests)
        else:
            avg_500_time = 0
    else:
        avg_response_time = avg_success_time = max_time = min_time = avg_500_time = 0
    
    # Relatório final
    logging.info("\n" + "="*60)
    logging.info("RELATÓRIO DETALHADO DO TESTE DE CARGA")
    logging.info("="*60)
    logging.info(f"Site testado: {BASE_URL}")
    logging.info(f"Total de requisições: {len(results)}")
    logging.info(f"Requisições bem-sucedidas (200-299): {len(successful_requests)}")
    logging.info(f"Redirecionamentos (300-399): {len(redirect_requests)}")
    logging.info(f"Erros de cliente (400-499): {len(client_error_requests)}")
    logging.info(f"Erros internos (500): {len(error_500_requests)}")
    logging.info(f"Timeouts: {len(timeout_requests)}")
    logging.info(f"Erros de conexão: {len(connection_error_requests)}")
    logging.info(f"Taxa de sucesso: {len(successful_requests)/len(results)*100 if results else 0:.2f}%")
    
    # Detalha os códigos de status específicos encontrados
    logging.info("\nCódigos de status encontrados:")
    for status, count in sorted(status_counter.items()):
        status_desc = {
            200: "OK",
            301: "Moved Permanently",
            302: "Found/Redirect",
            304: "Not Modified",
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            405: "Method Not Allowed",
            429: "Too Many Requests",
            500: "Internal Server Error",
            502: "Bad Gateway",
            503: "Service Unavailable",
            504: "Gateway Timeout"
        }.get(status, "")
        
        status_desc = f" ({status_desc})" if status_desc else ""
        logging.info(f"  Status {status}{status_desc}: {count} ocorrências ({count/len(status_codes)*100:.1f}%)")
    
    logging.info("\nEstatísticas de tempo:")
    logging.info(f"Tempo total de execução: {total_time:.2f} segundos")
    logging.info(f"Tempo médio de resposta (todos): {avg_response_time:.2f} segundos")
    logging.info(f"Tempo médio de resposta (sucessos): {avg_success_time:.2f} segundos")
    if error_500_requests:
        logging.info(f"Tempo médio de resposta (erro 500): {avg_500_time:.2f} segundos")
    logging.info(f"Tempo máximo de resposta: {max_time:.2f} segundos")
    logging.info(f"Tempo mínimo de resposta: {min_time:.2f} segundos")
    logging.info("="*60)
    
    # Exibe também no console
    print("\n" + "="*60)
    print("RELATÓRIO DETALHADO DO TESTE DE CARGA")
    print("="*60)
    print(f"Site testado: {BASE_URL}")
    print(f"Total de requisições: {len(results)}")
    print(f"Requisições bem-sucedidas (200-299): {len(successful_requests)}")
    print(f"Redirecionamentos (300-399): {len(redirect_requests)}")
    print(f"Erros de cliente (400-499): {len(client_error_requests)}")
    print(f"Erros internos (500): {len(error_500_requests)} {'<-- ATENÇÃO' if error_500_requests else ''}")
    print(f"Timeouts: {len(timeout_requests)}")
    print(f"Erros de conexão: {len(connection_error_requests)}")
    print(f"Taxa de sucesso: {len(successful_requests)/len(results)*100 if results else 0:.2f}%")
    
    # Detalha os códigos de status específicos encontrados
    if status_codes:
        print("\nCódigos de status encontrados:")
        for status, count in sorted(status_counter.items()):
            status_desc = {
                200: "OK",
                301: "Moved Permanently",
                302: "Found/Redirect",
                304: "Not Modified",
                400: "Bad Request",
                401: "Unauthorized",
                403: "Forbidden",
                404: "Not Found",
                405: "Method Not Allowed",
                429: "Too Many Requests",
                500: "Internal Server Error",
                502: "Bad Gateway",
                503: "Service Unavailable",
                504: "Gateway Timeout"
            }.get(status, "")
            
            status_desc = f" ({status_desc})" if status_desc else ""
            print(f"  Status {status}{status_desc}: {count} ocorrências ({count/len(status_codes)*100:.1f}%)")
    
    print("\nEstatísticas de tempo:")
    print(f"Tempo total de execução: {total_time:.2f} segundos")
    print(f"Tempo médio de resposta (todos): {avg_response_time:.2f} segundos")
    print(f"Tempo médio de resposta (sucessos): {avg_success_time:.2f} segundos")
    if error_500_requests:
        print(f"Tempo médio de resposta (erro 500): {avg_500_time:.2f} segundos")
    print(f"Tempo máximo de resposta: {max_time:.2f} segundos")
    print(f"Tempo mínimo de resposta: {min_time:.2f} segundos")
    print("="*60)
    print(f"Detalhes completos salvos no arquivo: load_test.log")
    
    # Se encontrou erros 500, mostra detalhes adicionais
    if error_500_requests:
        print("\nDetalhe das URLs com erro 500:")
        unique_500_urls = set(r['url'] for r in error_500_requests)
        for i, url in enumerate(unique_500_urls):
            count = sum(1 for r in error_500_requests if r['url'] == url)
            print(f"{i+1}. {url} - {count} ocorrências")
    
    return results

if __name__ == "__main__":
    try:
        print("\nIniciando teste de carga...")
        results = run_load_test()
        print("\nTeste de carga concluído.")
    except KeyboardInterrupt:
        print("\nTeste interrompido pelo usuário.")
        logging.warning("Teste interrompido pelo usuário.")
    except Exception as e:
        print(f"\nErro durante a execução do teste: {str(e)}")
        logging.error(f"Erro durante a execução do teste: {str(e)}")