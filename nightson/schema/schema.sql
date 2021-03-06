-- Enabling postgis extensions

-- Enable PostGIS (includes raster)
CREATE EXTENSION postgis;
-- Enable Topology
CREATE EXTENSION postgis_topology;
-- Enable PostGIS Advanced 3D
-- and other geoprocessing algorithms
-- sfcgal not available with all distributions
CREATE EXTENSION postgis_sfcgal;
-- fuzzy matching needed for Tiger
CREATE EXTENSION fuzzystrmatch;
-- rule based standardizer
CREATE EXTENSION address_standardizer;
-- example rule data set
CREATE EXTENSION address_standardizer_data_us;
-- Enable US Tiger Geocoder
CREATE EXTENSION postgis_tiger_geocoder;


CREATE TABLE Users(
  id SERIAL PRIMARY KEY NOT NULL ,
  first_name VARCHAR(64) NOT NULL ,
  last_name VARCHAR(64) NOT NULL ,
  email VARCHAR(32) NOT NULL ,
  photo_url VARCHAR(512),
  password VARCHAR(256) NOT NULL ,
  phone VARCHAR(12) ,
  location GEOGRAPHY(POINT,4326),
  location_recorded_at TIMESTAMP,
  created_at TIMESTAMP,
  deleted_at TIMESTAMP,
  updated_at TIMESTAMP
);


CREATE TABLE Events(
  id SERIAL PRIMARY KEY NOT NULL,
  name VARCHAR(64) NOT NULL ,
  description VARCHAR(1024),
  photo_url VARCHAR(256),
  created_by_user_id INT NOT NULL,
  location GEOGRAPHY(POINT,4326) ,
  start_time TIMESTAMP NOT NULL ,
  end_time TIMESTAMP NOT NULL,
  created_at TIMESTAMP,
  deleted_at TIMESTAMP,
  updated_at TIMESTAMP,
  FOREIGN KEY (created_by_user_id) REFERENCES Users(id)
);

CREATE TABLE Sessions(
  user_id INT ,
  token VARCHAR (256) ,
  created_at TIMESTAMP ,
  expires_at TIMESTAMP ,
  FOREIGN KEY(user_id) REFERENCES Users(id)
);


CREATE TABLE UsersEvents(
  user_id INT,
  event_id INT,
  FOREIGN KEY (user_id) REFERENCES Users(id),
  FOREIGN KEY (event_id) REFERENCES Events(id)
);



-- SOME UPDATES

ALTER TABLE Events ADD COLUMN photo_url VARCHAR(256);
ALTER TABLE Events ADD COLUMN description VARCHAR(1024);


-- CREATING INDEXES
CREATE INDEX events_spatial_index ON Events USING GIST(location);
CREATE INDEX users_spatial_index ON Users USING GIST(location);
CREATE INDEX users_id_in_usersevents ON UsersEvents USING btree(user_id);
CREATE INDEX event_id_in_usersevents ON UsersEvents USING btree(event_id);
CREATE INDEX token_in_sessions ON Sessions USING btree(token);
