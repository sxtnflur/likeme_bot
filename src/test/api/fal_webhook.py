import unittest

import requests


class TestAPI(unittest.TestCase):
    def test_create_model(self):
        res = requests.post(
              'https://bigling.ru/likeme/fal_webhook/train-model',
                json={
                'request_id': 'e7f2abec-e7d6-4434-96f1-cd1317c03303',
                'status': 'OK',
                'payload': {
                      "diffusers_lora_file": {
                        "url": "https://v3b.fal.media/files/b/lion/CXDH9Xl68QagWlxNHo0Ua_pytorch_lora_weights.safetensors",
                        "content_type": None,
                        "file_name": None,
                        "file_size": None
                      },
                      "config_file": {
                        "url": "https://v3b.fal.media/files/b/elephant/xGcJwKxxJOxgUk9tGmL_P_config.json",
                        "content_type": "application/octet-stream",
                        "file_name": "config.json",
                        "file_size": 356
                      }
                }
            })
        data = res.json()
        print(f'{data=}')
        assert res.status_code == 200
