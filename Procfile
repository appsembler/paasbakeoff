# Unlike the gunicorn defined in Heroku's Django example, we're going
# to use one of the async worker classes, "gevent". Using an async worker class
# is recommended when serving traffic directly to gunicorn (which is what
# happens under the Heroku Cedar stack).
#
# The web service is special-cased to provide a $PORT environment variable, 
# which is where Heroku will send your web traffic. We're using some sane 
# defaults (9 workers, 250 requests per worker before restarting them) for Gunicorn.

web: gunicorn_django -b 0.0.0.0:\$PORT -w 9 -k gevent --max-requests 250 --preload mywebsite/settings.py
#web: python mywebsite/manage.py run_gunicorn -b 0.0.0.0:\$PORT -w 9 -k gevent --max-requests 250 --preload
#web: python mywebsite/manage.py run_gunicorn -b "0.0.0.0:$PORT" -w 3
#web: python mywebsite/manage.py runserver 0.0.0.0:$PORT --noreload
