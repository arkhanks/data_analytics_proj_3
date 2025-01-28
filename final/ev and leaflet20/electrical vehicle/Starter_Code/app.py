from flask import Flask, jsonify, render_template, request,send_from_directory
import psycopg2
from flask_cors import CORS  # Import CORS to use globally

app = Flask(__name__)
CORS(app)  # Enable CORS globally for all routes



def get_db_connection():
    conn = psycopg2.connect(
        dbname="ev_database",   # Your actual database name
        user="postgres",        # Your username
        password="postgres",    # Your password
        host="localhost",       # Default is localhost
        port="5432"             # Default port
    )
    return conn

# Route to get regions (this is the route called in your frontend)
@app.route('/regions', methods=['GET'])
def get_regions():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT DISTINCT region FROM ev_adoption")  # Assuming 'ev_adoption' is your table name
    regions = cursor.fetchall()
    cursor.close()
    conn.close()
    
    # Return as JSON response
    region_list = [region[0] for region in regions]
    region_list.sort()
    return jsonify(region_list)

# Route to handle the form submission (fetch EV data)
@app.route('/data', methods=['POST'])
def handle_data():
    data = request.get_json()
    parameter = data.get('parameter')
    region = data.get('region')
    start_year = data.get('start_year')
    end_year = data.get('end_year')

    conn = get_db_connection()
    cursor = conn.cursor()

    # Base query
    query = """
    SELECT region, category, parameter, year, SUM(value) AS total_value
    FROM ev_adoption
    WHERE parameter = %s AND region = %s AND category = 'Historical'
      AND year BETWEEN %s AND %s
    """

    # If the parameter is 'EV sales share' or 'EV stock share', add the mode condition
    if parameter in ['EV sales share', 'EV stock share']:
        query += " AND mode = 'Cars'"

    # Adding GROUP BY and ORDER BY at the end of the query
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

# Route for the World Projection page (Grouped Bar Chart)
#@app.route('/world_projection')
#def world_projection():
   # return render_template('EVSalesShare.html')  # Render the index1.html file for World Projection

# Route to get the data for the grouped bar chart
@app.route('/get_data', methods=['GET'])
def get_grouped_bar_chart_data():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Example query to fetch the data (modify based on your schema)
    query = """
    SELECT year, mode, AVG(value) AS mean_value
    FROM ev_adoption
    WHERE parameter = 'EV sales share' AND region = 'World'
    GROUP BY year, mode
    ORDER BY year ASC;
    """
    cursor.execute(query)
    rows = cursor.fetchall()


    
    cursor.close()
    conn.close()

    # Format the data to match what your frontend is expecting
    years = sorted(set([row[0] for row in rows]))  # Extract unique years
    modes = sorted(set([row[1] for row in rows]))  # Extract unique modes

    # Create a data structure where `values` is a list of lists, where each list corresponds to a mode
    values = []
    for mode in modes:
        mode_values = [row[2] for row in rows if row[1] == mode]
        values.append(mode_values)

    # Return the formatted data as JSON
    return jsonify({
        'years': years,
        'modes': modes,
        'values': values
    })

# Route to fetch charging stations data
@app.route('/api/v1.0/charging_stations', methods=['GET'])
def get_charging_stations_data():
    stations = get_charging_stations()
    return jsonify(stations)

def get_charging_stations():
    # Connect to the PostgreSQL database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Query the charging_stations table
    cursor.execute("SELECT station_name, street_address, city, state, zip, latitude, longitude, level_1_ports, level_2_ports, dc_fast_ports FROM charging_stations;")
    result = cursor.fetchall()

    # Close the database connection
    cursor.close()
    conn.close()

    # Format the result as a list of dictionaries
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

