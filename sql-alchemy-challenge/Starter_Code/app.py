# Import the dependencies.

import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measure = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



# Create our session (link) from Python to the DB
session = Session(engine)




#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    print("All availbale API routes") 
    return (f"/api/v1.0/precipitation<br/>"
            f"/api/v1.0/stations<br/>"
            f"/api/v1.0/tobs<br/>"
            f"/api/v1.0/<start><br/>"
            f"/api/v1.0/<start>/<end><br/>"
            )

@app.route("/api/v1.0/precipitation")
def precipitation():
    
    print("Return a JSON dictionary of date and prcp")
    recentDate = session.query(Measure.date).order_by(Measure.date.desc()).first()
    oneYear = dt.datetime.strptime(recentDate[0], '%Y-%m-%d') - dt.timedelta(days=366)
    time_stations = session.query(Measure.prcp, Measure.date).\
        filter(Measure.date >= oneYear).\
        order_by(Measure.date).all()

    precip = []
    for prcp, date in time_stations:
        dict1 = {}
        dict1['prcp'] = prcp
        dict1['date'] = date
        precip.append(dict1)
    
    # not entirely sure how to make it more readable
    # so, sorry for the jumble of observations
    return jsonify(precip)

        
@app.route("/api/v1.0/stations")
def station():
    print("Return a JSON list of stations")
    station_query = session.query(Measure.station).\
        group_by(Measure.station).all()
    
    station_vals = []
    for station in station_query:
        station_vals.append(station)
    
    return jsonify(station_vals)

@app.route("/api/v1.0/tobs")
def tobs():

    print("Return a JSON list of temps in last year")
    
    recentDate = session.query(Measure.date).order_by(Measure.date.desc()).first()
    oneYear = dt.datetime.strptime(recentDate[0], '%Y-%m-%d') - dt.timedelta(days=366)
    year_query = session.query(Measure.date, Measure.tobs).\
        filter(Measure.date >= oneYear, Measure.station == 'USC00519281').\
        group_by(Measure.date).\
        order_by(Measure.date).all()
    
    tobs_dates = []
    tobs_vals = []
    for date, temperature in year_query:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = temperature
        tobs_dates.append(tobs_dict)
    
    return jsonify(tobs_dates)

@app.route("/api/v1.0/<start>")
def start(start_date):

    print("JSON list of min, max, avg temps for a start date")
    start_query = session.query(func.min(Measure.tobs), func.avg(Measure.tobs), func.min(Measure.tobs)).\
        filter(Measure.date >= start_date).all()
    
    start_array = []
    for min, avg, max in start_query:
        start_dict = {}
        start_dict["min"] = min
        start_dict["average"] = avg
        start_dict["max"] = max
        start_array.append(start_dict)

    # sorry again for the jumble of observations
    return jsonify(start_array)

@app.route("/api/v1.0/<start>/<end>")
def start_and_end(start_date, end_date):

    print("JSON list of min, max, avg temps for a start and end date")

    both_query = session.query(func.min(Measure.tobs), func.avg(Measure.tobs), func.min(Measure.tobs)).\
        filter(Measure.date >= start_date, Measure.date <= end_date).all()
    
    both_array = []
    for min, avg, max in both_query:
        both_dict = {}
        both_dict["min"] = min
        both_dict["average"] = avg
        both_dict["max"] = max
        both_array.append(both_dict)

    return jsonify(both_array)

session.close()

if __name__ == "__main__":
    app.run(debug=True)