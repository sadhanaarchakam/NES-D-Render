from click import group
import pandas as pd
import dash
from dash import State, dcc, html, Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc

# --------------Load & Prep Data-------------#

# table5
table1 = pd.read_excel("table_5_new.xlsx")

dem_labels = ["SEX_LABEL", "RACE_GROUP_LABEL", "ETH_GROUP_LABEL", "FOREIGN_BORN_GROUP_LABEL", "LFO_LABEL",
              "VET_GROUP_LABEL", "W2_GROUP_LABEL" ]

# owner table:
table_owner = pd.read_excel("table_O1_new.xlsx")
table_owner["OWNNOPD"] = pd.to_numeric(table_owner["OWNNOPD"], errors='coerce')

owner_label_map = {
    "SEX_LABEL": "OWNER_SEX_LABEL",
    "RACE_GROUP_LABEL": "OWNER_RACE_LABEL",
    "ETH_GROUP_LABEL": "OWNER_ETH_LABEL",
    "VET_GROUP_LABEL": "OWNER_VET_LABEL",
    "FOREIGN_BORN_GROUP_LABEL": "OWNER_FOREIGN_BORN_LABEL",
    "W2_GROUP_LABEL": "OWNER_W2_LABEL",
    "AGE_LABEL": "OWNER_AGE_LABEL",
    "USCITIZEN_LABEL": "OWNER_USCITIZEN_LABEL"
}

# -------------Initialize Dash app----------#
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP]) # choose theme
app.title = "Nonemployer Experimental Data Dashboard"
server = app.server


#-----Add Bootstrap Wrapper for layout---#
app.layout = dbc.Container([

    # --- Header/Navbar --- #
    dbc.NavbarSimple(
        brand=html.Strong("NES-D Dashboard: Nonemployer Firms by Demographics"),
        style={"borderRadius": "10px"},
        color="#1A73E8",
        dark=True,
        fluid=True
    ),

    html.Br(),
        #------- About Section ------#
    # dropdown?
    dbc.Card(
        [
            dbc.CardHeader(
                dbc.Button(
                    "About this Data",
                    id="about-toggle",
                    color="primary",
                    n_clicks=0,
                    style={"width": "100%", "textAlign": "left"}
                ),
                style={"padding": "0"}
            ),
            dbc.Collapse(
                dbc.CardBody(
                    [
                        html.P(
                            "This dashboard visualizes data from the U.S. Census Bureau's Nonemployer Statistics by Demographics (NES-D) Experimental Dataset, released from the years 2017 to 2019."
                        ),
                        html.P(
                            "The NES-D provides new insights into nonemployer businesses, which are businesses that have no paid employees, are subject to federal income tax, and usually operate as sole proprietorships, partnerships, or corporations."
                        ),
                        html.P(
                            "These businesses are often freelancers, gig workers, independent contractors, or self-employed individuals who contribute significantly to the U.S. economy despite not having payroll employees."
                        ),
                        html.P(
                            "The NES-D experimental dataset links nonemployer business activity with (demographic) characteristics of business owners including:"
                        ),
                        html.Ul(
                            [
                                html.Li("Sex"),
                                html.Li("Race"),
                                html.Li("Ethnicity"),
                                html.Li("Veteran Status"),
                                html.Li("Foreign-Born Status"),
                                html.Li("W2 Income Status"),
                                html.Li("LFO Status"),
                            ]
                        ),
                        html.P(
                            [
                                "For more information, visit the ",
                                html.A(
                                    "NES-D experimental data site",
                                    href="https://www.census.gov/data/experimental-data-products/nes-d-wage-work-tables.html",
                                    target="_blank",
                                ),
                                " or read the ",
                                html.A(
                                    "experimental methodology",
                                    href="https://www2.census.gov/data/experimental-data-products/nes-d-wage-work-tables/methodology.pdf",
                                    target="_blank",
                                ),
                                ".",
                            ]
                        ),
                    ]
                ),
                id="about-collapse",
                is_open=False,
            ),
        ],
        style={
            "borderRadius": "10px",
        },
    ),
    
    html.Br(),
  
    # --- Filters Section --- #
    # create section with filters 
    dbc.Card([
        dbc.CardHeader(
        "Filter Options",
        style={
            "backgroundColor": "#1A73E8",
            "color": "white"
        }, className="shadow-sm"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Label("Filter by Year:"),
                    dcc.Dropdown(
                        id="year-dropdown",
                        options=[{"label": y, "value": y} for y in sorted(table1["YEAR"].unique())],
                        value=2019,
                        placeholder="Select year...",
                        multi=False
                    ),
                ], md=6),

                dbc.Col([
                    html.Label("Filter by Sector:"),
                    dcc.Dropdown(
                        id="industry-dropdown",
                        options=[{"label": industry, "value": industry} for industry in 
                                sorted(table1["NAICS2017_LABEL"].unique())] +
                                [{"label": "All Sectors", "value": "All"}],
                        value="All",
                        clearable=False
                    )
                ], md=6),
            ]),

            html.Br(), # tab for new row w filters for bar-plot specific 

            dbc.Row([
                dbc.Col([
                    html.Label("Color By Demographic:"),
                    dcc.Dropdown(
                        id='color-dem-dropdown',
                        options=[{'label': l.replace("_LABEL", "").replace("_", " ").title(), "value": l} for l in dem_labels],
                        value="RACE_GROUP_LABEL",
                        clearable=False,
                    ),
                ], md=4),

                dbc.Col([
                    html.Label("Select Demographic (X-Axis):"),
                    dcc.Dropdown(
                        id='bar-dem-dropdown',
                        options=[{'label': l.replace("_LABEL", "").replace("_", " ").title(), "value": l} for l in dem_labels],
                        value="SEX_LABEL",
                        clearable=False,
                    ),
                ], md=4),

                dbc.Col([
                    html.Label("Select Measure (Y-Axis):"),
                    dcc.Dropdown(
                        id='yaxis-metric-dropdown',
                        options=[
                            {'label': 'Firm Counts', 'value': 'FIRMNOPD'},
                            {'label': 'Owner Counts', 'value': 'OWNNOPD'},
                            {'label': 'Business Receipts', 'value': 'RCPNOPD'},
                            {'label': 'Avg Receipts per Firm', 'value': 'AVG_REVENUE_PER_FIRM'}
                        ],
                        value='FIRMNOPD',
                        clearable=False
                    )
                ], md=4),
            ])
        ], style={"backgroundColor": "#f9f9f9"})
    ], className="mb-4"),

    # --- Tabs --- #
    dbc.Tabs([
        dbc.Tab(label='Bar Plot', tab_id='bar'),
        dbc.Tab(label='Time Series', tab_id='line'),
    ], id='plot-tabs', active_tab='bar'),

    html.Br(),

    # --- Plots --- #
    # section for actual plots
    dbc.Card([
        dbc.CardBody([
            dcc.Loading(
                id="loading-plot",
                type="default",
                children=html.Div(id='plot-content')
            )
        ])
    ], style={"backgroundColor": "#f9f9f9"})
], fluid=True)


