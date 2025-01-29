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

# Route to fetch EV adoption data for the heatmap
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

    # Filter for the top 10 countries + USA + World
    total_ev_adoption_by_country = df.groupby('region')['value'].sum().reset_index()
    top_10_countries = total_ev_adoption_by_country.sort_values(by='value', ascending=False).head(10)
    
    countries_of_interest = top_10_countries['region'].tolist()
    countries_of_interest.extend(['USA', 'World'])
    
    # Filter data for the countries of interest
    df_filtered = df[df['region'].isin(countries_of_interest)]

    # Pivot the data: years as rows, countries as columns
    pivot_data = df_filtered.pivot(index='year', columns='region', values='value')

    # Convert to a dictionary for JSON response
    heatmap_data = pivot_data.to_dict(orient='index')

    return jsonify(heatmap_data)

# Route to render the heatmap template (HTML)
@app.route('/heatmap')
def heatmap():
    # Generate the heatmap
    generate_heatmap()
    
    # Return the template
    return render_template('heatmap.html')

# Function to generate the heatmap and save it as an image
def generate_heatmap():
    # Fetch data and create the dataframe for heatmap
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

    # Filter for the top 10 countries + USA + World
    total_ev_adoption_by_country = df.groupby('region')['value'].sum().reset_index()
    top_10_countries = total_ev_adoption_by_country.sort_values(by='value', ascending=False).head(10)
    
    countries_of_interest = top_10_countries['region'].tolist()
    countries_of_interest.extend(['USA', 'World'])
    
    # Filter data for the countries of interest
    df_filtered = df[df['region'].isin(countries_of_interest)]

    # Pivot the data: years as rows, countries as columns
    pivot_data = df_filtered.pivot(index='year', columns='region', values='value')

    # Generate the heatmap
    plt.figure(figsize=(14, 10))
    sns.heatmap(pivot_data, annot=True, fmt='.2f', cmap='YlGnBu', cbar_kws={'label': 'EV Adoption Percentage of Sales'}, linewidths=0.5)
    
    # Add titles and labels
    plt.title('Top 10 Countries, USA, and World with EV Adoption (2011-2023)', fontsize=16)
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Region', fontsize=12)
    
    # Save the heatmap as an image file in the static directory
    plt.xticks(rotation=45)
    image_path = os.path.join(TEMP_DIR, 'ev_adoption_heatmap.png')
    plt.savefig(image_path)
    plt.close()  # Close the plot to avoid display in console

# Route to serve the generated heatmap image
@app.route('/static/heatmaps/<filename>')
def serve_image(filename):
    return send_from_directory(TEMP_DIR, filename)

if __name__ == '__main__':
    app.run(debug=True)
