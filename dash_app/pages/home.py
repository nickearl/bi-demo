import os
from dotenv import load_dotenv
import dash_bootstrap_components as dbc
from dash import html, dcc
import plotly.io as pio
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import date, datetime
from dash_app import VirtualInterview
from conf import global_config

load_dotenv()

class UInterface:
	def __init__(self):
		print('Initializing Home')
		self.init_time = datetime.now()
		self.conf = {
			'panel_width': '80vw',
			'panels': {},
			'articles': {
				'Variety': {
					'logo': 'variety_logo.png',
					'url': 'https://variety.com/lists/video-game-tv-series-ideas-study/',
					'text': 'What Video Games Should Streamers Adapt?',
					'images': ['variety_1.png','variety_2.png'],
				},
				'Ad Week': {
					'logo': 'adweek_logo.png',
					'url': 'https://www.adweek.com/convergent-tv/streamer-releases-weekly-binge/',
					'text': "Binge or Weekly? Here's the Best Way for Streamers to Release Shows",
					'images': ['adweek_1.png'],
				},
				'LA Times': {
					'logo': 'latimes_logo.png',
					'url': 'https://www.latimes.com/entertainment-arts/tv/newsletter/2024-08-09/the-boys-bridgerton-house-of-the-dragon-the-bear-weekly-binge-screen-gab',
					'text': "Weekly Episode Drops are Better Than Binge.  And There's Data to Back it Up.",
					'images': ['latimes_1.png','latimes_2.png'],
				},
				'TheWrap': {
					'logo': 'thewrap_logo.png',
					'url': 'https://www.thewrap.com/fandom-avatar-top-gun-oscars-fan-vote/',
					'text': 'What if Fans Voted for the Oscars?',
					'images': ['thewrap_1.png'],
				},
			}
		}
		self.conf['panels']['virtual_interview'] = {
			'display_name': 'Demo: Virtual Interview',
			'summary_header': "An AI agent trained to answer questions about my background, experience, and interests.",
			'summary_text': """
				Hi, I'm Nick's AI clone!  Nick created me using LLM/RAG models to answer your questions about his background, experience, and interests.
				I have been trained on a structured dataset of details about Nick, and I can reference that information to have a natural conversation with you.

				Try asking me something like:
				
				- "Tell me a little about yourself."

				- "Describe your experience with ETL pipelines."

				- "Talk about a time you overcame a challenge, but pretend to be a pirate while doing it."
			""",
			'image': 'assets/images/ai_interview.png',
			'enabled': True,
			# 'link': 'chatbot',
			}
		for k,v in global_config['pages'].items():
			if v['enabled']:
				self.conf['panels'][k] = v
		analyses_content = self.create_article_content()
		self.conf['panels']['analyses'] = {
			'display_name': 'Analyses',
			'summary_header': 'Press coverage of analyses my teams and I have performed',
			'summary_text': None,
			'image': None,
			'enabled': True,
			'content_left': analyses_content[0],
			'content_right': analyses_content[1],
			# 'link': 'analyses',
			}
		vi = VirtualInterview()
		self.layout = {
			'intro': dbc.Card([
				dbc.Stack([
					dcc.Markdown(global_config['intro_text'],className='intro-text px-2'),
					dbc.Stack([
						html.Img(src='assets/images/spock_sunglasses.png',className='intro-image'),
						html.A([html.I(className='bi bi-linkedin'),' linkedin.com/in/nickearl'],href='https://www.linkedin.com/in/nickearl/',target='_blank',className='intro-link'),
						html.A([html.I(className='bi bi-github'),' github.com/nickearl'],href='https://github.com/nickearl/',target='_blank',className='intro-link'),
						html.A([html.I(className='bi bi-at'),' nickearl.net'],href='https://www.nickearl.net',target='_blank',className='intro-link'),
					],gap=3, className='align-items-center justify-content-start'),
				],direction='horizontal', gap=3)
			],color='light',className='shadow-lg align-items-center justify-content-center',style={'flex':'1','border-radius':'1rem','border-width':'3px','max-width': self.conf['panel_width'],'padding':'1rem'}),
			'virtual_interview': dbc.Card([
				dbc.CardHeader([
					dbc.Stack([
						html.Span(self.conf['panels']['virtual_interview']['summary_header'],style={'font-weight':'bold','font-size':'1.2rem'}),
					],gap=3,className='align-items-center justify-content-start'),
				]),
				dbc.CardBody([
					dbc.Stack([
						dcc.Loading([
							dbc.Stack([
								vi.render_chat_response(response_text=self.conf['panels']['virtual_interview']['summary_text'],role='assistant'),
							],gap=3,className='align-items-center justify-content-center',style={'flex':'1','border-radius':'1rem','height':'65vh','overlow':'scroll'},id='vi-chat-history'),
						],parent_style={'flex':'1','border-radius':'1rem'},overlay_style={'visibility':'visible', 'filter': 'blur(2px)'}),
					],gap=3,className='align-items-center justify-content-center',style={'flex':'2','border-radius':'1rem'}),
				]),
				dbc.CardFooter([
					dbc.Stack([
						dbc.Textarea(id='vi-user-input',placeholder='ie, "Why should I hire you?"',style={'width':'100%'}),
						dbc.Button([html.I(className='bi bi-arrow-up-circle-fill')],id='vi-submit-button',n_clicks=0,style={'width':'5vw','height':'3vw'}),
					],direction='horizontal',gap=3,className='align-items-center justify-content-start'),
				]),
			],style={'flex':'2','align-self':'stretch','border-top-right-radius':'1rem','border-bottom-right-radius':'1rem'}),
		}
		self.conf['panels']['virtual_interview']['content_right'] = self.layout['virtual_interview']
		toc_links = []
		for k,v in self.conf['panels'].items():
			if v['enabled'] and k != 'home':
				p = self.create_home_content_panel(v)
				toc_links.append(p)
		self.layout['toc'] = dbc.Stack(toc_links,gap=5,className='align-items-center justify-content-center')

	def create_article_content(self):
		alist_buttons = []
		carousel_images = []
		a_count = 0
		i_count = 0
		for k,v in self.conf['articles'].items():
			o = dbc.NavItem([
				dbc.Button([
					dbc.Stack([
						dbc.Stack([
							html.Img(src=f'assets/images/{v['logo']}', className='a-list-logo')
						],className='d-flex align-items-start justify-content-center w-100 ps-2',style={'min-width':'100px'}),
						dbc.Stack([
							html.A(v['text'],href=v['url'],target='_blank',className='carousel-link'),
						],className='bg-light d-flex align-items-center justify-content-center w-100',style={'border-top-right-radius':'.5rem','border-bottom-right-radius':'.5rem'}),
					],direction='horizontal',gap=1,className='d-flex justify-content-start align-items-center',style={'min-height':'6rem'}),
				],className='bg-dark a-list-button',id=f'a-list-button-{a_count}',style={'background':'none'})
			])
			alist_buttons.append(o)
			alist_buttons.append(html.Br())
			for image in v['images']:
				image_val = {
					'key': f'{i_count + 1}',
					'src': f'assets/images/{image}',
					'img_className': 'carousel-image',
					'img_style': {'border-radius':'1rem','height':'100%'},
				}
				carousel_images.append(image_val)
				i_count = i_count + 1
			a_count = a_count + 1
			content_left = dbc.Stack([
				dbc.Nav(
					alist_buttons,
					vertical=True,pills=True
				)
			],gap=3,className='bg-light align-items-center justify-content-center',style={'flex':'1','border-radius':'1rem','width':'100%','padding':'1rem'})
			content_right = dbc.Stack([
				dbc.Carousel(
					items=carousel_images,
					controls=True,
					indicators=True,
					ride='carousel',
					variant='dark',
					interval=5000,
					id='article-carousel',
					style={'border-radius':'1rem'}
				)
			],gap=3,className='align-items-center justify-content-center',style={'flex':'2','border-radius':'1rem','width':'100%'})
		return content_left, content_right

	def create_home_content_panel(self,config:dict)->dbc.Card:
		"""
			config:
			{
				'prefix':'dash',
				'image': 'assets/images/dashboard_screenshot.png',
				'display_name': 'Interactive Data Visualization',
				'summary_header': 'An interactive demo dashboard for a fictional new streaming service',
				'summary_text': ""
				'enabled': True,
				'content_left': [] # Optional list of dbc components to replace default left side content
				'content_right': [] # Optional list of dbc components to replace default right side content
			}
		"""
		
		content_left = config['content_left'] if 'content_left' in config.keys() and config['content_left'] != None else dbc.Stack([
			html.Img(src=config['image'],style={'width':'80%','border-radius':'1rem'}),
			dcc.Link(f'{config['display_name']}', href=config['full_path'] if 'full_path' in config.keys() and config['full_path'] else None, className='directory-link',style={'border-bottom-left-radius':'1rem'}),
		],gap=3,className='bg-dark align-items-center justify-content-center',style={'flex':'1','border-radius':'1rem'})
		content_right = config['content_right'] if 'content_right' in config.keys() else dbc.Stack([
			html.Span(config['summary_header'],style={'font-weight':'bold','font-size':'1.1rem'}) if config['summary_header'] else None,
			dcc.Markdown(config['summary_text'],style={'text-align':'left','font-size':'1rem'}) if config['summary_text'] else None,
		],gap=3,className='align-items-center justify-content-center',style={'flex':'2','border-radius':'1rem'})

		card = dbc.Stack([
			dbc.Stack([
				html.Span(config['display_name'],style={'font-weight':'bold','font-size':'1.6rem'}),
			],direction='horizontal',gap=3,className='align-items-center justify-content-start'),
			dbc.Button([

				dbc.Stack([
					content_left,
					content_right
				],direction='horizontal',gap=3,className='align-items-start justify-content-around'),

			],href=config['full_path'] if 'full_path' in config.keys() and config['full_path'] else None,className='shadow-lg bg-light',style={'color':'black','flex':'1','border-radius':'1rem','border-width':'3px','width':'100%'}),
		],gap=3,className='align-items-center justify-content-center',style={'flex':'1','max-width':self.conf['panel_width']})

		return card

def create_app_layout(ui):

	layout = dbc.Container([
		dbc.Row([
			dbc.Col([
				ui.layout['intro'],
				ui.layout['toc'],
			]),
		]),
	],fluid=True,className='d-flex flex-column align-items-center justify-content-center')

	return layout





