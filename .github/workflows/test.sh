#!/bin/bash

cd /home/ubuntu/django-app/climatenet
# Update the repository
git checkout staging
git stash
git pull origin staging

# Activate virtual environment and install/update dependencies
source venv/bin/activate
pip install -r requirements.txt

# Collect static files (if needed)
python manage.py collectstatic --noinput

# Restart Gunicorn
sudo systemctl daemon-reload
sudo systemctl restart gunicorn

# Restart Nginx
sudo systemctl restart nginx
