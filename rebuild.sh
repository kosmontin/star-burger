#!/bin/bash
param=$1
set -e
echo "Trying to rebuild star-burger project..."
cd /opt/projects/star-burger/
if [[ $(git status) != *"nothing to commit, working tree clean"* ]]
then
echo "Uncommited changes are present. Use <git status> in bash to show more details"
exit 0
fi
if [[ $(git pull) == *"Already up to date"* ]]
then
echo "Nothing to update"
exit 0
fi
. ./venv/bin/activate
pip install -r requirements.txt
npm ci
./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"
./manage.py collectstatic --noinput
./manage.py migrate
sudo systemctl restart gunicorn.service
sudo systemctl reload nginx.service
deactivate
if [[ $param != '' ]]
then
commit=$(git rev-parse --short HEAD)
token='X-Rollbar-Access-Token: '$param
curl --request POST --url https://api.rollbar.com/api/1/deploy --header $token --header 'accept: application/json' --header 'content-type: application/json' --data '{"environment": "production", "revision": $commit, "status": "succeeded"}'
fi
echo "Rebuild project completed"

