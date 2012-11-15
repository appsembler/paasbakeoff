OpenShift is a platform-as-a-service (PaaS) that lets you quickly and easily deploy Django/Python apps to a production hosting environment. The OpenShift software is open source so you can either run it on servers that you own or rent, or you can use Redhat's hosted OpenShift service at http://openshift.redhat.com

This is the third article in `a series about deploying Django web applications using a PaaS <http://appsembler.com/blog/django-deployment-using-paas/>`_. I'll walk you through the steps to deploy Mezzanine, a popular Django-based blogging and content management system (CMS).

The first thing you need to do is install the OpenShift client (rhc). We're assuming that you're on Linux or MacOSX and have Ruby already installed::

    $ sudo gem install rhc

Next we'll run the setup which creates a config file and SSH keypair::

    $ rhc setup

I found that at least on MacOSX, I had to add the SSH key and start the SSH agent::

    $ ssh-add ~/.ssh/id_rsa
    $ ssh-agent

To make sure that you have everything set up properly, you can run some tests which should all pass::

    $ rhc domain status

Quick 'n dirty instructions
---------------------------

If you don't want to go through the entire example below, but just want a shortcut to deploying Mezzanine, you can do the following::

    $ rhc app create -a mezzanineopenshift -t python 2.6
    $ rhc cartridge add -c mysql-5.1 -a mezzanineopenshift
    $ cd mezzanineopenshift
    $ git remote add paasbakeoff git://github.com/appsembler/paasbakeoff.git
    $ git fetch paasbakeoff
    $ git merge paasbakeoff/openshift
    $ git push

The repository that contains the code used in this example can be found in the `openshift` branch:
https://github.com/appsembler/paasbakeoff/tree/openshift

Creating the app
----------------

Now we'll create a new app for our Mezzanine site::

    $ rhc app create -a mezz -t python-2.6
    Password: ******

    Creating application 'mezz'
    ===========================

      Scaling:   no
      Cartridge: python-2.6
      Namespace: natea
      Gear Size: default

    Your application's domain name is being propagated worldwide (this might take a minute)...
    Cloning into 'mezz'...
    done

    mezz @ http://mezz-natea.rhcloud.com/
    =====================================
      Application Info
      ================
        UUID      = 0e94a6186e07430f8d9b989fdf702362
        Gear Size = small
        Git URL   = ssh://0e94a6186e07430f8d9b989fdf702362@mezz-natea.rhcloud.com/~/git/mezz.git/
        SSH URL   = ssh://0e94a6186e07430f8d9b989fdf702362@mezz-natea.rhcloud.com
        Created   = 9:20 PM
      Cartridges
      ==========
        python-2.6

    RESULT:
    Application mezz was created.

Check to see that it is in fact running::

    $ rhc app show mezz --state
    Password: ******

    RESULT:
    Geargroup python-2.6 is started

You'll notice that it created the app with the URL mezz-natea.rhcloud.com. That's because "natea" is my namespace. In OpenShift, each app is a "gear" and with the free account you only get 3 gears. `A gear <https://openshift.redhat.com/community/faq/what-is-a-gear>`_ is a container with a set of resources that allows users to run their applications. OpenShift runs many gears on each virtual machine and dynamically distributes gears across them. 

Applications are made up of at least one framework that is contained in a cartridge and runs on one or more gears. Additional cartridges can be added to the application on the same or different gears.

Inspecting the auto-generated git repository
--------------------------------------------

You'll also notice that there is a Git URL and an SSH URL. A git repo has already been cloned to my computer, and using the SSH credentials, I can login to the remote instance and poke around - although unlike the Stackato PaaS, we can't install arbitrary system packages using apt-get or yum.

Let's take a look at the git repo that was created::

    $ cd mezz
    $ ls -la
    total 24
    drwxr-xr-x   7 nateaune  staff   340 Nov 13 21:20 .
    drwxr-xr-x  23 nateaune  staff   816 Nov 13 21:20 ..
    drwxr-xr-x   8 nateaune  staff   442 Nov 13 21:20 .git
    -rw-r--r--   1 nateaune  staff    12 Nov 13 21:20 .gitignore
    drwxr-xr-x   5 nateaune  staff   170 Nov 13 21:20 .openshift
    -rw-r--r--   1 nateaune  staff  2703 Nov 13 21:20 README
    drwxr-xr-x   2 nateaune  staff   102 Nov 13 21:20 data
    drwxr-xr-x   2 nateaune  staff   102 Nov 13 21:20 libs
    -rw-r--r--   1 nateaune  staff   283 Nov 13 21:20 setup.py
    drwxr-xr-x   3 nateaune  staff   136 Nov 13 21:20 wsgi


