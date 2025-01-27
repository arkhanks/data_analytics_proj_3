from flask import Flask, jsonify
import psycopg2
import pandas as pd
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all domains (required for fetching data from frontend)

# Function to establish a database connection
def get_db_connection():
    conn = psycopg2.connect(
        dbname="ev_database",   # database name
        user="postgres",        # username
        password="postgres",    # password
        host="localhost",       # Default is localhost
        port="5432"             # Default port
    )
    return conn

# Function to get data from PostgreSQL and reshape for Plotly
def get_data_from_postgresql():
    conn = get_db_connection()  # Establish DB connection
    
    # SQL query to fetch the relevant data
    query = """
    SELECT year, mode, parameter, value
    FROM ev_adoption
    WHERE parameter = 'EV sales share' AND region = 'World';
    """
    
    # Execute the query and load the results into a pandas DataFrame
    df = pd.read_sql(query, conn)
    
    # Close the database connection
    conn.close()
    
    # Reshape the data for Plotly (pivoting data for the heatmap)
    heatmap_data = {
        'years': df['year'].unique().tolist(),
        'modes': df['mode'].unique().tolist(),
        'values': df.pivot_table(index='year', columns='mode', values='value', aggfunc='mean').values.tolist()
    }
    
    return heatmap_data

# API endpoint to return data as JSON
@app.route('/get_data')
def get_data():
    data = get_data_from_postgresql()  # Call the function to get data from DB
    return jsonify(data)  # Return the data as JSON

# API endpoint for charging stations
@app.route("/api/v1.0/chargers")
def get_chargers():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM charging_stations")  # Replace with your actual table query
    
    results = cur.fetchall()  # Fetch the results from the DB
    
    cur.close()
    conn.close()
    
    chargers_data = [{
        'station_name': row[1],  # column indices based on table schema
        'street_address': row[2],
        'city': row[3],
        'state': row[4],
        'zip': row[5],
        'latitude': row[6],
        'longitude': row[7],
        'total_charging_ports': row[8]  # Assuming this column exists
    } for row in results]
    
    return jsonify(chargers_data)  # Return the data as JSON

if __name__ == '__main__':
    app.run(debug=True)  # Run the Flask app in debug mode
