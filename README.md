# _Quantified Self Tracker App_
The project is aimed at creating an app that allows multiple users to create trackers to track their routine activities, keeps logs of their activities, and lets them see their progress via trendlines.

# Local Setup
- Clone the project
- Run `setup.sh`

# Local Development Run
- `local_run.sh` It will start the flask app in `development`. Suited for local development

# Replit Run
- Go to shell and run
    `pip install --upgrade poetry`
- Click on `main.py` and click button Run
- Project is at https://mad1trackon.shagundwivedi.repl.co/

# Folder Structure

- `trackerdb`  is the sqlite database.
- `madapp` is where our application code is.
- `setup.sh` set up the virtualenv inside a local `.env` folder. Uses `pyproject.toml` and `poetry` to setup the project.
- `local_run.sh`  Used to run the flask application in development mode.
- `static` - default `static` files folder. It serves at '/static' path, and has images required .
- `templates` - Default flask templates folder.


```
├── local_run.sh
├── local_setup.sh
├── madapp
│   ├── api.py
│   ├── controller.py
│   ├── database.py
│   ├── models.py
│   ├── plotforapp.py
│   └── __pycache__
│       ├── controller.cpython-310.pyc
│       ├── database.cpython-310.pyc
│       ├── models.cpython-310.pyc
│       └── plotforapp.cpython-310.pyc
├── main.py
├── readme.md
├── app_apis.yaml
├── static
│   ├── login.jpg
│   ├── minimalism1.gif
│   └── plot.jpg
├── templates
│   ├── addlog.html
│   ├── addtracker.html
│   ├── dash.html
│   ├── homepage.html
│   ├── login.html
│   ├── logs.html
│   ├── signup.html
│   ├── updatelog.html
│   └── updatetracker.html
└── trackerdb.sqlite3
```