Defining dependencies in the setup.py file
------------------------------------------

Unlike the other PaaS providers that use a `requirements.txt`, with OpenShift they use a more Pythonic way of requiring a `setup.py` to be in your repo. In this file you define all of your Python package dependencies.

Since we're deploying Mezzanine, we only have one package to list in our setup.py file::

    from setuptools import setup, find_packages

    setup(name='paasbakeoff',
        version='1.0',
        author='Nate Aune',
        author_email='nate@appsembler.com',
        url='https://github.com/appsembler/paasbakeoff',
        packages=find_packages(),
        include_package_data=True,
        description='Example Mezzanine CMS deploy to OpenShift PaaS',
        install_requires=['Mezzanine==1.2.4',],
    )

Now we can install Mezzanine into our virtualenv with::

    $ python setup.py develop

Creating a new skeleton Mezzanine project
-----------------------------------------

Next we use the `mezzanine-project` command that comes with Mezzanine to create a new project::

    $ mezzanine-project mywebsite
    $ ls mywebsite
    -rw-r--r--  1 nateaune  staff      0 Nov 13 21:35 __init__.py
    drwxr-xr-x  2 nateaune  staff    238 Nov 13 21:37 deploy
    -rw-r--r--  1 nateaune  staff  15282 Nov 13 21:35 fabfile.py
    -rw-r--r--  1 nateaune  staff    548 Nov 13 21:35 local_settings.py
    -rw-r--r--  1 nateaune  staff    898 Nov 13 21:35 manage.py
    drwxr-xr-x  2 nateaune  staff    102 Nov 13 21:37 requirements
    -rw-r--r--  1 nateaune  staff  13115 Nov 13 21:37 settings.py
    -rw-r--r--  1 nateaune  staff   3955 Nov 13 21:35 urls.py

You can see that this is a standard Django project directory layout, with manage.py, settings.py and urls.py files.

Tell setup.py to reference project.txt (optional)
-------------------------------------------------

Mezzanine includes it's requirements in a `requirements/project.txt` file, so we can tell our `setup.py` to use this file instead of hardcoding the dependencies. This means we only need to add new requirements to `project.txt` instead of keeping both of these files up-to-date::

    import os
    from setuptools import setup, find_packages

    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

    setup(name='paasbakeoff',
        version='1.0',
        author='Nate Aune',
        author_email='nate@appsembler.com',
        url='https://github.com/appsembler/paasbakeoff',
        packages=find_packages(),
        include_package_data=True,
        description='Example Mezzanine CMS deploy to OpenShift PaaS',
        install_requires=open('%s/mywebsite/requirements/project.txt' % os.environ.get('OPENSHIFT_REPO_DIR', PROJECT_ROOT)).readlines(),
    )

You'll notice that we're referencing `OPENSHIFT_REPO_DIR` here to indicate the root of our repo, but it will fallback to `PROJECT_ROOT` if it doesn't find that in the environment. We'll explain these OpenShift environment variables more later.

Note: this is not a necessary step for deploying Mezzanine to OpenShift. It's optional and only mentioned here for convenience.

Creating the wsgi application
-----------------------------

Next we need to edit the `/wsgi/application` file to tell OpenShift how to bind to our application. Replace the `application` file in the `wsgi` directory with this::

    #!/usr/bin/env python

    import os
    import sys

    sys.path.append(os.path.join(os.environ['OPENSHIFT_REPO_DIR']))

    os.environ['DJANGO_SETTINGS_MODULE'] = 'mywebsite.settings'

    virtenv = os.environ['OPENSHIFT_HOMEDIR'] + 'python-2.6/virtenv/'
    os.environ['PYTHON_EGG_CACHE'] = os.path.join(virtenv, 'lib/python2.6/site-packages')

    virtualenv = os.path.join(virtenv, 'bin/activate_this.py')
    try:
        execfile(virtualenv, dict(__file__=virtualenv))
    except IOError:
        pass
    #
    # IMPORTANT: Put any additional includes below this line.  If placed above this
    # line, it's possible required libraries won't be in your searchable path
    # 

    import django.core.handlers.wsgi
    application = django.core.handlers.wsgi.WSGIHandler()

We're adding the `OPENSHIFT_REPO_DIR` to our Python path, so that `mywebsite` will be found, and then we're setting `mywebsite.settings` as our `DJANGO_SETTINGS_MODULE`. 

