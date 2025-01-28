import numpy as np
from flask import Flask, jsonify, render_template, request, send_from_directory
from flask_cors import CORS
import psycopg2
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS globally for all routes

# Database Setup
engine = create_engine('postgresql://postgres:postgres@localhost:5432/ev_database')

Base = automap_base()
Base.prepare(autoload_with=engine)

Session = scoped_session(sessionmaker(bind=engine))

# Routes for various pages

@app.route("/")
def index():
    return "Hello, world!"

@app.route("/api/v1.0/chargers")
def get_chargers():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT station_name, street_address, city, state, latitude, longitude FROM charging_stations")
    results = cur.fetchall()
    cur.close()
    conn.close()
    
    chargers_data = []
    for row in results:
        chargers_data.append({
            'station_name': row[0],
            'street_address': row[1],
            'city': row[2],
            'state': row[3],
            'latitude': row[4],
            'longitude': row[5]
        })
    return jsonify(chargers_data)

@app.route("/regions", methods=['GET'])
def get_regions():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT DISTINCT region FROM ev_adoption")  # Assuming 'ev_adoption' is your table name
    regions = cursor.fetchall()
    cursor.close()
    conn.close()
    
    region_list = [region[0] for region in regions]
    region_list.sort()
    return jsonify(region_list)

@app.route('/data', methods=['POST'])
def handle_data():
    data = request.get_json()
    parameter = data.get('parameter')
    region = data.get('region')
    start_year = data.get('start_year')
    end_year = data.get('end_year')

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    SELECT region, category, parameter, year, SUM(value) AS total_value
    FROM ev_adoption
    WHERE parameter = %s AND region = %s AND category = 'Historical'
      AND year BETWEEN %s AND %s
    """
    if parameter in ['EV sales share', 'EV stock share']:
        query += " AND mode = 'Cars'"
    
    query += """
    GROUP BY region, category, parameter, year
    ORDER BY year ASC;
    """
    cursor.execute(query, (parameter, region, start_year, end_year))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    results = [{'region': row[0], 'category': row[1], 'parameter': row[2], 'year': row[3], 'value': row[4]} for row in rows]
    return jsonify(results)

# Fetch Charging Stations Data (used by your frontend)
@app.route('/api/v1.0/charging_stations', methods=['GET'])
def get_charging_stations_data():
    stations = get_charging_stations()
    return jsonify(stations)

def get_charging_stations():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT station_name, street_address, city, state, zip, latitude, longitude, level_1_ports, level_2_ports, dc_fast_ports FROM charging_stations;")
    result = cursor.fetchall()
    cursor.close()
    conn.close()

    stations = []
    for row in result:
        stations.append({
            'station_name': row[0],
            'street_address': row[1],
            'city': row[2],
            'state': row[3],
            'zip': row[4],
            'latitude': row[5],
            'longitude': row[6],
            'level_1_ports': row[7],
            'level_2_ports': row[8],
            'dc_fast_ports': row[9]
        })
    return stations

# Other routes (You can keep adding all the additional routes here)
@app.route('/top_ten')
def top_ten():
    return render_template('top_ten.html')  # This will render the top_ten.html file

@app.route('/map')
def map_view():
    print("Rendering map template: state_map.html")
    return render_template('state_map.html')

# Static and Template Routes
@app.route('/static/data/us_states.geojson')
def geojson_file():
    return send_from_directory('static/data', 'us_states.geojson')

# Connect to the Database
def get_db_connection():
    conn = psycopg2.connect(
        dbname="ev_database",  # database name
        user="postgres",        # username
        password="postgres",    # password
        host="localhost",       # Default is localhost
        port="5432"             # Default port
    )
    return conn

if __name__ == '__main__':
    app.run(debug=True)
