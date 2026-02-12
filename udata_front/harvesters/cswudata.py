"""
Harvester for the Almada Municipality Environment Portal.

This module defines a custom udata harvester backend for collecting datasets from a CSW (Catalogue Service for the Web)
endpoint provided by the Almada Municipality. It fetches metadata records, normalizes resource URLs,
and maps them to udata datasets and resources.

Classes:
    AlmadaCSWBackend: Custom udata harvester backend for the Almada Municipality.

Functions:
    normalize_url_slashes(url: str) -> str: Utility to normalize slashes in URLs (imported).

Usage:
    This backend is intended to be used as a plugin in a udata instance. It will fetch datasets from the configured
    CSW endpoint, process their metadata, and create or update corresponding datasets and resources in udata.
"""

from datetime import datetime
import requests
from urllib.parse import urlparse, urlencode

from udata.harvest.backends.base import BaseBackend
from udata.models import Resource, Dataset, License, SpatialCoverage, GeoZone
from owslib.csw import CatalogueServiceWeb

from udata.harvest.models import HarvestItem
from udata.harvest.exceptions import HarvestException
from udata.harvest.filters import (
    boolean,
    email,
    to_date,
    slug,
    normalize_tag,
    normalize_string,
)

from .tools.harvester_utils import normalize_url_slashes

# backend = 'https://metadados.cm-almada.pt/geonetwork/srv/eng/csw?service=CSW&version=2.0.2&request=GetRecords&resultType=results&typeNames=csw:Record&elementSetName=full&startPosition=1&maxRecords=1000&outputSchema=http://www.opengis.net/cat/csw/2.0.2'


