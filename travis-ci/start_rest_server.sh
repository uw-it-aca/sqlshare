
STARTING_DIR=`pwd`

mkdir /tmp/rest_server
cd /tmp/rest_server


git clone https://github.com/uw-it-aca/sqlshare-rest.git
cd sqlshare-rest
virtualenv .
git checkout develop
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

python manage.py runserver localhost:9000 &
python manage.py run_dataset_queue --verbose &
python manage.py run_query_queue --verbose &

cd $STARTING_DIR