#------------------- Create Plot Functions ---------------#
def update_plot(group_by, year_select, selected_industry, y_metric="AVG_REVENUE_PER_FIRM", color_group=None):
    

    if y_metric == "OWNNOPD":
        owner_label_map = {
        "SEX_LABEL": "OWNER_SEX_LABEL",
        "RACE_GROUP_LABEL": "OWNER_RACE_LABEL",
        "ETH_GROUP_LABEL": "OWNER_ETH_LABEL",
        "VET_GROUP_LABEL": "OWNER_VET_LABEL",
        "FOREIGN_BORN_GROUP_LABEL": "OWNER_FOREIGN_BORN_LABEL",
        "W2_GROUP_LABEL": "OWNER_W2_LABEL"
    }


    if y_metric == "OWNNOPD":
        df = table_owner.copy()

        unused_owner_cols = ["OWNER_AGE_LABEL", "OWNER_USCITIZEN_LABEL"]
        df = df.drop(columns=[col for col in unused_owner_cols if col in df.columns], errors="ignore")

        df = df[df["OWNER_RACE_LABEL"] != "All owners of nonemployer firms"]
        df = df[df["NAICS2017_LABEL"] != "Total for all sectors"]

        group_by_owner = owner_label_map.get(group_by, group_by)
        color_group_owner = owner_label_map.get(color_group, color_group) if color_group else None
        
        # handling valid pairings 
        valid_pair_bases = {"OWNER_RACE_LABEL", "OWNER_W2_LABEL"}
        if not (valid_pair_bases & {group_by_owner, color_group_owner}):
            return px.bar(title="Only combinations with RACE or W2 are supported for Owner Counts.")
        
        if group_by_owner in df.columns:
            df = df[df[group_by_owner] != "All owners of nonemployer firms"]

        if color_group_owner and color_group_owner != group_by_owner and color_group_owner in df.columns:
            df = df[df[color_group_owner] != "All owners of nonemployer firms"]

        
        for owner_col in owner_label_map.values():
            # owner_col = owner_label_map.get(base_col)
            if owner_col in df.columns and owner_col not in [group_by_owner, color_group_owner]:
                if df[owner_col].nunique() > 1:
                    df = df[df[owner_col] != "All owners of nonemployer firms"]

        group_cols = [group_by_owner]
        if color_group_owner and color_group_owner != group_by_owner:
            group_cols.append(color_group_owner)

        bar_df = df.groupby(group_cols, as_index=False).agg(
            y_value=("OWNNOPD", "sum")
        )

        # px.bar for OWNER:
        fig = px.bar(
            bar_df,
            x=group_by_owner,
            y="y_value",
            color=color_group_owner if color_group_owner and color_group_owner in bar_df.columns else None,
            barmode="group",
            labels={
                "y_value": "Owner Counts",
                group_by_owner: group_by.replace("_LABEL", "").replace("_", " ").title(),
                color_group_owner: color_group.replace("_LABEL", "").replace("_", " ").title() if color_group else None
            },
            title=f"Owner Counts by {group_by.replace('_LABEL', '').replace('_', ' ').title()}" +
                  (f" and Colored by {color_group.replace('_LABEL', '').replace('_', ' ').title()}" if color_group and color_group != group_by else ""),
            color_discrete_sequence=px.colors.qualitative.Safe
        )

    else:
        df = table1.copy()

        # remove minoity, nonminority, and equally
        if "RACE_GROUP_LABEL" in df.columns:
            exclude_terms = ["minority", "nonminority", "equally"]
            df = df[~df["RACE_GROUP_LABEL"].str.lower().str.contains('|'.join(exclude_terms), na=False)]

        if "ETH_GROUP_LABEL" in df.columns:
            exclude_terms = ["equally"]
            df = df[~df["ETH_GROUP_LABEL"].str.lower().str.contains('|'.join(exclude_terms), na=False)]
        
        
        if year_select:
            if not isinstance(year_select, list):
                year_select = [year_select]
            df = df[df["YEAR"].isin(year_select)]

        if selected_industry != "All":
            df = df[df["NAICS2017_LABEL"] == selected_industry]
        else:
            if "Total for all sectors" in df["NAICS2017_LABEL"].unique():
                df = df[df["NAICS2017_LABEL"] == "Total for all sectors"]
  
        # filtering out Totals: 
        if group_by in df.columns:
            df = df[df[group_by] != "Total"]

        if color_group and color_group != group_by and color_group in df.columns:
            df = df[df[color_group] != "Total"]

        for col in dem_labels:
            if col in df.columns and col not in [group_by, color_group]:
                # skip LFO unless it's being used
                if col == "LFO_LABEL":
                    continue
                if "Total" in df[col].unique():
                    df = df[df[col] == "Total"]
                
        # handle duplicate counts:
        group_cols = [group_by, color_group] if color_group else [group_by]
        group_cols = list(dict.fromkeys(group_cols))

        # update to handle diff metrics:
        if y_metric == "FIRMNOPD":
            bar_df = df.groupby(group_cols, as_index=False).agg(y_value=("FIRMNOPD", "sum"))
        elif y_metric == "RCPNOPD":
            bar_df = df.groupby(group_cols, as_index=False).agg(y_value=("RCPNOPD", "sum"))
        elif y_metric == "AVG_REVENUE_PER_FIRM":
            bar_df = df.groupby(group_cols, as_index=False).agg(y_value=("AVG_REVENUE_PER_FIRM", "mean"))

            
        # plotting for FIRM LEVEL:
        y_axis_labels = {
            "FIRMNOPD": "Firm Counts",
            "RCPNOPD": "Business Receipts ($1000s)",
            "AVG_REVENUE_PER_FIRM": "Avg Receipts per Firm ($1000s)",
            "OWNNOPD": "Owner Counts"
        }

        fig = px.bar(
            bar_df,
            x=group_by,
            y="y_value",
            color=color_group if color_group and color_group in bar_df.columns else None,
            barmode="group",
            labels={
                "y_value": y_axis_labels.get(y_metric, y_metric),
                group_by: group_by.replace("_LABEL", "").replace("_", " ").title(),
                color_group: color_group.replace("_LABEL", "").replace("_", " ").title() if color_group else None
            },
            title=f"{y_axis_labels.get(y_metric, y_metric)} by {group_by.replace('_LABEL', '').replace('_', ' ').title()}" +
                  (f" and Colored by {color_group.replace('_LABEL', '').replace('_', ' ').title()}" if color_group and color_group != group_by else ""),
            color_discrete_sequence=px.colors.qualitative.Safe
        )

    # modify layout and style of plots: 

    fig.update_layout(
        transition_duration=500,
        xaxis_tickangle=-45,
        title_x=0.5,
        plot_bgcolor="#f9f9f9",
        paper_bgcolor="#ffffff",
        font=dict(family="Segoe UI", size=13),
    )
    fig.update_traces(marker=dict(line=dict(width=1, color='#d4d2d2')))

    return fig



