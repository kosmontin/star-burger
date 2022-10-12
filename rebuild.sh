#!/bin/bash
set -e
echo "Trying to rebuild star-burger project..."
cd /opt/projects/star-burger/
commit=$(git rev-parse --short HEAD)
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
if [[ $1 != '' ]]
then
curl --request POST --url https://api.rollbar.com/api/1/deploy --header 'X-Rollbar-Access-Token: '$1 --header 'accept: application/json' --header 'content-type: application/json'  --data '{"environment": "production", "revision": "'$commit'", "rollbar_username": "kosta"}'
fi
echo "Rebuild project completed"

