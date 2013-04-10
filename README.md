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

Heroku
------

Download the [Heroku toolbelt](https://toolbelt.heroku.com/) and create an account on [Heroku](http://heroku.com).

```
$ cd paasbakeoff
$ git checkout heroku
$ heroku create myapp
$ heroku addons:add heroku-postgresql:dev
$ git push heroku heroku:master
$ heroku run python mywebsite/manage.py syncdb
$ heroku run python mywebsite/manage.py collectstatic
```


If you would like to contribute another PaaS (Gondor, AWS Elastic Beanstalk, Google App Engine, etc), please fork the project and submit a pull request. Thanks!