def update_line_plot(selected_industry, y_metric):
    if y_metric == "OWNNOPD":
        df = table_owner.copy()

        df = df[df["OWNER_RACE_LABEL"] != "All owners of nonemployer firms"]
        df = df[df["NAICS2017_LABEL"] != "Total for all sectors"]

        for base_col, owner_col in owner_label_map.items():
            if owner_col in df.columns and df[owner_col].nunique() > 1:
                df = df[df[owner_col] != "All owners of nonemployer firms"]

        if selected_industry and selected_industry != "All":
            df = df[df["NAICS2017_LABEL"] == selected_industry]

        value_col = "OWNNOPD"                                                                                                                                                                                                      
        label = "Owner Counts"
    
        # Always group by both year and industry for line plot
        group_cols = ["YEAR", "NAICS2017_LABEL"]

        line_df = df.groupby(group_cols, as_index=False)[value_col].sum()

        fig = px.line(
            line_df,
            x="YEAR",
            y=value_col,
            color="NAICS2017_LABEL", 
            markers=True,
            title="Owner Counts Over Time",
            labels={
                "YEAR": "Year",
                value_col: label,
                "NAICS2017_LABEL": "Industry" 
            },
            color_discrete_sequence=px.colors.qualitative.Safe
        )

    else:
        df = table1.copy()

        if selected_industry and selected_industry != "All":
            df = df[df["NAICS2017_LABEL"] == selected_industry]

        df = df[df["NAICS2017_LABEL"] != "Total for all sectors"]
        
        # remove totals:
        for col in dem_labels:
            if col in df.columns and df[col].nunique() > 1:
                df = df[df[col] != "Total"]

        value_col = y_metric
        label_map = {
            "FIRMNOPD": "Firm Counts",
            "RCPNOPD": "Business Receipts ($1000s)",
            "AVG_REVENUE_PER_FIRM": "Avg Receipts per Firm ($1000s)"
        }
        label = label_map.get(value_col, value_col)

        line_df = df.groupby(["YEAR", "NAICS2017_LABEL"])[value_col].sum().reset_index()

        fig = px.line(
            line_df,
            x="YEAR",
            y=value_col,
            color="NAICS2017_LABEL",
            markers=True,
            title=f"{label} Trends by Industry",
            labels={"YEAR": "Year", value_col: label},
            color_discrete_sequence=px.colors.qualitative.Safe
        )

    fig.update_traces(
        mode="lines+markers",
        marker=dict(
            size=6,
            line=dict(width=1, color='#d4d2d2')
        )
    )

    fig.update_layout(
        template="plotly_white",
        transition_duration=500,
        xaxis_tickangle=-45,
        title_x=0.5,
        plot_bgcolor="#f9f9f9",
        paper_bgcolor="#ffffff",
        font=dict(family="Segoe UI", size=13)
    )
    


    return fig


#-------------  Plot Callback with Tabs ----------------#
@app.callback(
    Output('plot-content', 'children'),
    Input('plot-tabs', 'active_tab'), # update tab callback
    Input('bar-dem-dropdown', 'value'),
    Input('color-dem-dropdown', 'value'),
    Input('yaxis-metric-dropdown', 'value'),
    Input('industry-dropdown', 'value'),
    Input('year-dropdown', 'value')
)
def render_tab_content(tab, x_dem, color_dem, y_metric, industry, year):
    if tab == 'bar':
        fig = update_plot(x_dem, year, industry, y_metric, color_dem)
        return dcc.Graph(figure=fig)

    elif tab == 'line':
        fig = update_line_plot(industry, y_metric)
        return dcc.Graph(figure=fig)

#-------------About Section Click Callback-------------#
@app.callback(
    Output("about-collapse", "is_open"),
    Input("about-toggle", "n_clicks"),
    State("about-collapse", "is_open")
)
def toggle_about_collapse(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open

if __name__ == '__main__':
    app.run(debug=True)
