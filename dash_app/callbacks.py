import os, time, json, hashlib, re, io, zipfile
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
from dash_app import auto_num_format, get_quote, VirtualInterview

load_dotenv()
REDISCLOUD_URL = os.environ['REDISCLOUD_URL']

def register_callbacks(app):
	from app import BACKGROUND_CALLBACK_MANAGER

#######################
# Global
#######################

	app.clientside_callback(
		"""
		function(n_intervals) {
			if (n_intervals > 0) {
				window.location.reload(true);
			}
			return ''; 
		}
		""",
		Output('full-refresh-script','children'),
		Input('full-refresh-interval','n_intervals'),
	)

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
		Output('loading-card-quote-container','children'),
		Input('quote-refresh-interval','n_intervals'),
		background=True,
		manager=BACKGROUND_CALLBACK_MANAGER,
	)
	def update_quotes(n_intervals):
		# print('[' + str(datetime.now()) + '] | '+ '[update_quotes] | ' + str(dash.ctx.triggered_id))
		q = get_quote()
		return q

	@app.callback(
		Output('download-results-downloader', 'data'),
		Input('download-results-button','n_clicks'),
		State('download-results-store','data'),
		prevent_initial_call=True
	)
	def download_files(n_clicks, data):
		print(f'[{datetime.now()}] | [download_files] | trig_id: [{dash.ctx.triggered_id}]')
		if n_clicks == None:
			raise PreventUpdate
		else:
			try:
				results = json.loads(data)
			except Exception as e:
				print(f'Error loading data from store: {e}')
				raise PreventUpdate
			for key, value in results.items():
				results[key] = pd.DataFrame(value)
			zip_buffer = io.BytesIO()
			with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
				for name,df in results.items():
					csv_buffer = io.StringIO()
					df.to_csv(csv_buffer, index=False)
					zf.writestr(f"{name}.csv", csv_buffer.getvalue())

			zip_buffer.seek(0)  # Rewind the buffer for reading
			return dcc.send_bytes(zip_buffer.getvalue(), 'results.zip')
			# single file version:
			# df = pd.DataFrame().from_dict(json.loads(data))
			# csv_string = df.to_csv(index=False)
			# return dcc.send_string(csv_string, 'results.csv')

	def start_run_status(tool_key, run_id, progress_list_values=['Loading...']):

		r = redis.from_url(REDISCLOUD_URL)
		init_time = datetime.now().isoformat()
		run_durations_key = f'{tool_key}:run_durations'
		run_id_key = f'{tool_key}:active_queries:{run_id}'
		recent_durations = r.lrange(run_durations_key, 0, -1)
		recent_durations = [json.loads(duration) for duration in recent_durations]
		average_duration = 0
		if not recent_durations:
			print(f'No recent duration data found for key: {run_durations_key}')
		else:
			recent_avg_minutes, recent_avg_seconds = divmod(average_duration, 60)
			print(f'Average analysis duration of the most recent 5 runs: {int(recent_avg_minutes)}:{int(recent_avg_seconds):02d}')
			average_duration = sum(recent_durations) / len(recent_durations)
		payload = {
			'init_time': init_time,
			'average_duration': average_duration,
			'progress_list_values': progress_list_values}
		r.set(run_id_key, json.dumps(payload))
		r.expire(run_id_key, 1800)  # Set the key to expire after 30 minutes (1800 seconds)
		print(f'Set run status metadata values in Redis for key: {run_id_key}')

	def end_run_status(tool_key, run_id):
		r = redis.from_url(REDISCLOUD_URL)
		run_id_key = f'{tool_key}:active_queries:{run_id}'
		run_durations_key = f'{tool_key}:run_durations'
		run_data = json.loads(r.get(run_id_key))
		run_duration = datetime.now() - datetime.fromisoformat(run_data['init_time'])
		print('Caching run duration')
		r.lpush(run_durations_key, json.dumps(run_duration.total_seconds()))
		r.ltrim(run_durations_key, 0, 4)  # Keep only the most recent 5 durations
		r.expire(run_id_key, 30)
		print(f'Cleared run status metadata values from Redis for key: {run_id_key}')
	
	@app.callback(
		Output('loading-modal-text','children'),
		Output('loading-modal-list','children'),
		Output('loading-modal-average-duration','children'),
		Input('loading-modal-bar','value'),
		Input('loading-modal-refresh-interval','n_intervals'),
		State('loading-modal-bar','value'),
		State('loading-modal-bar','max'),
		State('loading-modal-data','data'),
		State('session-id-store','data'),
	)
	def display_loading_text(input_progress_value,n_intervals,progress_value,max_value, loading_modal_data, session_id_data):
		print(f'[{datetime.now()}] | [display_loading_text] | trig_id: [{dash.ctx.triggered_id}] | progress_value: [{progress_value}]')
		message = 'Loading...'
		average_duration = None
		recent_avg_minutes = None
		recent_avg_seconds = None
		run_duration = None
		if max_value == None:
			max_value = 0
		steps = []
		if loading_modal_data != None:
			try:
				r = redis.from_url(REDISCLOUD_URL)
				run_key = f'{json.loads(loading_modal_data)}:active_queries:{str(session_id_data)}'
				data = json.loads(r.get(run_key))
				average_duration = data['average_duration']
				init_time = data['init_time']
				progress_list_values = data['progress_list_values']
				recent_avg_minutes, recent_avg_seconds = divmod(average_duration, 60)
				run_duration = datetime.now() - datetime.fromisoformat(init_time)
				run_minutes, run_seconds = divmod(int(run_duration.total_seconds()), 60)
				steps = list(progress_list_values)
				message = str(steps[progress_value])
			except Exception as e:
				pass
		checklist = []
		for step in steps:
			item = dbc.ListGroupItem([
				dbc.Stack([
					html.I(className='bi bi-hourglass',style={'color':'gray'}),
					step,
				],direction='horizontal',gap=3),
			],className='loading-list')
			checklist.append(item)

		for i in range(max_value-1):
			if i <= progress_value:
				try:
					checklist[i].children[0].children[0] = html.I(className='bi bi-check-circle-fill',style={'color':'green'})
				except Exception as e:
					pass

		duration_content = dbc.ListGroupItem([
			dbc.Stack([
				dbc.Stack([
					html.I(className='bi bi-clock',style={'color':'white'}),
					html.Span(f'Running: {int(run_minutes)}:{int(run_seconds):02d}',style={'font-weight':'bold','color':'white'}),
				],direction='horizontal',gap=3,className='align-items-center justify-content-center') if run_duration != None else [],
				dbc.Stack([
					' Average Run Time (Last 5 Runs): ',
					html.Span(f'{int(recent_avg_minutes)}:{int(recent_avg_seconds):02d}',style={'font-weight':'bold','color':'white'}),
				],direction='horizontal',gap=3,className='align-items-center justify-content-center') if average_duration != None else [],
			],direction='horizontal',gap=3,className='align-items-center justify-content-center')
		],className='loading-list')

		return message, checklist, duration_content

