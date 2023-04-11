from flask import Flask, render_template
import dash
from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
from dash import html
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from datetime import timedelta, datetime
from dash import Dash, Input, Output, dcc, html

app = Flask(__name__)
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
creds = ServiceAccountCredentials.from_json_keyfile_name("keys.json", scope)
client = gspread.authorize(creds)
sheet = client.open("trials").worksheet("Sheet3")
list_of_dicts = sheet.get_all_records()

# Convert data to a Pandas dataframe and format date column
data = (
    pd.DataFrame(list_of_dicts)
    .assign(Date=lambda data: pd.to_datetime(data["Date"], format="%d-%m-%Y"))
    .sort_values(by="Date")
)
external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]


dash_app = dash.Dash(__name__, server=app, url_base_pathname='/', assets_folder='assets')

dash_app.layout = html.Div(
                            children=[
                                
                                html.Div(
                                    children=[
                                        html.Img(src="https://upload.wikimedia.org/wikipedia/commons/6/69/RSMStandardLogoRGB.png", height=59, style={ "margin-left":"10px"}),
                                        html.Button(
                                            id="logout-button",
                                            children="Logout",
                                            n_clicks=0,
                                            className="logout-button",
                                            style={
                                                "background-color": "#dc3545",
                                                "border": "none",
                                                "position": "absolute",
                                                "color": "white",
                                                "padding": "0.5rem 1rem",
                                                "border-radius": "0.25rem",
                                                "cursor": "pointer",
                                                "margin-left":"84%",
                                                "font-size":"16px",
                                                "margin-top":"10px",
                                            },
                                        ),
                                 html.Img(src='https://nexuses.s3.us-east-2.amazonaws.com/Nexuses+logo+WHITE+(1).png', style={'width': '250px', 'display': 'block', 'margin': 'auto', 'margin-top':'25px'}),
                                html.P(children="Client Dashboard", className="header-description"),
                                
                            ],
                            className="header",
                        ),
                        html.Div(
                            className="menu",
                            children=[
                                html.Div(
                                    className="menu-item",
                                    children=[
                                        html.Div(
                                            children="Date Range",
                                            className="menu-title",
                                            style={"text-align": "center"}
                                        ),
                                        dcc.DatePickerRange(
                                            id="date-range",
                                            min_date_allowed=data["Date"].min().date(),
                                            max_date_allowed=data["Date"].max().date(),
                                            start_date=data["Date"].min().date(),
                                            end_date=data["Date"].max().date(),
                                        ),
                                    ],
                                ),
                            ]
                        ),
                        html.Div(
                            children=[
                                html.Div(
                                    children=dcc.Graph(
                                        id="price-chart",
                                        config={"displayModeBar": False},
                                    ),
                                    className="card",
                                ),
                                html.Div(
                                    children=dcc.Graph(
                                        id="volume-chart",
                                        config={"displayModeBar": False},
                                    ),
                                    className="card",
                                ),
                                html.Div(
                                    children=dcc.Graph(
                                        id="drip-chart",
                                        config={"displayModeBar": False},
                                    ),
                                    className="card",
                                ),
                                html.Div(
                                    children=dcc.Graph(
                                        id="drip-pie-chart",
                                        config={"displayModeBar": False},
                                    ),
                                    className="card",
                                ),
                                html.Div(
                                    children=dcc.Graph(
                                        id="data-chart",
                                        config={"displayModeBar": False},
                                    ),
                                    className="card",
                                ),
                            ],
                            className="wrapper",
                        ),
                    ]
                )
    # Add other Dash components here

@dash_app.callback(
    Output("price-chart", "figure"),
    Output("drip-pie-chart", "figure"),
    Output("drip-chart", "figure"),
    Output("volume-chart", "figure"),
    Output("data-chart", "figure"),
    Input("date-range", "start_date"),
    Input("date-range", "end_date"),
)



