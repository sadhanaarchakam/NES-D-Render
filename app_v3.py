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


# standardize labeling:
def standardize_label(col):
    
    # map w legthen label names:
    map = {
        "Eth": "Ethnicity",
        "Vet": "Veteran Status",
        "W2": "Wage Work Status",
        "Lfo": "LFO"
    }

    base = col.replace("OWNER_", "").replace("_GROUP", "").replace("_LABEL", "").replace("_", " ").title()
    return map.get(base, base)

standardize_label_map = {col: standardize_label(col) for col in dem_labels}

# -------------Initialize Dash app----------#
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP]) # choose theme
app.title = "Nonemployer Experimental Data Dashboard"
server = app.server


#-----Add Bootstrap Wrapper for layout---#
app.layout = dbc.Container([

    # --- Header/Navbar --- #
    dbc.NavbarSimple(
        brand=html.Strong("NES-D Dashboard: Nonemployer Firms by Demographics"),
        style={"borderRadius": "10px", "backgroundColor": "#1A73E8"},
        color="primary",   # use a Bootstrap color name
        dark=True,
        fluid=True
    ),

    html.Br(),

    # ------- About Section ------ #
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
                            "This dashboard visualizes data from the U.S. Census Bureau's Nonemployer Statistics by Demographics (NES-D) Experimental Dataset for the years 2017 to 2019."
                        ),
                        html.P(
                            "The NES-D provides new insights into nonemployer businesses, which are businesses that have no paid employees, are subject to federal income tax."
                        ),
                        html.P(
                            "Nonemployers contribute significantly to the U.S. economy despite not having payroll employees, and they are often freelancers, gig workers, independent contractors, or self-employed individuals."
                        ),
                        html.P(
                            "The NES-D experimental dataset reports statistics on nonemployer business activity with (demographic) characteristics of business owners including:"
                        ),
                        html.Ul(
                            [
                                html.Li("Sex"),
                                html.Li("Race"),
                                html.Li("Ethnicity"),
                                html.Li("Veteran Status"),
                                html.Li("Foreign-Born Status"),
                                html.Li("Wage Work Status")
                            ]
                        ),
                        html.P(
                            "The NES-D experimental dataset additionally reports statistics by nonemployer business characteristics including: "
                        ),
                        html.Ul(
                            [
                                html.Li("Sector"),
                                html.Li("Legal Form of Organization (LFO) ")
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
        style={"borderRadius": "10px"},
    ),

    html.Br(),

    # --- Filters Section --- #
    dbc.Card([
        dbc.CardHeader(
            "Filter Options",
            style={"backgroundColor": "#1A73E8", "color": "white"},
            className="shadow-sm"
        ),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Label("Filter by Year:", className="me-2 fw-semibold"),
                    dcc.Dropdown(
                        id="year-dropdown",
                        options=[{"label": y, "value": y} for y in sorted(table1["YEAR"].unique())],
                        value=2019,
                        placeholder="Select year...",
                        multi=False
                    ),
                ], md=6),

                dbc.Col([
                    html.Label("Filter by Sector:", className="me-2 fw-semibold"),
                    dcc.Dropdown(
                        id="industry-dropdown",
                        options=[{"label": industry, "value": industry}
                                 for industry in sorted(table1["NAICS2017_LABEL"].unique())] +
                                [{"label": "All Sectors", "value": "All"}],
                        value="All",
                        clearable=False
                    )
                ], md=6),
            ]),

            html.Br(),

            # Bar-plot controls
            dbc.Row([
                dbc.Col([
                    html.Label("Select Demographic (X-Axis):", className="me-2 fw-semibold"),
                    dcc.Dropdown(
                        id='bar-dem-dropdown',
                        options=[{'label': standardize_label_map[col], 'value': col} for col in dem_labels],
                        value="SEX_LABEL",
                        clearable=False,
                    ),
                
                # ], md=4),
                # dbc.Col([
                #     # Label + checkbox on one line
                    html.Div(
                        [
                            html.Span("Color by Second Demographic?", className="me-2 fw-semibold"),
                            dbc.Checkbox(
                                id="compare-toggle",
                                value=False,
                                label="",
                                label_class_name="mb-0", 
                            ),
                        ],
                        className="d-flex align-items-center gap-2"
                    ),

                    # The dropdown lives in its own container so we can hide/show it
                    html.Div(
                        dcc.Dropdown(
                            id='color-dem-dropdown',
                            options=[{'label': standardize_label(col), 'value': col} for col in dem_labels],
                            value="RACE_GROUP_LABEL",
                            clearable=False,
                        ),
                        id="color-dem-container",
                        className="mt-2"
                    ),
                ], md=6),

                dbc.Col([
                    html.Label("Select Measure (Y-Axis):", className="me-2 fw-semibold"),
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
                ], md=6),
            ]),

            html.Br(),

            # --- Tabs --- #
            dbc.Tabs([
                dbc.Tab(label='Bar Plot', tab_id='bar'),
                dbc.Tab(label='Time Series', tab_id='line'),
                dbc.Tab(label='Stacked Area Plot', tab_id='stacked-plot')
            ], id='plot-tabs', active_tab='bar'),

            html.Br(),

            # --- Plots --- #
            dbc.Card([
                dbc.CardBody([
                    dcc.Loading(
                        id="loading-plot",
                        type="default",
                        children=html.Div(id='plot-content')
                    )
                ])
            ], style={"backgroundColor": "#f9f9f9"}),
        ])
    ])
], fluid=True)

