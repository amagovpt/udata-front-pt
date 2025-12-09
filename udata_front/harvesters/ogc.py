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
        Fetches OGC API collections and enqueues them for processing.
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

        # Try to find the list of datasets/collections
        # OGC API - Collections uses 'collections'
        metadata = data.get("collections") or data.get("member") or data.get("datasets") or data.get("dataset")

        # Handle different response structures
        if not metadata and isinstance(data, list):
            metadata = data
        elif not metadata and isinstance(data, dict):
            # Maybe it's a single collection object?
            if data.get("id") and data.get("title"):
                metadata = [data]

        if not metadata:
            msg = f'Could not find collections/datasets in OGC response. Keys found: {list(data.keys())}'
            self.logger.error(msg)
            raise Exception(msg)

        # Ensure metadata is always a list
        if isinstance(metadata, dict):
            metadata = [metadata]

        # Loop through the metadata and process each collection
        for each in metadata:
            remote_id = (
                each.get("id") or 
                each.get("identifier") or 
                each.get("@id")
            )
            
            if not remote_id:
                self.logger.warning(f"Skipping OGC collection without identifier: {each.get('title')}")
                continue

            item = {
                "remote_id": str(remote_id),
                "title": each.get("title") or each.get("dct:title") or each.get("name") or "Untitled Dataset",
                "description": each.get("description") or each.get("abstract") or each.get("dct:description") or "",
                "keywords": each.get("keywords") or each.get("keyword") or [],
                "links": each.get("links") or each.get("link") or each.get("distribution") or [],
                "extent": each.get("extent", {})
            }

            self.process_dataset(item["remote_id"], items=item)

    def inner_process_dataset(self, item: HarvestItem, **kwargs):
        """
        Process harvested OGC collection data into a dataset.
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

        links = item_data.get("links", [])
        if isinstance(links, list):
            for link in links:
                if isinstance(link, dict):
                    url = link.get("href", "")
                    if not url:
                        continue
                    
                    # Determine format from link type or URL
                    link_type = link.get("type", "")

                    # Skip HTML and PNG resources as requested
                    if link_type in ('text/html', 'image/png'):
                        continue
                    link_rel = link.get("rel", "")
                    
                    # Extract format from MIME type or use the type directly
                    if link_type:
                        format_value = self._extract_format_from_mime(link_type)
                    else:
                        # Try to extract from URL
                        format_value = url.split('.')[-1] if '.' in url.split('/')[-1] else "unknown"
                    
                    # Use link title or create a descriptive title
                    resource_title = link.get("title") or f"{item_data['title']} - {link_rel}"

                    new_resource = Resource(
                        title=resource_title,
                        url=normalize_url_slashes(url),
                        filetype='remote',
                        format=format_value
                    )
                    dataset.resources.append(new_resource)

        # Add extra metadata
        dataset.extras['harvest:name'] = self.source.name
        
        # Store extent information if available
        extent = item_data.get('extent', {})
        if extent:
            spatial = extent.get('spatial', {})
            if spatial and spatial.get('bbox'):
                dataset.extras['spatial:bbox'] = str(spatial.get('bbox'))

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