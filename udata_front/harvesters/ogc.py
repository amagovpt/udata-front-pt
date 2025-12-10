from udata.harvest.backends.base import BaseBackend
from udata.models import Resource, Dataset, License
from udata.harvest.models import HarvestItem
import requests
import logging

from .tools.harvester_utils import normalize_url_slashes


class OGCBackend(BaseBackend):
    """
    Harvester backend for OGC API - Collections (JSON format).
    Processes collections from OGC API endpoints and creates datasets with resources.
    """
    display_name = 'Harvester OGC'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)

    def inner_harvest(self):
        """
        Fetches OGC API collections (JSON-LD) and enqueues them for processing.
        """
        headers = {
            'content-type': 'application/json',
            'Accept-Charset': 'utf-8'
        }
        
        try:
            res = requests.get(self.source.url, headers=headers)
            res.encoding = 'utf-8'
            data = res.json()
        except Exception as e:
            msg = f'Error fetching OGC data: {e}'
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
                self.logger.warning(f"Skipping OGC dataset without @id: {each.get('name')}")
                continue

            item = {
                "remote_id": str(remote_id),
                "title": each.get("name") or "Untitled Dataset",
                "description": each.get("description") or "",
                "keywords": each.get("keywords") or [],
                "distributions": each.get("distribution") or [],
                "spatial": each.get("spatial")
            }

            self.process_dataset(item["remote_id"], items=item)

    def inner_process_dataset(self, item: HarvestItem, **kwargs):
        """
        Process harvested OGC JSON-LD data into a dataset.
        """
        dataset = self.get_dataset(item.remote_id)
        item_data = kwargs.get('items')

        # Set basic dataset fields
        dataset.title = item_data['title']
        dataset.license = License.guess('cc-by')
        dataset.description = item_data['description']
        dataset.tags = ["ogcapi.dgterritorio.gov.pt"]

        # Add keywords as tags
        keywords = item_data.get('keywords', [])
        if isinstance(keywords, list):
            for keyword in keywords:
                if keyword and isinstance(keyword, str):
                    dataset.tags.append(keyword)
        elif isinstance(keywords, str) and keywords:
            dataset.tags.append(keywords)

        # Recreate all resources
        dataset.resources = []

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
                    if link_type in ('text/html', 'image/png'):
                        continue
                    
                    # Extract format from MIME type or use the type directly
                    if link_type:
                        format_value = self._extract_format_from_mime(link_type)
                    else:
                        # Try to extract from URL
                        format_value = url.split('.')[-1] if '.' in url.split('/')[-1] else "unknown"
                    
                    # Use link title or create a descriptive title
                    resource_title = dist.get("description") or dist.get("name") or "Resource"

                    new_resource = Resource(
                        title=resource_title,
                        url=normalize_url_slashes(url),
                        filetype='remote',
                        format=format_value
                    )
                    dataset.resources.append(new_resource)

        # Add extra metadata
        dataset.extras['harvest:name'] = self.source.name
        
        # Store spatial information if available
        spatial = item_data.get('spatial')
        if spatial:
             dataset.extras['spatial'] = spatial

        return dataset

    def _extract_format_from_mime(self, mime_type: str) -> str:
        """
        Extract a simple format string from a MIME type.
        """
        mime_to_format = {
            'application/json': 'JSON',
            'application/ld+json': 'JSON-LD',
            'application/xml': 'XML',
            'application/xls': 'XLS',
            'application/xlsx': 'XLSX',
            'application/csv': 'CSV',
            'text/csv': 'CSV',
            'text/xml': 'XML',
            'application/geo+json': 'GeoJSON',
            'application/gml+xml': 'GML',
        }
        return mime_to_format.get(mime_type, mime_type.split('/')[-1].upper() if '/' in mime_type else mime_type)