release: python manage.py migrate --no-input && python manage.py collectstatic --clear --noinput
web: gunicorn --workers=3 monitorias.wsgi