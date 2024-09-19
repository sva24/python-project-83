from validators.url import url


def validate(_url: dict) -> str | None:
    """Проверяет корректность URL.

        Args:
            _url (dict): Словарь, содержащий ключ 'url' с
            проверяемым URL-адресом.

        Returns:
            str | None: Возвращает строку с сообщением об ошибке, если
            URL некорректен или превышает 255 символов. Если URL корректен,
            возвращает None.
         """
    if not url(_url['url']):
        return "Некорректный URL"
    if len(_url['url']) > 255:
        return "Некорректный URL"
    return None
