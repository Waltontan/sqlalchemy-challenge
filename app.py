import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import numpy as np
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"<hr> "
        f"/api/v1.0/precipitation<br/>"
        f"_____<em>returns the list of the preciitation level</em><br/>"
        f"<br> "
        f"/api/v1.0/stations<br/>"
        f"_____<em>returns the list of all stations</em><br/>"
        f"<br> "
        f"/api/v1.0/tobs<br/>"
        f"_____<em>returns a list of temperature from the most used station in the last 12 months</em><br/>"
        f"<br> "
        f"/api/v1.0/<em>start_date</em><br/>"
        f"_____<em>returns data in the sequence of <em>Min, Max, Average</em><br/>"
        f"<br> "
        f"/api/v1.0/<em>start_date</em>/<em>end_date</em></br>"
        f"_____<em>returns data in the sequence of <em>Min, Max, Average</em><br/>"
        f"<hr>"
        f"Note: <em>start_date & end_date</em> to be inserted in the order of '%Y-%m-%d'"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query date and precipitation value
    results = session.query(Measurement.date,Measurement.prcp).all()

    session.close()

    # Convert list of tuples into normal list
    prcp = list(np.ravel(results))

    return jsonify(prcp)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all station information
    results = session.query(Station.id,
               Station.station,
               Station.name,
               Station.latitude,
               Station.longitude,
               Station.elevation).all()

    session.close()

    # Convert list of tuples into normal list
    all_station = list(np.ravel(results))

    return jsonify(all_station)


@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query for the most used station
    results = session.query(Measurement.station,
              func.count(Measurement.station)
            ).group_by(Measurement.station
            ).order_by(func.count(Measurement.station).desc()
            ).all()

    Most_used_station = results[0][0]

    # Calculate the date 1 year ago from the last data point in the database
    last_date = (session.query(func.max(Measurement.date)).all())[0][0]
    start_date = dt.datetime.strptime(last_date, '%Y-%m-%d') - dt.timedelta(days=365)

    # Perform a query to retrieve the data and tobs
    results=session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= start_date).filter(Measurement.station == Most_used_station).all()

    session.close()

    # Convert list of tuples into normal list
    Last_year_tobs = list(np.ravel(results))

    return jsonify(Last_year_tobs)


@app.route("/api/v1.0/<start>")
def tobs_start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Convert date to date time format
    start_date = dt.datetime.strptime(start, '%Y-%m-%d') 
    
    # Perform a query to retrieve the data and tobs
    results=session.query(func.min(Measurement.tobs),
                        func.max(Measurement.tobs),
                        func.round(func.avg(Measurement.tobs),1)
                        ).filter(Measurement.date >= start_date
                        ).all()

    session.close()

    # Convert list of tuples into normal list
    start_date_tobs = list(np.ravel(results))

    return jsonify(start_date_tobs)

    return jsonify({"error": f"Check date format"}), 404

@app.route("/api/v1.0/<start>/<end>")
def tobs_start_end(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Convert date to date time format
    start_date = dt.datetime.strptime(start, '%Y-%m-%d') 
    end_date = dt.datetime.strptime(end, '%Y-%m-%d')

    # Perform a query to retrieve the data and tobs
    results=session.query(func.min(Measurement.tobs),
                        func.max(Measurement.tobs),
                        func.round(func.avg(Measurement.tobs),1)
                        ).filter(Measurement.date >= start_date
                        ).filter(Measurement.date <= end_date
                        ).all()

    session.close()

    # Convert list of tuples into normal list
    start_end_date_tobs = list(np.ravel(results))

    return jsonify(start_end_date_tobs)

    return jsonify({"error": f"Check date format"}), 404


if __name__ == '__main__':
    app.run(debug=True)
