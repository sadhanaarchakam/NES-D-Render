from click import group
import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc

# --------------Load & Prep Data-------------#

# table1
table1 = pd.read_excel("table_1_new.xlsx")

dem_labels = ["SEX_LABEL", "RACE_GROUP_LABEL", "ETH_GROUP_LABEL", "FOREIGN_BORN_GROUP_LABEL", 
              "VET_GROUP_LABEL", "W2_GROUP_LABEL" ]

# owner table:
table_owner = pd.read_excel("table_O1_new.xlsx")
table_owner["OWNNOPD"] = pd.to_numeric(table_owner["OWNNOPD"], errors='coerce')

# -------------Initialize Dash app----------#
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MINTY]) # choose theme
app.title = "Nonemployer Experimental Data Dashboard"
server = app.server


#-----Add Bootstrap Wrapper for layout---#
app.layout = dbc.Container([

    # --- Header/Navbar --- #
    dbc.NavbarSimple(
        brand="NES-D Dashboard: Nonemployer Firms by Demographics",
        style={"borderRadius": "10px"},
        color="primary",
        dark=True,
        fluid=True
    ),

    html.Br(),

    # --- Filters Section --- #
    # create section with filters 
    dbc.Card([
        dbc.CardHeader(
        "Filter Options",
        style={
            "backgroundColor": "#a1e3d0", # b4f0de
            "color": "white"
        }, className="shadow-sm"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Label("Filter by Year:"),
                    dcc.Dropdown(
                        id="year-dropdown",
                        options=[{"label": y, "value": y} for y in sorted(table1["YEAR"].unique())],
                        value=2017,
                        placeholder="Select year...",
                        multi=False
                    ),
                ], md=6),

                dbc.Col([
                    html.Label("Filter by Industry:"),
                    dcc.Dropdown(
                        id="industry-dropdown",
                        options=[{"label": industry, "value": industry} for industry in 
                                sorted(table1["NAICS2017_LABEL"].unique())] +
                                [{"label": "All Industries", "value": "All"}],
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
                        value="SEX_LABEL",
                        clearable=False,
                    ),
                ], md=4),

                dbc.Col([
                    html.Label("Select Demographic Group for Bar Graph (X-Axis):"),
                    dcc.Dropdown(
                        id='bar-dem-dropdown',
                        options=[{'label': l.replace("_LABEL", "").replace("_", " ").title(), "value": l} for l in dem_labels],
                        value="W2_GROUP_LABEL",
                        clearable=False,
                    ),
                ], md=4),

                dbc.Col([
                    html.Label("Select Measure for Bar Graph (Y-Axis):"),
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
        dbc.Tab(label='Receipt Trends', tab_id='line'),
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
    # owner labels:

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
        df = df[df["OWNER_RACE_LABEL"] != "All owners of nonemployer firms"]
        df["OWNER_SEX_LABEL"] = df["OWNER_SEX_LABEL"].str.replace("OWNER_SEX_LABEL=", "")

        group_by_owner = owner_label_map.get(group_by, group_by)
        color_group_owner = owner_label_map.get(color_group, color_group) if color_group else None

        # if group_by_owner not in df.columns:
        #     return px.bar(title=f"Column {group_by_owner} not found in Owner data.")
        # if color_group_owner and color_group_owner not in df.columns:
        #     return px.bar(title=f"Column {color_group_owner} not found in Owner data.")

        group_cols = [group_by_owner]
        if color_group_owner and color_group_owner != group_by_owner:
            group_cols.append(color_group_owner)

        bar_df = df.groupby(group_cols, as_index=False).agg(
            y_value=("OWNNOPD", "sum")
        )

    else:
        df = table1.copy()

        if year_select:
            if not isinstance(year_select, list):
                year_select = [year_select]
            df = df[df["YEAR"].isin(year_select)]

        if selected_industry != "All":
            df = df[df["NAICS2017_LABEL"] == selected_industry]

        group_cols = [group_by]
        if color_group and color_group != group_by:
            group_cols.append(color_group)

        bar_df = df.groupby(group_cols, as_index=False).agg(
            y_value=(y_metric, "sum")
        )

    y_axis_labels = {
        "FIRMNOPD": "Firm Counts",
        "RCPNOPD": "Business Receipts ($1000s)",
        "AVG_REVENUE_PER_FIRM": "Avg Receipts per Firm ($1000s)",
        "OWNNOPD": "Owner Counts"
    }

    fig = px.bar(
        bar_df,
        x=group_cols[0],
        y="y_value",
        color=group_cols[1] if len(group_cols) > 1 else None,
        barmode="group",
        labels={
            "y_value": y_axis_labels.get(y_metric, y_metric),
            group_cols[0]: group_by.replace("_LABEL", "").replace("_", " ").title(),
            group_cols[1] if len(group_cols) > 1 else "": color_group.replace("_LABEL", "").replace("_", " ").title() if color_group else None
        },
        title=f"{y_axis_labels.get(y_metric, y_metric)} by {group_by.replace('_LABEL', '').title()}" +
              (f" and Colored by {color_group.replace('_LABEL', '').title()}" if color_group and color_group != group_by else ""),
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



def update_line_plot(selected_industry, selected_years, y_metric):
    if y_metric == "OWNNOPD":
        df = table_owner.copy()
        df = df[df["OWNER_RACE_LABEL"] != "All owners of nonemployer firms"]

        # removing NAICS "total for all sectors" - maybe?
        df = df[df["NAICS2017_LABEL"] != "Total for all sectors"]

        value_col = "OWNNOPD"                                                                                                                                                                                                      
        label = "Owner Counts"

        if selected_industry and selected_industry != "All":
            df = df[df["NAICS2017_LABEL"] == selected_industry]

        # Always group by both year and industry for line plot
        group_cols = ["YEAR", "NAICS2017_LABEL"]

        line_df = df.groupby(group_cols, as_index=False)[value_col].sum()

        fig = px.line(
            line_df,
            x="YEAR",
            y=value_col,
            color="NAICS2017_LABEL" if "NAICS2017_LABEL" in line_df.columns else None,
            markers=True,
            title="Owner Counts Over Time",
            labels={
                "YEAR": "Year",
                value_col: label,
                "NAICS2017_LABEL": "Industry" if "NAICS2017_LABEL" in line_df.columns else None
            },
            color_discrete_sequence=px.colors.qualitative.Safe
        )

    else:
        df = table1.copy()

        if selected_years:
            if not isinstance(selected_years, list):
                selected_years = [selected_years]
            df = df[df["YEAR"].isin(selected_years)]

        if selected_industry and selected_industry != "All":
            df = df[df["NAICS2017_LABEL"] == selected_industry]

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
        fig = update_line_plot(industry, year, y_metric)
        return dcc.Graph(figure=fig)


if __name__ == '__main__':
    app.run(debug=True)
