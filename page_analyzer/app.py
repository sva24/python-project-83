import os
from dotenv import load_dotenv
import psycopg2

from .validator import validate
from .normalizer import normalize
from .check import check_page
from .urls_repository import UrlsRepository

from flask import (
    get_flashed_messages,
    flash,
    Flask,
    redirect,
    render_template,
    request,
    url_for
)


load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')

conn = psycopg2.connect(app.config['DATABASE_URL'])
repo = UrlsRepository(conn)


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
    """Обрабатывает POST-запрос для добавления нового URL.

    Returns:
        Перенаправляет на страницу добавленного URL
        или на главную страницу в случае ошибки.
    """
    data = request.form.to_dict()
    errors = validate(data)

    if errors:
        flash(errors, 'danger')
        return redirect(url_for('get_index'))
    else:

        url_id = repo.save(normalize(data))

        if url_id is not None:
            flash('Страница успешно добавлена', 'success')
            repo.close()
            return redirect(url_for('get_url', id=url_id))

        existing_url_id = repo.get_id_url(normalize(data))
        flash('Страница уже существует', 'info')
        repo.close()
        return redirect(url_for('get_url', id=existing_url_id))


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
        repo.close()
        return render_template('error.html')
    repo.close()
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
    data = repo.get_content()
    repo.close()
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
    data = check_page(url['name'])
    if data is None:
        repo.close()
        flash('Произошла ошибка при проверке', 'danger')
        return redirect(url_for('get_url', id=id))
    else:
        repo.save_checks(id, data)
        repo.close()
        flash('Страница успешно проверена', 'success')
        return redirect(url_for('get_url', id=id))
