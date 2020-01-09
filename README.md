# django-booking-sample
Djangoを使った予約サイトのサンプル。[解説ブログ](https://narito.ninja/blog/detail/157/)

## 動かし方
```
git clone https://github.com/naritotakizawa/django-booking-sample
cd django-booking-sample
python manage.py runserver
```

その後、ブラウザで http://127.0.0.1:8000 へアクセスしてください。


## テストする
```
coverage run --source='.' manage.py test booking
coverage report -m
```
