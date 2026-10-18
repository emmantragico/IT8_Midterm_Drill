DROP DATABASE IF EXISTS harborwing_air;
CREATE DATABASE harborwing_air;
USE harborwing_air;

CREATE TABLE calendar_date (
    date_val DATE PRIMARY KEY,
    day_of_month INT NOT NULL CHECK (day_of_month BETWEEN 1 AND 31),
    is_business_day BOOLEAN NOT NULL
) ENGINE=InnoDB;

CREATE TABLE reservation_status (status_code VARCHAR(20) PRIMARY KEY) ENGINE=InnoDB;
CREATE TABLE ticket_type (ticket_type_code VARCHAR(20) PRIMARY KEY) ENGINE=InnoDB;
CREATE TABLE travel_class (travel_class_code VARCHAR(20) PRIMARY KEY) ENGINE=InnoDB;
CREATE TABLE payment_status (payment_status_code VARCHAR(20) PRIMARY KEY) ENGINE=InnoDB;
CREATE TABLE aircraft_type (aircraft_type_code VARCHAR(20) PRIMARY KEY) ENGINE=InnoDB;
CREATE TABLE airline (airline_code VARCHAR(10) PRIMARY KEY) ENGINE=InnoDB;

CREATE TABLE booking_agent (
    agent_id INT AUTO_INCREMENT PRIMARY KEY,
    agent_name VARCHAR(100) NOT NULL,
    additional_details TEXT
) ENGINE=InnoDB;

CREATE TABLE passenger (
    passenger_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    second_name VARCHAR(50),
    last_name VARCHAR(50) NOT NULL,
    phone_number VARCHAR(25) NOT NULL,
    email_address VARCHAR(100) NOT NULL UNIQUE,
    address_line1 VARCHAR(100) NOT NULL,
    address_line2 VARCHAR(100),
    city VARCHAR(50) NOT NULL,
    state_province_county VARCHAR(50),
    country VARCHAR(50) NOT NULL,
    other_details TEXT
) ENGINE=InnoDB;

CREATE TABLE reservation (
    reservation_id INT AUTO_INCREMENT PRIMARY KEY,
    main_passenger_id INT NOT NULL,
    booking_agent_id INT NULL,
    reservation_status_code VARCHAR(20) NOT NULL,
    ticket_type_code VARCHAR(20) NOT NULL,
    travel_class_code VARCHAR(20) NOT NULL,
    creation_datetime DATETIME NOT NULL,
    number_in_party INT NOT NULL CHECK (number_in_party > 0),
    FOREIGN KEY (main_passenger_id) REFERENCES passenger(passenger_id),
    FOREIGN KEY (booking_agent_id) REFERENCES booking_agent(agent_id),
    FOREIGN KEY (reservation_status_code) REFERENCES reservation_status(status_code),
    FOREIGN KEY (ticket_type_code) REFERENCES ticket_type(ticket_type_code),
    FOREIGN KEY (travel_class_code) REFERENCES travel_class(travel_class_code)
) ENGINE=InnoDB;

CREATE TABLE payment (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    payment_status_code VARCHAR(20) NOT NULL,
    payment_date DATETIME NOT NULL,
    payment_amount DECIMAL(10, 2) NOT NULL CHECK (payment_amount > 0.00),
    FOREIGN KEY (payment_status_code) REFERENCES payment_status(payment_status_code)
) ENGINE=InnoDB;

CREATE TABLE airport (
    airport_code VARCHAR(5) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(100) NOT NULL,
    other_details TEXT
) ENGINE=InnoDB;

CREATE TABLE flight_schedule (
    flight_number VARCHAR(10) PRIMARY KEY,
    airline_code VARCHAR(10) NOT NULL,
    usual_aircraft_type_code VARCHAR(20) NOT NULL,
    origin_airport VARCHAR(5) NOT NULL,
    destination_airport VARCHAR(5) NOT NULL,
    scheduled_departure_datetime DATETIME NOT NULL,
    scheduled_arrival_datetime DATETIME NOT NULL,
    CONSTRAINT chk_schedule_airports CHECK (origin_airport <> destination_airport),
    FOREIGN KEY (airline_code) REFERENCES airline(airline_code),
    FOREIGN KEY (usual_aircraft_type_code) REFERENCES aircraft_type(aircraft_type_code),
    FOREIGN KEY (origin_airport) REFERENCES airport(airport_code),
    FOREIGN KEY (destination_airport) REFERENCES airport(airport_code)
) ENGINE=InnoDB;

CREATE TABLE flight_leg (
    leg_id INT AUTO_INCREMENT PRIMARY KEY,
    scheduled_flight VARCHAR(10) NOT NULL,
    origin_airport VARCHAR(5) NOT NULL,
    destination_airport VARCHAR(5) NOT NULL,
    actual_departure_datetime DATETIME NULL,
    actual_arrival_datetime DATETIME NULL,
    CONSTRAINT chk_leg_airports CHECK (origin_airport <> destination_airport),
    FOREIGN KEY (scheduled_flight) REFERENCES flight_schedule(flight_number),
    FOREIGN KEY (origin_airport) REFERENCES airport(airport_code),
    FOREIGN KEY (destination_airport) REFERENCES airport(airport_code)
) ENGINE=InnoDB;

CREATE TABLE flight_cost (
    scheduled_flight VARCHAR(10) NOT NULL,
    aircraft_type_code VARCHAR(20) NOT NULL,
    valid_from_date DATE NOT NULL,
    valid_to_date DATE NOT NULL,
    cost_amount DECIMAL(10, 2) NOT NULL CHECK (cost_amount >= 0.00),
    PRIMARY KEY (scheduled_flight, aircraft_type_code, valid_from_date),
    CONSTRAINT chk_validity_dates CHECK (valid_to_date >= valid_from_date),
    FOREIGN KEY (scheduled_flight) REFERENCES flight_schedule(flight_number),
    FOREIGN KEY (aircraft_type_code) REFERENCES aircraft_type(aircraft_type_code),
    FOREIGN KEY (valid_from_date) REFERENCES calendar_date(date_val),
    FOREIGN KEY (valid_to_date) REFERENCES calendar_date(date_val)
) ENGINE=InnoDB;

CREATE TABLE reservation_payment_link (
    reservation_id INT NOT NULL,
    payment_id INT NOT NULL,
    PRIMARY KEY (reservation_id, payment_id),
    FOREIGN KEY (reservation_id) REFERENCES reservation(reservation_id),
    FOREIGN KEY (payment_id) REFERENCES payment(payment_id)
) ENGINE=InnoDB;

CREATE TABLE reservation_leg_link (
    reservation_id INT NOT NULL,
    leg_id INT NOT NULL,
    PRIMARY KEY (reservation_id, leg_id),
    FOREIGN KEY (reservation_id) REFERENCES reservation(reservation_id),
    FOREIGN KEY (leg_id) REFERENCES flight_leg(leg_id)
) ENGINE=InnoDB;

CREATE INDEX idx_reservation_passenger ON reservation(main_passenger_id);
CREATE INDEX idx_leg_schedule ON flight_leg(scheduled_flight);
CREATE INDEX idx_flight_cost_dates ON flight_cost(valid_from_date, valid_to_date);