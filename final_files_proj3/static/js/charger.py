# import numpy as np
# from flask import Flask, jsonify
# from flask_cors import CORS
# from sqlalchemy.ext.automap import automap_base
# from sqlalchemy.orm import Session,sessionmaker,scoped_session
# from sqlalchemy import create_engine, func
# import psycopg2





# #################################################
# # Database Setup
# #################################################
# engine = create_engine('postgresql://postgres:postgres@localhost:5432/ev_database')

# # reflect an existing database into a new model
# Base = automap_base()
# # reflect the tables
# Base.prepare(autoload_with=engine)

# # Save reference to the table
# chargers = Base.classes.chargers

# Session = scoped_session(sessionmaker(bind=engine))

# #################################################
# # Flask Setup
# #################################################
# app = Flask(__name__)

# CORS(app) # Enable CORS for all domains

# def get_db_connection():
#     conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/ev_database")
#     return conn

# #################################################
# # Flask Routes
# #################################################

# @app.route("/")
# def index():
#     return "Hello, world!"

# # Route to fetch charging station data data
# @app.route("/api/v1.0/chargers")
# def chargers():
#     # Create our session (link) from Python to the DB
#     conn = get_db_connection()
#     cur=conn.cursor()
#     cur.execute("SELECT station_name, street_address, city, state, latitude, longitude FROM charging_stations")

#     """Return a list of all passenger names"""
#     # Query all passengers
#     results = cur.fetchall()

#     cur.close()
#     conn.close()

#     # Convert list of tuples into normal list
   

#     return jsonify(results)



# if __name__ == '__main__':
#     app.run(debug=True)

from flask import Flask, jsonify
from flask_cors import CORS
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine
import psycopg2

# Database Setup
engine = create_engine('postgresql://postgres:postgres@localhost:5432/ev_database')

# reflect an existing database into a new model
Base = automap_base()

# Reflect the tables, explicitly setting the schema name if necessary
Base.prepare(engine, reflect=True)

# Explicitly reference the schema if your table isn't in the 'public' schema
chargers = Base.classes['charging_stations']

# Set up session
Session = scoped_session(sessionmaker(bind=engine))

# Flask Setup
app = Flask(__name__)
CORS(app)  # Enable CORS for all domains

# Database connection function
def get_db_connection():
    conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/ev_database")
    return conn

# Flask Routes
@app.route("/api/v1.0/chargers")
def get_chargers():
    # Create session (link) from Python to the DB
    session = Session()

    # Query the charging_stations table (explicitly using schema if needed)
    chargers = session.query(chargers).all()  # Use your table reference here

    # Process data into a list of dictionaries
    charger_list = []
    for charger in chargers:
        charger_list.append({
            'station_name': charger.station_name,
            'street_address': charger.street_address,
            'city': charger.city,
            'state': charger.state,
            'latitude': charger.latitude,
            'longitude': charger.longitude,
        })

    session.close()

    return jsonify(charger_list)

if __name__ == '__main__':
    app.run(debug=True)