def update_charts(start_date , end_date):
    # filter data based on selected date range
    filtered_data = data[(data["Date"] >= start_date) & (data["Date"] <= end_date)]


    price_chart_figure = {
        "data": [
            {
                "x": filtered_data["Date"],
                "y": filtered_data["1-1 Email Sent"],
                "type": "lines",
                "name": "Sent",
                "hovertemplate": "%{y:.2f}<extra></extra>",
            },
            {
                "x": filtered_data["Date"],
                "y": filtered_data["1-1 Email Open"],
                "type": "lines",
                "name": "Open",
                "hovertemplate": "%{y:.2f}<extra></extra>",
            },
            {
                "x": filtered_data["Date"],
                "y": filtered_data["1-1 Email Click"],
                "type": "lines",
                "name": "click",
                "hovertemplate": "%{y:.2f}<extra></extra>",
            },
        ],
        "layout": {
            "title": {
                "text": "1-1 Email Sent, 1-1 Email Open, 1-1 Email Click",
                "x": 0.5,
                "xanchor": "center",
            },
            "xaxis": {"fixedrange": True},
            "yaxis": {"tickprefix": "", "fixedrange": True},
            "colorway": ["#17B597", "#E12D69", "#FFC697"],
        },
    }

    volume_chart_figure = {
        "data": [
            {
                "x": filtered_data["Date"],
                "y": filtered_data["Cold Leads"],
                "type": "bar",
                "name": "Cold Leads"
            },
            {
                "x": filtered_data["Date"],
                "y": filtered_data["Warm Leads"],
                "type": "bar",
                "name": "Warm Leads"
            },
            {
                "x": filtered_data["Date"],
                "y": filtered_data["Hot Leads"],
                "type": "bar",
                "name": "Hot Leads"
            },
            {
                "x": filtered_data["Date"],
                "y": filtered_data["Lead Lost"],
                "type": "bar",
                "name": "Lead Lost"
            }
        ],
        "layout": {
            "title": {"text": "Leads Analytics", "x": 0.5, "xanchor": "center"},
            "xaxis": {"fixedrange": True},
            "yaxis": {"fixedrange": True},
            "colorway": ["#E12D39", "#FF9F1C", "#17B897", "#845EC2"],
            "barmode": "group"
        },
    }
    drip_chart_figure = {
        "data": [
            {
                "x": filtered_data["Date"],
                "y": filtered_data["Drip Sent"],
                "type": "lines",
                "name": "Drip Sent",
                "hovertemplate": "%{y:.2f}<extra></extra>",
            },
            {
                "x": filtered_data["Date"],
                "y": filtered_data["Drip Open"],
                "type": "lines",
                "name": "Drip Open",
                "hovertemplate": "%{y:.2f}<extra></extra>",
            },
            {
                "x": filtered_data["Date"],
                "y": filtered_data["Drip Click"],
                "type": "lines",
                "name": "Drip CLick",
                "hovertemplate": "%{y:.2f}<extra></extra>",
            },
        ],
        "layout": {
            "title": {
                "text": "Drip Sent, Drip Open, Drip Click",
                "x": 0.5,
                "xanchor": "center",
            },
            "xaxis": {"fixedrange": True},
            "yaxis": {"tickprefix": "", "fixedrange": True},
            "colorway": ["#1326897", "#E19F39", "#F78627"],
        },
    }
    data_chart_figure = {
        "data": [
            {
                "x": filtered_data["Date"],
                "y": filtered_data["New Accounts added"],
                "type": "bar",
                "name": "New Accounts added",
                "hovertemplate": "%{y:.2f}<extra></extra>",
            },
            {
                "x": filtered_data["Date"],
                "y": filtered_data["New Contacts added"],
                "type": "bar",
                "name": "New Contacts added",
                "hovertemplate": "%{y:.2f}<extra></extra>",
            },
        ],
        "layout": {
            "title": {
                "text": "New Accounts added, New Contacts added",
                "x": 0.5,
                "xanchor": "center",
            },
            "xaxis": {"fixedrange": True},
            "yaxis": {"tickprefix": "", "fixedrange": True},
            "colorway": ["#17B897", "#E12D39", "#FFC627"],
        },
    }
    drip_pie_chart_figure = {
        "data": [
            {
                "values": [data['Drip Sent'].sum(), data['Drip Open'].sum(), data['Drip Click'].sum()],
                "labels": ["Drip Sent", "Drip Open", "Drip Click"],
                "type": "pie",
                "hole": 0.5,
                "hoverinfo": "label+percent",
                "textinfo": "value",
                "marker": {
                    "colors": ["#17B897", "#E12D39", "#FFC627"],
                    "line": {"color": "white", "width": 1},
                },
            }
        ],
        "layout": {
            "title": {
                "text": "Drip Data",
                "x": 0.5,
                "xanchor": "center",
            },
            "showlegend": True,
        },
    }
    return price_chart_figure, volume_chart_figure, drip_chart_figure, data_chart_figure, drip_pie_chart_figure





@app.route('/')
def index():
    return render_template('some2.html', dash_app=dash_app)

if __name__ == '__main__':
    app.run(host='45.76.227.41', port=8503, debug=True)