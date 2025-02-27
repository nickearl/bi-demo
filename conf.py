from datetime import date, datetime
import re

"""
Set global configurations
"""
global_config = {
	'app_name': 'Portfolio', # Keep it simple, this becomes the url base path
	'display_name': 'Nick Earl | Portfolio', # optional, replace with a string value to use as a different display name ie 'Dash Template | Example App' 
	'app_prefix': 'pf',
	'logos': {
		'light': 'assets/images/retro_chart.png',
		'dark': 'assets/images/retro_chart.png',
	},
	'colors': {
		'sequence': ["#FA005A", "#86D7DC", "#FFC500", "#520044", "#9B004E","#FA005A", "#86D7DC", "#FFC500", "#520044", "#9B004E"],
		'portrait_colors': ['#86D7DC', '#9B004E','#FA005A','#FFC500','#520044'],
	},
	'intro_text': """
		### Hi, I'm Nick Earl

		#### I build data teams & platforms to deliver powerful insights & data applications (like the one powering this portfolio), integrated directly into business workflows.

		#### I also guide executives, product owners, marketers and other stakeholders towards finding ways to create and use data to drive informed decision making, increase revenue and audience growth, and power engaging user experiences.

	""",
	'enable_google_auth': False,
	'enable_slack': False,
	'footer_text': f'Nick Earl © {datetime.now().year}',
}
global_config['pages'] = {
	'home': {
		'prefix':'home',
		'display_name': 'Home',
		'summary_header': 'Home Header',
		'summary_text': """
					- Explore the various tools and insights available in this app.

				""",
		'image': 'assets/images/spock_sunglasses.png', # Optional, leave this key out to just use the path name ie 'example-page.webp'
		'enabled': True,
	},
	'dashboard': {
		'prefix':'dash',
		'image': 'assets/images/dashboard_screenshot.png',
		'display_name': 'Interactive Data Visualization',
		'summary_header': 'An interactive demo dashboard for a fictional new streaming service',
		'summary_text': """
			- BI & data visualization best practices
			- Stakeholder guidance
			- Procedural dataset generation via python

				""",
		'enabled': True,
	},
	'ai': {
		'prefix':'ai',
		'image': 'assets/images/ai_and_human.webp',
		'display_name': 'AI: ML, LLM / RAG',
		'summary_header': 'Practical integration of ML- and LLM-based tools into data & visualization workflows',
		'summary_text': """
			- **Integrating LLMs / Generative AI with Data Visualization**  
			Utilizing Python to seamlessly integrate **LLM APIs** (such as GPT) with **data visualization tools** to power dynamic, AI-enhanced analytics and visual storytelling.

			- **AI-Generated Design Elements & Theming**  
			Using **ChatGPT** to generate **color themes, branding elements, and UX designs**, allowing for dynamic customization of dashboards and business intelligence reports.

			- **Prompt Engineering for Business Applications**  
			Developing structured **prompt templates** that optimize the consistency, reliability, and adaptability of LLM outputs.

			- **AI-Assisted Image Generation**  
			Leveraging **LLMs and diffusion models** to create custom images based on user prompts, enabling scalable visual content generation for marketing, reports, and presentations.

		""",
		'enabled': True,
	},
}


"""
Set defaults, etc
"""
global_config['display_name'] = global_config['display_name'] if global_config['display_name'] and not global_config['display_name'] == '' else global_config['app_name']
global_config['base_path'] = re.sub(r'[_\s]+', '-', global_config['app_name']).lower()
for page_name, page_config in global_config['pages'].items():
	page_key = re.sub(r'[_\s]+', '-', page_name).lower()
	page_config['path'] = f'/{page_key}' if page_name.lower() != 'home' else '/'
	page_config['full_path'] = f'/{global_config['base_path']}{page_config['path']}'
	page_config['image'] = page_config['image'] if 'image' in page_config.keys() and not page_config['image'] == '' else f'assets/images/{page_key}.webp'
	page_config['cache_path'] = f'{global_config['app_prefix']}:{page_config['prefix']}:cache'
	page_config['s3_path'] = page_config['s3_path'] if 's3_path' in page_config.keys() and not page_config['s3_path'] == '' else f'{global_config['base_path']}/{page_key}/'
	page_config['cache_ttl'] = page_config['cache_ttl'] if 'cache_ttl' in page_config.keys() else 60*60*24*30  # 30 days