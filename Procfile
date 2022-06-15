release: python manage.py migrate --no-input
release: python manage.py collectstatic --clear --noinput
web: gunicorn monitorias.wsgi