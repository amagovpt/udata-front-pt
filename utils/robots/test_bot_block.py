
import pytest
from flask import url_for

class TestBotBlocking:
    def test_googlebot_blocked_on_fr(self, client):
        # Normal user accessing /fr/ (should be 404 as it doesn't exist, but NOT 403)
        # Note: /fr/ might not be a valid route at all, so 404 is expected.
        # We just want to ensure it's NOT 403.
        response = client.get('/fr/datasets/some-dataset', headers={'User-Agent': 'Mozilla/5.0'})
        assert response.status_code != 403
        
        # Googlebot accessing /fr/ (should be 403)
        response = client.get('/fr/datasets/some-dataset', headers={'User-Agent': 'Googlebot/2.1'})
        assert response.status_code == 403

    def test_googlebot_allowed_on_home(self, client):
        # Googlebot accessing home (should be 200)
        response = client.get('/', headers={'User-Agent': 'Googlebot/2.1'})
        assert response.status_code == 200

    def test_other_bots_blocked(self, client):
        # Bingbot accessing /fr/ (should be 403)
        response = client.get('/fr/datasets/some-dataset', headers={'User-Agent': 'Bingbot/2.0'})
        assert response.status_code == 403