We're also defining the virtual environment as `python-2.6/virtenv/` inside the `OPENSHIFT_HOMEDIR`. If you're wondering what all the environment variables are, you can SSH into the environment and run `env` or you can consult `this page <https://openshift.redhat.com/community/page/openshift-environment-variables>`_

Create and bind the database
----------------------------

We could use a SQLite database and store that in OpenShift's persisted `/data/` directory, but MySQL or PostgreSQL are more suitable databases to use in production, so we'll show how to set those up with OpenShift.

To bind a database to this "gear", you must add what OpenShift calls a `cartridge <https://openshift.redhat.com/community/faq/what-is-a-cartridge>`_. Cartridges are the containers that house the framework or components that can be used to create an application. One or more cartridges run on each gear or the same cartridge can run on many gears for clustering or scaling.

Let's add the MySQL cartridge::

    $ rhc cartridge add -c mysql-5.1 -a mezz
    Password: ******

    Adding 'mysql-5.1' to application 'mezz'
    Success
    mysql-5.1
    =========
      Properties
      ==========
        Connection URL = mysql://127.12.26.129:3306/
        Database Name  = mezz
        Password       = **********
        Username       = admin

If you'd rather use PostgreSQL, the command is similar to the one above for creating a MySQL database::

    $ rhc cartridge add -c postgresql-8.4 -a mezz

Telling Django about the database OpenShift created for us
----------------------------------------------------------

Now we need to make some changes to the `settings.py` file so that our Django app will work with the database that OpenShift just created for us. 

Edit the `DATABASES` section of the `settings.py` file to have the following (yeah, this code could be cleaner)::

    import os
    import urlparse

    DATABASES = {}
    if 'OPENSHIFT_MYSQL_DB_URL' in os.environ:
        url = urlparse.urlparse(os.environ.get('OPENSHIFT_MYSQL_DB_URL'))

        DATABASES['default'] = {
            'ENGINE' : 'django.db.backends.mysql',
            'NAME': os.environ['OPENSHIFT_APP_NAME'],
            'USER': url.username,
            'PASSWORD': url.password,
            'HOST': url.hostname,
            'PORT': url.port,
            }

    elif 'OPENSHIFT_POSTGRESQL_DB_URL' in os.environ:
        url = urlparse.urlparse(os.environ.get('OPENSHIFT_POSTGRESQL_DB_URL'))

        DATABASES['default'] = {
            'ENGINE' : 'django.db.backends.postgresql_psycopg2',
            'NAME': os.environ['OPENSHIFT_APP_NAME'],
            'USER': url.username,
            'PASSWORD': url.password,
            'HOST': url.hostname,
            'PORT': url.port,
            }
            
    else:
        DATABASES['default'] = {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'dev.db',
            'USER': '',
            'PASSWORD': '',
            'HOST': '',
            'PORT': '',
            }

Again, we're using OpenShift-specific environment variables to test if there is a MySQL or PostgreSQL database available, and if so we're extracting the database name, username, password, hostname and post from the provided URL string.

Create a deploy script
----------------------

You'll notice that there is a `.openshift` directory in the project that contains another directory called `action_hooks`. This is where we define scripts that will run on every build or on every deploy.

Replace the `deploy` script with the following::

    #!/bin/bash
    # This deploy hook gets executed after dependencies are resolved and the
    # build hook has been run but before the application has been started back
    # up again.  This script gets executed directly, so it could be python, php,
    # ruby, etc.

    source ${OPENSHIFT_HOMEDIR}python-2.6/virtenv/bin/activate
     
    export PYTHON_EGG_CACHE=${OPENSHIFT_HOME_DIR}python-2.6/virtenv/lib/python-2.6/site-packages

    echo "Executing 'python ${OPENSHIFT_REPO_DIR}mywebsite/manage.py syncdb --noinput'"
    python "$OPENSHIFT_REPO_DIR"mywebsite/manage.py syncdb --noinput

    echo "Executing 'python ${OPENSHIFT_REPO_DIR}mywebsite/manage.py collectstatic --noinput -v0'"
    python "$OPENSHIFT_REPO_DIR"mywebsite/manage.py collectstatic --noinput -v0

Here we can define any Django management commands that we want to be run on every deploy, namely `syncdb` and `collectstatic`. If we were using South for database schema migrations (as all Django projects should do), we could add the `migrate` command as well.

You can read about all the different action hooks (pre-receive, pre-build, build, deploy, post-deploy) `here <https://openshift.redhat.com/community/developers/deploying-and-building-applications>`_.

