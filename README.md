PaaS bakeoff
============

A [Mezzanine](http://mezzanine.jupo.org) site that demonstrates how to deploy Django projects to [several PaaS providers](http://appsembler.com/blog/paas-bakeoff-comparing-stackato-openshift-dotcloud-and-heroku-for-django-hosting-and-deployment/)

Usage
=====

First clone the code repository:

```
$ git clone git://github.com/appsembler/paasbakeoff.git
```

Then checkout the branch for the PaaS provider that you want to deploy to:

Stackato
--------

Download the Stackato client and create an account on their sandbox.

```
$ cd paasbakeoff
$ git checkout stackato
$ stackato push
```

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

TODO

If you would like to contribute another PaaS (Gondor, AWS Elastic Beanstalk, Google App Engine, etc), please fork the project and submit a pull request. Thanks!

