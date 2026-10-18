import random
from datetime import datetime, timedelta
from faker import Faker
import mysql.connector

fake = Faker()
Faker.seed(42)
random.seed(42)

def seed_database():
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="emman", 
        database="harborwing_air"
    )
    cursor = db.cursor()

    print("Clearing old data and re-seeding...")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")

    tables = [
        "reservation_payment_link", "reservation_leg_link", "flight_cost",
        "flight_leg", "flight_schedule", "reservation", "payment",
        "passenger", "booking_agent", "airport", "calendar_date",
        "reservation_status", "ticket_type", "travel_class",
        "payment_status", "aircraft_type", "airline"
    ]
    for table in tables:
        cursor.execute(f"TRUNCATE TABLE {table};")

    statuses = [f"STATUS_{i}" for i in range(1, 51)]
    ticket_types = [f"TICKET_{i}" for i in range(1, 51)]
    travel_classes = [f"CLASS_{i}" for i in range(1, 51)]
    payment_statuses = [f"PAY_STAT_{i}" for i in range(1, 51)]
    aircraft_types = [f"AC_{i}" for i in range(1, 51)]
    airlines = [f"AL_{i}" for i in range(1, 51)]

    for s in statuses: cursor.execute("INSERT INTO reservation_status VALUES (%s)", (s,))
    for t in ticket_types: cursor.execute("INSERT INTO ticket_type VALUES (%s)", (t,))
    for c in travel_classes: cursor.execute("INSERT INTO travel_class VALUES (%s)", (c,))
    for ps in payment_statuses: cursor.execute("INSERT INTO payment_status VALUES (%s)", (ps,))
    for ac in aircraft_types: cursor.execute("INSERT INTO aircraft_type VALUES (%s)", (ac,))
    for al in airlines: cursor.execute("INSERT INTO airline VALUES (%s)", (al,))

    start_date = datetime(2026, 1, 1).date()
    calendar_dates = [start_date + timedelta(days=i) for i in range(100)]
    for d in calendar_dates:
        cursor.execute("INSERT INTO calendar_date VALUES (%s, %s, %s)", (d, d.day, d.weekday() < 5))
  
    for _ in range(50):
        cursor.execute("INSERT INTO booking_agent (agent_name, additional_details) VALUES (%s, %s)",
                       (fake.company(), fake.text(50)))
        cursor.execute("INSERT INTO passenger (first_name, second_name, last_name, phone_number, email_address, address_line1, city, country) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                       (fake.first_name(), fake.first_name(), fake.last_name(), fake.phone_number(), fake.unique.email(), fake.street_address(), fake.city(), fake.country()))

    airports = [f"AP{i:02d}" for i in range(1, 51)]
    for code in airports:
        cursor.execute("INSERT INTO airport VALUES (%s, %s, %s, %s)",
                       (code, f"{fake.city()} Airport", fake.city(), "Coastal Hub"))
        
    flight_numbers = [f"HW{i:03d}" for i in range(1, 51)]
    for fn in flight_numbers:
        orig, dest = random.sample(airports, 2)
        dep = fake.date_time_this_year()
        arr = dep + timedelta(hours=random.randint(1, 6))
        cursor.execute("INSERT INTO flight_schedule VALUES (%s, %s, %s, %s, %s, %s, %s)",
                       (fn, random.choice(airlines), random.choice(aircraft_types), orig, dest, dep, arr))

    for _ in range(50):
        fn = random.choice(flight_numbers)
        orig, dest = random.sample(airports, 2)
        cursor.execute("INSERT INTO flight_leg (scheduled_flight, origin_airport, destination_airport, actual_departure_datetime, actual_arrival_datetime) VALUES (%s, %s, %s, %s, %s)",
                       (fn, orig, dest, fake.date_time_this_year(), fake.date_time_this_year()))

    for _ in range(50):
        fn = random.choice(flight_numbers)
        ac = random.choice(aircraft_types)
        v_from = random.choice(calendar_dates[:30])
        v_to = v_from + timedelta(days=30)
        cursor.execute("INSERT IGNORE INTO flight_cost VALUES (%s, %s, %s, %s, %s)",
                       (fn, ac, v_from, v_to, round(random.uniform(100, 1200), 2)))
    for _ in range(50):
        cursor.execute("INSERT INTO reservation (main_passenger_id, booking_agent_id, reservation_status_code, ticket_type_code, travel_class_code, creation_datetime, number_in_party) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                       (random.randint(1, 50), random.choice([None, random.randint(1, 50)]), random.choice(statuses), random.choice(ticket_types), random.choice(travel_classes), fake.date_time_this_year(), random.randint(1, 5)))
        cursor.execute("INSERT INTO payment (payment_status_code, payment_date, payment_amount) VALUES (%s, %s, %s)",
                       (random.choice(payment_statuses), fake.date_time_this_year(), round(random.uniform(50, 1500), 2)))

    for _ in range(60):
        cursor.execute("INSERT IGNORE INTO reservation_payment_link VALUES (%s, %s)", (random.randint(1, 50), random.randint(1, 50)))
        cursor.execute("INSERT IGNORE INTO reservation_leg_link VALUES (%s, %s)", (random.randint(1, 50), random.randint(1, 50)))

    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
    db.commit()
    print("Success! Database cleared and populated with 50+ rows per table.")
    cursor.close()
    db.close()

if __name__ == "__main__":
    seed_database()