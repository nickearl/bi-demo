import os, time, json, hashlib, re
from datetime import date, datetime, timedelta
import dash
from dash import Dash, html, dcc, Input, Output, State, ALL, MATCH, Patch, callback, DiskcacheManager, CeleryManager, long_callback
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
import plotly.io as pio
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI
import redis
from dashboard import UInterface as dashboard_ui
from ai import UInterface as ai_ui

load_dotenv()
REDISCLOUD_URL = os.environ['REDISCLOUD_URL']

def register_callbacks(app):
	from app import BACKGROUND_CALLBACK_MANAGER



	@app.callback(
		Output('ai-image-container','children'),
		Input('ai-input-image-submit', 'n_clicks'),
		State('ai-input-image-text','value'),
		running=[
			(Output('ai-input-image-submit', 'disabled'), True, False),
			(Output('ai-input-image-submit', 'children'), [dbc.Spinner(size='sm'),' Asking ChatGPT...'], [html.I(className='bi bi-robot'),' Submit']),
		],
		prevent_initial_call=True,
		background=True,
    	manager=BACKGROUND_CALLBACK_MANAGER,
	)
	def ai_retrowave_image(n_clicks,input_prompt):
		print('[' + str(datetime.now()) + '] | '+ '[ai_custom_colors] | ' + str(dash.ctx.triggered_id))
		if dash.ctx.triggered_id == None:
			raise PreventUpdate
		else:
			if n_clicks != None and n_clicks > 0:
				image_url = None
				ui = ai_ui()
				try:
					image_url = ui.ai_retrowave_image(input_prompt)
				except Exception as e:
					print(f'Error getting image url: {e}')
				return html.Img(src=image_url,className='intro-image')


	@app.callback(
		Output('ai-chart-container','children'),
		Input('ai-input-colors-submit', 'n_clicks'),
		State('ai-input-colors-text','value'),
		running=[
			(Output('ai-colors-chart-object','style'), {'display':'none'}, None),
			(Output('loading-card', 'style'), None, {'display':'none'}),
			(Output('ai-input-colors-submit', 'disabled'), True, False),
			(Output('ai-input-colors-submit', 'children'), [dbc.Spinner(size='sm'),' Asking ChatGPT...'], [html.I(className='bi bi-robot'),' Submit']),
		],
		prevent_initial_call=True,
		background=True,
    	manager=BACKGROUND_CALLBACK_MANAGER,
	)
	def ai_custom_colors(n_clicks,input_prompt):
		print('[' + str(datetime.now()) + '] | '+ '[ai_custom_colors] | ' + str(dash.ctx.triggered_id))
		if dash.ctx.triggered_id == None:
			raise PreventUpdate
		else:
			if n_clicks != None and n_clicks > 0:
				o = None
				colors = []
				ui = ai_ui()
				try:
					colors = ui.ai_color_sequence(input_prompt)
					o = dashboard_ui().render_summary_charts(w=750,h=400,chart_only=True,colors=colors)
				except Exception as e:
					print('Retrying ...')
					print(e)
					try:
						colors = ui.ai_color_sequence(input_prompt)
						o = dashboard_ui().render_summary_charts(w=750,h=400,chart_only=True,colors=colors)
					except Exception as e:
						print('Retry failed, falling back to default colors')
						o = dbc.Stack([
							ui.show_alert("We didn't get a usable response from ChatGPT. Sometimes you get a miss!  Try your prompt again, or try modifying it slightly.",color='warning'),
							dashboard_ui().render_summary_charts(w=750,h=400,chart_only=True),
						],gap=3)
				return o
		 


	@app.callback(
		Output('query-result-grid', 'exportDataAsCsv'),
		Input('download_csv_button', 'n_clicks'),
	)
	def download_csv(n_clicks):
		print('[' + str(datetime.now()) + '] | '+ '[download_csv] | ' + str(dash.ctx.triggered_id))
		if dash.ctx.triggered_id == None:
			raise PreventUpdate
		if n_clicks != None and n_clicks > 0:
			return True
		else:
			return False

	@app.callback(
		Output('offcanvas-sidebar','is_open'),
		Input('nav-logo','n_clicks')
	)
	def open_sidebar(n_clicks):
		print('[' + str(datetime.now()) + '] | '+ '[open_sidebar] | ' + str(dash.ctx.triggered_id))
		if dash.ctx.triggered_id == None:
			raise PreventUpdate
		if n_clicks !=None:
			return True


	@app.callback(
		Output('article-carousel','active_index'),
		Input('a-list-button-0','n_clicks'),
		Input('a-list-button-1','n_clicks'),
		Input('a-list-button-2','n_clicks'),
		Input('a-list-button-3','n_clicks'),
	)
	def article_links(n0,n1,n2,n3):
		print('[' + str(datetime.now()) + '] | '+ '[article_links] | ' + str(dash.ctx.triggered_id))
		if dash.ctx.triggered_id == None:
			raise PreventUpdate
		if n0 !=None or n1 !=None or n2 !=None:
			if dash.ctx.triggered_id == 'a-list-button-0':
				return 0
			elif dash.ctx.triggered_id == 'a-list-button-1':
				return 2
			elif dash.ctx.triggered_id == 'a-list-button-2':
				return 3
			elif dash.ctx.triggered_id == 'a-list-button-3':
				return 5

