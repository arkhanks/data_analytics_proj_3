

CREATE TABLE ev_adoption (
    -- id SERIAL PRIMARY KEY,
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
    -- Station_id SERIAL PRIMARY KEY,
    station_name VARCHAR(255),
    street_address VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(50),
    zip VARCHAR(20),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    level_1_ports DOUBLE PRECISION,
    level_2_ports DOUBLE PRECISION,
    dc_fast_ports DOUBLE PRECISION,
    total_charging_ports DOUBLE PRECISION
);