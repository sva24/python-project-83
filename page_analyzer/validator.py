from validators.url import url


def validate(_url: dict):
    if not url(_url['url']):
        return "Некорректный URL"
    if len(_url['url']) > 255:
        return "Некорректный URL"
    return None
