

-- Drop tables if they already exist to reset the schema
DROP TABLE IF EXISTS ev_adoption;
DROP TABLE IF EXISTS charging_stations;
DROP TABLE IF EXISTS ev_sales_charging_data;

-- Create schema for the Electric Vehicle Adoption Trends and Charging Stations database
-- Table to import is named as ev_data.csv
-- Table to store EV adoption data
CREATE TABLE ev_adoption (
    id SERIAL PRIMARY KEY,         -- Auto-incrementing primary key
    region VARCHAR(255),           -- Region or country
    category VARCHAR(255),         -- Data category (e.g., historical,projection)
    parameter VARCHAR(255),        -- Specific parameter (e.g., number of EVs, market share)
    mode VARCHAR(255),             -- Mode of transportation (e.g. cars,trucks)
    powertrain VARCHAR(255),       -- Type of EV (e.g., BEV, PHEV)
    year INT,                      -- Year of the data point
    unit VARCHAR(255),             -- Unit of measurement (e.g., percentage, number)
    value NUMERIC                  -- Data value
);
--Table to import is named as cleaned_charging_stations_filtered.csv
-- Table to store charging station details
CREATE TABLE charging_stations (
    station_id SERIAL PRIMARY KEY,        -- Unique identifier for each charging station
    station_name VARCHAR(255),           -- Name of the charging station
    street_address VARCHAR(255),         -- Street address
    city VARCHAR(100),                   -- City where the station is located
    state VARCHAR(50),                   -- State where the station is located
    zip VARCHAR(20),                     -- ZIP code
    latitude DOUBLE PRECISION,           -- Latitude for geospatial mapping
    longitude DOUBLE PRECISION,          -- Longitude for geospatial mapping
    level_1_ports DOUBLE PRECISION,      -- Number of Level 1 charging ports
    level_2_ports DOUBLE PRECISION,      -- Number of Level 2 charging ports
    dc_fast_ports DOUBLE PRECISION       -- Number of DC fast charging ports
);
--Table to import is named as ev_sales_and_charging_data.csv
-- Table to store combined EV sales and charging station data
CREATE TABLE ev_sales_charging_data (
    id SERIAL PRIMARY KEY,           -- Auto-incrementing primary key
    region TEXT,                     -- Region or country
    year INT,                        -- Year of the data point
    ev_sales_total FLOAT,            -- Total EV sales
    charging_ports_total FLOAT,      -- Total number of charging ports
    latitude DOUBLE PRECISION,       -- Latitude for geospatial mapping
    longitude DOUBLE PRECISION       -- Longitude for geospatial mapping
);

-- Sample SELECT statement for testing the schema
SELECT * FROM ev_sales_charging_data;