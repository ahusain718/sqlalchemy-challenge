# Import the dependencies.
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt
from datetime import datetime 
import os


#################################################
# Database Setup
#################################################
engine = create_engine(r"sqlite:////Users/ah230/Downloads/DABC/Class Folder/SurfsUp/Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def home(): 
    """List all available api routes."""
    return (
        f"Available API Routes for Hawaii Weather Data:<br/><br>"
        f"/api/v1.0/precipitation <br/>"
        f"/api/v1.0/stations <br/>"
        f"/api/v1.0/tobs <br/>"
        f"/api/v1.0/trip/yyyy-mm-dd *insert start date here* <br/>"
        f"/api/v1.0/trip/yyyy-mm-dd/yyyy-mm-dd *insert start and end date here* <br/>"
  
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    most_recent_date = session.query(func.max(Measurement.date)).scalar()

    # Calculate the date one year from the last date in data set
    latest_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d')
    start_date = latest_date - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= start_date).all()

    # Convert results to a dictionary
    prcp_dict = {date: prcp for date, prcp in results}

    # Convert the dictionary to JSON
    prcp_json = jsonify(prcp_dict)

    session.close()
    
    return prcp_json  

@app.route("/api/v1.0/stations")
def stations():
    print("Stations route hit!")
    session = Session(engine)
    results = session.query(Station.station).all()

    session.close()

    station_names = list(np.ravel(results))
    return jsonify(station_names)

@app.route("/api/v1.0/tobs")
def tobs():
    print("Tobs route hit!")
    session = Session(engine)
    
    # Get the most recent date in the dataset
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    latest_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d')

    # Calculate the start date for the previous year
    start_date = latest_date - dt.timedelta(days=365)

    # Query the most active station 
    most_active_station = 'USC00519281'  
    tobs = session.query(Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= start_date).all()

    # Convert query results to a list
    temperature_list = [temp[0] for temp in tobs]  # Extract the temperature values

    session.close()

    # Return the JSON response
    return jsonify(temperature_list)

@app.route("/api/v1.0/trip/<start>")
def trip1(start):
    session = Session(engine)
    
    try:
        start = dt.datetime.strptime(start, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Invalid start date format. Please use YYYY-MM-DD."}), 400

    result = session.query(
        func.min(Measurement.tobs), 
        func.avg(Measurement.tobs), 
        func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    session.close()

    if not result:
        return jsonify({"error": "No data found for the specified start date."}), 404

    trip_dict = {
        "Min": result[0][0],
        "Average": result[0][1],
        "Max": result[0][2]
    }

    return jsonify(trip_dict)

@app.route("/api/v1.0/trip/<start>/<end>")
def trip2(start, end):
    session = Session(engine)

    try:
        start = dt.datetime.strptime(start, '%Y-%m-%d')
        end = dt.datetime.strptime(end, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD."}), 400

    result = session.query(
        func.min(Measurement.tobs), 
        func.avg(Measurement.tobs), 
        func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()

    if not result:
        return jsonify({"error": "No data found for the specified date range."}), 404

    # Prepare the result as a dictionary
    trip_dict = {
        "Min": result[0][0],
        "Average": result[0][1],
        "Max": result[0][2]
    }

    return jsonify(trip_dict)

if __name__ == "__main__":
    app.run(debug=True)