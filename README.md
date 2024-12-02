 # Django-app backend
Clone the repository
```bash
git clone repository_url
```

## Prepare the directories


1.After cloning the repository go to "climatenet" directory:

```bash

cd climatenet

```

2. Create virtual environment:
```bash

python3 -m venv venv

```


3. Activate virtual environment
```bash

source venv/bin/activate

```


4. Install all required libraries:
```bash

pip3 install -r requirements.txt

```
5. Create `.env` file in the same folder as requirements.txt using an [example](https://github.com/ClimateNetTumoLabs/django-app/blob/staging/climatenet/.env_template)
6. To run web server code with frontend static folder you need to create static folder. 

7. Go to frontend folder(you need to clone from [Frontend](https://github.com/ClimateNetTumoLabs/frontend)) and run following commands

If everything is okay run

```bash
sudo apt install npm
```
For installing dependencies run
```bash
npm install
```
For preparing your application for production run
```bash
npm run build  
```
Structure of the folders need to be like this 
```
.
├── django-app
│   ├── README.md
│   └── climatenet
└── frontend
    ├── README.md
    ├── build
    ├── node_modules
    ├── package-lock.json
    ├── package.json
    ├── public
    └── src
```
Go back to `django-app/climatenet` and run 
```bash
python3 manage.py collectstatic
```
## If you add, change or modify models, run

``` bash
python3 manage.py makemigrations --empty backend
```
`--empty backend` helps not to add any values from terminal
``` bash
python3 manage.py migrate
```
## Run the application
Check in settings.py file, if DEBUG=False run

```bash
python3 manage.py runserver --insecure
```
else run 
```bash
python3 manage.py runserver
```
After all steps open browser go to http://127.0.0.1:8000/ to see django app running.


