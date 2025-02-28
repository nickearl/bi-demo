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
from openai import OpenAI
from conf import global_config

# Get environment variables
load_dotenv()
PAGE = 'ai'
REDISCLOUD_URL = os.environ['REDISCLOUD_URL']
pd.set_option('future.no_silent_downcasting', True)

class UInterface:
	def __init__(self):
		self.conf = global_config['pages'][PAGE]
		print(f'Initializing {self.conf['display_name']} UI')
		self.init_time = datetime.now()
		self.styles = {
			'color_sequence': ['#FD486D', '#9F4A86', '#F5D107', '#86D7DC', '#333D79', '#E5732D', '#4CAF8E', '#722B5C', '#FFC10A', '#005580'],
			'portrait_colors': ['#86D7DC', '#9B004E','#FA005A','#FFC500','#520044'],
			'comp_colors':['#54898d','#9F4A86'],
		}
		self.data = {
			'traffic_daily': pd.read_csv('dash_app/assets/data/traffic_daily.csv'),
		}
		self.layout = {
			'header': dbc.Stack([
				dbc.Stack([
					# html.Img(src='assets/images/robot_and_human.png',style={'width':'150px','height':'150px'}),
					html.Img(src=self.conf['image'],style={'width':'150px','height':'150px'}),
					html.H3(self.conf['display_name']),
				],direction='horizontal',gap=3,className='justify-content-end',style={'width':'50%','max-width':'500px'}),
				dbc.Stack([
					html.Span(self.conf['summary_header'],style={'font-weight':'bold'}),
					html.Span("For these examples I'm using the OpenAI python client to programatically prompt ChatGPT and parse the responses. "),
					html.Span('>More Info<',id='ai-more-info',style={'font-weight':'bold','color':self.styles['color_sequence'][1]}),
					dbc.Popover(
						[
							dbc.PopoverHeader(dcc.Markdown('**Step by Step**')),
							dbc.PopoverBody([
								dbc.Stack([
									dcc.Markdown("""
										1. Define a template prompt with system instructions and base knowledge that returns some useful information.  The prompt should be tested to ensure it returns a predictably formatted reponse.
										2. Get user input values from the UI or external data source (Retrieval Augmented Generation aka RAG), inject them into the prompt template.
										3. Send the payload to the LLM
										4. Parse response from AI, for example a list of records to insert into a dataframe, or a list of color hex codes.
									"""),
									html.Img(src='assets/images/ai_screenshot.png', style={'max-width':'65vw'}),
									html.Span([
										'You can ',
										html.A('view the source code in my Github repo',href='https://github.com/nickearl/bi-demo',target='_blank',style={'font-weight':'bold'}),
										'.',
									]),
								],gap=3,className='d-flex align-items-center justify-content-center'),
							]),
						],
						placement='bottom',
						target='ai-more-info',
						trigger='hover',
						style={'min-width':'50vw'},
					),

				],gap=1,className='justify-content-start',style={'width':'50%','max-width':'500px'}),
				
			],direction='horizontal',gap=3,className='header d-flex justify-content-center align-items-center'),
			'loading_card': dbc.Card([
				dbc.CardHeader([
					dbc.Progress(id='loading-card-bar',value=0, striped=True, animated=True, color='#86D7DC',style={'background-color':'#3A434B'}),
					html.H3(['Asking ChatGPT...'],id='loading-card-text',style={'color':'white'}),
					dbc.ListGroup([],id='loading-card-list'),
				]),
				dbc.CardBody([
					dbc.Stack([],id='loading-card-quote-container',className='d-flex justify-content-center align-items-center')
				]),
			],className='loading-card',id='loading-card',style={'display':'none'}),
		}
		from dashboard import UInterface as dashboard_ui
		self.layout['example_chart'] = dbc.Container([
			dbc.Card([
				dbc.CardHeader([
					html.H4('Branding & Theming')
				]),
				dbc.CardBody([
					dbc.Container([
						dbc.Row([
							dbc.Col([
								dbc.Stack([
									dcc.Markdown("""
										This simple example uses AI to generate color themes to apply to a data visualization based on a brief description typed out by the user.  This example simply changes some colors,
										but the implementation can be easily scaled up further to generate more complex themes and UX customization via HTML/CSS styling and dynamic page layouts.

										**Use Case**: Creation of sales collateral, exportable PNG images of visualizations for use in presentation slides or publication.
									"""),

									dbc.Container([
										dashboard_ui().render_summary_charts(w=750,h=400,chart_only=True),
										self.layout['loading_card']
									],id='ai-chart-container',fluid=True),

								],gap=3),
							],width={'size':8}),
							dbc.Col([
								dbc.Card([
									dbc.CardBody([
										dcc.Markdown("""
											#### **Try it yourself!**

											Here are some example prompts with distinctive, recognizable colors that usually work well:
											
											>
											> Create a color theme that represents the corporate branding colors of the American coffee chain Starbucks.
											>


											>
											> Create a color theme using complementary pastel colors to represent springtime.
											>
											

											>
											> Create a color theme representing Pride and the LGBTQ+ community
											>
										"""),
									]),
									dbc.CardFooter([
										dbc.Stack([
											dbc.Stack([
												dbc.Textarea(className="mb-3", placeholder='i.e., "Create a color theme representing the corporate colors of the American logistics company FedEx"',id='ai-input-colors-text'),
												dbc.FormText('Describe the color scheme you would like in a few sentences.'),
											],gap=0),
											dbc.Stack([
												dbc.Button(children=[html.I(className='bi bi-stars'),' Submit'], id='ai-input-colors-submit', className='p-1', color='success'),
											],gap=3,className='d-flex justify-content-end align-items-center'),
										],gap=3)

									]),
								],color='light'),
							],width={'size':4}),
						])
					])
				]),
				#dbc.CardFooter([]),
			]),
		])
		self.layout['example_image'] = dbc.Container([
			dbc.Card([
				dbc.CardHeader([
					html.H4('Image Generation')
				]),
				dbc.CardBody([
					dbc.Container([
						dbc.Row([
							dbc.Col([
								dbc.Stack([
									html.Span([
										"This example uses AI to generate images based on user input, subject to whatever constraints are built in to the prompt template.",
										html.Span(' The template here',id='ai-show-prompt',style={'font-weight':'bold','color':self.styles['color_sequence'][1]}),
										" is the same one used to generate most of the artwork in this app.  Specify what you'd like the image to depict,",
										" and the app should generate that image in a similar artstyle to the rest of the images in use here.",
									]),
									dbc.Popover(
										[
											dbc.PopoverHeader(dcc.Markdown('**Prompt Template**')),
											dbc.PopoverBody([
												dcc.Markdown("""
						 							>
													>
													> Role / Persona
						 							>
													> You are a digital artist with a well defined style, of which all your work is representative.
													>
						 							>
													> Your Style
						 							>
													> 1. Hand-Drawn Anime Look with Digital Enhancements
												 	>							
						 							> The linework has a slightly organic, hand-drawn feel, rather than the perfectly smooth digital look of modern anime.
													> Line weights vary, with thicker outlines around characters but detailed, refined interior lines for facial features and mechanical elements.
													> The shading style uses cel-shading with some soft gradients, adding depth without losing the sharp, high-contrast aesthetic.
													>
						 							>
						 							> 2. Expressive Faces with Larger, More Detailed Eyes
													>
						 							> Eyes are slightly larger than in 1990s anime, inspired by modern anime’s focus on expressiveness, but not exaggerated like in moe or slice-of-life anime.
													> Detailed reflections and highlights in the irises make them feel luminous and alive, but still maintaining a gritty sci-fi intensity.
													> Facial features retain subtle, naturalistic expressions, avoiding exaggerated reactions in favor of nuanced emotions.
													>
						 							>
						 							> 3. Bold Outlines and Rich Shading
													>							
						 							> Characters and objects are defined with thick, confident outlines, similar to 1990s anime.
													> Shading employs multi-tone cel-shading, giving a three-dimensional look with a hand-painted touch.
													> Soft airbrushed lighting effects (used sparingly) enhance the cyberpunk glow.
													>
						 							>
						 							> 4. Muted Yet Striking Colors
													>
						 							> The overall palette is subdued and industrial, like Ghost in the Shell, but with strategic neon accents.
													> Deep blues, purples, and grays dominate, with vibrant neon blue and cyan highlights adding a futuristic glow.
													> Backgrounds remain hand-drawn and painterly, with textured brush strokes, rather than the hyper-polished CGI aesthetic of modern anime.
													>
						 							>
						 							> 5. Cinematic Framing with a Slightly Gritty Look
													>
						 							> A mix of sharp angles and dynamic close-ups, inspired by 1990s cinematography.
													> Glowing effects, digital distortion, and holographic flickering are present but hand-painted rather than fully CGI-rendered.
													> The scene has a slight grain texture, simulating the look of an old-school anime cel transferred to film.
													>
												"""),
											]),
										],
										placement='bottom',
										target='ai-show-prompt',
										trigger='hover',
										style={'min-width':'50vw'},	
									),
									dcc.Markdown("""
										**Use Case**: Dynamic marketing copy, sales collateral, user personalization, etc
									"""),
									dcc.Loading([
										dbc.Stack([
											html.Img(src='assets/images/placeholder.png',style={'width':'100%','border-radius':'4rem','padding':'2rem'}),
										],gap=3,className='justify-content-center align-items-center',id='ai-image-container',),
									],overlay_style={'visibility':'visible', 'filter': 'blur(2px)'})

								],gap=3),
							],width={'size':8}),
							dbc.Col([
								dbc.Card([
									dbc.CardBody([
										dcc.Markdown("""
											#### **Try it yourself!**

											Some starting ideas:
											
											>
											> Create an image of a cat misbehaving
											>


											>
											> Create an image depicting an exciting sporting event
											>
											

											>
											> Create an image of mysterious person
											>
										"""),
									]),
									dbc.CardFooter([
										dbc.Stack([
											dbc.Stack([
												dbc.Textarea(className="mb-3", placeholder='i.e., "Create an image of..."',id='ai-input-image-text'),
												dbc.FormText('Describe the image you would like in a few sentences.'),
											],gap=0),
											dbc.Stack([
												dbc.Button(children=[html.I(className='bi bi-stars'),' Submit'], id='ai-input-image-submit', className='p-1',color='success'),
											],gap=3,className='d-flex justify-content-end align-items-center'),
										],gap=3)

									]),
								],color='light'),
							],width={'size':4}),
						])
					])
				]),
				#dbc.CardFooter([]),
			]),
		])

	def ai_color_sequence(self, input_prompt):
		client = OpenAI()
		assistant = client.beta.assistants.create(
			name='Arthur',
			instructions='You are a graphic design artist. Write code to represent the colors and styles provided by user prompt as python objects',
			tools=[{'type': 'code_interpreter'}],
			model='gpt-3.5-turbo-0125',
		)
		
		thread = client.beta.threads.create()
		
		message = client.beta.threads.messages.create(
			thread_id=thread.id,
			role='user',
			content=input_prompt
		)
		
		run = client.beta.threads.runs.create_and_poll(
		  thread_id=thread.id,
		  assistant_id=assistant.id,
		  instructions="""
		  Please return a valid JSON string containing a python list containing 12 hex color code values based on the user's prompt.
		  The list must be sorted in order of colors most to least representative of the prompt.
		  Very light shades of white cannot be used, and this requirement is more important than any other.
		  Include only this JSON string in your response, with no other explanations or text.  Do not deviate from this output format.
		  """
		)
		if run.status == 'completed': 
			messages = client.beta.threads.messages.list(
			thread_id=thread.id
		  )
			print(messages)
		else:
			print(run.status)

		m = messages.data[0].content[0].text.value
		ex = re.search(r'\[(.*)\]',m)
		color_palette = []
		if ex:
			print('Received a list object:')
			c_string = ex.group(1).upper()
			c_string = re.sub(r'[\"\']','',c_string)
			print(c_string)
			color_palette = []
			for hex in c_string.split(','):
				color_palette.append(hex)
		return color_palette

	def ai_generate_image(self, input_prompt:str,style='synthwave')->str:
		print(f'Generating image with prompt: {input_prompt} | style: {style}')
		client = OpenAI()

		prompt = None
		if style == 'synthwave':
			prompt = f"""
				'You are a digital artist.   All of your work uses the Outrun/Synthwave visual aesthetic, often including visual elements like neon lights and colors (but never green),
				palm trees, sunsets, geometric shapes and line patterns, and imagery of the 1980s.  Your work typically has an extremely minimalist design to minimize visual clutter.
				Your clients ask you to create pictures of various subjects in your usual style.  I am your client.'

				{input_prompt}
				"""
		elif style == 'anime':
			prompt = f"""
				Role / Persona
				You are a digital artist with a well defined style, of which all your work is representative.

				Your Style
				1. Hand-Drawn Anime Look with Digital Enhancements
				The linework has a slightly organic, hand-drawn feel, rather than the perfectly smooth digital look of modern anime.
				Line weights vary, with thicker outlines around characters but detailed, refined interior lines for facial features and mechanical elements.
				The shading style uses cel-shading with some soft gradients, adding depth without losing the sharp, high-contrast aesthetic.
				2. Expressive Faces with Larger, More Detailed Eyes
				Eyes are slightly larger than in 1990s anime, inspired by modern anime’s focus on expressiveness, but not exaggerated like in moe or slice-of-life anime.
				Detailed reflections and highlights in the irises make them feel luminous and alive, but still maintaining a gritty sci-fi intensity.
				Facial features retain subtle, naturalistic expressions, avoiding exaggerated reactions in favor of nuanced emotions.
				3. Bold Outlines and Rich Shading
				Characters and objects are defined with thick, confident outlines, similar to 1990s anime.
				Shading employs multi-tone cel-shading, giving a three-dimensional look with a hand-painted touch.
				Soft airbrushed lighting effects (used sparingly) enhance the cyberpunk glow.
				4. Muted Yet Striking Colors
				The overall palette is subdued and industrial, like Ghost in the Shell, but with strategic neon accents.
				Deep blues, purples, and grays dominate, with vibrant neon blue and cyan highlights adding a futuristic glow.
				Backgrounds remain hand-drawn and painterly, with textured brush strokes, rather than the hyper-polished CGI aesthetic of modern anime.
				5. Cinematic Framing with a Slightly Gritty Look
				A mix of sharp angles and dynamic close-ups, inspired by 1990s cinematography.
				Glowing effects, digital distortion, and holographic flickering are present but hand-painted rather than fully CGI-rendered.
				The scene has a slight grain texture, simulating the look of an old-school anime cel transferred to film.

				{input_prompt}
				"""

		if prompt is None:
			raise ValueError('Invalid style provided')
		print(f'Sending prompt to LLM: {prompt}')
		response = client.images.generate(
			model="dall-e-3",
			prompt=prompt,
			size="1024x1024",
			quality="standard",
			n=1,
		)
		print(f'Image generation response: {response}')
		image_url = response.data[0].url
		return image_url
	
	# def ai_retrowave_image(self, input_prompt):
	# 	client = OpenAI()


	# 	response = client.images.generate(
	# 		model="dall-e-3",
	# 		prompt=f"""
	# 			'You are a digital artist.   All of your work uses the Outrun/Synthwave visual aesthetic, often including visual elements like neon lights and colors (but never green),
	# 			palm trees, sunsets, geometric shapes and line patterns, and imagery of the 1980s.  Your work typically has an extremely minimalist design to minimize visual clutter.
	# 			Your clients ask you to create pictures of various subjects in your usual style.  I am your client.'

	# 			{input_prompt}
	# 		""",
	# 		size="1024x1024",
	# 		quality="standard",
	# 		n=1,
	# 	)

	# 	image_url = response.data[0].url
	# 	return image_url



	def show_alert(self, text, color='warning'):
		icon = None
		dismissable = True
		if color in ['warning','danger']:
			icon = 'bi bi-exclamation-triangle-fill'
		else:
			icon = 'bi bi-info-circle-fill'
		alert = dbc.Alert([
			dbc.Stack([
				html.I(className=icon),
				html.Span(text),
			],direction='horizontal',gap=3),
		],color=color,dismissable=dismissable, className=f'alert-{color}')
		return alert

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
				ui.layout['header'],
				html.Br(),
				ui.layout['example_chart'],
				html.Br(),
				ui.layout['example_image']
			],className='d-flex flex-column justify-content-center align-items-center'),
		]),
		dcc.Interval(id='interval-10-sec',interval=10*1000,n_intervals=0),
	],fluid=True)

	return layout