###### Dashboard ############

	@app.callback(
		Output('store-configs','data'),
		Input('filter-date','value'),
		Input('filter-country','value'),
		Input('filter-device-type','value'),
		Input('filter-video-category','value'),
		Input('filter-video-title', 'value'),
		Input('filter-num-chart-items','value'),
		State('filter-date','value'),
		State('filter-country','value'),
		State('filter-device-type','value'),
		State('filter-video-category','value'),
		State('filter-video-title', 'value'),
		Input('filter-num-chart-items','value'),
		State('store-configs','data'),
	)
	def set_configs(in_date,in_country,in_device_type,in_video_category,in_video_title,in_num_chart_items,st_date,st_country,st_device_type,st_video_category,st_video_title,st_num_chart_items,store_data):
		print('[' + str(datetime.now()) + '] | '+ '[set_configs] | ' + str(dash.ctx.triggered_id))
		# if dash.ctx.triggered_id == None:
		# 	raise PreventUpdate
		ui = dashboard_ui()
		data = ui.default_configs
		try:
			data = json.loads(store_data)
		except Exception as e:
			print(f'Could not load configs from store: {e}')
			pass
		try:
			data['date'] = st_date
			data['country'] = st_country
			data['device_type'] = st_device_type
			data['video_category'] = st_video_category
			data['video_title'] = st_video_title
			data['num_chart_items'] = st_num_chart_items
		except Exception as e:
			print(f'Error setting config values: {e}')
		return json.dumps(data)



	@app.callback(
		Output('tab-summary','children'),
		Output('tab-content-performance','children'),
		Output('tab-devices','children'),
		#Output('grid-container','children'),
		Input('store-configs','data'),
		State('tab-summary','children'),
		State('tab-content-performance','children'),
		State('tab-devices','children'),
		#State('grid-container','children'),
	)
	def visualize_results(data,s1,s2,s3):
		print('[' + str(datetime.now()) + '] | '+ '[visualize_results] | ' + str(dash.ctx.triggered_id))
		if dash.ctx.triggered_id == None:
			if s1 == None or s1 == [] or s2 == None or s2 == [] or s3 == None or s3 == []:
				print('initial chart load')
				pass
			else:
				raise PreventUpdate
		chart_configs = None
		try:
			chart_configs = json.loads(data)
		except Exception as e:
			print(f'No config, using default: {e}')
			pass
		ui = dashboard_ui()
		grid = ui.render_daily_grid(chart_configs)
		line_chart = ui.render_daily_line_chart(chart_configs)
		device_pie = ui.render_device_share(chart_configs)
		content_sun = ui.render_category_share(chart_configs)

		summary = ui.render_summary_charts(chart_configs)
		
		content_perf = dbc.Container([
			content_sun,
			html.Br(),
			line_chart,
			html.Br(),
			grid,

		])
		devices = dbc.Container([
			device_pie
		])

		return summary, content_perf, devices

	@app.callback(
		Output('daily-chart-grid', 'exportDataAsCsv'),
		Input('download-csv', 'n_clicks'),
	)
	def download_csv(n_clicks):
		print('[' + str(datetime.now()) + '] | '+ '[download_csv] | ' + str(dash.ctx.triggered_id))
		if dash.ctx.triggered_id == None:
			raise PreventUpdate
		if n_clicks != None and n_clicks > 0:
			return True
		else:
			return False

	@app.callback(
		Output('loading-card-quote-container','children'),
		Input('interval-10-sec','n_intervals'),
	)
	def update_quotes(n_intervals):
		print('[' + str(datetime.now()) + '] | '+ '[update_quotes] | ' + str(dash.ctx.triggered_id))
		ui = dashboard_ui()
		q = ui.get_quote()
		return q
