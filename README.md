paasbakeoff
===========

A skeleton Mezzanine project demonstrating how to deploy it to each PaaS provider.


Create the app
--------------

Before you can deploy the app, you need to tell Heroku about it::

	$ heroku create paasbakeoff
	Creating paasbakeoff... done, stack is cedar
	http://paasbakeoff.herokuapp.com/ | git@heroku.com:paasbakeoff.git

Attach a PostgreSQL database
----------------------------

Add a PostgreSQL database using the free plan (10,000 rows max)::

	$ heroku addons:add heroku-postgresql:dev
	Adding heroku-postgresql:dev on paasbakeoff... done, v10 (free)
	Attached as HEROKU_POSTGRESQL_GOLD_URL
	Database has been created and is available

Push it to Heroku
-----------------

When you want to deploy to Heroku, you need to set some environment variables.

This will set the RACK_ENV value to production so that settings.py will use the Heroku settings::

	$ heroku config:add RACK_ENV=production

And then do the actual push using git::

	$ git push heroku heroku:master
	...
	-----> Launching... done, v7
	       http://paasbakeoff.herokuapp.com deployed to Heroku
	...

Set the AWS credentials
-----------------------

You need to set up some AWS settings for static files and uploaded media to be served up by S3::

	$ heroku config:set AWS_ACCESS_KEY_ID=xxxxxxxxxxxxxxxxx
	$ heroku config:set AWS_SECRET_ACCESS_KEY=yyyyyyyyyyyyyyyyyyyyyyyyy
	$ heroku config:set AWS_STORAGE_BUCKET_NAME=zzzzzzzzzzzzz

Sync and migrate the database
-----------------------------

Mezzanine provides a convenience command for running syncdb and migrate::

	$ heroku run python mywebsite/manage.py createdb

Collect the static assets
-------------------------

Collect the static assets using the collectstatic command::

	$ heroku run python mywebsite/manage.py collectstatic

If your static media doesn't show up, try running this::

	$ heroku labs:enable user-env-compile -a coderaising
	$ heroku run python manage.py collectstatic

If the deploy is taking too long, you can tell Heroku not to run the collectstatic command::

	$ mkdir .heroku
	$ touch .heroku/collectstatic_disabled

Read more about serving up static assets with Django on Heroku:
https://devcenter.heroku.com/articles/django-assets

Setting up email
----------------

In order to send emails when new users register on the site, we need to add Sendgrid::

	$ heroku addons:add sendgrid:starter

Then go to http://sendgrid.com/account/overview to see your Sendgrid username and password::

	$ heroku config:add SENDGRID_USERNAME=<username>
	$ heroku config:add SENDGRID_PASSWORD=<password>

Read more about Sendgrid configuration with Django here: http://sendgrid.com/docs/Integrate/Frameworks/django.html
Also check out django-sendgrid-events: http://django-sendgrid-events.readthedocs.org/en/latest/