Example of a `more sophisticated deploy script <https://github.com/openshift/reviewboard-example/blob/master/.openshift/action_hooks/deploy>`_ for deploying Reviewboard.

Handling static media
---------------------

OpenShift provides a directory `wsgi/static` that can be exposed to Apache and serve up static assets, so we need to tell Django to collect the static media to this directory. Replace the `STATIC_ROOT` definition in `settings.py` with the following::

    if 'OPENSHIFT_REPO_DIR' in os.environ:
        STATIC_ROOT = os.path.join(os.environ.get('OPENSHIFT_REPO_DIR'), 'wsgi', 'static')
    else:
        STATIC_ROOT = os.path.join(PROJECT_ROOT, STATIC_URL.strip("/"))

Next we need to tell Apache to serve up media at `/static/` from this directory. Add an `.htaccess` file to `/wsgi/static/` directory::

    RewriteEngine On
    RewriteRule ^application/static/(.+)$ /static/$1 [L]

Handling uploaded media
-----------------------

OpenShift will wipe out the remote repo directory on every deploy, so if you want to make sure uploaded media files are persisted, you need to store them in the special `/data/` dir that OpenShift provides. Replace the `MEDIA_ROOT` definition in `settings.py` with the following::

    if 'OPENSHIFT_DATA_DIR' in os.environ:
        MEDIA_ROOT = os.path.join(os.environ.get('OPENSHIFT_DATA_DIR'), 'media')
    else:
        MEDIA_ROOT = os.path.join(PROJECT_ROOT, *MEDIA_URL.strip("/").split("/"))

We also need to symlink this directory into `/wsgi/static/media/` so that the media assets will be served up by Apache. Add the following to the `build` script in `.openshift/action_hooks`::

    #!/bin/bash
    # This is a simple build script and will be executed on your CI system if 
    # available.  Otherwise it will execute while your application is stopped
    # before the deploy step.  This script gets executed directly, so it
    # could be python, php, ruby, etc.

    if [ ! -d $OPENSHIFT_DATA_DIR/media ]; then
    mkdir $OPENSHIFT_DATA_DIR/media
    fi

    ln -sf $OPENSHIFT_DATA_DIR/media $OPENSHIFT_REPO_DIR/wsgi/static/media

Deploying the app
-----------------

Once you've got all of these things in place, it's finally time to try deploying the app. This is done with a simple `git push`::

    $ git push
    Counting objects: 5, done.
    Delta compression using up to 2 threads.
    Compressing objects: 100% (3/3), done.
    Writing objects: 100% (3/3), 498 bytes, done.
    Total 3 (delta 1), reused 0 (delta 0)
    remote: restart_on_add=false
    remote: Waiting for stop to finish
    remote: Done
    remote: restart_on_add=false
    remote: ~/git/mezz.git ~/git/mezz.git
    remote: ~/git/mezz.git
    remote: Running .openshift/action_hooks/pre_build
    remote: setup.py found.  Setting up virtualenv
    remote: New python executable in /var/lib/openshift/0e94a6186e07430f8d9b989fdf702362/python-2.6/virtenv/bin/python
    remote: Installing setuptools............done.
    remote: Installing pip...............done.
    ...
    remote: Running .openshift/action_hooks/deploy
    remote: hot_deploy_added=false
    remote: MySQL already running
    remote: Done
    remote: Running .openshift/action_hooks/post_deploy
    To ssh://0e94a6186e07430f8d9b989fdf702362@mezz-natea.rhcloud.com/~/git/mezz.git/
       03605bf..e05607c  master -> master

If everything went well, you can go to http://mezz-natea.rhcloud.com to see the running app. 
You can login to the Mezzanine admin dashboard with these credentials. Username: admin Password: P@s$w0rd1

Troubleshooting
---------------

If there were any errors they will show up in the stdout, or you can tail the log files with::

    $ rhc tail -a mezz

Subsequent deploys
------------------

One thing that is nice about OpenShift is that the next time we deploy, it will see that these eggs are already installed in the virtual environment and not install them again. If we want to force a clean build, we can add a `force_clean_build` marker file in the `.openshift/markers/` directory.

Since downloading all the packages and installing them is the most time-consuming part of the build and deploy process, this feature significantly speeds up subsequent deploys.

Avoiding downtime during deploys
--------------------------------

You can also set a marker `hot_deploy` which will dynamically reload python scripts via WSGI Daemon mode, so that you don't experience any downtime when deploying a new version of your app.

