#!/usr/bin/env python
# coding: utf-8

import os, json, random, re, base64, io, uuid, time, socket, calendar
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

# Get environment variables
load_dotenv()


class UInterface:
	def __init__(self):
		print('Initializing Home')
		self.init_time = datetime.now()
		self.product_name = 'Portfolio | Nick Earl'
		self.styles = {
			'color_sequence': ["#FA005A", "#86D7DC", "#FFC500", "#520044", "#9B004E","#FA005A", "#86D7DC", "#FFC500", "#520044", "#9B004E"],
		}
		links = {
			'dashboard': {
				'path': '/portfolio/dashboard',
				'name': 'Dashboards & Visualization',
				'image': 'assets/images/retro_chart.png',
				'content': dbc.Stack([
					html.H5('An interactive demo dashboard for a fictional new streaming service'),
					dbc.Stack([
						html.Img(src='assets/images/dashboard_screenshot.png',style={'max-height':'300px','max-width':'500px'}),
						dcc.Markdown("""
							- BI & data visualization best practices
							- Stakeholder guidance
							- Procedural dataset generation via python
						""",style={'text-align':'left'}),
					],direction='horizontal',gap=3),
				],gap=1, className='d-flex align-items-center justify-content-center p-2',style={'color':'black','min-width':'275px'}),
			},
			'ai': {
				'path': '/portfolio/ai',
				'name': 'Fun with Gen AI',
				'image': 'assets/images/robot_and_human.png',
				'content': dbc.Stack([
					html.H5('Practical integration of gen AI tools into data & visualization workflows'),
					dbc.Stack([
						html.Img(src='assets/images/ai_screenshot.png',style={'max-height':'300px','max-width':'400px'}),
						dcc.Markdown("""
							- Using python to integrate gen AI APIs with data visualization tools
							- Using ChatGPT to generate design elements, color themes & branding
							- Prompt engineering
							- Image generation
						""",style={'text-align':'left'}),
					],direction='horizontal',gap=3),
				],gap=1, className='d-flex align-items-center justify-content-center p-2',style={'color':'black','min-width':'275px'}),
			},
		}

		toc_links = []
		for k,v in links.items():
			p = dbc.Stack([
				html.H3(v['name']),
				dbc.Button([
					dbc.Stack([
						dbc.Stack([
							html.Img(src=v['image'],className='directory-image'),
							dcc.Link(f'{v['name']}', href=v['path'],className='directory-link'),
						],gap=1, className='bg-dark d-flex align-items-center justify-content-center p-2',style={'width':'400px'}),
						v['content'],
					],direction='horizontal',gap=3,className='d-flex align-items-start justify-content-center'),
				],href=v['path'],className='bg-light directory-row d-flex align-items-center justify-content-start',style={'background':'none'})
			])
			toc_links.append(p)
		intro_text = """
		### Hi, I'm Nick Earl

		#### I build data teams & platforms capable of delivering powerful insights & data applications (like the one powering this portfolio)

		#### I also guide executives, product owners, marketers and other stakeholders towards fully understanding every insight from their data
		"""
		# analysis_text = """
		# #### Press coverage of analyses my teams and I have performed

		# """
		alist_buttons = []
		carousel_images = []
		articles = {
			'Variety': {
				'url': 'https://variety.com/lists/video-game-tv-series-ideas-study/',
				'text': 'What Video Games Should Streamers Adapt?',
				'images': ['variety_1.png','variety_2.png'],
			},
			'TheWrap': {
				'url': 'https://www.thewrap.com/fandom-avatar-top-gun-oscars-fan-vote/',
				'text': 'What if Fans Voted for the Oscars?',
				'images': ['thewrap_1.png'],
			},
			'LA Times': {
				'url': 'https://www.latimes.com/entertainment-arts/tv/newsletter/2024-08-09/the-boys-bridgerton-house-of-the-dragon-the-bear-weekly-binge-screen-gab',
				'text': "Weekly Episode Drops are Better Than Binge.  And There's Data to Back it Up.",
				'images': ['latimes_1.png','latimes_2.png'],
			},
			'Ad Week': {
				'url': 'https://www.adweek.com/convergent-tv/streamer-releases-weekly-binge/',
				'text': "Binge or Weekly? Here's the Best Way for Streamers to Release Shows",
				'images': ['adweek_1.png'],
			},

		}
		a_count = 0
		i_count = 0
		for k,v in articles.items():
			o = dbc.NavItem([
				dbc.Button([
					dbc.Stack([
						html.Span([
							html.H5(k),
						],className='d-flex align-items-start justify-content-center ps-2 h-100',style={'min-width':'100px'}),
						html.Span([
							html.A(v['text'],href=v['url'],target='_blank',className='carousel-link'),
						],className='bg-primary w-100 p-3'),
					],direction='horizontal',gap=1,className='d-flex justify-content-start align-items-center'),
				],className='bg-dark a-list-button',id=f'a-list-button-{a_count}',style={'background':'none'})
			])
			alist_buttons.append(o)
			alist_buttons.append(html.Br())
			for image in v['images']:
				image_val = {'key': f'{i_count + 1}', 'src': f'assets/images/{image}', 'img_className': 'carousel-image',}
				carousel_images.append(image_val)
				i_count = i_count + 1
			a_count = a_count + 1

		self.layout = {
			# 'table_of_contents': dbc.Card([
			# 	dbc.Stack(toc_links)
			# ],color='light',className='home-panel d-flex align-items-center justify-content-center'),
			'intro': dbc.Card([
				dbc.Stack([
					dcc.Markdown(intro_text,className='intro-text'),
					dbc.Stack([
						html.Img(src='assets/images/spock_sunglasses.png',className='intro-image'),
						html.A([html.I(className='bi bi-linkedin'),' linkedin.com/in/nickearl'],href='https://www.linkedin.com/in/nickearl/',target='_blank',className='intro-link'),
						html.A([html.I(className='bi bi-github'),' github.com/nickearl'],href='https://github.com/nickearl/',target='_blank',className='intro-link'),
						html.A([html.I(className='bi bi-at'),' nickearl.net'],href='https://www.nickearl.net',target='_blank',className='intro-link'),
					], className='d-flex flex-column justify-content-start align-items-center'),
				],direction='horizontal', gap=3)
			],color='light',className='home-panel d-flex align-items-center justify-content-center'),
			'dashboard': toc_links[0],
			'ai': toc_links[1],
			'analyses': dbc.Stack([
				html.H3('Analyses',className='home-panel-feature'),
				dbc.Card([
					#dcc.Markdown(analysis_text,className='analysis-text'),
					html.Span('Press coverage of analyses my teams and I have performed',className='home-panel-feature',style={'font-size':'1.1rem'}),
					dbc.Stack([
						dbc.Stack([
							dbc.Nav(
								alist_buttons,
								vertical=True,pills=True
							),
							dbc.Carousel(
								items=carousel_images,
								controls=True,
								indicators=True,
								ride='carousel',
								variant='dark',
								interval=5000,
								id='article-carousel',

							),
						],direction='horizontal',gap=3),
					]),
				],color='light',className='home-panel d-flex align-items-start justify-content-center fluid-container'),
			],className='d-flex align-items-start justify-content-center'),
		}


	def get_random_song(self):
		pathname = 'assets/data/taylor_swift_songs.csv'
		with open(pathname) as g:
			df = pd.read_csv(g, sep=",", header=0)
		r = random.randrange(len(df.index))
		q = df.iloc[r]
		return q

	
def create_app_layout(ui):

	layout = dbc.Container([
		dbc.Row([
			dbc.Col([
				dbc.Stack([
					ui.layout['intro'],
					ui.layout['dashboard'],
					ui.layout['ai'],
					ui.layout['analyses'],
				],gap=5,className='d-flex flex-column align-items-center justify-content-center'),
			]),
		]),
		# html.Br(),
		# html.Div([
		# 	html.H3('Analyses'),
		# ],className='d-flex align-items-center justify-content-start',style={'width':'1000px'}),
		# dbc.Row([
		# 	dbc.Col([
		# 		ui.layout['analyses'],
		# 	],className='d-flex align-items-center justify-content-center'),
		# ]),
		# html.Br(),
		# dbc.Row([
		# 	dbc.Col([
		# 		ui.layout['footer'],
		# 	],className='d-flex align-items-center justify-content-center'),
		# ]),
	],fluid=True,className='d-flex flex-column align-items-center justify-content-center')

	return layout





