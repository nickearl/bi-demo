# Nick Earl | Interactive Portfolio Demo and Idea Sandbox
## View the app: [https://portfolio.nickearl.net](https://portfolio.nickearl.net)


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

The [`scripts/gen_datasets.ipynb`](https://github.com/nickearl/bi-demo/blob/main/scripts/gen_datasets.ipynb) Jupyter Notebook works as a standalone script to generate the fictional datasets used in this app, subject to these configurable constraints:

    DAYS = 30                                           # Number of days of data to generate 
    COUNTRIES = 20                                      # Number of countries to generate data for
    BASELINE_USERS_DAILY = 1200000                      # Average total users across all dimensions
    DAILY_USER_CHANGE = 0.05                            # Determines how much user count can vary day to day
    DAILY_VARIANCE_LAG = 3                              # How many preceding days to consider when calculating day over day growth
    MEAN_VIDEO_ENGAGEMENT = 2.2                         # Mean number of video plays per user across all shows
    VAR_VIDEO_ENGAGEMENT = 1                            # Used as one std dev when assiging engagement rates to shows based on a normal distribution
    DAILY_ENGAGEMENT_CHANGE = .05                       # Soft limit on how much video engagement can change by day to day for each simulated 
    MOBILE_SHARE = .55                                  # Baseline percentage of mobile traffic
    VAR_MOBILE_SHARE = .5                               # Used as one std dev when assiging device type values to records based on a normal distribution
    DOW_INDEX = [1.0, 0.95, 0.9, 1.0, 1.0, 1.1, 1.2]    # Simulate weekly cyclicality, DOW_INDEX[0] is weight for Monday, DOW_INDEX[6] is weight for Sunday
    VAR_DOW_INDEX = .1                                  # Used as one std dev when weighting traffic by day of the week based on a normal distribution




## About This App
* Written in Plotly Dash/Flask
* Design: Bootstrap "Flatly" theme, custom CSS, GIMP image editor, various python image libraries
* Integrates ChatGPT 3.5 Turbo via OpenAI API with custom assistants, prompt templates
* Cloud hosted on Heroku, using Redis as cache and Redis/Celery for background processing
