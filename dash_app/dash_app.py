import os, json, random, re, base64, io, uuid, time, socket
from dotenv import load_dotenv
import dash
import dash_bootstrap_components as dbc
import dash_auth
from dash import Dash, html, dcc, Input, Output, State, ALL, MATCH, Patch, callback
from dash.exceptions import PreventUpdate
import dash_ag_grid as dag
import plotly.io as pio
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import date, datetime
from openai import OpenAI
from flask.helpers import get_root_path

# Get environment variables
load_dotenv()

PRODUCT_NAME = os.environ['APP_NAME']
APP_NAME = os.environ['APP_NAME']

LOGO_PATHS = {
            'dark': 'assets/images/retro_chart.png',
            'light': 'assets/images/retro_chart.png',
        }


def create_dash_app(server, url_base_pathname, assets_folder, meta_tags, use_pages=False, pages_folder=''):

    print('root path: {}'.format(get_root_path('dash_app')))
    pd.options.mode.copy_on_write = True
    pd.options.display.float_format = '{:.2f}'.format
    pd.options.display.precision = 4
    pio.templates.default = "plotly_white"

    #Basic auth

    # VALID_USERNAME_PASSWORD_PAIRS = {
    #     os.environ['USER1']: os.environ['PASS1'],
    # }


    app = dash.Dash(
        server=server,
        assets_folder=assets_folder,
        meta_tags=meta_tags,
        routes_pathname_prefix=url_base_pathname,
        suppress_callback_exceptions=True,
        prevent_initial_callbacks='initial_duplicate',
        update_title=None,
        use_pages=use_pages,
        pages_folder=pages_folder,
        external_stylesheets=[dbc.themes.FLATLY, dbc.icons.BOOTSTRAP,dbc.icons.FONT_AWESOME]
    )
    print('host ip: ' + str(socket.gethostbyname(socket.gethostname())))
    print('environment: ' + str(os.environ['DEPLOY_ENV']))
    # if os.environ['DEPLOY_ENV'] == 'prod':
    #     auth = dash_auth.BasicAuth(
    #         app,
    #         VALID_USERNAME_PASSWORD_PAIRS
    #     )

    global_ui = {
        'sidebar' : dbc.Offcanvas(
            dbc.Container([
                            dbc.Row([
                                dbc.Col(html.Img(src=LOGO_PATHS['dark'], height='30px')),
                            ], align='center'),
                            dbc.Row([
                                dbc.Col(dbc.NavbarBrand(PRODUCT_NAME, className='ms-2'))
                            ]),
                            html.Hr(className='dash-bootstrap', style={'borderWidth': '1vh', 'width': '100%', 'backgroundColor': 'primary', 'opacity':'1'}),
                            dbc.Nav([
                                dbc.NavLink(PRODUCT_NAME, href=f'{url_base_pathname}', active='exact',style={'color': '#280033','border-radius':'10px'}),
                                dbc.NavLink('Dashboard', href=f'{url_base_pathname}/dashboard/', active='exact',style={'color': '#280033','border-radius':'10px'}),
                                dbc.NavLink('Gen AI', href=f'{url_base_pathname}/ai', active='exact',style={'color': '#280033','border-radius':'10px'}),
                            ],
                            vertical=True,
                            pills=True
                            ),                  
                    ], fluid=True,style={'background-color':'info'}),
            id='offcanvas-sidebar',
            #title=self.product_name,
            is_open=False,
        ),
        'navbar': dbc.Navbar([
                dbc.Container([
                    dbc.Row([
                        dbc.Col([
                            dbc.Stack([
                                dbc.Button([
                                   html.I(className="bi bi-list", style={'font-size': '2em', 'font-weight': 'bold'}),
                                ],id='nav-logo',color='primary'),
                                dbc.NavbarBrand('Portfolio | Nick Earl', class_name='mx-auto', style={'color':'white','font-size': '2em', 'font-weight': 'bold'}),
                                html.Img(src=LOGO_PATHS['light'],style={'height':'50px'}),
                            ],direction='horizontal',gap=2),
                        ],align='center',width={'size':12,'offset':0}),
                    ],class_name='container-fluid',align='start',justify='around'),
                ]),
            ],class_name='navbar container-fluid',color='secondary'),
        'footer': dbc.Stack([
            html.Span(f'Nick Earl © {datetime.now().year}', className='footer-text'),
            html.A([html.I(className='bi bi-linkedin'),' linkedin.com/in/nickearl'],href='https://www.linkedin.com/in/nickearl/',target='_blank',className='footer-text'),
            html.A([html.I(className='bi bi-github'),' github.com/nickearl'],href='https://github.com/nickearl/',target='_blank',className='footer-text'),
            html.A([html.I(className='bi bi-at'),' nickearl.net'],href='https://www.nickearl.net',target='_blank',className='footer-text'),
        ],direction='horizontal',gap=3, className='footer d-flex justify-content-center align-items-center'),
        }


    app.layout = dbc.Container([
        dbc.Row([
            dbc.Col([
                global_ui['sidebar'],
                global_ui['navbar'],
                html.Br(),
            ]),
        ]),
        dash.page_container,
        html.Br(),
        dbc.Row([
            dbc.Col([
                global_ui['footer'],
            ],className='d-flex align-items-center justify-content-center'),
        ]),
    ],fluid=True)

    return app

if __name__ == '__main__':
    app.run(debug=True,jupyter_mode='tab')







