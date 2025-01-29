import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from flask import Flask, send_file, Response
import psycopg2
import io
from io import BytesIO

# Read your CSV data
df = pd.read_csv('../../datasets/ev_data.csv')

# Filter for relevant 'parameter' values
ev_adoption_data = df[df['parameter'].isin(['EV stock share'])]

# Filter by unit (e.g., percent)
ev_adoption_data = ev_adoption_data[ev_adoption_data['unit'].isin(['percent'])]

# Further filter data for years 2011-2023
ev_adoption_data = ev_adoption_data[(ev_adoption_data['year'] >= 2011) & (ev_adoption_data['year'] <= 2023)]

# Aggregate duplicates by taking the mean of the 'value' for each combination of region, year, and parameter
ev_adoption_data = ev_adoption_data.groupby(['region', 'year', 'parameter'], as_index=False)['value'].mean()

# Only keep relevant columns
ev_adoption_data = ev_adoption_data[['region', 'year', 'parameter', 'value']]

# Pivot the data: rows = region, columns = year, values = EV adoption percentage
pivot_data = ev_adoption_data.pivot(index='region', columns='year', values='value')

# Generate and Save the Heatmap Chart to a BytesIO object
def generate_and_save_image():
    plt.figure(figsize=(14, 10))  # Adjust figure size as necessary
    sns.heatmap(pivot_data, annot=True, fmt='.2f', cmap='YlGnBu', cbar_kws={'label': 'EV Adoption Percentage of Sales'}, linewidths=0.5)

    # Add titles and labels
    plt.title('EV Adoption by Region and Year', fontsize=16)
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Region', fontsize=12)

    # Save the plot to a BytesIO object
    img_bytes = io.BytesIO()
    plt.savefig(img_bytes, format='png')
    img_bytes.seek(0)  # Reset the pointer to the start of the BytesIO object

    # Connect to the database and insert the image data
    conn = psycopg2.connect(
        dbname='ev_database', 
        user='postgres', 
        password='postgres', 
        host='localhost', 
        port='5432'
    )
    cur = conn.cursor()
    cur.execute("INSERT INTO chart_images (name, image_data) VALUES (%s, %s)", 
                ('ev_adoption_all_regions', psycopg2.Binary(img_bytes.read())))
    conn.commit()
    cur.close()
    conn.close()

# Flask app setup
app = Flask(__name__)

# Route to generate and save the chart image
@app.route('/generate_image', methods=['GET'])
def generate_image():
    generate_and_save_image()
    return "Image generated and saved to database!"

# Route to serve the chart image from the database
@app.route('/chart/<chart_name>', methods=['GET'])
def serve_chart(chart_name):
    conn = psycopg2.connect(
        dbname='ev_database', 
        user='postgres', 
        password='postgres', 
        host='localhost', 
        port='5432'
    )
    cur = conn.cursor()

    # Query the database for the image data
    cur.execute("SELECT image_data FROM chart_images WHERE name = %s", (chart_name,))
    image_data = cur.fetchone()

    cur.close()
    conn.close()

    if image_data:
        # Convert the binary data into a byte stream and return it as a PNG image
        return Response(image_data[0], mimetype='image/png')
    else:
        print("Image not found!")
        return "Image not found", 404
if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
