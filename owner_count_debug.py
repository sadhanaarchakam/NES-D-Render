
from click import group
import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc


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

app = dash.Dash(__name__)


def update_owner_plot_debug(group_by, year_select, selected_industry, color_group=None):
    df = table_owner.copy()
    df = df[df["YEAR"] == year_select]

    for col in owner_label_map.values():
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    if selected_industry != "Total for all sectors":
        df = df[df["NAICS2017_LABEL"] == selected_industry]
    else:
        if "Total for all sectors" in df["NAICS2017_LABEL"].unique():
            df = df[df["NAICS2017_LABEL"] == "Total for all sectors"]

    group_by_owner = owner_label_map.get(group_by, group_by)
    color_group_owner = owner_label_map.get(color_group, color_group) if color_group else None

    if "LFO_LABEL" in [group_by, color_group]:
        return px.bar(title="LFO is not available for owner counts.")

    if group_by_owner in df.columns:
        df = df[df[group_by_owner] != "All owners of nonemployer firms"]
    if color_group_owner and color_group_owner != group_by_owner and color_group_owner in df.columns:
        df = df[df[color_group_owner] != "All owners of nonemployer firms"]

    for base_col in owner_label_map.keys():
        owner_col = owner_label_map.get(base_col)
        if owner_col in df.columns and owner_col not in [group_by_owner, color_group_owner]:
            df = df[df[owner_col] != "All owners of nonemployer firms"]

    group_cols = [group_by_owner]
    if color_group_owner and color_group_owner != group_by_owner:
        group_cols.append(color_group_owner)

    bar_df = df.groupby(group_cols, as_index=False).agg(y_value=("OWNNOPD", "sum"))

    print("DEBUG bar_df columns:", bar_df.columns.tolist())
    print("DEBUG bar_df shape:", bar_df.shape)
    print(bar_df.head(10))

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
        title=f"[DEBUG] Owner Counts by {group_by.replace('_LABEL', '').replace('_', ' ').title()}" +
              (f" and Colored by {color_group.replace('_LABEL', '').replace('_', ' ').title()}" if color_group and color_group != group_by else ""),
        color_discrete_sequence=px.colors.qualitative.Safe
    )

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
