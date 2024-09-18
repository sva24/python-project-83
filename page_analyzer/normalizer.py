from urllib.parse import urlparse


def normalize(url):
    parsed_url = {}
    url = urlparse(url['url'])
    parsed_url['url'] = f'{url.scheme.lower()}://{url.netloc.lower()}'
    return parsed_url