Or you can `use Jenkins <https://access.redhat.com/knowledge/docs/en-US/OpenShift/2.0/html/User_Guide/sect-OpenShift-User_Guide-Using_the_Jenkins_Embedded_Build_System.html>`_ to avoid downtime when deploying.

Deploying an existing Git repo
------------------------------

Since OpenShift creates a git repo for your app, if you have code living in an existing Github repo, you need to pull that into the OpenShift git repo before you can push it. The OpenShift documentation says to do it this way::

    $ rhc app create -a mydjangoapp -t python-2.6
    $ cd mydjangoapp
    $ git remote add upstream -m master git://github.com/openshift/django-example.git
    $ git pull -s recursive -X theirs upstream master

This will pull in the code from the `django-example` and merge it with the repo that OpenShift created on your local machine. You can then deploy this with the usual `git push`.

I've found that you can also just fetch the code from the remote repo and merge it like this::

    $ git remote add django-example git://github.com/openshift/django-example.git
    $ git fetch django-example
    $ git merge django-example/master

Python 2.7 on OpenShift
-----------------------

OpenShift currently only supports Python 2.6, but there are `several <https://github.com/ehazlett/openshift-diy-py27-django>`_ `Github <https://github.com/zemanel/openshift-diy-django-example>`_ `repos <https://github.com/ksurya/openshift-diy-py27-django-jenkins>`_ explaining how to build Python 2.7 on a DIY cartridge.


Other features of OpenShift
---------------------------

For this blog post, we didn't have time to go into all the features of OpenShift, but if you're interested in learning more I invite you to check out the following links. And if you'd like to see more articles like this one, `subscribe to the SaaS Developers Kit newsletter <http://eepurl.com/qlVfj>`_, and you'll get an email the next time we publish.

 * `Snapshotting (backing up) your application <https://access.redhat.com/knowledge/docs/en-US/OpenShift/2.0/html/User_Guide/chap-OpenShift-User_Guide-Storage_Management.html#sect-OpenShift-User_Guide-Backing_up_and_Restoring_Configuration_and_User_Data>`_
 * `Cron jobs <https://openshift.redhat.com/community/videos/getting-started-with-cron-jobs-on-openshift>`_
 * `Celery support <https://bugzilla.redhat.com/show_bug.cgi?id=814991>`_
 * `Remote SSH access <https://openshift.redhat.com/community/developers/remote-access>`_
 * `Scaling your application <https://openshift.redhat.com/community/developers/scaling>`_
 * `Jenkins builds <https://openshift.redhat.com/community/jenkins>`_
 * `Extending OpenShift with your own languages and datastores <https://openshift.redhat.com/community/developers/do-it-yourself>`_

What's next?
------------

Now that you've successfuly deployed Mezzanine, you can try a bunch of other apps (Python or non-Python) on the `getting started <https://openshift.redhat.com/community/developers/get-started>`_ page, or you can use `Luke Macken's <http://lewk.org/>`_ excellent `OpenShift quickstarter <https://github.com/lmacken/openshift-quickstarter>`_ which lets you deploy 22 different frameworks and applications to OpenShift with a single command.

OpenShift is open source software, so if you want to test out OpenShift on your local machine, you can `download the LiveCD <https://openshift.redhat.com/community/wiki/getting-started-with-openshift-origin-livecd>`_

Or if you're feeling really adventurous, you can use OpenShift to `build a private PaaS on servers that you control <https://openshift.redhat.com/community/wiki/build-your-own>`_.

References
----------

 * `OpenShift Manual <https://access.redhat.com/knowledge/docs/en-US/OpenShift/2.0/html/User_Guide/index.html>`_
 * `Official OpenShift Django example <https://github.com/openshift/django-example>`_
 * `How to create a Django application on OpenShift <http://peng-fei-xue.blogspot.com/2012/06/howto-create-django-application-in.html>`_
 * `Mezzanine customized and optimized for the OpenShift platform <https://github.com/overshard/mezzanine-openshift>`_
 * `Running Mezzanine on OpenShift <https://github.com/k4ml/mezzanine-openshift/>`_
 * `Rapid Python and Django App Deployment to the Cloud with a PaaS  (July 2012) <https://openshift.redhat.com/community/blogs/rapid-python-and-django-app-deployment-to-the-cloud-with-a-paas>`_
 * `Serving up media files <http://masci.wordpress.com/2012/07/17/serving-django-media-files-in-openshift/>`_
 * `Adding custom python packages <https://openshift.redhat.com/community/forums/openshift/how-to-install-a-custom-python-package>`_
