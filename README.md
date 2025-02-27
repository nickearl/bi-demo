# Nick Earl | Interactive Portfolio Demo and Idea Sandbox
## View the app: [https://portfolio.nickearl.net](https://portfolio.nickearl.net)


## UHF+ Streaming Dashboard
### Data Visualization & UX


A demonstration of a complete dashboard app for a fictional new streaming service.  
* Chart visualizations
* Dynamic data filtering
* Styling / UX
* Stakeholder guidance


## **AI Demo**
### **Integrating LLMs with Business Intelligence (BI)**

This section showcases practical applications of **Large Language Models (LLMs)** in **data-driven decision-making and visualization workflows**. These examples illustrate how generative AI can enhance business intelligence tools by enabling **context-aware automation, dynamic styling, and AI-assisted content creation**. 

For this demonstration, I am using **OpenAI’s ChatGPT-3.5 Turbo** via the **OpenAI API** to enhance BI functionality in the following ways:

---

### **1. AI-Driven Theming & UX Customization**  
This implementation leverages LLMs to generate **dynamic color themes** for data visualizations based on a natural language description provided by the user. The model suggests and applies color palettes that align with the specified context.

- **Scalability:** While this demo focuses on basic color adjustments, the approach can be extended to **comprehensive UI/UX customization**, including **adaptive HTML/CSS styling, real-time component layout adjustments, and theme consistency across dashboards**.

**Use Case:** Automating the creation of branded sales collateral by generating export-ready **PNG images** of customized visualizations for presentation slides, reports, or publications.

---

### **2. AI-Assisted Image Generation**  
This feature enables the automatic generation of images based on user-defined prompts. The AI model adheres to a structured **prompt engineering framework**, ensuring that outputs remain consistent with the application’s defined **visual style** and business constraints.

#### **Implementation Details:**  
- The model processes **semantic descriptions** and converts them into visual content that aligns with predefined branding and aesthetic guidelines.  
- A structured **prompt template** ensures reproducibility, maintaining stylistic coherence with other AI-generated assets used in the application.

**Use Case:** Enhancing marketing and design workflows by allowing teams to quickly generate **tailored visual assets** without requiring manual graphic design intervention.


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
* Integrates ChatGPT 3.5 Turbo and 4.0 models via OpenAI API with custom assistants, prompt templates
* Cloud hosted on Heroku, using Redis as cache and Redis/Celery for background processing
