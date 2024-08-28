# Nick Earl | Interactive Portfolio Demo and Idea Sandbox


## UHF+ Streaming Dashboard
### Data Visualization & UX


A demonstration of a complete dashboard app for a fictional new streaming service.  
* Chart visualizations
* Dynamic data filtering
* Styling / UX
* Stakeholder guidance


## AI Demo
### Integrating AI with BI


Some simple but practical examples of integrating generative AI with data & visualization.  For these I'm using ChatGPT (3.5 Turbo) via the OpenAI API to do the following:

#### Color & Theming

Uses AI to generate color themes to apply to a data visualization based on a brief description typed out by the user. This example simply changes some colors, but the implementation can be easily scaled up further to generate more complex themes and UX customization via HTML/CSS styling and dynamic page layouts.

**Use Case:** Creation of sales collateral, exportable PNG images of visualizations for use in presentation slides or publication.



#### Image Generation

This example uses AI to generate images based on user input, subject to whatever constraints are built in to the prompt template. The template here is the same one used to generate most of the artwork in this app. Specify what you'd like the image to depict, and the app should generate that image in a similar artstyle to the rest of the images in use here.


## Dataset Generator

The `scripts/gen_datasets.ipynb` Jupyter Notebook works as a standalone script to generate the fictional datasets used in this app.


## About This App
* Written in Plotly Dash/Flask
* Design: Bootstrap "Flatly" theme, custom CSS, GIMP image editor, various python image libraries
* Integrates ChatGPT 3.5 Turbo via OpenAI API with custom assistants, prompt templates
* Cloud hosted on Heroku, using Redis as cache and Redis/Celery for background processing
