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
    flash(url.hostname)
    with make_pg_conn() as conn:
        rep = URLRepository(conn)

        if rep.get_by_name(url.hostname):
            flash('URL already exists', 'error')
            conn.close()
            return render_template('index.html')

        flash('Страница успешно добавлена', 'success')

        id = rep.insert_url(f'{url.scheme}://{url.hostname}')

    return redirect(url_for('get_url', id=id))


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

    return render_template(
        'url.html',
        url=url,
    )


@app.route('/urls/<int:id>/checks', methods=['POST'])
def get_url_data(id):
    with make_pg_conn() as conn:
        rep = URLRepository(conn)
        url = rep.get_by_id(id)

        try:
            response = requests.get(url['name'], timeout=1)
            response.raise_for_status()
        except requests.RequestException as e:
            flash('Во время проверки возникла ошибка', 'error')
            print(e)
            return redirect(url_for('get_url', id=id))

        data = parse_response(response)
        rep.insert_url_check(url['id'], data)
        flash('Страница успешно проверена', 'success')
        url_checks = rep.get_url_checks(id)
        return render_template(
            'url.html',
            url=url,
            url_checks=url_checks,
        )
