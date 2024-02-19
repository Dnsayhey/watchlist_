### Watchlist

```shell
pip install -r requirements.txt
pip install gunicorn
flask initdb --drop
flask forge
flask admin --username admin --password admin
gunicorn --workers=2 --bind=0.0.0.0:5000 wsgi:app
```