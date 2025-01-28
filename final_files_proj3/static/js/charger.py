import numpy as np
from flask import Flask, jsonify
from flask_cors import CORS
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session,sessionmaker,scoped_session
from sqlalchemy import create_engine, func
import psycopg2





#################################################
# Database Setup
#################################################
engine = create_engine('postgresql://postgres:postgres@localhost:5432/ev_database')

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the table
chargers = Base.classes.charging_stations

Session = scoped_session(sessionmaker(bind=engine))

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

CORS(app) # Enable CORS for all domains

def get_db_connection():
    conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/ev_database")
    return conn

#################################################
# Flask Routes
#################################################

@app.route("/")
def index():
    return "Hello, world!"

# Route to fetch charging station data data
@app.route("/api/v1.0/charging_stations")
def chargers():
    # Create our session (link) from Python to the DB
    conn = get_db_connection()
    cur=conn.cursor()
    cur.execute("SELECT station_name, street_address, city, state, latitude, longitude FROM charging_stations")

    """Return a list of all passenger names"""
    # Query all passengers
    results = cur.fetchall()

    cur.close()
    conn.close()

    # Convert list of tuples into normal list
   

    return jsonify(results)



if __name__ == '__main__':
    app.run(debug=True)

