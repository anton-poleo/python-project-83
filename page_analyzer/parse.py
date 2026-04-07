from bs4 import BeautifulSoup


def parse_response(response):
    content = BeautifulSoup(response.content, "html.parser")
    meta = content.find('meta', {'name': 'description'})

    h1 = content.h1.text if content.h1 else None
    title = content.title.string if content.title else None

    description = meta.get('content') if meta else None
    if description and len(description) > 200:
        description = f'{description[:200]}...'
    return {
        'status': response.status_code,
        'h1': f'{h1[:200]}...' if h1 and len(h1) > 200 else h1,
        'title': f'{title[:200]}...' if title and len(title) > 200 else title,
        'description': description,
    }