#------------------- Bar Plot ---------------#
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

        df = table_owner.copy()

        unused_owner_cols = ["OWNER_AGE_LABEL", "OWNER_USCITIZEN_LABEL"]
        df = df.drop(columns=[col for col in unused_owner_cols if col in df.columns], errors="ignore")

        df = df[df["OWNER_RACE_LABEL"] != "All owners of nonemployer firms"]
        df = df[df["NAICS2017_LABEL"] != "Total for all sectors"]

        group_by_owner = owner_label_map.get(group_by, group_by)
        color_group_owner = owner_label_map.get(color_group, color_group) if color_group else None
     
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

        x_pretty = standardize_label(group_by_owner)
        c_pretty = standardize_label(color_group_owner) if color_group_owner else None

        # px.bar for OWNER:
        fig = px.bar(
            bar_df,
            x=group_by_owner,
            y="y_value",
            color=color_group_owner if color_group_owner and color_group_owner in bar_df.columns else None,
            barmode="group",
            labels={
                "y_value": "Owner Counts",
                group_by_owner: x_pretty,
                color_group_owner: c_pretty if color_group_owner else None
            },
                title=f"Owner Counts by " + x_pretty + (
                    f" and Colored by {c_pretty}" if color_group_owner and color_group_owner != group_by_owner else ""),
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

        x_pretty = standardize_label(group_by)
        c_pretty = standardize_label(color_group) if color_group else None

        fig = px.bar(
            bar_df,
            x=group_by,
            y="y_value",
            color=color_group if color_group and color_group in bar_df.columns else None,
            barmode="group",
            labels={
                "y_value": y_axis_labels.get(y_metric, y_metric),
                group_by: x_pretty,
                color_group: c_pretty if color_group else None
            },
            title=(
                f"{y_axis_labels.get(y_metric, y_metric)} by {x_pretty}"
                + (f" and Colored by {c_pretty}" if color_group and color_group != group_by else "")
            ),
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


#------------------- Line Plot ---------------#
def update_line_plot(selected_industry, y_metric, x_dem):
 
 # using same structure as bar plot -> add x_dem filtering
    
    x_dem = x_dem or "NAICS2017_LABEL"

    y_axis_labels = {
        "FIRMNOPD": "Firm Counts",
        "RCPNOPD": "Business Receipts ($1000s)",
        "AVG_REVENUE_PER_FIRM": "Avg Receipts per Firm ($1000s)",
        "OWNNOPD": "Owner Counts",
    }

    # owner level
    if y_metric == "OWNNOPD":
        owner_label_map = {
            "SEX_LABEL": "OWNER_SEX_LABEL",
            "RACE_GROUP_LABEL": "OWNER_RACE_LABEL",
            "ETH_GROUP_LABEL": "OWNER_ETH_LABEL",
            "VET_GROUP_LABEL": "OWNER_VET_LABEL",
            "FOREIGN_BORN_GROUP_LABEL": "OWNER_FOREIGN_BORN_LABEL",
            "W2_GROUP_LABEL": "OWNER_W2_LABEL",
        }

        df = table_owner.copy()

        
        unused_owner_cols = ["OWNER_AGE_LABEL", "OWNER_USCITIZEN_LABEL"]
        df = df.drop(columns=[c for c in unused_owner_cols if c in df.columns], errors="ignore")

        
        if selected_industry and selected_industry != "All":
            df = df[df["NAICS2017_LABEL"] == selected_industry]
        else:
            if "Total for all sectors" in df["NAICS2017_LABEL"].unique():
                df = df[df["NAICS2017_LABEL"] == "Total for all sectors"]

        group_by_owner = owner_label_map.get(x_dem, x_dem)

 
        if group_by_owner in df.columns:
            df = df[df[group_by_owner] != "All owners of nonemployer firms"]

        for owner_col in owner_label_map.values():
            if owner_col in df.columns and owner_col != group_by_owner:
                if df[owner_col].nunique() > 1:
                    df = df[df[owner_col] != "All owners of nonemployer firms"]

        group_cols = ["YEAR"]
        if group_by_owner in df.columns:
            group_cols.append(group_by_owner)

        line_df = df.groupby(group_cols, as_index=False).agg(y_value=("OWNNOPD", "sum"))

        g_pretty = standardize_label(group_by_owner) if group_by_owner in df.columns else None
        title = "Owner Counts over Time" + (f" by {g_pretty}" if g_pretty else "")

        fig = px.line(
            line_df,
            x="YEAR",
            y="y_value",
            color=(group_by_owner if group_by_owner in line_df.columns else None),
            markers=True,
            labels={"YEAR": "Year", "y_value": y_axis_labels["OWNNOPD"], group_by_owner: g_pretty if g_pretty else None},
            title=title,
            color_discrete_sequence=px.colors.qualitative.Safe
        )

    # Firm level counts:
    else:
        df = table1.copy()

        # remove "equally" for race/eth
        if "RACE_GROUP_LABEL" in df.columns:
            df = df[~df["RACE_GROUP_LABEL"].str.lower().str.contains("minority|nonminority|equally", na=False)]
        if "ETH_GROUP_LABEL" in df.columns:
            df = df[~df["ETH_GROUP_LABEL"].str.lower().str.contains("equally", na=False)]

        if selected_industry and selected_industry != "All":
            df = df[df["NAICS2017_LABEL"] == selected_industry]
        else:
            if "Total for all sectors" in df["NAICS2017_LABEL"].unique():
                df = df[df["NAICS2017_LABEL"] == "Total for all sectors"]

        group_by = x_dem

        # Remove "Total" 
        if group_by in df.columns:
            df = df[df[group_by] != "Total"]

       
        for col in dem_labels:
            if col in df.columns and col != group_by:
                if col == "LFO_LABEL":
                    continue
                if "Total" in df[col].unique():
                    df = df[df[col] == "Total"]

        # group by + year agg
        group_cols = ["YEAR"]
        if group_by in df.columns:
            group_cols.append(group_by)

        if y_metric == "FIRMNOPD":
            line_df = df.groupby(group_cols, as_index=False).agg(y_value=("FIRMNOPD", "sum"))
        elif y_metric == "RCPNOPD":
            line_df = df.groupby(group_cols, as_index=False).agg(y_value=("RCPNOPD", "sum"))
        elif y_metric == "AVG_REVENUE_PER_FIRM":
            line_df = df.groupby(group_cols, as_index=False).agg(y_value=("AVG_REVENUE_PER_FIRM", "mean"))
        else:
            line_df = df.groupby(group_cols, as_index=False).agg(y_value=(y_metric, "sum"))

        g_pretty = standardize_label(group_by) if group_by in df.columns else None
        y_pretty = y_axis_labels.get(y_metric, y_metric)
        title = f"{y_pretty} over Time" + (f" by {g_pretty}" if g_pretty else "")

        fig = px.line(
            line_df,
            x="YEAR",
            y="y_value",
            color=(group_by if group_by in line_df.columns else None),
            markers=True,
            labels={"YEAR": "Year", "y_value": y_pretty, group_by: g_pretty if g_pretty else None},
            title=title,
            color_discrete_sequence=px.colors.qualitative.Safe
        )

    
    fig.update_traces(mode="lines+markers", marker=dict(size=6, line=dict(width=1, color="#d4d2d2")))
    fig.update_layout(
        template="plotly_white",
        transition_duration=500,
        xaxis_tickangle=-45,
        title_x=0.5,
        plot_bgcolor="#f9f9f9",
        paper_bgcolor="#ffffff",
        font=dict(family="Segoe UI", size=13),
    )

    return fig



#------------------ Stacked Area Plot ---------------#
def update_stacked_area_plot(industry, y_metric, x_dem):
    # owner count ratio:
    if y_metric == "OWNNOPD":
        df = table_owner.copy()

        df = df[df["NAICS2017_LABEL"] != "Total for all sectors"]

        if industry and industry != "All":
            df = df[df["NAICS2017_LABEL"] == industry]
        
        df = df[df[owner_label_map.get(x_dem, x_dem)] != "All owners of nonemployer firms"]
        group_col = owner_label_map.get(x_dem, x_dem)
        
        # group by year + x_dem (group_col) 
        group_df = df.groupby(["YEAR", group_col], as_index=False)["OWNNOPD"].sum()
        # calc total and percentage (ratio):
        group_df["TOTAL"] = group_df.groupby("YEAR")["OWNNOPD"].transform("sum")
        group_df["PERCENTAGE"] = (group_df["OWNNOPD"] / group_df["TOTAL"]) * 100
        # declare y metric:
        y_label = "Owner Share (%)"

    # firm count ratio + business receipt ratio:
    else:
        df = table1.copy()

        if industry and industry != "All":
                df = df[df["NAICS2017_LABEL"] == industry]

        df = df[df[x_dem] != "Total"]

        # df = df[df["NAICS2017_LABEL"] != "Total for all sectors"]

        # Group by year and industry and sum firm counts
        group_df = df.groupby(["YEAR", x_dem], as_index=False)[y_metric].sum()
        # Calculate total firms per year
        group_df["TOTAL"] = group_df.groupby("YEAR")[y_metric].transform("sum")
        # Calculate percentage (ratio)
        group_df["PERCENTAGE"] = (group_df[y_metric] / group_df["TOTAL"]) * 100

        # choose which y_metric to use:
        y_label = {
            "FIRMNOPD": "Firm Share (%)",
            "RCPNOPD": "Business Receipts Share (%)"
        }.get(y_metric, "Share (%)")

    # Plot

    x_pretty = standardize_label(x_dem)

    fig = px.area(
        group_df,
        x="YEAR",
        y="PERCENTAGE",
        color=group_col if y_metric == "OWNNOPD" else x_dem,
        line_group=group_col if y_metric == "OWNNOPD" else x_dem,
        labels={
            "PERCENTAGE": y_label,
            **({group_col: x_pretty} if y_metric == "OWNNOPD" else {x_dem: x_pretty})
        },
        title=f"{y_label.replace(' (%)', '')} by {x_pretty} Over Time",
        color_discrete_sequence=px.colors.qualitative.Safe
    )

    fig.update_layout(
        title_x=0.5,
        template="plotly_white",
        yaxis_ticksuffix="%",
        xaxis_tickangle=-45,
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
    Input('year-dropdown', 'value'),
    Input('compare-toggle', 'value') 
)
def render_tab_content(tab, x_dem, color_dem, y_metric, industry, year, compare_on):
    if tab == 'bar':
        # add toggle handling
        color_value = color_dem if (compare_on and color_dem and color_dem != x_dem) else None
        fig = update_plot(x_dem, year, industry, y_metric, color_value)
        return dcc.Graph(figure=fig)

    elif tab == 'line':
        fig = update_line_plot(industry, y_metric, x_dem)
        return dcc.Graph(figure=fig)
    
    elif tab == 'stacked-plot':
        fig = update_stacked_area_plot(industry, y_metric, x_dem)
        return dcc.Graph(figure=fig)

#------Hide Dropdown when Checkbox--------
@app.callback(
    Output("color-dem-container", "style"),
    Input("compare-toggle", "value"),
)
def toggle_color_container(compare_on):
    # show when checked, hide when unchecked
    return {} if compare_on else {"display": "none"}

# ----------------Clear Year Filter Callback=----------------#
@app.callback(
    Output('year-dropdown', 'value'),
    Input('plot-tabs', 'active_tab')
)
def clear_year_filter(tab):
    if tab in ['line', 'stacked-plot']:
        return None  # Clear year filter for line and stacked plots
    else:
        # default as 2019
        return 2019

# ---------------Update Select Demogrpaghic (X-axis) Dropdown options ---------------#
@app.callback(
    Output("bar-dem-dropdown", "options"),
    Input("yaxis-metric-dropdown", "value"),
    Input("plot-tabs", "active_tab")
)
def update_x_dem_options(y_metric, graph_type):
    dem_options = [
        {"label": "Industry", "value": "NAICS2017_LABEL"},
        {"label": "Sex", "value": "SEX_LABEL"},
        {"label": "Race", "value": "RACE_GROUP_LABEL"},
        {"label": "Ethnicity", "value": "ETH_GROUP_LABEL"},
        {"label": "Veteran Status", "value": "VET_GROUP_LABEL"},
        {"label": "Foreign Born Status", "value": "FOREIGN_BORN_GROUP_LABEL"},
        {"label": "W2 Status", "value": "W2_GROUP_LABEL"},
        {"label": "Legal Form of Organization", "value": "LFO_LABEL"}
    ]

    # take out LFO label is owner counts
    if y_metric == "OWNNOPD" and graph_type in ["bar", "line"]:  
        dem_options = [opt for opt in dem_options if opt["value"] != "LFO_LABEL"]

    return dem_options    

#---------------Update Y-Metric Dropdown Options----------------#
@app.callback(
    Output('yaxis-metric-dropdown', 'options'),
    Input('plot-tabs', 'active_tab'),
)
def update_ymetric_options(tab):
    options = [
        {'label': 'Firm Counts', 'value': 'FIRMNOPD'},
        {'label': 'Owner Counts', 'value': 'OWNNOPD'},
        {'label': 'Business Receipts', 'value': 'RCPNOPD'},
        {'label': 'Avg Receipts per Firm', 'value': 'AVG_REVENUE_PER_FIRM'}
    ]

    if tab == 'stacked-plot':
        options = [options for options in options if options['value'] != 'OWNNOPD']

    return options

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
