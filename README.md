# ILLiad article handler

## Brief overview

A Django application that helps library users reach an ILLiad article-request form from an OpenURL link.

## More info

The application reads Shibboleth identity information, checks the user's ILLiad account through an API, and attempts registration for new users. It then redirects the browser to ILLiad with the original query parameters. No local database is configured.

[Overview](#brief-overview) · [More info](#more-info) · [Local installation](#local-installation) · [Usage](#usage) · [Primary dependencies](#primary-dependencies)

## Local installation

You need Git and a Python installation compatible with the versions in [config/requirements.pip](config/requirements.pip). From the directory where you want to keep the checkout:

```bash
mkdir illiad_article_handler_stuff
cd illiad_article_handler_stuff
git clone https://github.com/birkin/illiad_article_handler_project.git
cd illiad_article_handler_project
python3 -m venv ../env
source ../env/bin/activate
python -m pip install -r config/requirements.pip
```

Create `../.env`, outside the checkout, with shell variable assignments for every environment variable read by [config/settings.py](config/settings.py). These include Django settings, logging and email settings, development identity data, and ILLiad and page-header service configuration. Use development service values and a writable log location. Settings ending in `_JSON` must contain valid JSON.

Load these settings before running management commands:

```bash
set -a
source ../.env
set +a
export ILL_ART_HNDLR__ENV_SETTINGS_PATH="$(cd .. && pwd)/.env"
```

The last variable tells the application where to read the same settings file when it starts.

## Usage

From the checkout, with the virtual environment active and settings loaded:

```bash
python manage.py runserver 127.0.0.1:8000
```

Open `http://127.0.0.1:8000/info/` to see the placeholder information response. Send article OpenURL parameters to `/openurl/` to run the request workflow. Local requests use `ILL_ART_HNDLR__DEV_SHIB_DCT_JSON` for identity information; the workflow contacts the configured ILLiad API and may create an account before redirecting the browser. The message page fetches and caches its header from the configured header service.

## Primary dependencies

Declared in [config/requirements.pip](config/requirements.pip) and confirmed in the source:

- **Django**: request routing, views, templates, and caching; configured in [config/settings.py](config/settings.py).
- **requests**: calls the ILLiad API and fetches the message-page header in [the application helpers](illiad_article_handler_app/lib/).
- **shellvars-py**: reads the environment settings file in [config/wsgi.py](config/wsgi.py).

There is no lockfile documenting supporting packages. The commented-out `mysqlclient` and `PyMySQL` entries are inactive legacy declarations; review them if database support is introduced.
