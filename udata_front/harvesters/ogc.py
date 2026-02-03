import logging
import requests

from udata.i18n import gettext as _
from udata.harvest.backends.base import BaseBackend, HarvestFilter
from udata.models import Resource, Dataset, License, SpatialCoverage
from udata.core.contact_point.models import ContactPoint
from udata.harvest.models import HarvestItem

from .tools.harvester_utils import normalize_url_slashes


class OGCBackend(BaseBackend):
    """
    Harvester backend for OGC API - Collections (JSON format).
    Processes collections from OGC API endpoints and creates datasets with resources.
    """

    display_name = "Harvester OGC"

    # Filtros configuráveis expostos no backoffice para este harvester.
    # Cada filtro é um `HarvestFilter(label, field, type, help_text)` que permite
    # incluir ou excluir datasets com base em campos do metadata.
    # Campos suportados (comparação sem distinção entre maiúsculas/minúsculas):
    #  - 'organization': verifica `provider.name` ou identificador do provedor (substring).
    #  - 'tags': verifica a lista de `keywords` do dataset.
    #  - 'id': verifica o `remote_id` do dataset.
    # Tipos de filtro: 'include' (padrão) ou 'exclude' (quando configurado no backoffice).
    # Exemplos de configuração (no campo `filters` da fonte):
    #  - {"type": "exclude", "field": "organization", "value": "turismo-de-portugal-ip"}
    #  - {"type": "include", "field": "tags", "value": "climate"}
    filters = (
        HarvestFilter(
            _("Organization"), "organization", str, _("A OGC Organization name")
        ),
        HarvestFilter(_("Tag"), "tags", str, _("A OGC tag name")),
        HarvestFilter(_("Remote ID"), "id", str, _("A dataset remote id")),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)

    def inner_harvest(self):
        """
        Fetches OGC API collections (JSON-LD) and enqueues them for processing.
        """
        headers = {"content-type": "application/json", "Accept-Charset": "utf-8"}

        try:
            res = requests.get(self.source.url, headers=headers)
            res.encoding = "utf-8"
            data = res.json()
        except Exception as e:
            msg = f"Error fetching OGC data: {e}"
            self.logger.error(msg)
            raise Exception(msg)

        # OGC/Schema.org JSON-LD structure: look for 'dataset' array
        metadata = data.get("dataset")

        if not metadata:
            msg = f'Could not find "dataset" in OGC response. Keys found: {list(data.keys())}'
            self.logger.error(msg)
            raise Exception(msg)

        # Ensure metadata is always a list
        if isinstance(metadata, dict):
            metadata = [metadata]

        # Loop through the metadata and process each dataset
        for each in metadata:
            remote_id = each.get("@id")

            if not remote_id:
                self.logger.warning(
                    f"Skipping OGC dataset without @id: {each.get('name')}"
                )
                continue

            item = {
                "remote_id": str(remote_id),
                "title": each.get("name") or "Untitled Dataset",
                "description": each.get("description") or "",
                "keywords": each.get("keywords") or [],
                "distributions": each.get("distribution") or [],
                "license": each.get("license"),
                "temporal_coverage": each.get("temporalCoverage"),
                "provider": each.get("provider") or data.get("provider"),
            }

            # Apply configurable filters (if any) before processing
            filters = self.config.get("filters", []) or []
            try:
                if not self._passes_filters(item, filters):
                    self.logger.debug(
                        f"Skipping dataset {item.get('remote_id')} due to filters"
                    )
                    continue
            except Exception as e:
                self.logger.error(
                    f"Error while applying filters for {item.get('remote_id')}: {e}"
                )
                # On filter errors, skip the dataset to avoid processing unintended items
                continue

            self.process_dataset(item["remote_id"], items=item)

    def inner_process_dataset(self, item: HarvestItem, **kwargs):
        """
        Process harvested OGC JSON-LD data into a dataset.
        """
        dataset = self.get_dataset(item.remote_id)
        item_data = kwargs.get("items")

        # Set basic dataset fields
        dataset.title = item_data["title"]
        dataset.description = item_data["description"]
        dataset.tags = ["ogcapi.dgterritorio.gov.pt"]

        # Add keywords as tags
        keywords = item_data.get("keywords", [])
        if isinstance(keywords, list):
            for keyword in keywords:
                if keyword and isinstance(keyword, str):
                    dataset.tags.append(keyword)
        elif isinstance(keywords, str) and keywords:
            dataset.tags.append(keywords)

        # Recreate all resources
        dataset.resources = []
        dataset.contact_points = []

        distributions = item_data.get("distributions", [])
        if isinstance(distributions, list):
            for dist in distributions:
                if isinstance(dist, dict):
                    url = dist.get("contentURL", "")
                    if not url:
                        continue

                    # Determine format from encodingFormat
                    link_type = dist.get("encodingFormat", "")

                    # Skip HTML and PNG resources as requested
                    if link_type in ("text/html", "image/png"):
                        continue

                    # Extract format from MIME type or use the type directly
                    if link_type:
                        format_value = self._extract_format_from_mime(link_type)
                    else:
                        # Try to extract from URL
                        format_value = (
                            url.split(".")[-1]
                            if "." in url.split("/")[-1]
                            else "unknown"
                        )

                    # Use link title or create a descriptive title
                    resource_title = (
                        dist.get("description") or dist.get("name") or "Resource"
                    )

                    new_resource = Resource(
                        title=resource_title,
                        url=normalize_url_slashes(url),
                        filetype="remote",
                        format=format_value,
                    )
                    dataset.resources.append(new_resource)

        # Add extra metadata
        dataset.extras["harvest:name"] = self.source.name

        # License logic
        license_url = item_data.get("license")
        if license_url:
            dataset.license = License.guess(license_url)
        if not dataset.license:
            # Fallback if guess failed or no license provided
            dataset.license = License.guess("notspecified")

        # Temporal Coverage
        temporal = item_data.get("temporal_coverage")
        if temporal:
            dataset.extras["temporal_coverage"] = temporal

        # Provider/Publisher
        provider = item_data.get("provider")
        if provider and isinstance(provider, dict):
            publisher_name = provider.get("name")
            publisher_email = provider.get("contactPoint", {}).get("email")

            # dataset.extras["publisher_name"] = publisher_name
            # dataset.extras["publisher_email"] = publisher_email

            if publisher_name:
                contact = ContactPoint.objects(
                    name=publisher_name, email=publisher_email, role="publisher"
                ).first()

                if not contact:
                    contact = ContactPoint(
                        name=publisher_name, email=publisher_email, role="publisher"
                    )
                    try:
                        contact.save()
                    except Exception as e:
                        self.logger.warning(
                            f"Could not save contact point {publisher_name}: {e}"
                        )
                        contact = None

                if contact:
                    dataset.contact_points.append(contact)

        return dataset

    def _normalize_val(self, value):
        """Normalize a value for comparisons (lowercased string)."""
        if value is None:
            return ""
        if isinstance(value, (list, tuple)):
            # flatten to a comma-separated string
            return ",".join([str(v).strip().lower() for v in value if v is not None])
        return str(value).strip().lower()

    def _normalize_filter(self, f):
        """Turn a filter spec (dict/tuple/str) into a normalized dict.

        Expected normalized keys: {'type': 'include'|'exclude', 'field': <field>, 'value': <value>}
        Acceptable input forms:
        - dict with 'type'/'field'/'value'
        - tuple/list (type, field, value) or (field, value)
        - string (interpreted as a tag include)
        """
        if isinstance(f, dict):
            ftype = f.get("type", "include") or "include"
            field = f.get("field") or f.get("key") or f.get("name")
            value = f.get("value")
        elif isinstance(f, (list, tuple)):
            if len(f) == 3:
                ftype, field, value = f
            elif len(f) == 2:
                ftype = "include"
                field, value = f
            else:
                raise ValueError("Invalid filter tuple/sequence")
        else:
            # plain string -> tag include
            ftype = "include"
            field = "tags"
            value = f

        return {
            "type": str(ftype).strip().lower(),
            "field": str(field).strip().lower() if field is not None else "",
            "value": str(value).strip() if value is not None else "",
        }

    def _matches_filter(self, f, item):
        """Return True if `item` matches the single normalized filter `f`.

        Supported fields: 'organization' (provider name or id), 'tags' (keywords), 'id' (remote_id), 'title'
        Matching is case-insensitive and uses substring matching for convenience.
        """
        field = f.get("field")
        value = self._normalize_val(f.get("value"))
        if not value:
            return False

        # Organization: check provider name / id
        if field in ("organization", "org", "organization_id"):
            provider = item.get("provider") or {}
            if isinstance(provider, dict):
                provider_name = self._normalize_val(
                    provider.get("name")
                    or provider.get("id")
                    or provider.get("identifier")
                )
                return value in provider_name
            # provider may be a string
            prov_str = self._normalize_val(provider)
            return value in prov_str

        # Tags: check keywords
        if field in ("tag", "tags", "label"):
            keywords = item.get("keywords") or []
            if isinstance(keywords, str):
                keywords = [k.strip() for k in keywords.split(",") if k.strip()]
            for kw in keywords:
                if value in self._normalize_val(kw):
                    return True
            return False

        # ID: check remote_id
        if field in ("id", "remote_id", "dataset_id"):
            remote = self._normalize_val(item.get("remote_id"))
            return value in remote

        # Title: check title substring
        if field in ("title",):
            title = self._normalize_val(item.get("title"))
            return value in title

        # Fallback: try to look in remote_id or title
        remote = self._normalize_val(item.get("remote_id"))
        title = self._normalize_val(item.get("title"))
        return (value in remote) or (value in title)

    def _passes_filters(self, item, filters):
        """Evaluate the list of filters for a given `item`.

        - Any matching 'exclude' filter will cause the item to be excluded (returns False).
        - If one or more 'include' filters are present, the item must match at least one include to pass.
        - If no include filters are present, and no exclude matches, the item passes.
        """
        if not filters:
            return True

        parsed = [self._normalize_filter(f) for f in filters]

        # Exclude if any exclude filter matches
        for f in parsed:
            if f.get("type") == "exclude" and self._matches_filter(f, item):
                self.logger.debug(
                    f"Filter exclude matched for {item.get('remote_id')}: {f}"
                )
                return False

        # Check include filters (if any)
        include_filters = [f for f in parsed if f.get("type") == "include"]
        if include_filters:
            for f in include_filters:
                if self._matches_filter(f, item):
                    return True
            # No include filters matched
            self.logger.debug(f"No include filters matched for {item.get('remote_id')}")
            return False

        # No include filters and no excludes matched => pass
        return True

    def _extract_format_from_mime(self, mime_type: str) -> str:
        """
        Extract a simple format string from a MIME type.
        """
        mime_to_format = {
            "application/json": "JSON",
            "application/ld+json": "JSON-LD",
            "application/xml": "XML",
            "application/xls": "XLS",
            "application/xlsx": "XLSX",
            "application/csv": "CSV",
            "text/csv": "CSV",
            "text/xml": "XML",
            "application/geo+json": "GeoJSON",
            "application/gml+xml": "GML",
        }
        return mime_to_format.get(
            mime_type,
            mime_type.split("/")[-1].upper() if "/" in mime_type else mime_type,
        )
