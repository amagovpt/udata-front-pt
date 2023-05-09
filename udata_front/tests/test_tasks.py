import copy
import pytest

from flask import current_app

from udata.core.dataset.factories import DatasetFactory
from udata_front import APIGOUVPT_EXTRAS_KEY
from udata_front.tests import gouvptSettings
from udata_front.tasks import apigouvpt_load_apis


@pytest.mark.usefixtures('clean_db')
class ApigouvptTasksTest:
    settings = gouvptSettings
    modules = []

    def test_apigouvpt_load_apis(app, rmock):
        dataset = DatasetFactory()
        url = current_app.config.get('APIGOUVPT_URL')
        apis = [{
            'title': 'une API',
            'tagline': 'tagline',
            'path': '/path',
            'slug': 'slug',
            'owner': 'owner',
            'openness': 'open',
            'logo': '/logo.png',
        }]
        payload = copy.deepcopy(apis)
        payload[0]['datagouv_uuid'] = [str(dataset.id), 'nope']
        # missing fields, won't be processed
        payload.append({
            'title': 'une autre API',
            'datagouv_uuid': [str(dataset.id)],
        })
        rmock.get(url, json=payload)
        apigouvpt_load_apis()
        dataset.reload()
        assert dataset.extras.get(APIGOUVPT_EXTRAS_KEY) == apis
