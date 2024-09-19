import os
from dotenv import load_dotenv
import psycopg2
from .validator import validate
from .normalizer import normalize
from .check import check_page
from flask import (
    get_flashed_messages,
    flash,
    Flask,
    redirect,
    render_template,
    request,
    url_for
)
from .urls_repository import UrlsRepository

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')

conn = psycopg2.connect(app.config['DATABASE_URL'])
repo = UrlsRepository(conn)


@app.route('/')
def get_index():
    messages = get_flashed_messages(with_categories=True)
    return render_template('index.html', messages=messages)


@app.route('/urls', methods=['POST'])
def post_url():
    data = request.form.to_dict()
    errors = validate(data)

    if errors:
        flash(errors, 'danger')
        return redirect(url_for('get_index'))
    else:

        url_id = repo.save(normalize(data))

        if url_id is not None:
            flash('Страница успешно добавлена', 'success')
            return redirect(url_for('get_url', id=url_id))

        existing_url_id = repo.get_id_url(normalize(data))
        flash('Страница уже существует', 'info')
        return redirect(url_for('get_url', id=existing_url_id))


@app.route('/urls/<id>', methods=['GET'])
def get_url(id):
    messages = get_flashed_messages(with_categories=True)
    print(messages)
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
    data = repo.get_content()
    return render_template('urls.html', urls=data)


@app.route('/urls/<id>/checks', methods=['POST'])
def run_checks(id):
    url = repo.find(id)
    data = check_page(url['name'])
    if data is None:
        flash('Произошла ошибка при проверке', 'danger')
        return redirect(url_for('get_url', id=id))
    else:
        repo.save_checks(id, data)
        flash('Страница успешно проверена', 'success')
        return redirect(url_for('get_url', id=id))
