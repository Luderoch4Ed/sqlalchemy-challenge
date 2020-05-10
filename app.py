import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify



engine = create_engine("sqlite:///Resources/hawaii.sqlite")


Base = automap_base()

Base.prepare(engine, reflect=True)
Base.classes.keys()

Measurement = Base.classes.measurement
Station = Base.classes.station


session = Session(engine)


app = Flask(__name__)



# Flask Routes


@app.route("/")
def welcome():
    return (
        f"Hawaii Climate Analysis API<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start/end"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation data for the last year"""
    Recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    max_date = Recent_date[0]

    year_ago =  dt.datetime.strptime(max_date, "%Y-%m-%d") - dt.timedelta(days=366)

    
    query = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_ago).all()

   
    precip = {date: prcp for date, prcp in query}
    return jsonify(precip)


@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations."""
    reporting_stations = session.query(Measurement.station).distinct().count()

   
    stations = list(np.ravel(reporting_stations))
    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def temp_monthly():
    """Return the temperature observations (tobs) for previous year."""
  
    Recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    max_date = Recent_date[0]

    year_ago =  dt.datetime.strptime(max_date, "%Y-%m-%d") - dt.timedelta(days=366)

   
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= year_ago).all()

    
    temps = list(np.ravel(results))

    
    return jsonify(temps)


@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    """Return TMIN, TAVG, TMAX."""

    
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
      
        temps = list(np.ravel(results))
        return jsonify(temps)

  
    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
   
    temps = list(np.ravel(results))
    return jsonify(temps)


if __name__ == '__main__':
    app.run(debug=True)