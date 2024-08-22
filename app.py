import os, uuid
import flask
import dash
from dash import Dash, DiskcacheManager, CeleryManager, Input, Output, html, callback
from dotenv import load_dotenv
from flask.helpers import get_root_path
from flask_server import create_flask_server
from home import UInterface as home_ui, create_app_layout as home_layout_func
from dashboard import UInterface as dashboard_ui, create_app_layout as dashboard_layout_func
from ai import UInterface as ai_ui, create_app_layout as ai_layout_func

load_dotenv()

if os.environ['DEPLOY_ENV'] == 'dev':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


PORT = os.environ['PORT']
APP_NAME = os.environ['APP_NAME']
cache_uuid = uuid.uuid4().hex

if 'REDISCLOUD_URL' in os.environ:
    print('Using Redis for background callbacks')
    from celery import Celery
    #celery_app = Celery(__name__, broker=os.environ['REDIS_URL'], backend=os.environ['REDIS_URL'])
    celery_app = Celery(__name__, broker=os.environ['REDISCLOUD_URL'], backend=os.environ['REDISCLOUD_URL'])
    BACKGROUND_CALLBACK_MANAGER = CeleryManager(celery_app, cache_by=[lambda: cache_uuid], expire=60)

else:
    print('Using DiskCache for background callbacks')
    import diskcache
    cache = diskcache.Cache("./cache",timeout=1200)
    BACKGROUND_CALLBACK_MANAGER = DiskcacheManager(cache)

def create_server():
    server = create_flask_server(port=PORT)
    return server

def create_app(server):

    from dash_app import create_dash_app
    from callbacks import register_callbacks as register_callbacks
    print(f'using APP_NAME: {APP_NAME}')
    print(f'{APP_NAME.replace(' ','-').lower()}')
    register_dash_app(server, 'dash_app', APP_NAME, APP_NAME.replace(' ','-').lower(), create_dash_app, register_callbacks)

    return server


def register_dash_app(app, app_dir, title, base_pathname, create_dash_fun, register_callbacks_fun):
    meta_viewport = {"name": "viewport", "content": "width=device-width, initial-scale=1, shrink-to-fit=no"}

    with app.app_context():
        new_dash_app = create_dash_fun(
            server=app,
            url_base_pathname=f'/{base_pathname}/',
            #assets_folder=get_root_path(__name__) + f'/{app_dir}/assets/',
            assets_folder=f'{app_dir}/assets/',
            meta_tags=[meta_viewport],
            use_pages=True,
            pages_folder=get_root_path(__name__) + f'/{app_dir}/pages/',
        )
        new_dash_app.title = title
        #dash.register_page('Home', path='/', layout='You are home')
        dash.register_page('Home',title='Portfolio | Nick Earl',path='/', layout=home_layout_func(home_ui()))
        dash.register_page('Dashboard',title='Dashboard | Nick Earl',path='/dashboard', layout=dashboard_layout_func(dashboard_ui()))
        dash.register_page('AI',title='Fun with GenAI | Nick Earl',path='/ai', layout=ai_layout_func(ai_ui()))
        #new_dash_app.layout = layout
        register_callbacks_fun(new_dash_app)

print('app.py successfuly initialized')
server = create_server()
print('server successfuly initialized')
server = create_app(server)
print('dash successfuly initialized')
