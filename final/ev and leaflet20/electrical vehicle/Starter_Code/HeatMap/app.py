import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from flask import Flask, jsonify, render_template, send_from_directory
import psycopg2
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS globally for all routes

# Directory to save the heatmap image temporarily
TEMP_DIR = "static/heatmaps"
os.makedirs(TEMP_DIR, exist_ok=True)

# Database connection function
def get_db_connection():
    conn = psycopg2.connect(
        dbname="ev_database",  # Database name
        user="postgres",       # Username
        password="postgres",   # Password
        host="localhost",      # Host
        port="5432"            # Port
    )
    return conn

# Route to fetch all EV adoption data for the heatmap
@app.route('/api/v1.0/ev_adoption_data', methods=['GET'])
def get_ev_adoption_data():
    conn = get_db_connection()
    query = """
        SELECT region, year, parameter, value
        FROM ev_adoption
        WHERE year >= 2011 AND year <= 2023
        AND parameter = 'EV stock share' AND unit = 'percent'
    """
    # Execute query
    df = pd.read_sql(query, conn)
    conn.close()
    
    # Aggregate data to avoid duplicates
    df = df.groupby(['region', 'year', 'parameter'], as_index=False)['value'].mean()

    # Convert to a dictionary for JSON response
    heatmap_data = df.to_dict(orient='records')

    return jsonify(heatmap_data)

# Route to generate and serve heatmap for all regions
@app.route('/generate_all_regions_heatmap')
def generate_all_regions_heatmap():
    print('Generating heatmap for all regions...')
    conn = get_db_connection()
    query = """
        SELECT region, year, parameter, value
        FROM ev_adoption
        WHERE year >= 2011 AND year <= 2023
        AND parameter = 'EV stock share' AND unit = 'percent'
    """
    df = pd.read_sql(query, conn)
    conn.close()

    # Aggregate data to avoid duplicates
    df = df.groupby(['region', 'year', 'parameter'], as_index=False)['value'].mean()

    print('Data loaded successfully')
    print(df.head())

    # Pivot the data for all regions
    pivot_data = df.pivot(index='region', columns='year', values='value')

    # Generate the heatmap for all regions
    plt.figure(figsize=(14, 10))
    sns.heatmap(pivot_data, annot=True, fmt='.2f', cmap='YlGnBu', cbar_kws={'label': 'EV Adoption Percentage of Sales'}, linewidths=0.5)
    
    # Add titles and labels
    plt.title('EV Adoption by Region and Year (All Regions)', fontsize=16)
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Region', fontsize=12)
    
    # Debug: Check if directory exists and is writable
    print(f"Saving heatmap to: {TEMP_DIR}")
    print(f"Does the directory exist? {os.path.exists(TEMP_DIR)}")

    # Save the heatmap as an image
    image_path = os.path.join(TEMP_DIR, 'ev_adoption_all_regions_heatmap.png')
    print(f"Image will be saved at: {image_path}")
    plt.xticks(rotation=45)
    try:
        plt.savefig(image_path)
        print(f"Heatmap image successfully saved at {image_path}")
    except Exception as e:
        print(f"Error saving heatmap: {e}")
    finally:
        plt.close()  # Close the plot to avoid display in console

    return render_template('heatmap.html', image_url=image_path)

    
# Route to generate and serve heatmap for top 10 countries, USA, and World
@app.route('/generate_top_10_heatmap')
def generate_top_10_heatmap():
    print('Generating heatmap for top 10 countries, USA, and World...')
    
    conn = get_db_connection()
    query = """
        SELECT region, year, parameter, value
        FROM ev_adoption
        WHERE year >= 2011 AND year <= 2023
        AND parameter = 'EV stock share' AND unit = 'percent'
    """
    df = pd.read_sql(query, conn)
    conn.close()

    # Aggregate data to avoid duplicates
    df = df.groupby(['region', 'year', 'parameter'], as_index=False)['value'].mean()

    # Sum EV adoption by region across all years
    total_ev_adoption_by_country = df.groupby('region')['value'].sum().reset_index()

    # Get the top 10 countries, USA, and World
    top_10_countries = total_ev_adoption_by_country.sort_values(by='value', ascending=False).head(10)
    countries_of_interest = top_10_countries['region'].tolist()
    countries_of_interest.extend(['USA', 'World'])  # Add 'USA' and 'World' to the list
    
    # Filter data for these countries
    df_filtered = df[df['region'].isin(countries_of_interest)]

    # Pivot the data for top 10 countries + USA + World
    pivot_data = df_filtered.pivot(index='year', columns='region', values='value')

    # Generate the heatmap for top 10 countries, USA, and World
    plt.figure(figsize=(14, 10))
    sns.heatmap(pivot_data, annot=True, fmt='.2f', cmap='YlGnBu', cbar_kws={'label': 'EV Adoption Percentage of Sales'}, linewidths=0.5)

    # Add titles and labels
    plt.title('Top 10 Countries, USA, and World with EV Adoption (2011-2023)', fontsize=16)
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Region', fontsize=12)

    # Save the heatmap as an image
    image_path = os.path.join(TEMP_DIR, 'ev_adoption_top_10_heatmap.png')
    plt.xticks(rotation=45)
    plt.savefig(image_path)
    plt.close()  # Close the plot to avoid display in console
    
    return render_template('heatmap.html', image_url=image_path)

# Route to serve the generated heatmap image
@app.route('/static/heatmaps/<filename>')
def serve_image(filename):
    return send_from_directory(TEMP_DIR, filename)

# Route to render the heatmap template (HTML)
@app.route('/heatmap')
def heatmap():
    return render_template('heatmap.html')

if __name__ == '__main__':
    app.run(debug=True)