#######################
# Home
########################


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
			

#######################
# AI Demos
#######################


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
	def ai_generate_image(n_clicks,input_prompt):
		print('[' + str(datetime.now()) + '] | '+ '[ai_generate_image] | ' + str(dash.ctx.triggered_id))
		if dash.ctx.triggered_id == None:
			raise PreventUpdate
		else:
			if n_clicks != None and n_clicks > 0:
				image_url = None
				ui = ai_ui()
				try:
					image_url = ui.ai_generate_image(input_prompt, style='anime')
				except Exception as e:
					print(f'Error getting image url: {e}')
				return html.Img(src=image_url,style={'width':'100%','border-radius':'4rem','padding':'2rem'})


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
		 


#######################
# Dashboard
#######################

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
		Input('store-configs','data'),
		State('tab-summary','children'),
		State('tab-content-performance','children'),
		State('tab-devices','children'),
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


#########################
# Virtual Interview
#########################

	@app.callback(
		Output('vi-chat-history','children'),
		Output('vi-user-input','value'),
		Input('vi-submit-button','n_clicks'),
		State('vi-user-input','value'),
		State('session-id-store','data'),
	)
	def vi_send_message(n_clicks, user_input_text, session_id_data):
		print(f'[ {str(datetime.now())} ] | [vi_send_message] | {str(dash.ctx.triggered_id)}')
		if dash.ctx.triggered_id == None:
			raise PreventUpdate
		if n_clicks != None and n_clicks > 0 and user_input_text != None and user_input_text != '':
			vi = VirtualInterview(session_id=session_id_data)
			response, chat_history = vi.submit_message(user_input_text)
			print('response: ****')
			print(response)
			print('****')
			rendered_history = vi.render_chat_history(chat_history=chat_history)
			return rendered_history, None

	app.clientside_callback(
		"""
		function(children) {
			console.log("Chat container updated. Children count:", children ? children.length : 0);
			var chatContainer = document.getElementById("chat-history-stack");
			if (chatContainer) {
				chatContainer.scrollTop = chatContainer.scrollHeight;
				console.log("Scroll position set to:", chatContainer.scrollTop);
			} else {
				console.log("Element 'chat-history-stack' not found.");
			}
			return "";
		}
		""",
		Output('dev-null', 'children'),
		Input('chat-history-stack', 'children')
	)