
from __future__ import annotations

import os
import re
import time
import random
import shutil
import tempfile
import unicodedata
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

import requests
from flask import current_app

from udata.models import Resource, License
from udata.harvest.backends.base import BaseBackend
from udata.harvest.exceptions import HarvestSkipException
from udata.harvest.models import HarvestItem

from .tools.harvester_utils import normalize_url_slashes


class INEBackend(BaseBackend):
    """
    Harvester INE otimizado e robusto contra bloqueios de escrita no MongoDB.

    Features:
    - Processamento sequencial (evita contenção/locks do Mongo e do pipeline udata).
    - Fonte preferencial: /home/babel/workspace/temp/INE.xml
      - Se existir: usa local
      - Se não existir: baixa da web e salva nesse caminho
      - Não remove no final
    - Parsing com XMLPullParser em chunks: mostra progresso antes do primeiro </indicator>.
    - Watchdog/timeout por dataset: se um dataset "travar" em save/hook, aborta e continua.
    - Normalização de tags na extração (tags_norm) e comparação barata (resource_sig).
    - Consistência de tags: sempre 'ine-pt' (não usa 'ine.pt').
    - save_job batching para reduzir overhead de persistência do job.
    """

    display_name = "Instituto nacional de estatística"

    MAX_RETRIES = 5
    INITIAL_RETRY_DELAY = 2
    MAX_RETRY_DELAY = 60
    TIMEOUT_CONNECT = 15
    TIMEOUT_READ = 300

    INE_XML_PATH = "/home/babel/workspace/temp/INE.xml"

    HVD_INDICATOR_IDS: set[str] = set()

    _KW_SPLIT_RE = re.compile(r"\s*(?:;|,|/|\n|\r|\t|\s+-\s+)\s*")
    _NON_ALNUM_DASH_RE = re.compile(r"[^a-z0-9\-]+")
    _MULTI_DASH_RE = re.compile(r"\-+")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # save_job batching
        self._save_job_counter = 0
        self._save_job_interval = int(os.getenv("INE_SAVE_JOB_INTERVAL", "50"))
        self._original_save_job = super().save_job

        # logging/parsing tuning
        self._log_every = int(os.getenv("INE_LOG_EVERY", "50"))  # datasets
        self._progress_interval_s = int(os.getenv("INE_PROGRESS_INTERVAL_S", "10"))  # segundos
        self._chunk_size = int(os.getenv("INE_XML_CHUNK_SIZE", str(1024 * 1024)))  # 1MB

        # watchdog por dataset (segundos)
        # se queres mesmo agressivo p/ 2s, põe INE_DATASET_TIMEOUT_S=10/20
        self._dataset_timeout_s = int(os.getenv("INE_DATASET_TIMEOUT_S", "120"))

        # cache licença
        self._cc_by_license = None

        # session HTTP
        self._session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(pool_connections=16, pool_maxsize=16, max_retries=0)
        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)

        # logger
        try:
            self._log = current_app.logger
        except Exception:
            import logging
            self._log = logging.getLogger(__name__)

        self._log.info(
            "[INE] sequencial + watchdog ativo. save_job_interval=%s log_every=%s timeout_dataset=%ss xml_path=%s chunk=%sKB",
            self._save_job_interval, self._log_every, self._dataset_timeout_s, self.INE_XML_PATH, int(self._chunk_size / 1024)
        )

    # --------------------------
    # save_job batching
    # --------------------------
    def save_job(self):
        self._save_job_counter += 1
        if self._save_job_counter % self._save_job_interval == 0:
            self._original_save_job()

    # --------------------------
    # HTTP com retry
    # --------------------------
    def _make_request_with_retry(self, url: str, headers=None, stream=True, **kwargs):
        if headers is None:
            headers = {}
        if "timeout" not in kwargs:
            kwargs["timeout"] = (self.TIMEOUT_CONNECT, self.TIMEOUT_READ)

        delay = self.INITIAL_RETRY_DELAY
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                resp = self._session.get(url, headers=headers, stream=stream, **kwargs)
                resp.raise_for_status()
                return resp
            except (requests.exceptions.ConnectionError,
                    requests.exceptions.Timeout,
                    requests.exceptions.ChunkedEncodingError,
                    ConnectionResetError,
                    ConnectionAbortedError):
                if attempt >= self.MAX_RETRIES:
                    raise
                jitter = random.uniform(0, 0.1 * delay)
                time.sleep(min(delay + jitter, self.MAX_RETRY_DELAY))
                delay = min(delay * 2, self.MAX_RETRY_DELAY)
            except requests.exceptions.RequestException:
                raise

        raise requests.exceptions.RequestException("Falha desconhecida na requisição")

    # --------------------------
    # Normalização de tags
    # --------------------------
    def _normalize_tag(self, tag: str) -> str:
        if not tag:
            return ""
        tag = (tag
               .replace("º", "o").replace("ª", "a")
               .replace("²", "2").replace("³", "3").replace("¹", "1")
               .replace("€", "eur").replace("$", "usd").replace("£", "gbp")
               .replace(".", "-"))
        nfd = unicodedata.normalize("NFD", tag)
        tag = "".join(ch for ch in nfd if unicodedata.category(ch) != "Mn")
        tag = tag.lower()
        tag = self._NON_ALNUM_DASH_RE.sub("-", tag)
        tag = self._MULTI_DASH_RE.sub("-", tag).strip("-")
        return tag

    # --------------------------
    # HVD IDs
    # --------------------------
    def _fetch_hvd_ids(self) -> set[str]:
        url = "https://www.ine.pt/ine/xml_indic_hvd.jsp?opc=3&lang=PT"
        try:
            resp = self._make_request_with_retry(url, timeout=30, stream=False)
            root = ET.fromstring(resp.content)
            ids = {ind.attrib["id"] for ind in root.findall(".//indicator") if "id" in ind.attrib}
            self._log.info("[INE] HVD IDs carregados: %s", len(ids))
            return ids
        except Exception as e:
            self._log.warning("[INE] Falha ao carregar HVD IDs: %s", e)
            return set()

    # --------------------------
    # XML local preferencial
    # --------------------------
    def _ensure_local_xml(self) -> str:
        xml_path = self.INE_XML_PATH
        if os.path.exists(xml_path) and os.path.getsize(xml_path) > 0:
            self._log.info("[INE] Usando XML local: %s (%.2f MB)",
                           xml_path, os.path.getsize(xml_path) / (1024 * 1024))
            return xml_path

        os.makedirs(os.path.dirname(xml_path), exist_ok=True)
        self._log.info("[INE] XML local não encontrado. Fazendo download de %s ...", self.source.url)

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name
            resp = self._make_request_with_retry(self.source.url, stream=True)
            resp.raw.decode_content = True
            shutil.copyfileobj(resp.raw, tmp)

        os.replace(tmp_path, xml_path)

        self._log.info("[INE] Download concluído. XML salvo em: %s (%.2f MB)",
                       xml_path, os.path.getsize(xml_path) / (1024 * 1024))
        return xml_path

    # --------------------------
    # Extração de metadados
    # --------------------------
    def _extract_metadata(self, elem: ET.Element) -> dict:
        md = {}

        node = elem.find("title")
        if node is not None and node.text:
            md["title"] = node.text

        desc = ""
        node = elem.find("description")
        if node is not None and node.text:
            desc = node.text

        html_node = elem.find("html")
        if html_node is not None:
            bdd_url = html_node.find("bdd_url")
            if bdd_url is not None and bdd_url.text:
                desc = (desc + "\n" + bdd_url.text) if desc else bdd_url.text

        if desc:
            md["description"] = desc

        resources = []
        json_node = elem.find("json")
        if json_node is not None:
            jds = json_node.find("json_dataset")
            if jds is not None and jds.text:
                resources.append({
                    "title": "Dataset json url",
                    "description": "Dataset em formato json",
                    "url": normalize_url_slashes(jds.text),
                    "filetype": "remote",
                    "format": "json",
                })
            jmi = json_node.find("json_metainfo")
            if jmi is not None and jmi.text:
                resources.append({
                    "title": "Json metainfo url",
                    "description": "Metainfo em formato json",
                    "url": normalize_url_slashes(jmi.text),
                    "filetype": "remote",
                    "format": "json",
                })

        md["resources"] = resources
        md["resource_urls"] = [r["url"].strip() for r in resources]
        md["resource_sig"] = {(r["url"].strip(), r["title"], r["description"], r["format"]) for r in resources}

        keywords = set()
        for kn in elem.findall("keywords"):
            text = (kn.text or "").strip()
            if not text:
                continue
            for part in self._KW_SPLIT_RE.split(text):
                part = part.strip().strip(",")
                if part:
                    keywords.add(part)

        for tagname in ("theme", "subtheme"):
            for tn in elem.findall(tagname):
                val = (tn.text or "").strip()
                if val:
                    keywords.add(val)

        tags_norm = {self._normalize_tag(t) for t in keywords if t}
        tags_norm.discard("")
        tags_norm.add("ine-pt")
        md["tags_norm"] = sorted(tags_norm)

        return md

    # --------------------------
    # Change detection (barato)
    # --------------------------
    def _has_changed(self, dataset, new_md: dict, remote_id: str | None = None) -> bool:
        if not dataset.id:
            return True

        if (dataset.title or "") != (new_md.get("title") or ""):
            return True

        if (dataset.description or "") != (new_md.get("description") or ""):
            return True

        desired = set(new_md.get("tags_norm") or [])
        if remote_id and remote_id in self.HVD_INDICATOR_IDS:
            desired.update({"estatisticas", "hvd"})

        if set(dataset.tags or []) != desired:
            return True

        current_urls = {r.url for r in dataset.resources}
        if current_urls != set(new_md.get("resource_urls") or []):
            return True

        current_sig = {(r.url, r.title or "", r.description or "", r.format or "") for r in dataset.resources}
        if current_sig != (new_md.get("resource_sig") or set()):
            return True

        return False

    # --------------------------
    # Dataset fetch: save(validate=False)
    # --------------------------
    def get_dataset(self, remote_id):
        dataset = super().get_dataset(remote_id)
        original_save = dataset.save

        def save_without_validation(*args, **kwargs):
            kwargs["validate"] = False
            return original_save(*args, **kwargs)

        dataset.save = save_without_validation
        return dataset

    # --------------------------
    # Watchdog / timeout por dataset
    # --------------------------
    def _process_dataset_with_timeout(self, remote_id: str, md: dict):
        """
        Executa process_dataset com timeout (Linux, thread principal).
        Se estourar, levanta TimeoutError e segue.
        """
        import signal

        class _Timeout(Exception):
            pass

        def _handler(_signum, _frame):
            raise _Timeout()

        old_handler = signal.signal(signal.SIGALRM, _handler)
        signal.alarm(self._dataset_timeout_s)

        try:
            return self.process_dataset(remote_id, **md)
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)

    # --------------------------
    # inner_harvest (sequencial + progresso + watchdog)
    # --------------------------
    def inner_harvest(self):
        start = time.time()

        self.HVD_INDICATOR_IDS = self._fetch_hvd_ids()

        xml_path = self._ensure_local_xml()
        file_size = os.path.getsize(xml_path)

        processed = 0
        skipped = 0
        failed = 0

        last_progress = time.time()
        first_indicator_seen = False

        self._log.info(
            "[INE] Iniciando parse streaming (sequencial) do XML: %s (%.2f MB)",
            xml_path, file_size / (1024 * 1024)
        )

        parser = ET.XMLPullParser(events=("end",))

        with open(xml_path, "rb") as f:
            while True:
                chunk = f.read(self._chunk_size)
                if not chunk:
                    break

                parser.feed(chunk)

                for _event, elem in parser.read_events():
                    if elem.tag != "indicator" or "id" not in elem.attrib:
                        continue

                    if not first_indicator_seen:
                        first_indicator_seen = True
                        self._log.info(
                            "[INE] Primeiro <indicator> encontrado após %.1fs (lido %.2f MB)",
                            time.time() - start, f.tell() / (1024 * 1024)
                        )

                    remote_id = elem.attrib["id"]
                    t0 = time.time()

                    # LOG CRÍTICO: indica dataset em processamento
                    self._log.info("[INE] Processando dataset %s ...", remote_id)

                    try:
                        md = self._extract_metadata(elem)

                        # process_dataset com watchdog
                        self._process_dataset_with_timeout(remote_id, md)

                        processed += 1
                        dt = time.time() - t0
                        self._log.info("[INE] OK dataset %s em %.2fs", remote_id, dt)

                    except HarvestSkipException:
                        skipped += 1
                        dt = time.time() - t0
                        self._log.info("[INE] SKIP dataset %s em %.2fs (sem mudanças)", remote_id, dt)

                    except Exception as e:
                        failed += 1
                        dt = time.time() - t0
                        self._log.exception("[INE] FAIL dataset %s após %.2fs (%s)", remote_id, dt, type(e).__name__)

                    finally:
                        elem.clear()

                    total = processed + skipped + failed
                    if total % self._log_every == 0:
                        elapsed = time.time() - start
                        rate = total / elapsed if elapsed else 0
                        self._log.info(
                            "[INE] progresso datasets: total=%s (ok=%s skip=%s fail=%s) | %.2f ds/s",
                            total, processed, skipped, failed, rate
                        )

                now = time.time()
                if now - last_progress >= self._progress_interval_s:
                    bytes_read = f.tell()
                    elapsed = now - start
                    mb_read = bytes_read / (1024 * 1024)
                    mb_total = file_size / (1024 * 1024)
                    mbps = mb_read / elapsed if elapsed else 0
                    pct = (bytes_read / file_size * 100) if file_size else 0
                    remaining_mb = (mb_total - mb_read)
                    eta = (remaining_mb / mbps) if mbps > 0 else None
                    eta_str = "ETA=indisponível" if eta is None else f"ETA~{eta:.0f}s (~{eta/60:.1f}min)"
                    self._log.info(
                        "[INE] progresso XML: %.1f%% | lido %.2f/%.2f MB | %.2f MB/s | %s",
                        pct, mb_read, mb_total, mbps, eta_str
                    )
                    last_progress = now

        try:
            parser.close()
        except Exception:
            pass

        # save final do job
        if getattr(self, "job", None):
            self._original_save_job()

        total_time = time.time() - start
        self._log.info(
            "[INE] Harvest concluído: %ss (%.1f min) | ok=%s skip=%s fail=%s | XML mantido em %s",
            round(total_time, 1), total_time / 60, processed, skipped, failed, xml_path
        )

    # --------------------------
    # inner_process_dataset
    # --------------------------
    def inner_process_dataset(self, item: HarvestItem, **kwargs):
        dataset = self.get_dataset(item.remote_id)

        if "tags_norm" in kwargs and not self._has_changed(dataset, kwargs, item.remote_id):
            raise HarvestSkipException("sem mudanças nos metadados")

        if self._cc_by_license is None:
            self._cc_by_license = License.guess("cc-by")

        dataset.license = self._cc_by_license
        dataset.resources = []
        dataset.frequency = "unknown"

        if "tags_norm" in kwargs:
            tags = list(kwargs.get("tags_norm") or [])

            if item.remote_id in self.HVD_INDICATOR_IDS:
                for t in ("estatisticas", "hvd"):
                    if t not in tags:
                        tags.append(t)

            if "ine-pt" not in tags:
                tags.append("ine-pt")

            dataset.tags = tags

            if "title" in kwargs:
                dataset.title = kwargs["title"]
            if "description" in kwargs:
                dataset.description = kwargs["description"]
            for res_data in (kwargs.get("resources") or []):
                dataset.resources.append(Resource(**res_data))

            return dataset

        # fallback (não deveria acontecer no fluxo normal)
        base_url = self.source.url
        parsed = urlparse(base_url)
        qs = parse_qs(parsed.query)
        qs["lang"] = ["PT"]
        qs["varcd"] = [str(item.remote_id)]
        new_query = urlencode({k: v[0] for k, v in qs.items()})
        final_url = urlunparse(parsed._replace(query=new_query))

        resp = self._make_request_with_retry(final_url, headers={"charset": "utf8"}, stream=True)
        resp.raw.decode_content = True

        pull = ET.XMLPullParser(events=("end",))
        target = None
        while True:
            chunk = resp.raw.read(self._chunk_size)
            if not chunk:
                break
            pull.feed(chunk)
            for _event, el in pull.read_events():
                if el.tag == "indicator" and el.get("id") == str(item.remote_id):
                    target = el
                    break
                el.clear()
            if target is not None:
                break

        if target is not None:
            md = self._extract_metadata(target)
            tags = list(md.get("tags_norm") or [])
            if item.remote_id in self.HVD_INDICATOR_IDS:
                for t in ("estatisticas", "hvd"):
                    if t not in tags:
                        tags.append(t)
            if "ine-pt" not in tags:
                tags.append("ine-pt")

            dataset.tags = tags
            if "title" in md:
                dataset.title = md["title"]
            if "description" in md:
                dataset.description = md["description"]
            for res_data in (md.get("resources") or []):
                dataset.resources.append(Resource(**res_data))
            target.clear()
        else:
            dataset.tags = ["ine-pt"]

        return dataset
