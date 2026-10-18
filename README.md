# HarborWing Air Database System

## Setup Instructions
1. Open MySQL Workbench and execute `schema.sql` to build the database, constraints, and performance indexes.
2. Open terminal in VS Code and run `python seed_database.py` to seed all 11 tables with synthetic data.
3. Execute the verification query in MySQL Workbench to confirm all tables contain 50+ rows.

## Table Relationships
* **Passenger & Reservation:** One-to-Many ($1:N$). Each reservation belongs to one main passenger to eliminate repetitive personal data.
* **Schedules & Legs:** One-to-Many ($1:N$). Schedules represent planned flight timetables, while legs track actual operational flight data separately.
* **Linking Tables:** Many-to-Many ($M:N$). `reservation_payment_link` and `reservation_leg_link` connect payments and flight legs to reservations without duplicating payment or leg records.

## Design Trade-Offs & Limitations
* Shared payment links enable split payments across reservations but do not track individual dollar allocations per reservation.
* Group party sizes are stored via `number_in_party` on the reservation rather than maintaining separate profile records for non-booking party members.
* Flight costs rely on a composite key `(scheduled_flight, aircraft_type_code, valid_from_date)` to handle rate changes over validity periods.