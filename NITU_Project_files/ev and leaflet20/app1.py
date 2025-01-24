from flask import Flask, jsonify
import psycopg2
import pandas as pd

from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all domains (required for fetching data from frontend)

# Function to establish a database connection
def get_db_connection():
    conn = psycopg2.connect(
        dbname="ev_database",  # Your actual database name
        user="postgres",        # Your username
        password="postgres",    # Your password
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

if __name__ == '__main__':
    app.run(debug=True)  # Run the Flask app in debug mode
