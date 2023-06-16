# TransHelp

## Running with Docker

```bash
docker compose build
docker compose up
```

To add some user you may use:
```bash
docker exec -it e13bfeffbc6e python3 /code/manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_user('user', 'user@email.com', 'pass'); from django.contrib.auth.models import Permission; permission = Permission.objects.get(codename='add_registrationoffer'); adminuser = User.objects.create_user('adminuser', 'some@email.pl', 'pass'); adminuser.user_permissions.add(permission); adminuser.save()"
```

where `e13bfeffbc6e` is container id of `transhelp-web` service that you may check with `docker container ls`

Try http://localhost:8000 to make some tests.

## Running locally

To avoid setting up nginx to serve static and user files you need to change configuration.
Make sure that `REC_ROOT_DP` from `settings.py` points to existing directory. Set the following:
```python
DEBUG = True

MEDIA_ROOT = REC_ROOT_DP
MEDIA_URL = "/media/"
REC_PORT = 8000

STATIC_URL = "/static/"
```

Try the following steps:

```bash
virtualenv -p python3 venv
. venv/bin/activate
pip install -r requirements.txt
cd transhelp
python manage.py makemigrations trans
python manage.py migrate

###
# add users
###

python3 manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_user('user', 'user@email.com', 'pass'); from django.contrib.auth.models import Permission; permission = Permission.objects.get(codename='add_registrationoffer'); adminuser = User.objects.create_user('adminuser', 'some@email.pl', 'pass'); adminuser.user_permissions.add(permission); adminuser.save()"

python manage.py runserver 127.0.0.1:8000

###
# or
###
gunicorn --bind=127.0.0.1 --workers=2 --threads=4 transhelp.wsgi
```


