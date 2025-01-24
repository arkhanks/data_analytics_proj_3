

CREATE TABLE ev_adoption (
    id SERIAL PRIMARY KEY,
    region VARCHAR(255),
    category VARCHAR(255),
    parameter VARCHAR(255),
    mode VARCHAR(255),
    powertrain VARCHAR(255),
    year INT,
    unit VARCHAR(255),
    value NUMERIC
);

CREATE TABLE charging_stations (
    Station_id SERIAL PRIMARY KEY,            -- Unique identifier for each station
    station_name VARCHAR(255),
    street_address VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(50),
    zip VARCHAR(20),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    level_1_ports VARCHAR(50),
    level_2_ports DOUBLE PRECISION,
    dc_fast_ports DOUBLE PRECISION
);    
CREATE TABLE ev_sales_charging_data (
    id SERIAL PRIMARY KEY,  -- Auto-incrementing primary key
    region TEXT,
    year INT,
    ev_sales_total FLOAT,
    charging_ports_total FLOAT,
	latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION
);