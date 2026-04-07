import validators


def validate_url(url):
    errors = []
    if not validators.url(url):
        errors.append('Некорректный URL')
    if len(url) > 255:
        errors.append('URL должен быть короче 255 символов')
    print(errors)
    return errors
