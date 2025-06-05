from udata.harvest.backends.base import BaseBackend
from udata.models import Resource, Dataset, License
import requests
import logging

class DGTINEBackend(BaseBackend):
    display_name = 'INE Harvester'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)

    def inner_harvest(self):
        url = self.source.url
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'https://www.ine.pt/',
        }
        session = requests.Session()
        # Optional: visit the main page to get cookies
        session.get('https://www.ine.pt/', headers=headers)
        res = session.get(url, headers=headers)
        print(res.status_code)
        print(res.text[:500])
        res.encoding = 'utf-8'
        try:
            data = res.json()
        except Exception as e:
            self.logger.error(f'Error parsing JSON: {e}')
            return

        indicators = data.get('catalog', {}).get('indicators', [])
        if not indicators:
            self.logger.error('No indicators found in INE JSON.')
            return

        for ind in indicators:
            item = {
                'remote_id': ind.get('indicator_id'),
                'title': ind.get('title'),
                'description': ind.get('description'),
                'theme': ind.get('theme'),
                'sub_theme': ind.get('sub_theme'),
                'tags': ind.get('tags', []),
                'geo_lastlevel': ind.get('geo_lastlevel'),
                'date_published': ind.get('date_published'),
                'last_update': ind.get('last_update'),
                'periodicity': ind.get('periodicity'),
                'source': ind.get('source'),
                'resources': [
                    ind.get('bdd_url'),
                    ind.get('json_dataset'),
                    ind.get('json_metainfo')
                ],
                'meta_url': ind.get('meta_url'),
                'last_period_available': ind.get('last_period_available'),
                'activity_type': ind.get('activity_type'),
                'differenceInDays': ind.get('differenceInDays')
            }
            self.process_dataset(item['remote_id'], items=item)

    def inner_process_dataset(self, item: 'HarvestItem', **kwargs):
        dataset = self.get_dataset(item.remote_id)
        data = kwargs.get('items')

        dataset.title = data['title']
        dataset.description = (
            f"{data['description']}\n\n"
            f"Theme: {data['theme']} | Subtheme: {data['sub_theme']}\n"
            f"Geo: {data.get('geo_lastlevel', '')}\n"
            f"Source: {data['source']}\n"
            f"Periodicity: {data['periodicity']}\n"
            f"Published on: {data['date_published']} | Updated on: {data['last_update']}\n"
            f"Last period available: {data.get('last_period_available', '')}\n"
            f"Activity type: {data.get('activity_type', '')}\n"
            f"Days since last update: {data.get('differenceInDays', '')}\n"
            f"Metadata: {data['meta_url']}"
        )
        dataset.license = License.guess('cc-by')
        dataset.tags = ['ine.pt'] + data.get('tags', [])

        # Resources
        dataset.resources = []
        for url in data.get('resources', []):
            if url:
                dataset.resources.append(Resource(
                    title=data['title'],
                    url=url,
                    filetype='remote',
                    format=url.split('.')[-1] if '.' in url else 'file'
                ))

        dataset.extras['harvest:name'] = self.source.name
        return dataset
