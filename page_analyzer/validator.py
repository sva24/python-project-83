from validators.url import url
from urllib.parse import urlparse

URL_MAX_LENGTH = 255


class UrlValidator:
    def __init__(self):
        """Инициализирует UrlValidator."""
        self.url = url
        self.error = ""

    def set_url(self, url: str) -> 'UrlValidator':
        """Устанавливает URL для проверки."""
        self.url = url
        return self

    def validate(self) -> 'UrlValidator':
        """Проверяет корректность URL.

        Returns:
            UrlValidator: Возвращает текущий экземпляр класса.
        """
        if not url(self.url):
            self.error = "Некорректный URL"
        if len(self.url) > URL_MAX_LENGTH:
            self.error = "Некорректный URL"
        return self

    def get_errors(self):
        return self.error


class UrlNormalizer:
    def __init__(self):
        """Инициализирует UrlNormalizer с URL для нормализации.

        Args:
            url (str): Не нормализованный URL-адрес.
        """
        self.url = url
        self.url_normalized = ''

    def set_url(self, url: str) -> 'UrlNormalizer':
        """Устанавливает URL для проверки."""
        self.url = url
        return self

    def normalize(self) -> str:
        """Нормализует URL, преобразуя его в нижний регистр.

        Returns:
            str: Нормализованный URL в формате 'scheme://netloc',
            где 'scheme' и 'netloc' приведены к нижнему регистру.
        """
        parsed_url = urlparse(self.url)
        self.url_normalized = (f'{parsed_url.scheme.lower()}:'
                               f'//{parsed_url.netloc.lower()}')
        return self.url_normalized
