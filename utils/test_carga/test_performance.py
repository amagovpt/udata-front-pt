#!/usr/bin/env python3
"""
Script de teste de performance e estabilidade para udata-front-pt
Valida a eficácia das melhorias no uwsgi/front.ini

Testa:
1. Ausência de erros 502 durante carga
2. Tempo de resposta sob stress
3. Estabilidade durante reciclagem de workers
4. Capacidade de throughput
"""

import sys
import subprocess

# Função para instalar pacotes faltantes
def install_package(package_name):
    """Instala um pacote Python usando pip"""
    print(f"📦 Instalando {package_name}...", flush=True)
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "--quiet", package_name
        ])
        print(f"✅ {package_name} instalado com sucesso!", flush=True)
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Falha ao instalar {package_name}", flush=True)
        return False

# Verificar e instalar dependências
required_packages = {
    'aiohttp': 'aiohttp'
}

missing_packages = []
for import_name, package_name in required_packages.items():
    try:
        __import__(import_name)
    except ImportError:
        missing_packages.append((import_name, package_name))

if missing_packages:
    print("⚠️  Pacotes Python faltantes detectados!")
    print("   Instalando dependências necessárias...\n")
    
    for import_name, package_name in missing_packages:
        if not install_package(package_name):
            print(f"\n❌ ERRO: Não foi possível instalar {package_name}")
            print(f"   Tente instalar manualmente:")
            print(f"   pip3 install {package_name}\n")
            sys.exit(1)
    
    print("\n✅ Todas as dependências instaladas!")
    print("   Reiniciando script...\n")
    
    # Recarregar os módulos instalados
    import importlib
    for import_name, _ in missing_packages:
        try:
            globals()[import_name] = importlib.import_module(import_name)
        except ImportError:
            pass

# Importações principais
import asyncio
import aiohttp
import time
import statistics
from datetime import datetime
from typing import List, Dict, Tuple
from collections import defaultdict


class ProgressBar:
    """Barra de progresso para terminal"""
    def __init__(self, total: int, prefix: str = "", length: int = 50):
        self.total = total
        self.prefix = prefix
        self.length = length
        self.current = 0
        
    def update(self, current: int = None, suffix: str = ""):
        """Atualiza a barra de progresso"""
        if current is not None:
            self.current = current
        else:
            self.current += 1
            
        percent = min(100, int(100 * self.current / self.total))
        filled = int(self.length * self.current / self.total)
        bar = '█' * filled + '░' * (self.length - filled)
        
        # Usa \r para sobrescrever a linha
        sys.stdout.write(f'\r{self.prefix} |{bar}| {percent}% {suffix}')
        sys.stdout.flush()
        
        if self.current >= self.total:
            sys.stdout.write('\n')
            sys.stdout.flush()


