from __future__ import annotations

import os
import re
import time
import random
import shutil
import tempfile
import unicodedata
import xml.etree.ElementTree as ET
from io import BytesIO
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from flask import current_app

from udata.models import Resource, License, Dataset
from udata.harvest.backends.base import BaseBackend
from udata.harvest.models import HarvestItem
from slugify import slugify

from .tools.harvester_utils import normalize_url_slashes


class INEBackend(BaseBackend):
    """
    INE Harvester - modo FAST (2 fases):
    1) Parse XML -> metadados em memória
    2) Change detection + bulk_write no Mongo (muito mais rápido)

    Fonte XML:
    - Usa /home/babel/workspace/temp/INE.xml se existir
    - Caso contrário baixa self.source.url e grava nesse caminho
    - Não remove o ficheiro no final

    Robustez:
    - Captura BulkWriteError, extrai bwe.details['writeErrors'] e isola operação falhada
      sem abortar o harvest inteiro. [1](https://www.mongodb.com/docs/languages/python/pymongo-driver/current/crud/bulk-write/)[2](https://pymongo.readthedocs.io/en/4.11/examples/bulk.html)
    - Gera slug a partir do título sanitizado para novos datasets.
    """

    display_name = "Instituto nacional de estatística"

    MAX_RETRIES = 5
    INITIAL_RETRY_DELAY = 2
    MAX_RETRY_DELAY = 60
    TIMEOUT_CONNECT = 15
    TIMEOUT_READ = 300

    HVD_INDICATOR_IDS: set[str] = set()

    _KW_SPLIT_RE = re.compile(r"\s*(?:;|,|/|\n|\r|\t|\s+-\s+)\s*")
    _NON_ALNUM_DASH_RE = re.compile(r"[^a-z0-9\-]+")
    _MULTI_DASH_RE = re.compile(r"\-+")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._bulk_size = int(os.getenv("INE_BULK_SIZE", "500"))
        self._log_every = int(os.getenv("INE_FAST_MODE_LOG_EVERY", "200"))
        self._check_changes = os.getenv("INE_CHECK_CHANGES", "true").lower() == "true"
        self._stream_memory = os.getenv("INE_STREAM_MEMORY", "true").lower() == "true"

        self._progress_interval_s = int(os.getenv("INE_PROGRESS_INTERVAL_S", "10"))
        self._chunk_size = int(os.getenv("INE_XML_CHUNK_SIZE", str(1024 * 1024)))  # 1MB

        self._cc_by_license = None

        self._session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=16, pool_maxsize=16, max_retries=0
        )
        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)

        try:
            self._log = current_app.logger
        except Exception:
            import logging

            self._log = logging.getLogger(__name__)

        self._log.info(
            "[INE] FAST MODE (2 fases) ativo: bulk_size=%s, log_every=%s, stream_memory=%s, chunk=%sKB",
            self._bulk_size,
            self._log_every,
            self._stream_memory,
            int(self._chunk_size / 1024),
        )

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
            except (
                requests.exceptions.ConnectionError,
                requests.exceptions.Timeout,
                requests.exceptions.ChunkedEncodingError,
                ConnectionResetError,
                ConnectionAbortedError,
            ):
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
            ids = {
                ind.attrib["id"]
                for ind in root.findall(".//indicator")
                if "id" in ind.attrib
            }
            self._log.info("[INE] HVD IDs carregados: %s", len(ids))
            return ids
        except Exception as e:
            self._log.warning("[INE] Falha ao carregar HVD IDs: %s", e)
            return set()

    # --------------------------
    # Extrai metadados do indicator (já normalizados)
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
                resources.append(
                    {
                        "title": "Dataset json url",
                        "description": "Dataset em formato json",
                        "url": normalize_url_slashes(jds.text),
                        "filetype": "remote",
                        "format": "json",
                    }
                )
            jmi = json_node.find("json_metainfo")
            if jmi is not None and jmi.text:
                resources.append(
                    {
                        "title": "Json metainfo url",
                        "description": "Metainfo em formato json",
                        "url": normalize_url_slashes(jmi.text),
                        "filetype": "remote",
                        "format": "json",
                    }
                )

        md["resources"] = resources
        md["resource_urls"] = [r["url"].strip() for r in resources]
        md["resource_sig"] = {
            (r["url"].strip(), r["title"], r["description"], r["format"])
            for r in resources
        }

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
    # Change detection (barato + deep size check)
    # --------------------------
    def _has_changed(self, dataset, new_md: dict, remote_id: str) -> bool:
        if not getattr(dataset, "id", None):
            return True

        if (dataset.title or "") != (new_md.get("title") or ""):
            return True

        if (dataset.description or "") != (new_md.get("description") or ""):
            return True

        desired = set(new_md.get("tags_norm") or [])
        if remote_id in self.HVD_INDICATOR_IDS:
            desired.update({"estatisticas", "hvd"})

        if set(dataset.tags or []) != desired:
            return True

        current_urls = {r.url for r in dataset.resources}
        if current_urls != set(new_md.get("resource_urls") or []):
            return True

        current_sig = {
            (r.url, r.title or "", r.description or "", r.format or "")
            for r in dataset.resources
        }
        if current_sig != (new_md.get("resource_sig") or set()):
            return True

        return False

    # --------------------------
    # Aplica metadata ao dataset (sem salvar)
    # --------------------------
    def _apply_metadata_to_dataset(self, dataset, remote_id: str, md: dict):
        if self._cc_by_license is None:
            self._cc_by_license = License.guess("cc-by")

        dataset.license = self._cc_by_license
        dataset.frequency = "unknown"

        tags = list(md.get("tags_norm") or [])
        if remote_id in self.HVD_INDICATOR_IDS:
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

        dataset.resources = []
        for res_data in md.get("resources") or []:
            r = Resource(**res_data)
            dataset.resources.append(r)

        if not dataset.harvest:
            dataset.harvest = Dataset.harvest.document_type_obj()

        dataset.harvest.remote_id = str(remote_id)
        dataset.harvest.source_id = getattr(self.source, "id", None)
        dataset.harvest.last_update = datetime.now(timezone.utc)

        try:
            dataset.harvest.domain = current_app.config.get("SERVER_NAME") or ""
        except Exception:
            dataset.harvest.domain = ""

        # Gera slug a partir do título para novos datasets
        # Adiciona remote_id ao final para garantir unicidade
        if not getattr(dataset, "id", None):
            if not getattr(dataset, "slug", None) and dataset.title:
                base_slug = slugify(dataset.title, to_lower=True)
                dataset.slug = (
                    f"{base_slug}-{remote_id}" if base_slug else f"ine-{remote_id}"
                )

        return dataset

    # --------------------------
    # Flush bulk com tratamento de BulkWriteError
    # --------------------------
    def _flush_bulk(self, collection, ops, op_ids):
        """
        Executa bulk_write e trata BulkWriteError:
        - Loga bwe.details['writeErrors'] com o remote_id correspondente (via índice)
        - Reprocessa o batch em modo "divide and conquer" para salvar o máximo possível.
        """
        from pymongo.errors import BulkWriteError

        if not ops:
            return 0, 0, 0  # matched, modified, upserted

        t0 = time.time()
        try:
            res = collection.bulk_write(ops, ordered=False)
            dt = time.time() - t0
            upserted = len(getattr(res, "upserted_ids", {}) or {})
            self._log.info(
                "[INE] bulk_write OK: ops=%s em %.2fs | matched=%s modified=%s upserted=%s",
                len(ops),
                dt,
                getattr(res, "matched_count", "?"),
                getattr(res, "modified_count", "?"),
                upserted,
            )
            return (
                getattr(res, "matched_count", 0),
                getattr(res, "modified_count", 0),
                upserted,
            )

        except BulkWriteError as bwe:
            dt = time.time() - t0
            details = getattr(bwe, "details", {}) or {}
            werrors = details.get("writeErrors", []) or []

            self._log.error(
                "[INE] BulkWriteError em %.2fs (ops=%s). writeErrors=%s",
                dt,
                len(ops),
                len(werrors),
            )

            # log detalhado por erro (inclui código/mensagem/índice)
            for err in werrors[:10]:  # limita para não explodir logs
                idx = err.get("index")
                rid = op_ids[idx] if isinstance(idx, int) and idx < len(op_ids) else "?"
                self._log.error(
                    "[INE] writeError remote_id=%s idx=%s code=%s errmsg=%s",
                    rid,
                    idx,
                    err.get("code"),
                    err.get("errmsg"),
                )

            # Estratégia: dividir o batch e tentar salvar a maioria
            if len(ops) == 1:
                # não há como dividir mais; já logamos
                return 0, 0, 0

            mid = len(ops) // 2
            self._flush_bulk(collection, ops[:mid], op_ids[:mid])
            self._flush_bulk(collection, ops[mid:], op_ids[mid:])

            return 0, 0, 0

    # --------------------------
    # inner_harvest (2 fases)
    # --------------------------
    def inner_harvest(self):
        self._log.info("[INE] Iniciando harvester de %s", self.source.url)
        self._log.info(
            "[INE] Config: BulkSize=%s, LogEvery=%s, CheckChanges=%s, StreamMemory=%s",
            self._bulk_size,
            self._log_every,
            self._check_changes,
            self._stream_memory,
        )

        start_time = time.time()
        self.HVD_INDICATOR_IDS = self._fetch_hvd_ids()

        # Prepare Streaming Source
        temp_file_path = None
        source_context = None

        local_file_path = "/tmp/INE.xml"

        try:
            if os.path.exists(local_file_path):
                self._log.info("[INE] Usando ficheiro local: %s", local_file_path)
                source_context = local_file_path
            elif self._stream_memory:
                self._log.info("[INE] Modo Memória: Baixando XML para RAM...")
                resp = self._session.get(self.source.url)
                resp.raise_for_status()
                # Cria BytesIO
                source_context = BytesIO(resp.content)
            else:
                self._log.info("[INE] Modo Disco: Baixando XML para Temp File...")
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    temp_file_path = tmp.name
                    with self._session.get(self.source.url, stream=True) as r:
                        r.raise_for_status()
                        shutil.copyfileobj(r.raw, tmp)
                self._log.info("[INE] Download concluído: %s", temp_file_path)
                source_context = temp_file_path

            # Fase 1: Criação do iterador sobre o XML
            # source_context pode ser file path ou file-like object (BytesIO)
            context = ET.iterparse(source_context, events=("start", "end"))
            context = iter(context)
            event, root = next(context)  # Pega o elemento raiz

            metadata_map = {}  # {remote_id: metadata_dict}
            total_parsed = 0

            for event, elem in context:
                if event == "end" and elem.tag == "indicator":
                    total_parsed += 1
                    md = self._extract_metadata(elem)
                    remote_id = elem.get("id")

                    # Skip items without title (mandatory field)
                    if remote_id and md.get("title"):
                        metadata_map[remote_id] = md
                    elif remote_id:
                        self._log.warning(
                            "[INE] Skipping item %s: missing title", remote_id
                        )

                    elem.clear()
                    root.clear()  # Limpa memoria da arvore XML

            self._log.info(
                "[INE] Parsing XML concluído. Total items: %s. Iniciando processamento...",
                total_parsed,
            )

        except Exception as e:
            self._log.error("[INE] Erro no download/parsing do XML: %s", e)
            raise e
        finally:
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except:
                    pass

        # --- Fim Fase 1, Inicio Fase 2 (Processamento) ---
        self._log.info(
            "[INE] FAST MODE - Fase 2: change detection + bulk_write (bulk_size=%s)",
            self._bulk_size,
        )

        from pymongo import ReplaceOne, UpdateOne

        ops = []
        op_ids = []
        # Lista temporária para HarvestItems deste batch
        batch_harvest_items = []

        dataset_collection = None

        changed = 0
        created = 0
        skipped = 0
        failed = 0
        processed = 0

        # Para reporting no Job
        if not hasattr(self, "job") or self.job is None:
            self._log.warning(
                "[INE] Atenção: self.job não existe. O progresso não será visível na UI."
            )

        processed = 0

        # Para reporting no Job
        if not hasattr(self, "job") or self.job is None:
            self._log.warning(
                "[INE] Atenção: self.job não existe. O progresso não será visível na UI."
            )

        # Convertermos para lista para poder iterar em chunks se quisermos,
        # mas como e dict, iteramos items().
        # Para paralelizar os HEAD requests, precisamos saber QUAIS precisam de check.
        # Estrategia:
        # Iterar todos. Se metadata basico difere -> changed (sem check de tamanho).
        # Se metadata igual -> check tamanho.
        # Isto implica que temos de fazer o check ANTES de decidir.

        # Para ser eficiente com Threads, vamos processar em batches.
        all_items = list(metadata_map.items())
        total_items = len(all_items)

        # Processar em chunks do tamanho do bulk_size
        for i in range(0, total_items, self._bulk_size):
            chunk = all_items[i : i + self._bulk_size]

            # --- Passo A: Pre-fetch datasets (simplificado) ---
            for remote_id, md in chunk:
                md["__dataset_obj"] = self.get_dataset(remote_id)

            # --- Passo C: Processamento Normal do Chunk ---
            for remote_id, md in chunk:
                processed += 1
                item_status = "done"
                dataset = md.pop("__dataset_obj")  # recupera e limpa

                try:
                    if dataset_collection is None:
                        dataset_collection = dataset._get_collection()

                    # Se a flag estiver desligada -> assume changed=True sempre
                    should_update = True
                    if self._check_changes:
                        if not self._has_changed(dataset, md, remote_id):
                            should_update = False

                    if not should_update:
                        skipped += 1
                        item_status = "skipped"
                    else:
                        self._apply_metadata_to_dataset(dataset, remote_id, md)
                        doc = dataset.to_mongo()
                        doc_dict = dict(doc)

                        if getattr(dataset, "id", None):
                            _id = doc_dict.get("_id", dataset.id)
                            ops.append(ReplaceOne({"_id": _id}, doc_dict, upsert=True))
                            op_ids.append(remote_id)
                            changed += 1
                        else:
                            d = dict(doc_dict)
                            d.pop("_id", None)
                            ops.append(
                                UpdateOne(
                                    {
                                        "harvest.remote_id": str(remote_id),
                                        "harvest.source_id": getattr(
                                            self.source, "id", None
                                        ),
                                    },
                                    {"$set": d},
                                    upsert=True,
                                )
                            )
                            op_ids.append(remote_id)
                            created += 1

                except Exception:
                    failed += 1
                    item_status = "failed"
                    self._log.exception(
                        "[INE] Falha na fase 2 para remote_id=%s", remote_id
                    )

                # Criar HarvestItem
                if self.job:
                    h_item = HarvestItem(remote_id=remote_id, status=item_status)
                    if dataset and getattr(dataset, "id", None):
                        h_item.dataset = dataset.id
                    batch_harvest_items.append(h_item)

            # --- Fim do loop do chunk ---

            # Flush Ops e HarvestItems (igual a antes)
            if len(ops) >= self._bulk_size and dataset_collection is not None:
                self._flush_bulk(dataset_collection, ops, op_ids)
                ops, op_ids = [], []

            if self.job and len(batch_harvest_items) >= (self._bulk_size * 2):
                before_len = len(self.job.items)
                self.job.items.extend(batch_harvest_items)
                self.job.save()
                after_len = len(self.job.items)
                self._log.info(
                    "[INE] Job Save: items grew from %s to %s (added %s)",
                    before_len,
                    after_len,
                    len(batch_harvest_items),
                )
                batch_harvest_items = []

            if processed % (self._log_every * 5) == 0:
                self._log.info(
                    "[INE] Fase 2 progresso: processed=%s changed=%s created=%s skipped=%s failed=%s",
                    processed,
                    changed,
                    created,
                    skipped,
                    failed,
                )

        # Final Flush Ops
        if ops and dataset_collection is not None:
            self._flush_bulk(dataset_collection, ops, op_ids)

        # Final Flush Job Items
        if self.job and batch_harvest_items:
            before_len = len(self.job.items)
            self.job.items.extend(batch_harvest_items)
            self.job.save()
            after_len = len(self.job.items)
            self._log.info(
                "[INE] Final Job Save: items grew from %s to %s (added %s)",
                before_len,
                after_len,
                len(batch_harvest_items),
            )

        total_time = time.time() - start_time
        self._log.info(
            "[INE] FAST MODE concluído em %ss (%.1f min) | processed=%s changed=%s created=%s skipped=%s failed=%s",
            round(total_time, 1),
            total_time / 60,
            processed,
            changed,
            created,
            skipped,
            failed,
        )
