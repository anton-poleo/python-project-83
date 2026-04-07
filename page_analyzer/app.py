import os
from urllib.parse import urlparse

import requests

from dotenv import load_dotenv
from flask import (
    abort,
    flash,
    Flask,
    redirect,
    render_template,
    request,
    url_for,
)

from page_analyzer.parse import parse_response
from page_analyzer.repository import URLRepository, make_pg_conn
from page_analyzer.validate import validate_url


app = Flask(__name__)
load_dotenv()
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')


@app.route('/')
def index():
    return render_template(
        'index.html',
    )


@app.route('/urls', methods=['POST'])
def add_url():
    url = request.form.to_dict()['url']
    errors = validate_url(url)
    if errors:
        flash(' '.join(errors), 'error')
        return render_template('index.html')

    url = urlparse(url)
    with make_pg_conn() as conn:
        rep = URLRepository(conn)

        obj = rep.get_by_name(f'{url.scheme}://{url.hostname}')
        if obj:
            id_ = obj['id']
            flash('Страница уже существует', 'error')
        else:
            id_ = rep.insert_url(f'{url.scheme}://{url.hostname}')
            flash('Страница успешно добавлена', 'success')

    return redirect(url_for('get_url', id=id_))


@app.route('/urls', methods=['GET'])
def get_urls():
    with make_pg_conn() as conn:
        rep = URLRepository(conn)
        urls_checks = rep.get_urls_checks()

    return render_template(
        'urls.html',
        urls_checks=urls_checks,
    )


@app.route('/urls/<int:id>')
def get_url(id):
    with make_pg_conn() as conn:
        rep = URLRepository(conn)
        url = rep.get_by_id(id)

        if not url:
            abort(404)

        url_checks = rep.get_url_checks(url['id'])

    return render_template(
        'url.html',
        url=url,
        url_checks=url_checks
    )


@app.route('/urls/<int:id>/checks', methods=['POST'])
def get_url_data(id):
    with make_pg_conn() as conn:
        rep = URLRepository(conn)
        url = rep.get_by_id(id)

        try:
            response = requests.get(url['name'], timeout=1)
            response.raise_for_status()
        except requests.RequestException:
            flash('Во время проверки возникла ошибка', 'error')
            return redirect(url_for('get_url', id=id))

        data = parse_response(response)
        print(data)
        rep.insert_url_check(url['id'], data)
        flash('Страница успешно проверена', 'success')
        return redirect(url_for('get_url', id=id))