@app.route('/api/v1.0/get_ev_sales_vs_ports_data', methods=['POST'])
def get_ev_sales_vs_ports_data():
    data = request.get_json()
    region = data.get('region')

    conn = get_db_connection()
    cursor = conn.cursor()

    # Query for EV sales
    sales_query = """
    SELECT year, SUM(value) AS total_sales
    FROM ev_adoption
    WHERE parameter = 'EV sales' AND region = %s AND category = 'Historical'
    GROUP BY year
    ORDER BY year ASC;
    """
    cursor.execute(sales_query, (region,))
    sales_rows = cursor.fetchall()

    # Query for charging ports
    ports_query = """
    SELECT year, SUM(value) AS total_ports
    FROM ev_adoption
     WHERE parameter = 'EV charging points' AND region = %s AND category = 'Historical'
    GROUP BY year
    ORDER BY year ASC;
    """
    cursor.execute(ports_query, (region,))
    ports_rows = cursor.fetchall()

    cursor.close()
    conn.close()

    # Format the results into a dictionary for response
    sales = [{'year': row[0], 'value': row[1]} for row in sales_rows]
    ports = [{'year': row[0], 'value': row[1]} for row in ports_rows]

    return jsonify({'sales': sales, 'ports': ports})



# Route for the home page
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/charging_stations')
def charging_stations():
    return render_template('charging_stations.html')

@app.route('/top_ten')
def top_ten():
    return render_template('top_ten.html')  # This will render the top_ten.html file

@app.route('/EVSalesShare')
def EVSalesShare():
   return render_template('EVSalesShare.html')  # This will render the top_ten.html file
 
@app.route('/ev_sales_vs_charging_ports')
def ev_sales_vs_charging_ports():
    return render_template('/ev_sales_vs_charging_ports.html')

# Route to fetch top 10 EV sales for 2023 (excluding "World" region)
@app.route('/top_ten_ev_sales')

def top_ten_ev_sales():
    # Connect to the database and fetch data
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    SELECT region, SUM(value) AS total_ev_sales
    FROM ev_adoption
    WHERE parameter = 'EV sales' 
      AND year = 2023 
      AND category = 'Historical'
      AND region != 'World'
      AND region != 'Europe'
    GROUP BY region
    ORDER BY total_ev_sales DESC
    LIMIT 10;
    """
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close()

    # Check if result is empty
    if not result:
        return jsonify({"message": "No data found"}), 404

    # Return the results as a JSON response
    top_ten = [{"region": row[0], "total_ev_sales": row[1]} for row in result]
    return jsonify(top_ten)

@app.route('/sales_charging_map')
def sales_charging_map():
    return render_template('/sales_charging_map.html')  # Make sure this file exists

@app.route('/get_ev_data', methods=['GET'])
def get_ev_data():
    year = request.args.get('year', type=int)  # Get the year from query parameters

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Query to fetch the data filtered by year
    cursor.execute("""
        SELECT region, year, ev_sales_total, charging_ports_total, latitude, longitude
        FROM ev_sales_charging_data
        WHERE year = %s;
    """, (year,))
    rows = cursor.fetchall()

    # Format the result as a list of dictionaries
    data = []
    for row in rows:
        data.append({
            'region': row[0],
            'year': row[1],
            'ev_sales': row[2],
            'charging_ports': row[3],
            'latitude': row[4],
            'longitude': row[5]
        })
    
    cursor.close()
    conn.close()

    return jsonify(data)
    
@app.route('/get_charging_station_density', methods=['GET'])
def get_charging_station_density():
    # Connect to the database
    conn = get_db_connection()
    cur = conn.cursor()

    # Query to count the number of charging stations by state
    query = """
        SELECT state, COUNT("station_name") AS station_count
        FROM charging_stations
        GROUP BY state
        ORDER BY station_count DESC;
    """

    try:
        # Execute the query
        cur.execute(query)
        result = cur.fetchall()

        # Create a dictionary to map state names to station counts
        stations_data = {row[0]: row[1] for row in result}

        # Close the connection
        cur.close()
        conn.close()

        # Return the JSON data
        return jsonify(stations_data)

    except Exception as e:
        cur.close()
        conn.close()
        return jsonify({"error": str(e)})

# Change this route to '/map' to avoid conflict with the original '/'
@app.route('/map')
def map_view():
    print("Rendering map template: state_map.html")
    return render_template('state_map.html')

@app.route('/static/data/us_states.geojson')
def geojson_file():
    return send_from_directory('static/data', 'us_states.geojson')

if __name__ == '__main__':
    app.run(debug=True)
