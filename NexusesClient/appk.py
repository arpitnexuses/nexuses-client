from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
import gspread
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
import bcrypt
import dash
from dash import html
from dash import dcc
from datetime import timedelta, datetime
from dash import Dash, Input, Output, dcc, html
from oauth2client.service_account import ServiceAccountCredentials
import plotly.offline as pyo
import matplotlib.pyplot as plt
import io
import base64


app = Flask(__name__)
app.secret_key = 'super secret key'

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
    .assign(Date=lambda data: pd.to_datetime(data["Date"]))
    .sort_values(by="Date")
)
# external_stylesheets = [
#     {
#         "href": "https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap",
#         "rel": "stylesheet",
#     },
# ]


# Set up MongoDB connection
client = MongoClient('mongodb+srv://nexuses:nexuses123@cluster0.pbrqpu9.mongodb.net/?retryWrites=true&w=majority')
db = client['dashboard_app']

@app.route("/")
def index():
    return render_template("login.html")

# Login page
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('index.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = db.users.find_one({'username': username})
        if user and user['password'] == password:
            session['username'] = username
            session['logged_in'] = True
            return redirect(url_for('pipeline'))
        else:
            return "Invalid username or password", 401

# Registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('username') != 'Admin Nexuses':
        return "Unauthorized Access", 401
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        db.users.insert_one({'username': username, 'email': email, 'password': password})
        return redirect(url_for('login'))

# Dashboard view for each user
@app.route('/pipeline')
def pipeline():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    username = session['username']
    user = db.users.find_one({'username': username})
    if user:
        if username == 'RSM Dashboard':
            return render_template('rsm-dashboard.html', data=user)
        else:
            return "User not found", 404
    else:
        return "User not found", 404

@app.route('/database')
def database():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    username = session['username']
    user = db.users.find_one({'username': username})
    if user:
        if username == 'RSM Dashboard':
            return render_template('database.html', data=user)
        else:
            return "User not found", 404
    else:
        return "User not found", 404


@app.route('/dashboard/')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    df = pd.DataFrame(list_of_dicts)
    df['Date'] = pd.to_datetime(df['Date'])

    # Get the date range from the form or use the initial date range
    # if request.method == 'POST':
    #     date_range_select = request.form['date-range-select']
    #     if date_range_select == '7':
    #         start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    #         end_date = datetime.now().strftime('%d-%m-%Y')
    #     elif date_range_select == '15':
    #         start_date = (datetime.now() - timedelta(days=15)).strftime('%Y-%m-%d')
    #         end_date = datetime.now().strftime('%d-%m-%Y')
    #     elif date_range_select == '30':
    #         start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    #         end_date = datetime.now().strftime('%d-%m-%Y')
    #     elif date_range_select == 'last-month':
    #         end_date = datetime.now().replace(day=1).strftime('%d-%m-%Y')
    #         start_date = (datetime.strptime(end_date, '%d-%m-%Y') - relativedelta(months=1)).strftime('%d-%m-%Y')
    # else:
    #     start_date = df['Date'].min().strftime('%Y-%m-%d')
    #     end_date = df['Date'].max().strftime('%Y-%m-%d')

    # # Filter the data based on the selected date range
    # filtered_df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

    # Create the date picker with the initial date range selected
    # date_picker = '<input id="date-picker" type="text" class="form-control" name="daterange" value="{} - {}">'.format(start_date, end_date)

    # Create the chart with the filtered data
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Date'], y=df['1-1 Email Sent'], mode='lines', name='1-1 Email Sent'))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['1-1 Email Open'], mode='lines', name='1-1 Email Open'))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['1-1 Email Click'], mode='lines', name='1-1 Email Click'))
    fig.update_layout(title='1-1 Email Analysis', xaxis_title='Date', yaxis_title='Value', plot_bgcolor='white', paper_bgcolor='white', xaxis=dict(showgrid=True, gridcolor='lightgrey'), yaxis=dict(showgrid=True, gridcolor='lightgrey'))
    fig.update_yaxes(range=[0, df[['1-1 Email Sent', '1-1 Email Open', '1-1 Email Click']].values.max()])
    chart = fig.to_html(full_html=False)


    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=df['Date'], y=df['Drip Sent'], mode='lines', name='Drip Sent'))
    fig1.add_trace(go.Scatter(x=df['Date'], y=df['Drip Open'], mode='lines', name='Drip Open'))
    fig1.add_trace(go.Scatter(x=df['Date'], y=df['Drip Click'], mode='lines', name='Drip Click'))
    fig1.update_layout(title='Leads Report', xaxis_title='Date', yaxis_title='Value', plot_bgcolor='white', paper_bgcolor='white', xaxis=dict(showgrid=True, gridcolor='lightgrey'), yaxis=dict(showgrid=True, gridcolor='lightgrey'))
    fig1.update_yaxes(range=[0, df[['Drip Sent', 'Drip Open', 'Drip Click']].values.max()])
    chart2 = fig1.to_html(full_html=False)

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(x=df['Date'], y=df['Cold Leads'], name='Cold Leads', marker_color='#33A5FF'))
    fig2.add_trace(go.Bar(x=df['Date'], y=df['Warm Leads'], name='Warm Leads', marker_color='#2376B8'))
    fig2.add_trace(go.Bar(x=df['Date'], y=df['Hot Leads'], name='Hot Leads', marker_color='#114064'))
    fig2.update_layout(title='Leads Analysis', xaxis_title='Date', yaxis_title='Value', plot_bgcolor='white', paper_bgcolor='white', xaxis=dict(showgrid=True, gridcolor='lightgrey'), yaxis=dict(showgrid=True, gridcolor='lightgrey'))
    chart3 = fig2.to_html(full_html=False)

    fig3 = go.Figure()
    fig3.add_trace(go.Bar(x=df['Date'], y=df['Meeting scheduled'], name='Meeting scheduled', marker_color='#2376B8'))
    fig3.add_trace(go.Bar(x=df['Date'], y=df['Meeting Rescheduled'], name='Meeting Rescheduled', marker_color='#CCE400'))
    fig3.add_trace(go.Bar(x=df['Date'], y=df['Meeting Done'], name='Meeting Done', marker_color='#E57126'))
    fig3.update_layout(title='Meetings Report', xaxis_title='Date', yaxis_title='Value', plot_bgcolor='white', paper_bgcolor='white', xaxis=dict(showgrid=True, gridcolor='lightgrey'), yaxis=dict(showgrid=True, gridcolor='lightgrey'))
    chart4 = fig3.to_html(full_html=False)
    return render_template('dashboard.html', chart=chart, chart2=chart2, chart3=chart3, chart4=chart4)


    
   

    
@app.route("/iframe-content", methods=["GET"])
def iframe_content():
    
        iframe_src = 'https://sharing.clickup.com/2582608/l/2eu2g-8544/list'
        return f'<iframe src="{iframe_src}" width="100%" height="100%"></iframe>'
    
@app.route("/iframe-data", methods=["GET"])
def iframe_data():
    
        # iframe_src = 'https://sharing.clickup.com/2582608/l/2eu2g-8544/list'
        iframe_srcd = "https://arpitnexuses.retool.com/embedded/public/9ac895ae-08c1-416e-9dc0-e42bc592bd5a"
        return f'<iframe src="{iframe_srcd}" width="100%" height="100%"></iframe>'
  


@app.route('/admin')
def admin():
    # Check if user is admin (e.g. by checking session data)
    if session.get('is_admin'):
        # Retrieve all dashboard data from MongoDB
        data = db.dashboards.find()
        return render_template('admin.html', data=data)
    else:
        # User is not admin, redirect to login page
        return redirect(url_for('login'))


# Logout route
@app.route("/logout")
def logout():
    session.pop("username", None)
    session.pop("logged_in", None)
    return redirect(url_for("login"))
if __name__ == '__main__':
    app.run(host='45.76.227.41', port=8503, debug=True)