class UrlInDatabase(Exception):
    """Исключение, возникающее, когда URL уже существует в базе данных."""
    pass


class WrongUrl(Exception):
    """Исключение, возникающее при некорректном формате URL."""
    pass


class PageCheckError(Exception):
    """Исключение, возникающее при ошибках проверки веб-страницы."""
    pass
