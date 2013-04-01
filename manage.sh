PROJECT_NAME="mywebsite"
CLOUDSQL_DATABASENAME="blah"
CLOUDSQL_INSTANCENAME="djangomezzanine:djangomezzdb"
APPENGINE_SDK_LOCATION="/usr/local/google_appengine"
APPLICATION_ID="djangodeployermezz"

args=$@

manage_script () {
    env/bin/python $PROJECT_NAME/manage.py $@ --settings=$PROJECT_NAME.settings_appengine
}

export PYTHONPATH="env/lib/python2.7:$APPENGINE_SDK_LOCATION:$APPENGINE_SDK_LOCATION/lib/django-1.4"
export DJANGO_SETTINGS_MODULE="$PROJECT_NAME.settings_appengine"
export APPLICATION_ID

if [ $1 == "cloudcreatedb" ] ; then
    echo "create database $CLOUDSQL_DATABASENAME;" | $APPENGINE_SDK_LOCATION/google_sql.py $CLOUDSQL_INSTANCENAME 
elif [ $1 == "cloudsyncdb" ] ; then
    export SETTINGS_MODE=prod && manage_script syncdb
else
    manage_script $args
fi
