#!/usr/bin/env python3
"""
=============================================================================
TESTE DE PERFORMANCE QLD - uData Front PT
=============================================================================
Script robusto para testes de carga em ambiente QLD (Quality Assurance)

Funcionalidades:
- Rampa de carga configuravel (ramp-up/ramp-down)
- Multiplos endpoints com pesos
- SLAs e criterios de aceitacao definidos
- Metricas detalhadas (P50, P95, P99, desvio padrao)
- Relatorio JSON para integracao CI/CD
- Modo interactivo e nao-interactivo
- Deteccao de degradacao de performance
- Think time configuravel

Uso:
    python test_qld.py https://dados.gov.pt --duration 300 --max-rps 100
    python test_qld.py https://dados.gov.pt --profile stress
    python test_qld.py https://dados.gov.pt --ci --output results.json

Autor: Teste QLD para uData
Data: 2025-12-12
=============================================================================
"""

import asyncio
import argparse
import json
import ssl
import sys
import time
import random
import statistics
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Tuple
from collections idict
from enum import Enum

# Verificar e instalar dependencias
try:
    import aiohttp
except ImportError:
    print("[!] A instalar aiohttp...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "aiohttp"])
    import aiohttp


# =============================================================================
# CONFIGURACAO E SLAs
# =============================================================================

class TestProfile(Enum):
    """Perfis de teste pre-definidos"""
    SMOKE = "smoke"           # Teste rapido de sanidade
    LOAD = "load"             # Teste de carga normal
    STRESS = "stress"         # Teste de stress
    ENDURANCE = "endurance"   # Teste de longa duracao
    SPIKE = "spike"           # Teste de picos de carga


@dataclass
class SLA:
    """Service Level Agreement - Criterios de aceitacao"""
    max_error_rate: float = 0.5          # Taxa maxima de erro (%)
    max_p95_ms: float = 2000             # P95 maximo (ms)
    max_p99_ms: float = 5000             # P99 maximo (ms)
    max_avg_ms: float = 1000             # Media maxima (ms)
    max_502_rate: float = 0.1            # Taxa maxima de 502 (%)
    min_success_rate: float = 99.0       # Taxa minima de sucesso (%)


@dataclass
class TestConfig:
    """Configuracao do teste"""
    base_url: str
    duration_seconds: int = 300          # 5 minutos por defeito
    max_rps: int = 100                   # Requests por segundo maximo
    ramp_up_seconds: int = 60            # Tempo de rampa subida
    ramp_down_seconds: int = 30          # Tempo de rampa descida
    think_time_ms: Tuple[int, int] = (100, 500)  # Think time min/max
    timeout_seconds: int = 30            # Timeout por request
    sla: SLA = field(default_factory=SLA)
    profile: TestProfile = TestProfile.LOAD


# Perfis pre-definidos
PROFILES = {
    TestProfile.SMOKE: TestConfig(
        base_url="",
        duration_seconds=60,
        max_rps=20,
        ramp_up_seconds=10,
        ramp_down_seconds=5,
    ),
    TestProfile.LOAD: TestConfig(
        base_url="",
        duration_seconds=300,
        max_rps=100,
        ramp_up_seconds=60,
        ramp_down_seconds=30,
    ),
    TestProfile.STRESS: TestConfig(
        base_url="",
        duration_seconds=300,
        max_rps=200,
        ramp_up_seconds=30,
        ramp_down_seconds=30,
        sla=SLA(max_error_rate=2.0, max_502_rate=1.0),
    ),
    TestProfile.ENDURANCE: TestConfig(
        base_url="",
        duration_seconds=900,  # 15 minutos
        max_rps=50,
        ramp_up_seconds=60,
        ramp_down_seconds=60,
    ),
    TestProfile.SPIKE: TestConfig(
        base_url="",
        duration_seconds=180,
        max_rps=300,
        ramp_up_seconds=5,    # Rampa muito rapida
        ramp_down_seconds=5,
    ),
}


# =============================================================================
# ENDPOINTS E CENARIOS
# =============================================================================

# Endpoints com pesos (quanto maior o peso, mais frequente)
ENDPOINTS = [
    # Paginas principais
    {"path": "/pt/", "weight": 30, "name": "Homepage"},
    {"path": "/pt/datasets/", "weight": 20, "name": "Lista Datasets"},
    {"path": "/pt/organizations/", "weight": 10, "name": "Lista Organizacoes"},
    {"path": "/pt/reuses/", "weight": 5, "name": "Lista Reutilizacoes"},

    # API endpoints
    {"path": "/api/1/datasets/", "weight": 15, "name": "API Datasets"},
    {"path": "/api/1/organizations/", "weight": 10, "name": "API Organizacoes"},
    {"path": "/api/1/reuses/", "weight": 5, "name": "API Reutilizacoes"},

    # Pesquisa
    {"path": "/pt/datasets/?q=dados", "weight": 5, "name": "Pesquisa Datasets"},
]


# =============================================================================
# METRICAS E RESULTADOS
# =============================================================================

@dataclass
class RequestResult:
    """Resultado de um pedido individual"""
    timestamp: float
    endpoint: str
    status_code: int
    response_time_ms: float
    success: bool
    error: Optional[str] = None


@dataclass
class PhaseMetrics:
    """Metricas de uma fase do teste"""
    phase: str
    start_time: float
    end_time: float
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    errors_502: int = 0
    response_times: List[float] = field(default_factory=list)
    status_codes: Dict[int, int] = field(default_factory=lambda: defaultdict(int))
    errors: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    rps_achieved: float = 0.0


@dataclass
class TestResults:
    """Resultados completos do teste"""
    config: Dict
    start_time: str
    end_time: str
    duration_seconds: float
    total_requests: int
    successful_requests: int
    failed_requests: int

    # Taxas
    success_rate: float
    error_rate: float
    error_502_rate: float

    # Tempos de resposta
    min_response_ms: float
    max_response_ms: float
    avg_response_ms: float
    median_response_ms: float
    p50_response_ms: float
    p75_response_ms: float
    p90_response_ms: float
    p95_response_ms: float
    p99_response_ms: float
    std_dev_ms: float

    # Throughput
    avg_rps: float
    max_rps: float

    # Status codes
    status_codes: Dict[int, int]
    errors: Dict[str, int]

    # Por endpoint
    endpoint_stats: Dict[str, Dict]

    # Fases
    phases: List[Dict]

    # SLA
    sla_passed: bool
    sla_violations: List[str]

    # Tendencia (para detectar degradacao)
    performance_trend: str  # "stable", "degrading", "improving"


# =============================================================================
# MOTOR DE TESTE
# =============================================================================

class QldLoadTester:
    """Motor principal de testes de carga para QLD"""

    def __init__(self, config: TestConfig, verbose: bool = True):
        self.config = config
        self.verbose = verbose
        self.results: List[RequestResult] = []
        self.phase_metrics: List[PhaseMetrics] = []
        self.current_rps = 0
        self.start_time = 0
        self._stop_flag = False

        # SSL context para certificados auto-assinados
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE

        # Headers
        self.headers = {
            "User-Agent": "QLD-LoadTester/1.0 (Performance Test)",
            "Accept": "text/html,application/json",
            "Accept-Language": "pt-PT,pt;q=0.9,en;q=0.8",
        }

        # Weighted endpoints
        self._build_weighted_endpoints()

    def _build_weighted_endpoints(self):
        """Constroi lista de endpoints com pesos"""
        self.weighted_endpoints = []
        for ep in ENDPOINTS:
            self.weighted_endpoints.extend([ep] * ep["weight"])

    def _get_random_endpoint(self) -> Dict:
        """Selecciona endpoint aleatorio baseado nos pesos"""
        return random.choice(self.weighted_endpoints)

    def _calculate_target_rps(self, elapsed: float) -> int:
        """Calcula RPS alvo baseado na fase actual (rampa)"""
        duration = self.config.duration_seconds
        ramp_up = self.config.ramp_up_seconds
        ramp_down = self.config.ramp_down_seconds
        max_rps = self.config.max_rps

        # Fase de ramp-up
        if elapsed < ramp_up:
            progress = elapsed / ramp_up
            return max(1, int(max_rps * progress))

        # Fase de ramp-down
        elif elapsed > (duration - ramp_down):
            remaining = duration - elapsed
            progress = remaining / ramp_down
            return max(1, int(max_rps * progress))

        # Fase de carga sustentada
        else:
            return max_rps

    def _get_current_phase(self, elapsed: float) -> str:
        """Retorna a fase actual do teste"""
        duration = self.config.duration_seconds
        ramp_up = self.config.ramp_up_seconds
        ramp_down = self.config.ramp_down_seconds

        if elapsed < ramp_up:
            return "ramp_up"
        elif elapsed > (duration - ramp_down):
            return "ramp_down"
        else:
            return "sustained"

    async def _make_request(self, session: aiohttp.ClientSession) -> RequestResult:
        """Faz um pedido HTTP e retorna o resultado"""
        endpoint = self._get_random_endpoint()
        url = f"{self.config.base_url}{endpoint['path']}"

        start = time.time()
        timestamp = start - self.start_time

        try:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout_seconds)
            async with session.get(url, timeout=timeout, ssl=self.ssl_context) as response:
                await response.read()
                elapsed_ms = (time.time() - start) * 1000

                return RequestResult(
                    timestamp=timestamp,
                    endpoint=endpoint['name'],
                    status_code=response.status,
                    response_time_ms=elapsed_ms,
                    success=200 <= response.status < 400,
                )

        except asyncio.TimeoutError:
            return RequestResult(
                timestamp=timestamp,
                endpoint=endpoint['name'],
                status_code=408,
                response_time_ms=(time.time() - start) * 1000,
                success=False,
                error="timeout",
            )

        except aiohttp.ClientError as e:
            return RequestResult(
                timestamp=timestamp,
                endpoint=endpoint['name'],
                status_code=0,
                response_time_ms=(time.time() - start) * 1000,
                success=False,
                error=str(type(e).__name__),
            )

        except Exception as e:
            return RequestResult(
                timestamp=timestamp,
                endpoint=endpoint['name'],
                status_code=-1,
                response_time_ms=(time.time() - start) * 1000,
                success=False,
                error=str(e)[:50],
            )

    async def _worker(self, session: aiohttp.ClientSession, worker_id: int):
        """Worker que executa pedidos continuamente"""
        while not self._stop_flag:
            # Think time
            think_min, think_max = self.config.think_time_ms
            think_time = random.randint(think_min, think_max) / 1000

            result = await self._make_request(session)
            self.results.append(result)

            # Aguarda think time
            await asyncio.sleep(think_time)

    def _print_progress(self, elapsed: float, total_reqs: int, errors_502: int,
                        success_rate: float, avg_time: float):
        """Imprime progresso do teste"""
        if not self.verbose:
            return

        duration = self.config.duration_seconds
        progress = min(100, int(elapsed / duration * 100))
        phase = self._get_current_phase(elapsed)
        target_rps = self._calculate_target_rps(elapsed)

        bar_len = 30
        filled = int(bar_len * progress / 100)
        bar = "=" * filled + ">" + " " * (bar_len - filled - 1)

        phase_icon = {"ramp_up": "/", "sustained": "=", "ramp_down": "\\"}[phase]

        print(f"\r[{bar}] {progress:3d}% | "
              f"Fase: {phase_icon} | "
              f"RPS: {target_rps:3d} | "
              f"Reqs: {total_reqs:5d} | "
              f"502: {errors_502:3d} | "
              f"OK: {success_rate:5.1f}% | "
              f"Avg: {avg_time:6.0f}ms", end="", flush=True)

    async def run(self) -> TestResults:
        """Executa o teste completo"""
        print("\n" + "=" * 70)
        print("  TESTE DE PERFORMANCE QLD - uData Front PT")
        print("=" * 70)
        print(f"\n  URL:      {self.config.base_url}")
        print(f"  Perfil:   {self.config.profile.value}")
        print(f"  Duracao:  {self.config.duration_seconds}s")
        print(f"  Max RPS:  {self.config.max_rps}")
        print(f"  Ramp-up:  {self.config.ramp_up_seconds}s")
        print(f"  Ramp-dn:  {self.config.ramp_down_seconds}s")
        print(f"  Timeout:  {self.config.timeout_seconds}s")
        print("\n  SLAs:")
        print(f"    - Taxa erro max:    {self.config.sla.max_error_rate}%")
        print(f"    - Taxa 502 max:     {self.config.sla.max_502_rate}%")
        print(f"    - P95 max:          {self.config.sla.max_p95_ms}ms")
        print(f"    - P99 max:          {self.config.sla.max_p99_ms}ms")
        print(f"    - Media max:        {self.config.sla.max_avg_ms}ms")
        print(f"    - Sucesso min:      {self.config.sla.min_success_rate}%")
        print("\n" + "-" * 70)
        print("  A iniciar teste...\n")

        self.start_time = time.time()
        self.results = []
        self._stop_flag = False

        # Cria connector com limite de conexoes baseado no RPS
        connector = aiohttp.TCPConnector(
            limit=self.config.max_rps * 2,
            limit_per_host=self.config.max_rps * 2,
            ssl=self.ssl_context,
        )

        async with aiohttp.ClientSession(
            connector=connector,
            headers=self.headers,
        ) as session:

            # Loop principal com controlo de RPS
            duration = self.config.duration_seconds
            last_progress_time = 0

            while True:
                elapsed = time.time() - self.start_time

                if elapsed >= duration:
                    self._stop_flag = True
                    break

                # Calcula quantos pedidos fazer nesta iteracao
                target_rps = self._calculate_target_rps(elapsed)

                # Executa batch de pedidos
                tasks = [self._make_request(session) for _ in range(target_rps)]
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)

                for result in batch_results:
                    if isinstance(result, RequestResult):
                        self.results.append(result)

                # Actualiza progresso a cada segundo
                if elapsed - last_progress_time >= 1:
                    last_progress_time = elapsed

                    total = len(self.results)
                    errors_502 = sum(1 for r in self.results if r.status_code == 502)
                    successes = sum(1 for r in self.results if r.success)
                    success_rate = (successes / total * 100) if total > 0 else 0

                    times = [r.response_time_ms for r in self.results[-100:] if r.response_time_ms > 0]
                    avg_time = statistics.mean(times) if times else 0

                    self._print_progress(elapsed, total, errors_502, success_rate, avg_time)

                # Aguarda para manter o RPS
                iteration_time = time.time() - self.start_time - elapsed
                sleep_time = max(0, 1.0 - iteration_time)
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)

        print("\n\n" + "-" * 70)
        print("  Teste concluido. A processar resultados...")

        return self._process_results()

    def _process_results(self) -> TestResults:
        """Processa resultados e gera relatorio"""
        if not self.results:
            raise ValueError("Nenhum resultado para processar")

        end_time = time.time()
        duration = end_time - self.start_time

        # Estatisticas basicas
        total = len(self.results)
        successes = sum(1 for r in self.results if r.success)
        failures = total - successes
        errors_502 = sum(1 for r in self.results if r.status_code == 502)

        # Tempos de resposta (apenas pedidos com resposta)
        times = [r.response_time_ms for r in self.results if r.response_time_ms > 0]
        times_sorted = sorted(times)

        def percentile(data, p):
            if not data:
                return 0
            idx = int(len(data) * p / 100)
            return data[min(idx, len(data) - 1)]

        # Status codes
        status_codes = defaultdict(int)
        for r in self.results:
            status_codes[r.status_code] += 1

        # Erros por tipo
        errors = defaultdict(int)
        for r in self.results:
            if r.error:
                errors[r.error] += 1

        # Estatisticas por endpoint
        endpoint_stats = {}
        for ep in ENDPOINTS:
            ep_results = [r for r in self.results if r.endpoint == ep["name"]]
            if ep_results:
                ep_times = [r.response_time_ms for r in ep_results if r.response_time_ms > 0]
                ep_times_sorted = sorted(ep_times) if ep_times else [0]
                ep_successes = sum(1 for r in ep_results if r.success)

                endpoint_stats[ep["name"]] = {
                    "total": len(ep_results),
                    "success": ep_successes,
                    "success_rate": ep_successes / len(ep_results) * 100 if ep_results else 0,
                    "avg_ms": statistics.mean(ep_times) if ep_times else 0,
                    "p95_ms": percentile(ep_times_sorted, 95),
                    "errors_502": sum(1 for r in ep_results if r.status_code == 502),
                }

        # Calcula taxas
        success_rate = successes / total * 100 if total > 0 else 0
        error_rate = failures / total * 100 if total > 0 else 0
        error_502_rate = errors_502 / total * 100 if total > 0 else 0

        # Throughput
        avg_rps = total / duration if duration > 0 else 0

        # Calcula RPS por segundo para encontrar o maximo
        rps_per_second = defaultdict(int)
        for r in self.results:
            second = int(r.timestamp)
            rps_per_second[second] += 1
        max_rps = max(rps_per_second.values()) if rps_per_second else 0

        # Analisa tendencia de performance (ultimos 20% vs primeiros 20%)
        if len(times) > 100:
            first_20pct = times[:len(times)//5]
            last_20pct = times[-len(times)//5:]

            avg_first = statistics.mean(first_20pct)
            avg_last = statistics.mean(last_20pct)

            if avg_last > avg_first * 1.2:
                trend = "degrading"
            elif avg_last < avg_first * 0.8:
                trend = "improving"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"

        # Verifica SLAs
        sla = self.config.sla
        violations = []

        p95 = percentile(times_sorted, 95)
        p99 = percentile(times_sorted, 99)
        avg = statistics.mean(times) if times else 0

        if error_rate > sla.max_error_rate:
            violations.append(f"Taxa de erro {error_rate:.2f}% > {sla.max_error_rate}%")
        if error_502_rate > sla.max_502_rate:
            violations.append(f"Taxa 502 {error_502_rate:.2f}% > {sla.max_502_rate}%")
        if p95 > sla.max_p95_ms:
            violations.append(f"P95 {p95:.0f}ms > {sla.max_p95_ms}ms")
        if p99 > sla.max_p99_ms:
            violations.append(f"P99 {p99:.0f}ms > {sla.max_p99_ms}ms")
        if avg > sla.max_avg_ms:
            violations.append(f"Media {avg:.0f}ms > {sla.max_avg_ms}ms")
        if success_rate < sla.min_success_rate:
            violations.append(f"Taxa sucesso {success_rate:.2f}% < {sla.min_success_rate}%")

        return TestResults(
            config={
                "base_url": self.config.base_url,
                "profile": self.config.profile.value,
                "duration_seconds": self.config.duration_seconds,
                "max_rps": self.config.max_rps,
                "ramp_up_seconds": self.config.ramp_up_seconds,
                "ramp_down_seconds": self.config.ramp_down_seconds,
            },
            start_time=datetime.fromtimestamp(self.start_time).isoformat(),
            end_time=datetime.fromtimestamp(end_time).isoformat(),
            duration_seconds=duration,
            total_requests=total,
            successful_requests=successes,
            failed_requests=failures,
            success_rate=success_rate,
            error_rate=error_rate,
            error_502_rate=error_502_rate,
            min_response_ms=min(times) if times else 0,
            max_response_ms=max(times) if times else 0,
            avg_response_ms=avg,
            median_response_ms=percentile(times_sorted, 50),
            p50_response_ms=percentile(times_sorted, 50),
            p75_response_ms=percentile(times_sorted, 75),
            p90_response_ms=percentile(times_sorted, 90),
            p95_response_ms=p95,
            p99_response_ms=p99,
            std_dev_ms=statistics.stdev(times) if len(times) > 1 else 0,
            avg_rps=avg_rps,
            max_rps=max_rps,
            status_codes=dict(status_codes),
            errors=dict(errors),
            endpoint_stats=endpoint_stats,
            phases=[],  # TODO: implementar metricas por fase
            sla_passed=len(violations) == 0,
            sla_violations=violations,
            performance_trend=trend,
        )


# =============================================================================
# RELATORIO
# =============================================================================

def print_report(results: TestResults):
    """Imprime relatorio detalhado"""

    print("\n" + "=" * 70)
    print("  RELATORIO DE RESULTADOS")
    print("=" * 70)

    # Resumo
    print(f"\n  RESUMO")
    print(f"  " + "-" * 40)
    print(f"  Inicio:       {results.start_time}")
    print(f"  Fim:          {results.end_time}")
    print(f"  Duracao:      {results.duration_seconds:.1f}s")
    print(f"  Total Reqs:   {results.total_requests:,}")
    print(f"  Sucesso:      {results.successful_requests:,} ({results.success_rate:.2f}%)")
    print(f"  Falhas:       {results.failed_requests:,} ({results.error_rate:.2f}%)")
    print(f"  Erros 502:    {results.status_codes.get(502, 0):,} ({results.error_502_rate:.2f}%)")

    # Throughput
    print(f"\n  THROUGHPUT")
    print(f"  " + "-" * 40)
    print(f"  RPS Medio:    {results.avg_rps:.1f} req/s")
    print(f"  RPS Maximo:   {results.max_rps} req/s")

    # Tempos de resposta
    print(f"\n  TEMPOS DE RESPOSTA")
    print(f"  " + "-" * 40)
    print(f"  Minimo:       {results.min_response_ms:.0f}ms")
    print(f"  Maximo:       {results.max_response_ms:.0f}ms")
    print(f"  Media:        {results.avg_response_ms:.0f}ms")
    print(f"  Mediana:      {results.median_response_ms:.0f}ms")
    print(f"  Desvio Pad:   {results.std_dev_ms:.0f}ms")
    print(f"  P50:          {results.p50_response_ms:.0f}ms")
    print(f"  P75:          {results.p75_response_ms:.0f}ms")
    print(f"  P90:          {results.p90_response_ms:.0f}ms")
    print(f"  P95:          {results.p95_response_ms:.0f}ms")
    print(f"  P99:          {results.p99_response_ms:.0f}ms")

    # Status codes
    print(f"\n  CODIGOS HTTP")
    print(f"  " + "-" * 40)
    for code, count in sorted(results.status_codes.items()):
        pct = count / results.total_requests * 100
        icon = "[OK]" if 200 <= code < 400 else "[!!]" if code >= 500 else "[--]"
        print(f"  {icon} {code}: {count:,} ({pct:.2f}%)")

    # Erros
    if results.errors:
        print(f"\n  ERROS")
        print(f"  " + "-" * 40)
        for error, count in sorted(results.errors.items(), key=lambda x: -x[1]):
            print(f"  - {error}: {count:,}")

    # Por endpoint
    print(f"\n  POR ENDPOINT")
    print(f"  " + "-" * 40)
    for name, stats in sorted(results.endpoint_stats.items(), key=lambda x: -x[1]["total"]):
        print(f"  {name}:")
        print(f"    Reqs: {stats['total']:,} | OK: {stats['success_rate']:.1f}% | "
              f"Avg: {stats['avg_ms']:.0f}ms | P95: {stats['p95_ms']:.0f}ms | "
              f"502: {stats['errors_502']}")

    # Tendencia
    print(f"\n  TENDENCIA DE PERFORMANCE")
    print(f"  " + "-" * 40)
    trend_msg = {
        "stable": "[OK] Performance estavel ao longo do teste",
        "degrading": "[!!] Performance DEGRADOU durante o teste (possivel memory leak)",
        "improving": "[OK] Performance melhorou durante o teste (warm-up)",
        "insufficient_data": "[--] Dados insuficientes para analise de tendencia",
    }
    print(f"  {trend_msg.get(results.performance_trend, results.performance_trend)}")

    # SLA
    print(f"\n  VALIDACAO SLA")
    print(f"  " + "-" * 40)
    if results.sla_passed:
        print(f"  [PASSOU] Todos os SLAs foram cumpridos!")
    else:
        print(f"  [FALHOU] Violacoes de SLA detectadas:")
        for v in results.sla_violations:
            print(f"    - {v}")

    # Veredicto final
    print("\n" + "=" * 70)
    if results.sla_passed and results.error_502_rate == 0:
        print("  [PASSOU] TESTE QLD APROVADO")
    elif results.sla_passed:
        print("  [AVISO]  TESTE PASSOU MAS COM ERROS 502")
    else:
        print("  [FALHOU] TESTE QLD REPROVADO")
    print("=" * 70 + "\n")


def save_results(results: TestResults, output_file: str):
    """Guarda resultados em JSON"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(asdict(results), f, indent=2, ensure_ascii=False)
    print(f"  Resultados guardados em: {output_file}")


# =============================================================================
# VERIFICACAO DE SERVICO
# =============================================================================

async def check_service(url: str) -> bool:
    """Verifica se o servico esta disponivel"""
    print(f"\n  A verificar servico em {url}...")

    ssl_ctx = ssl.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE

    try:
        timeout = aiohttp.ClientTimeout(total=10)
        connector = aiohttp.TCPConnector(ssl=ssl_ctx)
        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            async with session.get(url) as response:
                if response.status in [200, 301, 302]:
                    print(f"  [OK] Servico disponivel (HTTP {response.status})")
                    return True
                elif response.status == 502:
                    print(f"  [!!] Servico com erros 502 - teste podera falhar")
                    return True
                else:
                    print(f"  [??] Resposta inesperada: HTTP {response.status}")
                    return True
    except Exception as e:
        print(f"  [ERRO] Nao foi possivel conectar: {e}")
        return False


# =============================================================================
# MAIN
# =============================================================================

def parse_args():
    """Parse argumentos da linha de comando"""
    parser = argparse.ArgumentParser(
        description="Teste de Performance QLD para uData Front PT",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  %(prog)s https://dados.gov.pt
  %(prog)s https://dados.gov.pt --profile stress
  %(prog)s https://dados.gov.pt --duration 600 --max-rps 150
  %(prog)s https://dados.gov.pt --ci --output results.json
        """
    )

    parser.add_argument("url", help="URL base do servico a testar")

    parser.add_argument("--profile", "-p",
                        choices=["smoke", "load", "stress", "endurance", "spike"],
                        default="load",
                        help="Perfil de teste pre-definido (default: load)")

    parser.add_argument("--duration", "-d", type=int,
                        help="Duracao do teste em segundos")

    parser.add_argument("--max-rps", "-r", type=int,
                        help="Maximo de requests por segundo")

    parser.add_argument("--ramp-up", type=int,
                        help="Tempo de ramp-up em segundos")

    parser.add_argument("--ramp-down", type=int,
                        help="Tempo de ramp-down em segundos")

    parser.add_argument("--timeout", "-t", type=int, default=30,
                        help="Timeout por request em segundos (default: 30)")

    parser.add_argument("--output", "-o",
                        help="Ficheiro JSON para guardar resultados")

    parser.add_argument("--ci", action="store_true",
                        help="Modo CI/CD (menos verbose, exit code baseado em SLA)")

    parser.add_argument("--quiet", "-q", action="store_true",
                        help="Modo silencioso (apenas resultado final)")

    # SLA overrides
    parser.add_argument("--sla-error-rate", type=float,
                        help="Taxa maxima de erro (%%)")
    parser.add_argument("--sla-502-rate", type=float,
                        help="Taxa maxima de erros 502 (%%)")
    parser.add_argument("--sla-p95", type=float,
                        help="P95 maximo (ms)")
    parser.add_argument("--sla-p99", type=float,
                        help="P99 maximo (ms)")

    return parser.parse_args()


async def main():
    """Ponto de entrada principal"""
    args = parse_args()

    # Selecciona perfil base
    profile = TestProfile(args.profile)
    config = TestConfig(
        base_url=args.url.rstrip('/'),
        duration_seconds=PROFILES[profile].duration_seconds,
        max_rps=PROFILES[profile].max_rps,
        ramp_up_seconds=PROFILES[profile].ramp_up_seconds,
        ramp_down_seconds=PROFILES[profile].ramp_down_seconds,
        timeout_seconds=args.timeout,
        sla=SLA(
            max_error_rate=PROFILES[profile].sla.max_error_rate,
            max_502_rate=PROFILES[profile].sla.max_502_rate,
            max_p95_ms=PROFILES[profile].sla.max_p95_ms,
            max_p99_ms=PROFILES[profile].sla.max_p99_ms,
        ),
        profile=profile,
    )

    # Aplica overrides
    if args.duration:
        config.duration_seconds = args.duration
    if args.max_rps:
        config.max_rps = args.max_rps
    if args.ramp_up:
        config.ramp_up_seconds = args.ramp_up
    if args.ramp_down:
        config.ramp_down_seconds = args.ramp_down
    if args.sla_error_rate:
        config.sla.max_error_rate = args.sla_error_rate
    if args.sla_502_rate:
        config.sla.max_502_rate = args.sla_502_rate
    if args.sla_p95:
        config.sla.max_p95_ms = args.sla_p95
    if args.sla_p99:
        config.sla.max_p99_ms = args.sla_p99

    # Verifica servico
    if not await check_service(config.base_url):
        print("\n  [ERRO] Servico nao disponivel. Abortando.\n")
        sys.exit(2)

    # Executa teste
    verbose = not args.quiet and not args.ci
    tester = QldLoadTester(config, verbose=verbose)

    try:
        results = await tester.run()
    except KeyboardInterrupt:
        print("\n\n  [!!] Teste interrompido pelo utilizador\n")
        sys.exit(130)

    # Imprime relatorio
    if not args.quiet:
        print_report(results)

    # Guarda resultados
    if args.output:
        save_results(results, args.output)

    # Exit code para CI/CD
    if args.ci:
        if results.sla_passed:
            print("QLD_RESULT=PASSED")
            sys.exit(0)
        else:
            print("QLD_RESULT=FAILED")
            for v in results.sla_violations:
                print(f"QLD_VIOLATION={v}")
            sys.exit(1)
    else:
        sys.exit(0 if results.sla_passed else 1)


if __name__ == "__main__":
    asyncio.run(main())
