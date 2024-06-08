import requests
import io
from os import path as osp


def load_from_url(url, loader: callable, **kwargs):
    response = requests.get(url)
    response.raise_for_status()
    return loader(io.BytesIO(response.content), **kwargs)
