# Importing libraries
from flask import Flask, render_template, url_for
import mysql.connector
import numpy as np
import json

app = Flask(__name__)

# freemysqlhosting.net --> info

# Updating numerical stats
def self_update_stats():
    mydb = mysql.connector.connect(host=host, port=port, user=user, passwd=passwd, database=database)
    cursor = mydb.cursor()

    cursor.execute("SELECT MAX(date) FROM india_wide")
    for x in cursor:
        latest_datetime_holder = x

    latest_datetime = latest_datetime_holder[0]

    cursor.execute("SELECT * FROM india_wide WHERE date = '{}'".format(latest_datetime))
    for x in cursor:
        # Filtering extracted values
        upload_cases = x[1]
        upload_deaths = x[2]
        upload_hospitalized = x[3]
        upload_recovered = x[5]
        upload_screened = x[6]

    """
    # Filtering extracted values
    upload_cases = extracted_values[1]
    upload_deaths = extracted_values[2]
    upload_hospitalized = extracted_values[3]
    upload_recovered = extracted_values[5]
    upload_screened = extracted_values[6]
    """
    mydb.close()
    # Returning results
    return upload_cases, upload_deaths, upload_screened, upload_recovered

# Updating values for the line graph
def self_update_graph():
    mydb = mysql.connector.connect(host=host, port=port, user=user, passwd=passwd, database=database)
    cursor = mydb.cursor()

    cursor.execute("SELECT Date FROM trend")

    trend_upload_dates = []
    for i in cursor:
        trend_upload_dates.append(str(i[0]))

    cursor.execute("SELECT Cases FROM trend")

    trend_upload_cases = []
    for x in cursor:
        trend_upload_cases.append(int(x[0]))
    
    trend_upload_deaths = []
    cursor.execute("SELECT Deaths FROM trend")
    for x in cursor:
        trend_upload_deaths.append(int(x[0]))
    
    trend_upload_recovered = []
    cursor.execute("SELECT Recovered FROM trend")
    for x in cursor:
        trend_upload_recovered.append(int(x[0]))
    
    mydb.close()
    # Returning results
    return None, trend_upload_dates, trend_upload_cases, trend_upload_deaths, trend_upload_recovered

# Updating values for the statewise geograph
def self_update_geograph():
    mydb = mysql.connector.connect(host=host, port=port, user=user, passwd=passwd, database=database)
    cursor = mydb.cursor()

    cursor.execute("SELECT State, Cases, Deaths FROM state_wise")

    state_names = []
    state_cases = []
    state_deaths = []

    for x in cursor:
        state_names.append(x[0])
        state_cases.append(x[1])
        state_deaths.append(x[-1])
    """
    print(state_names)
    print(state_cases)
    print(state_deaths)
    """

    mydb.close()
    # Returning results
    return state_names, state_cases, state_deaths

# Main page with the dashboard 
@app.route("/", methods=['GET', 'POST'])
def home():
    # Geograph
    upload_geograph = self_update_geograph()
    state_names = upload_geograph[0]
    state_cases = upload_geograph[1]
    state_deaths = upload_geograph[2]

    # Numericals
    upload_stats = self_update_stats()
    
    # Line graph
    reference = self_update_graph()
    trend_upload_all = reference[0]
    trend_upload_dates = reference[1]
    trend_upload_cases = reference[2]
    trend_upload_deaths = reference[3]
    trend_upload_recovered = reference[4]
    
    # Returning values into the html/css/javascript document
    return render_template("index.html", total_cases=upload_stats[0], total_deaths=upload_stats[1], total_hospitalized=upload_stats[2], total_recovered=upload_stats[3], # For major stats
                            upload_trend_dates=json.dumps(trend_upload_dates), upload_trend_cases=json.dumps(trend_upload_cases), upload_trend_deaths=json.dumps(trend_upload_deaths), upload_trend_recovered=json.dumps(trend_upload_recovered),# For line graphs
                            upload_state_names=json.dumps(state_names), upload_state_cases=json.dumps(state_cases), upload_state_deaths=json.dumps(state_deaths)) # For geo graph

if __name__ == '__main__':
    app.run(debug=True)
