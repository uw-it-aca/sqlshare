
STARTING_DIR=`pwd`

echo $STARTING_DIR

mkdir /tmp/rest_server
cd /tmp/rest_server

echo "now in `pwd`"


git clone https://github.com/uw-it-aca/sqlshare-rest.git
cd sqlshare-rest
virtualenv .
git checkout feature/management-command-client
source bin/activate
pip install -r requirements.txt
pip install PyMySQL
django-admin.py startproject project .
cp $STARTING_DIR/travis-ci/rest-server-settings.py project/settings.py
cp $STARTING_DIR/travis-ci/rest-server-urls.py project/urls.py

python manage.py syncdb --noinput

CLIENT_VALUES=`python manage.py create_client_app --name TestApp --return-url http://localhost:8000/oauth --owner-username=test_owner`
export OAUTH_CLIENT_ID=`echo $CLIENT_VALUES | cut -d ' ' -f 1 | cut -d : -f 2`
export OAUTH_CLIENT_SECRET=`echo $CLIENT_VALUES | cut -d ' ' -f 2 | cut -d : -f 2`

echo "ID: $OAUTH_CLIENT_ID, $OAUTH_CLIENT_SECRET"


python manage.py runserver localhost:9000 &

cd $STARTING_DIR

