#!/bin/bash
set -e
echo "Trying to rebuild star-burger project..."
cd /opt/projects/star-burger/
if [[ $(git status) != *"nothing to commit, working tree clean"* ]]
then
echo "Uncommited changes are present. Use <git status> in bash to show more details"
exit 1
fi
git pull
. ./venv/bin/activate
pip install -r requirements.txt
npm ci
./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"
./manage.py collectstatic --noinput
./manage.py migrate
sudo systemctl restart gunicorn.service
sudo systemctl reload nginx.service
echo "rebuild project completed"
deactivate