class CSWUdataBackend(BaseBackend):
    """
    Harvester backend for the Almada Municipality Environment Portal.

    This backend connects to a CSW endpoint provided by the Almada Municipality,
    fetches dataset records, processes metadata including tags and resources,
    and maps them to udata datasets.
    """

    display_name = "Harvester Almada"

    def inner_harvest(self):
        """
        Iterates over CSW records and adds them to the harvest job.
        """
        # base_url should be something like ".../srv/eng/csw"
        base_url = self.source.url

        # Discover the final URL to avoid POST -> GET conversion on redirects (common in GeoNetwork)
        try:
            # We use a GET request with stream=True to follow redirects and find the actual endpoint
            # without downloading the whole body.
            response = requests.get(
                base_url, timeout=10, allow_redirects=True, stream=True
            )
            base_url = response.url
            response.close()
        except Exception:
            # Fallback to source URL if anything goes wrong
            pass

        page_size = 100
        csw = CatalogueServiceWeb(base_url)

        # Force all operations to use https if our base_url is https
        # This is needed because some servers (like GeoNetwork) advertise http URLs in GetCapabilities
        # even when accessed via https, which causes OWSLib to fail on POST requests due to redirects.
        if base_url.startswith("https://"):
            for op in getattr(csw, "operations", []):
                for method in op.methods:
                    if method.get("url", "").startswith("http://"):
                        method["url"] = method["url"].replace("http://", "https://", 1)

        # First request to get matches and validate endpoint
        csw.getrecords2(maxrecords=1, esn="full")
        matches = int(csw.results.get("matches", 0) or 0)

        startposition = 1  # CSW is 1-based
        while matches > 0 and startposition <= matches:
            csw.getrecords2(
                maxrecords=page_size, startposition=startposition, esn="full"
            )
            nextrecord = int(csw.results.get("nextrecord", 0) or 0)

            for rec_id, record in csw.records.items():
                resources = []

                # CSW records use 'uris' field for resources, not 'references'
                uris = getattr(record, "uris", None)
                if uris:
                    for uri in uris:
                        if isinstance(uri, dict) and uri.get("url"):
                            resources.append(uri)

                # Fallback to references if uris is not available
                if not resources:
                    refs = getattr(record, "references", None)
                    if refs:
                        for ref in refs:
                            if isinstance(ref, dict) and ref.get("url"):
                                resources.append(ref)

                data = {
                    "id": record.identifier,
                    "title": getattr(record, "title", "") or "",
                    "description": getattr(record, "abstract", "") or "",
                    "tags": getattr(record, "subjects", []) or [],
                    "bbox": getattr(record, "bbox", None),
                    "resources": resources,
                    "type": getattr(record, "type", None),
                }

                self.process_dataset(data["id"], items=data)

                if self.has_reached_max_items():
                    return

            if nextrecord == 0 or nextrecord <= startposition:
                break
            startposition = nextrecord

    def inner_process_dataset(self, item: HarvestItem, **kwargs):
        """
        Maps harvested metadata to a udata dataset.

        Args:
            item (HarvestItem): The harvested item containing the remote_id.
            **kwargs: Additional keyword arguments, expects 'items' with the metadata dict.

        Returns:
            Dataset: The updated or created udata dataset.
        """
        dataset = self.get_dataset(item.remote_id)

        data = kwargs.get("items")
        if not data:
            raise HarvestException(
                "Missing data for dataset {0}".format(item.remote_id)
            )

        # Set basic dataset fields
        dataset.title = normalize_string(data["title"])
        dataset.license = License.guess("cc-by")

        # Process tags
        tags = [normalize_tag("almada")]
        for tag in data.get("tags", []):
            normalized = normalize_tag(tag)
            if normalized:
                tags.append(normalized)
        dataset.tags = list(set(tags))  # Remove duplicates

        dataset.description = normalize_string(data["description"])

        if data.get("date"):
            dataset.created_at = to_date(data["date"])

        # Process spatial coverage
        self._process_spatial(dataset, data)

        # Force recreation of all resources
        dataset.resources = []

        for res_data in data.get("resources", []):
            url = res_data.get("url")
            if not url:
                continue

            # Determine resource format/type
            # CSW URIs use 'protocol' field for MIME types or service types
            protocol = res_data.get("protocol", "")
            name = res_data.get("name", "")

            # Check for WMS/WFS services
            if protocol and ("wms" in protocol.lower() or "wfs" in protocol.lower()):
                res_type = protocol.split(":")[-1].lower() if ":" in protocol else "wms"
            elif data.get("type") == "liveData":
                res_type = "wms"
            # Try to extract format from protocol (e.g., 'image/jpeg' -> 'jpeg')
            elif protocol and "/" in protocol:
                res_type = protocol.split("/")[-1].lower()
            else:
                # Fallback to URL extension
                res_type = url.split(".")[-1].lower() if "." in url else "remote"
                if len(res_type) > 5:
                    # Extension too long or invalid
                    res_type = "remote"

            # Use resource name if available, otherwise use dataset title
            resource_title = name if name else dataset.title

            # Create and append the resource
            new_resource = Resource(
                title=resource_title, url=url, filetype="remote", format=res_type
            )
            dataset.resources.append(new_resource)

        return dataset

    def _process_spatial(self, dataset, data):
        """
        Process spatial coverage from CSW bounding box.
        """
        bbox = data.get("bbox")
        if not bbox:
            return

        try:
            # Extract coordinates ensuring float type
            minx = float(bbox.minx)
            miny = float(bbox.miny)
            maxx = float(bbox.maxx)
            maxy = float(bbox.maxy)

            # Ensure correct min/max order
            if minx > maxx:
                minx, maxx = maxx, minx
            if miny > maxy:
                miny, maxy = maxy, miny

            dataset.spatial = SpatialCoverage()

            if minx == maxx and miny == maxy:
                # It's a point
                dataset.spatial.geom = {"type": "Point", "coordinates": [minx, miny]}
            else:
                # Construct GeoJSON Polygon (counter-clockwise)
                # [[minx, miny], [maxx, miny], [maxx, maxy], [minx, maxy], [minx, miny]]
                polygon_coordinates = [
                    # Ring Exterior
                    [
                        [minx, miny],
                        [maxx, miny],
                        [maxx, maxy],
                        [minx, maxy],
                        [minx, miny],
                    ]
                ]
                # MultiPolygon coordinates: [ [ [[x,y]...] ] ]
                coordinates = [polygon_coordinates]
                dataset.spatial.geom = {
                    "type": "MultiPolygon",
                    "coordinates": coordinates,
                }
        except (ValueError, AttributeError, TypeError):
            pass
