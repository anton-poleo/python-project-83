from bs4 import BeautifulSoup


def parse_response(response):
    content = BeautifulSoup(response.text, "lxml")
    meta = content.find('meta', {'name': 'description'})

    return {
        'status': response.status_code,
        'h1': content.h1.string if content.h1 else None,
        'title': content.title.string if content.title else None,
        'description': meta.get('content') if meta else None,
    }
