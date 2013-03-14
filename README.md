PaaS bakeoff
============

A [Mezzanine](http://mezzanine.jupo.org) project template that demonstrates how to deploy Django projects to [several PaaS providers](http://appsembler.com/blog/paas-bakeoff-comparing-stackato-openshift-dotcloud-and-heroku-for-django-hosting-and-deployment/)

Usage
=====

First clone the code repository:

```
$ git clone git://github.com/appsembler/paasbakeoff.git
```

See the different PaaS providers that you can deploy to by looking at the branches:

```
$ git branch
* dotcloud
  heroku
  master
  openshift
  stackato
```

Then checkout the branch for the PaaS provider that you want to deploy to:

Stackato
--------

Download the Stackato [client](http://www.activestate.com/stackato/download_client) and create an account on their [sandbox](http://www.activestate.com/stackato/sandbox).

```
$ cd paasbakeoff
$ git checkout stackato
$ stackato push
```

See this [blog post](http://appsembler.com/blog/django-deployment-using-stackato/) for more details about deploying Mezzanine to Stackato.

OpenShift
---------

Download the OpenShift 'rhc' client and create an account on [OpenShift](http://openshift.redhat.com/).

```
$ rhc create -a mymezzanine -t python-2.6
$ rhc app cartridge add -c mysql-5.1 -a mymezzanine
$ cd mezzanine
$ git remote add paasbakeoff git://github.com/appsembler/paasbakeoff.git
$ git fetch paasbakeoff
$ git merge paasbakeoff/openshift
$ git push
```

See this [blog post](http://appsembler.com/blog/django-deployment-using-openshift/) for more details about deploying Mezzanine to OpenShift.

Dotcloud
--------

Pip install the dotcloud client and create an account on [Dotcloud](http://dotcloud.com)

```
$ cd paasbakeoff
$ git checkout dotcloud
$ dotcloud create mymezzanine
$ dotcloud push
```

Google App Engine
-----------------

```
	$ cd paasbakeoff
	$ git checkout gae
```

On MacOSX, you need to run this command::

```
	$ export PYTHONPATH="$PYTHONPATH:/Applications/GoogleAppEngineLauncher.app/Contents/Resources/GoogleAppEngine-default.bundle/Contents/Resources/google_appengine:/Applications/GoogleAppEngineLauncher.app/Contents/Resources/GoogleAppEngine-default.bundle/Contents/Resources/google_appengine/lib/django_1_4"
```

You must create the database from the SQL Prompt of the Google API Console with::

```
	CREATE DATABASE mezzdb;
```

Deploy using either the GoogleAppEngineLauncher app or on the command line. From the paasbakeoff directory::

```
	appcfg.py --oauth2 update .
```

Configuring 3rd party libraries
-------------------------------

* [Configuring libraries](https://developers.google.com/appengine/docs/python/python25/migrate27#Configuring_Libraries)

* [Supported libraries including Django, PIL, yaml, pycrypto, jinja2, lxml, numpy, ssl, matplotlib](https://developers.google.com/appengine/docs/python/tools/libraries27)

* [GAE and Virtualenv](http://rh0dium.blogspot.com/2010/02/development-strategy-for-google-app.html)

* [Running Django 1.3 in Google App Engine with Google Cloud SQL](http://www.joemartaganna.com/web-development/running-django-13-in-google-app-engine-with-google-cloud-sql/)