class PerformanceTest:
    def __init__(self, base_url: str = "http://dev.local:7000", timeout: int = 30):
        self.base_url = base_url
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        
        # Configurar SSL para aceitar certificados auto-assinados
        import ssl
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
        
        self.results = {
            'total_requests': 0,
            'successful': 0,
            'errors': defaultdict(int),
            'response_times': [],
            'status_codes': defaultdict(int)
        }

    async def make_request(self, session: aiohttp.ClientSession, endpoint: str = "/") -> Tuple[int, float]:
        """Faz uma requisição e retorna (status_code, response_time)"""
        start = time.time()
        try:
            async with session.get(f"{self.base_url}{endpoint}") as response:
                await response.text()
                elapsed = time.time() - start
                return response.status, elapsed
        except asyncio.TimeoutError:
            return 408, time.time() - start
        except aiohttp.ClientError as e:
            return 0, time.time() - start
        except Exception as e:
            return -1, time.time() - start

    async def concurrent_requests(self, num_requests: int, concurrency: int) -> Dict:
        """Executa requisições concorrentes"""
        print(f"\n{'='*60}")
        print(f"🚀 Teste: {num_requests} requisições com concorrência {concurrency}")
        print(f"{'='*60}")
        
        # Barra de progresso
        progress = ProgressBar(num_requests, prefix="Progresso", length=40)
        
        connector = aiohttp.TCPConnector(limit=concurrency, limit_per_host=concurrency, ssl=self.ssl_context)
        async with aiohttp.ClientSession(connector=connector, timeout=self.timeout) as session:
            tasks = []
            for i in range(num_requests):
                # Varia os endpoints para simular tráfego real
                endpoints = ["/", "/api/1/me/", "/api/1/datasets/"]
                endpoint = endpoints[i % len(endpoints)]
                tasks.append(self.make_request(session, endpoint))
            
            start_time = time.time()
            
            # Processa resultados conforme completam com barra de progresso
            completed = 0
            for coro in asyncio.as_completed(tasks):
                result = await coro
                completed += 1
                
                # Atualiza barra com estatísticas em tempo real
                errors_502 = self.results['errors']['502_bad_gateway']
                success_count = self.results['successful']
                suffix = f"✅ {success_count} | ❌502: {errors_502}"
                progress.update(completed, suffix)
                
                # Processa resultado
                if isinstance(result, Exception):
                    self.results['errors']['exception'] += 1
                else:
                    status, response_time = result
                    self.results['total_requests'] += 1
                    self.results['status_codes'][status] += 1
                    self.results['response_times'].append(response_time)
                    
                    if 200 <= status < 400:
                        self.results['successful'] += 1
                    elif status == 502:
                        self.results['errors']['502_bad_gateway'] += 1
                    elif status >= 500:
                        self.results['errors'][f'{status}_server_error'] += 1
                    elif status >= 400:
                        self.results['errors'][f'{status}_client_error'] += 1
            
            total_time = time.time() - start_time
            
            return {
                'total_time': total_time,
                'requests_per_second': num_requests / total_time
            }
    
    async def concurrent_requests_old_processing(self, results_list) -> None:
        """Método auxiliar removido - processamento agora inline"""
        pass
        


    async def sustained_load_test(self, duration_seconds: int = 60, rps: int = 50) -> Dict:
        """Teste de carga sustentada - detecta problemas durante reciclagem de workers"""
        print(f"\n{'='*60}")
        print(f"⏱️  Teste de Carga Sustentada: {duration_seconds}s @ {rps} req/s")
        print(f"{'='*60}")
        
        start_time = time.time()
        total_expected = duration_seconds * rps
        progress = ProgressBar(total_expected, prefix="Progresso", length=40)
        
        connector = aiohttp.TCPConnector(limit=rps, limit_per_host=rps, ssl=self.ssl_context)
        async with aiohttp.ClientSession(connector=connector, timeout=self.timeout) as session:
            iteration_count = 0
            while time.time() - start_time < duration_seconds:
                iteration_start = time.time()
                
                # Faz batch de requisições
                tasks = [self.make_request(session) for _ in range(rps)]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Processa resultados
                for result in results:
                    if isinstance(result, Exception):
                        self.results['errors']['exception'] += 1
                    else:
                        status, response_time = result
                        self.results['total_requests'] += 1
                        self.results['status_codes'][status] += 1
                        self.results['response_times'].append(response_time)
                        
                        if 200 <= status < 400:
                            self.results['successful'] += 1
                        elif status == 502:
                            self.results['errors']['502_bad_gateway'] += 1
                        elif status >= 500:
                            self.results['errors'][f'{status}_server_error'] += 1
                
                # Atualiza barra de progresso
                iteration_count += 1
                elapsed_time = int(time.time() - start_time)
                errors_502 = self.results['errors']['502_bad_gateway']
                success_count = self.results['successful']
                avg_time = statistics.mean(self.results['response_times'][-rps:]) * 1000 if self.results['response_times'] else 0
                
                suffix = f"⏱ {elapsed_time}s | ✅ {success_count} | ❌502: {errors_502} | ⚡ {avg_time:.0f}ms"
                progress.update(min(iteration_count * rps, total_expected), suffix)
                
                # Aguarda para manter a taxa de requisições
                elapsed = time.time() - iteration_start
                if elapsed < 1.0:
                    await asyncio.sleep(1.0 - elapsed)
        
        # Garante que a barra chega a 100%
        progress.update(total_expected)
        
        total_time = time.time() - start_time
        return {
            'total_time': total_time,
            'requests_per_second': self.results['total_requests'] / total_time
        }

    def print_report(self, test_metadata: Dict):
        """Imprime relatório completo dos testes"""
        print(f"\n{'='*60}")
        print(f"📊 RELATÓRIO DE PERFORMANCE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        print(f"\n🎯 Configuração do Teste:")
        print(f"   URL Base: {self.base_url}")
        print(f"   Duração Total: {test_metadata.get('duration', 0):.2f}s")
        
        print(f"\n📈 Estatísticas Gerais:")
        print(f"   Total de Requisições: {self.results['total_requests']}")
        print(f"   Requisições Bem-sucedidas: {self.results['successful']}")
        print(f"   Taxa de Sucesso: {(self.results['successful']/self.results['total_requests']*100):.2f}%")
        print(f"   Throughput Médio: {test_metadata.get('avg_rps', 0):.2f} req/s")
        
        print(f"\n⚡ Tempos de Resposta:")
        if self.results['response_times']:
            rt = self.results['response_times']
            print(f"   Mínimo: {min(rt)*1000:.2f}ms")
            print(f"   Máximo: {max(rt)*1000:.2f}ms")
            print(f"   Média: {statistics.mean(rt)*1000:.2f}ms")
            print(f"   Mediana: {statistics.median(rt)*1000:.2f}ms")
            if len(rt) > 1:
                print(f"   Desvio Padrão: {statistics.stdev(rt)*1000:.2f}ms")
            
            # Percentis
            sorted_rt = sorted(rt)
            p95 = sorted_rt[int(len(sorted_rt) * 0.95)]
            p99 = sorted_rt[int(len(sorted_rt) * 0.99)]
            print(f"   P95: {p95*1000:.2f}ms")
            print(f"   P99: {p99*1000:.2f}ms")
        
        print(f"\n📊 Códigos de Status HTTP:")
        for status, count in sorted(self.results['status_codes'].items()):
            percentage = (count / self.results['total_requests'] * 100)
            emoji = "✅" if 200 <= status < 300 else "⚠️" if 400 <= status < 500 else "❌"
            print(f"   {emoji} {status}: {count} ({percentage:.2f}%)")
        
        print(f"\n❌ Erros Detectados:")
        if self.results['errors']:
            for error_type, count in self.results['errors'].items():
                print(f"   🔴 {error_type}: {count}")
            
            # Dica se muitos erros 404/408
            errors_404 = self.results['errors'].get('404_client_error', 0)
            errors_408 = self.results['errors'].get('408_client_error', 0)
            if errors_404 > self.results['total_requests'] * 0.3:
                print(f"\n   ⚠️  NOTA: Muitos erros 404 - Endpoints não existem ou serviço mal configurado")
            if errors_408 > self.results['total_requests'] * 0.3:
                print(f"   ⚠️  NOTA: Muitos timeouts - Serviço pode estar sobrecarregado ou lento")
        else:
            print(f"   ✅ Nenhum erro detectado!")
        
        # Avaliação final
        print(f"\n{'='*60}")
        print(f"🏆 AVALIAÇÃO FINAL")
        print(f"{'='*60}")
        
        errors_502 = self.results['errors']['502_bad_gateway']
        errors_404 = self.results['errors'].get('404_client_error', 0)
        errors_408 = self.results['errors'].get('408_client_error', 0)
        success_rate = (self.results['successful'] / self.results['total_requests'] * 100) if self.results['total_requests'] > 0 else 0
        avg_response = statistics.mean(self.results['response_times']) * 1000 if self.results['response_times'] else 0
        
        # Detecta se o serviço não está disponível
        if errors_404 + errors_408 > self.results['total_requests'] * 0.5:
            print(f"❌ SERVIÇO INDISPONÍVEL!")
            print(f"   • Mais de 50% das requisições falharam")
            print(f"   • 404 (não encontrado): {errors_404}")
            print(f"   • 408 (timeout): {errors_408}")
            print(f"\n💡 O uData provavelmente não está a correr ou está inacessível")
            print(f"   Verifique se o serviço está ativo antes de executar os testes")
        else:
            issues = []
            if errors_502 > 0:
                issues.append(f"❌ CRÍTICO: {errors_502} erros 502 detectados - workers ainda reiniciam simultaneamente")
            if success_rate < 99.5 and success_rate > 50:
                issues.append(f"⚠️  Taxa de sucesso abaixo de 99.5% ({success_rate:.2f}%)")
            if avg_response > 1000:
                issues.append(f"⚠️  Tempo de resposta médio alto ({avg_response:.2f}ms)")
            
            if not issues and success_rate > 95:
                print(f"✅ EXCELENTE! Sistema estável e performante:")
                print(f"   • Zero erros 502 - Workers reciclam corretamente")
                print(f"   • Taxa de sucesso: {success_rate:.2f}%")
                print(f"   • Tempo médio: {avg_response:.2f}ms")
                print(f"   • Throughput: {test_metadata.get('avg_rps', 0):.2f} req/s")
            else:
                print(f"❌ PROBLEMAS DETECTADOS:")
                for issue in issues:
                    print(f"   {issue}")
        
        print(f"{'='*60}\n")

    async def run_full_test_suite(self):
        """Executa a suite completa de testes"""
        print(f"\n{'#'*60}")
        print(f"# SUITE DE TESTES DE PERFORMANCE - UDATA FRONT PT")
        print(f"# Objetivo: Validar melhorias em uwsgi/front.ini")
        print(f"{'#'*60}")
        
        suite_start = time.time()
        test_results = []
        
        # Teste 1: Burst de requisições (detecta problemas de concorrência)
        result1 = await self.concurrent_requests(num_requests=100, concurrency=20)
        test_results.append(result1)
        
        # Teste 2: Carga moderada sustentada (detecta reciclagem de workers)
        result2 = await self.sustained_load_test(duration_seconds=60, rps=30)
        test_results.append(result2)
        
        # Teste 3: Pico de carga (stress test)
        result3 = await self.concurrent_requests(num_requests=500, concurrency=50)
        test_results.append(result3)
        
        suite_duration = time.time() - suite_start
        avg_rps = sum(r['requests_per_second'] for r in test_results) / len(test_results)
        
        # Relatório final
        self.print_report({
            'duration': suite_duration,
            'avg_rps': avg_rps
        })


async def check_service_availability(base_url: str) -> bool:
    """Verifica se o serviço está disponível antes de executar os testes"""
    print(f"\n🔍 Verificando disponibilidade do serviço em {base_url}...")
    
    try:
        timeout = aiohttp.ClientTimeout(total=10)
        # Configurar SSL para aceitar certificados auto-assinados
        import ssl
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            async with session.get(base_url) as response:
                status = response.status
                
                if status == 200:
                    print(f"   ✅ Serviço disponível (HTTP {status})")
                    return True
                elif status == 302 or status == 301:
                    print(f"   ✅ Serviço disponível (HTTP {status} - Redirecionamento)")
                    return True
                elif status == 404:
                    print(f"   ⚠️  Serviço responde mas endpoint não existe (HTTP 404)")
                    print(f"   💡 Tentando endpoint /api/1/me/ ...")
                    async with session.get(f"{base_url}/api/1/me/") as response2:
                        if response2.status in [200, 401]:
                            print(f"   ✅ API disponível (HTTP {response2.status})")
                            return True
                    print(f"   ❌ Servidor não parece ser uData ou está mal configurado")
                    return False
                elif status >= 500:
                    print(f"   ⚠️  Servidor com erro (HTTP {status})")
                    print(f"   💡 Serviço pode estar a iniciar, aguarde alguns segundos...")
                    return True
                else:
                    print(f"   ⚠️  Resposta inesperada (HTTP {status})")
                    return True
                    
    except asyncio.TimeoutError:
        print(f"   ❌ Timeout ao conectar - Serviço não está disponível")
        print(f"   💡 Certifique-se que o uData está a correr em {base_url}")
        return False
    except aiohttp.ClientConnectorError as e:
        print(f"   ❌ Falha de conexão - Serviço não está a correr")
        print(f"   💡 Inicie o uData primeiro:")
        print(f"      docker-compose up -d")
        print(f"      ou")
        print(f"      docker start <container_udata>")
        return False
    except Exception as e:
        print(f"   ❌ Erro inesperado: {e}")
        return False


async def main():
    """Ponto de entrada principal"""
    # Permite passar URL como argumento
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://dev.local:7000"
    
    print(f"\n{'#'*60}")
    print(f"# TESTE DE PERFORMANCE - UDATA FRONT PT")
    print(f"{'#'*60}")
    print(f"\n🔧 Configuração:")
    print(f"   URL: {base_url}")
    
    # Verifica disponibilidade antes de executar testes
    if not await check_service_availability(base_url):
        print(f"\n{'='*60}")
        print(f"❌ TESTES ABORTADOS")
        print(f"{'='*60}")
        print(f"\n⚠️  O serviço uData não está disponível em {base_url}")
        print(f"\n📋 Checklist:")
        print(f"   1. O container Docker está a correr?")
        print(f"      → docker ps | grep udata")
        print(f"   2. O serviço está no porto correto?")
        print(f"      → netstat -tulpn | grep 7000")
        print(f"   3. Consegue aceder manualmente?")
        print(f"      → curl {base_url}")
        print(f"\n💡 Para iniciar o uData:")
        print(f"   docker-compose up -d")
        print(f"\n")
        sys.exit(2)
    
    print(f"\n✅ Serviço verificado! Iniciando testes...")
    print(f"   Aguarde enquanto os testes são executados...\n")
    
    test = PerformanceTest(base_url=base_url)
    await test.run_full_test_suite()
    
    # Retorna código de saída baseado em erros 502
    errors_502 = test.results['errors']['502_bad_gateway']
    sys.exit(1 if errors_502 > 0 else 0)


if __name__ == "__main__":
    asyncio.run(main())
