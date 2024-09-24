from .check import check_page, PageCheckError

from .config import SECRET_KEY, DATABASE_URL

from .db import DbConnection
from .validator import UrlValidator, UrlNormalizer
from .repository import UrlsRepository, WrongUrl, UrlInDatabase
from .models import Url

from flask import (
    get_flashed_messages,
    flash,
    Flask,
    redirect,
    render_template,
    request,
    url_for
)

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['DATABASE_URL'] = DATABASE_URL

url_validator = UrlValidator()
url_normalizer = UrlNormalizer()
db_connection = DbConnection(app.config['DATABASE_URL'])

repo = UrlsRepository(db_connection, url_validator, url_normalizer)


@app.route('/')
def get_index():
    """Отображает главную страницу.

    Returns:
        Рендеринг шаблона 'index.html'.
    """
    messages = get_flashed_messages(with_categories=True)
    return render_template('index.html', messages=messages)


@app.route('/urls', methods=['POST'])
def post_url():
    """Обрабатывает POST-запрос для добавления нового URL."""
    data = request.form.to_dict()
    url = data['url']

    url_to_save = Url(name=url)

    try:
        url_id = repo.save(url_to_save)
        flash('Страница успешно добавлена', 'success')
        return redirect(url_for('get_url', id=url_id))

    except UrlInDatabase as e:
        existing_url_id = repo.get_url_id(url)
        flash(str(e), 'info')
        return redirect(url_for('get_url', id=existing_url_id))

    except WrongUrl as e:
        flash(str(e), 'danger')
        return render_template('index.html'), 422


@app.route('/urls/<id>', methods=['GET'])
def get_url(id):
    """Отображает страницу с информацией об URL.

    Args:
        id (int): Идентификатор URL.

    Returns:
        Рендерит шаблон 'show.html' с данными о URL и
        результатами проверок или шаблон 'error.html' в случае
        ошибки.
    """
    messages = get_flashed_messages(with_categories=True)
    url = repo.find(id)
    checks = repo.get_checks_for_url(id)
    if checks is None:
        checks = {}
    if url is None:
        return render_template('error.html')
    return render_template(
        'show.html',
        url=url,
        checks=checks,
        messages=messages)


@app.route('/urls', methods=['GET'])
def show_urls():
    """Отображает список всех сохраненных URL.

       Returns:
        Рендерит шаблон 'urls.html' со списком URL.
    """
    data = repo.get_all_urls()
    return render_template('urls.html', urls=data)


@app.route('/urls/<id>/checks', methods=['POST'])
def run_checks(id):
    """Запускает проверку указанного URL.

    Args:
        id (int): Идентификатор URL.

    Returns:
       Отображает сообщения о результате проверки.
    """
    url = repo.find(id)
    if url is None:
        flash('Некорректный URL', 'danger')
        return redirect(url_for('show_urls'))
    try:
        data = check_page(url.name)
    except PageCheckError as e:
        flash(str(e), 'danger')
        return redirect(url_for('get_url', id=id))

    repo.save_checks(id, data)
    flash('Страница успешно проверена', 'success')
    return redirect(url_for('get_url', id=id))
