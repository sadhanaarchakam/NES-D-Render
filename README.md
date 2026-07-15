# NES-D Dashboard

An interactive dashboard built with Dash and Plotly that visualizes the U.S. Census Bureau's Nonemployer Statistics by Demographics (NES-D) Experimental Dataset (2017–2019).

The NES-D dataset reports statistics on nonemployer businesses (businesses with no paid employees, such as freelancers, gig workers, and independent contractors) broken down by owner demographics: sex, race, ethnicity, veteran status, foreign-born status, and wage work status, as well as by sector and legal form of organization.

**Hosted on Render!** 

[https://nes-d-demograpghics-dash-app.onrender.com/]


## Features:

- Filter data by year and sector
- Bar chart, line chart, and stacked area chart views
- Compare two demographic groups at once with a toggle
- Contextual info tooltips explaining each chart type
- Background on the dataset available in an expandable "About this Data" section


## Data Source

U.S. Census Bureau, NES-D Experimental Data Tables:

https://www.census.gov/programs-surveys/abs/data/nesd.html

## Running the Application Locally


**1. Clone the repo:**

```
   git clone https://github.com/sadhanaarchakam/NES-D-Render.git
   cd NES-D-Render
```

**2. Install dependencies:**

```
   pip install -r requirements.txt
```

**3. Run the app:**

```
   python app_v3.py
```

**4. Open the local link printed in the terminal**


## Tech Stack

- **Dash and Dash Bootstrap Components** for the app framework and layout
- **Plotly Express** for charting
- **Pandas** for data processing
- Gunicorn as the production WSGI server on **Render**
