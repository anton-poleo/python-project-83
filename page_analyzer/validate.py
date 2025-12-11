import validators


def validate_url(url):
    errors = []
    if not validators.url(url):
        errors.append('invalid URL.')
    if len(url) > 255:
        errors.append('URL must be no longer than 255 characters.')
    print(errors)
    return errors
