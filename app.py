import os
from flask import Flask, render_template_string, request, redirect, url_for, flash
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = "harborwing_secret_key"

def get_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "harborwing_air"),
        port=int(os.getenv("DB_PORT", 3306))
    )

BASE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>HarborWing Air - CRUD Portal</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f4f6f9; }
        h1, h2 { color: #1e3a8a; }
        nav a { margin-right: 15px; font-weight: bold; text-decoration: none; color: #2563eb; }
        .card { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #e2e8f0; }
        .alert { padding: 10px; border-radius: 5px; margin-bottom: 15px; }
        .success { background-color: #d1fae5; color: #065f46; }
        .error { background-color: #fee2e2; color: #991b1b; }
        input, select { padding: 6px; margin: 5px 0; }
        button { background-color: #2563eb; color: white; border: none; padding: 8px 12px; cursor: pointer; border-radius: 4px; }
        button.danger { background-color: #dc2626; }
    </style>
</head>
<body>
    <h1>✈️ HarborWing Air Employee Portal</h1>
    <nav>
        <a href="/">Dashboard & Passengers</a>
        <a href="/reservation">View Reservation</a>
        <a href="/manage-links">Manage Links</a>
        <a href="/demo-error">Demonstrate Error</a>
    </nav>
    <hr>
    
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        {% for category, message in messages %}
          <div class="alert {{ category }}">{{ message }}</div>
        {% endfor %}
      {% endif %}
    {% endwith %}

    {{ content | safe }}
</body>
</html>
"""

@app.route("/")
def index():
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM passenger ORDER BY passenger_id DESC LIMIT 10;")
        passengers = cursor.fetchall()
        conn.close()
    except Exception as e:
        passengers = []
        flash(f"Database connection warning: {e}", "error")

    content = """
    <div class="card">
        <h2>1. Passengers Management</h2>
        <h3>Add New Passenger</h3>
        <form action="/add-passenger" method="POST">
            <input type="text" name="first_name" placeholder="First Name" required>
            <input type="text" name="last_name" placeholder="Last Name" required>
            <input type="email" name="email" placeholder="Email" required>
            <input type="text" name="phone" placeholder="Phone Number">
            <button type="submit">Create Passenger</button>
        </form>
    </div>

    <div class="card">
        <h3>Existing Passengers</h3>
        <table>
            <tr><th>ID</th><th>Name</th><th>Email</th><th>Phone</th><th>Actions</th></tr>
            {% for p in passengers %}
            <tr>
                <td>{{ p.passenger_id }}</td>
                <td>{{ p.first_name }} {{ p.last_name }}</td>
                <td>{{ p.email_address }}</td>
                <td>{{ p.phone_number }}</td>
                <td>
                    <form action="/update-passenger/{{ p.passenger_id }}" method="POST" style="display:inline;">
                        <input type="text" name="phone" placeholder="New Phone" required>
                        <button type="submit">Update</button>
                    </form>
                    <form action="/delete-passenger/{{ p.passenger_id }}" method="POST" style="display:inline;" onsubmit="return confirm('Are you sure you want to delete this record?');">
                        <button type="submit" class="danger">Delete</button>
                    </form>
                </td>
            </tr>
            {% endfor %}
        </table>
    </div>
    """
    return render_template_string(BASE_TEMPLATE.replace("{{ content | safe }}", content), passengers=passengers)

@app.route("/add-passenger", methods=["POST"])
def add_passenger():
    fn = request.form["first_name"]
    ln = request.form["last_name"]
    email = request.form["email"]
    phone = request.form["phone"]
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SHOW COLUMNS FROM passenger;")
        columns_info = cursor.fetchall()
        
        input_data = {
            'first_name': fn,
            'last_name': ln,
            'email_address': email,
            'phone_number': phone,
            'address_line1': '123 Main St',
            'address_line2': '',
            'city': 'Default City',
            'state_province': 'State',
            'postal_code': '00000',
            'country': 'USA'
        }
        
        insert_cols = []
        insert_vals = []
        
        for col in columns_info:
            field = col['Field']
            is_auto_inc = 'auto_increment' in col['Extra']
            is_nullable = col['Null'] == 'YES'
            has_default = col['Default'] is not None
            
            if is_auto_inc:
                continue
                
            if field in input_data:
                insert_cols.append(field)
                insert_vals.append(input_data[field])
            elif not is_nullable and not has_default:
                insert_cols.append(field)
                insert_vals.append("N/A")
                
        placeholders = ", ".join(["%s"] * len(insert_cols))
        col_names = ", ".join(insert_cols)
        
        query = f"INSERT INTO passenger ({col_names}) VALUES ({placeholders})"
        
        cursor_raw = conn.cursor()
        cursor_raw.execute(query, insert_vals)
        conn.commit()
        flash(f"Passenger {fn} {ln} successfully created!", "success")
    except Exception as e:
        flash(f"Error creating passenger: {e}", "error")
    finally:
        conn.close()
    return redirect("/")

@app.route("/update-passenger/<int:pid>", methods=["POST"])
def update_passenger(pid):
    phone = request.form["phone"]
    conn = get_db()
    cursor = conn.cursor()
    try:
        query = "UPDATE passenger SET phone_number = %s WHERE passenger_id = %s"
        cursor.execute(query, (phone, pid))
        conn.commit()
        flash(f"Phone updated for Passenger ID {pid}", "success")
    except Exception as e:
        flash(f"Update failed: {e}", "error")
    finally:
        conn.close()
    return redirect("/")

@app.route("/delete-passenger/<int:pid>", methods=["POST"])
def delete_passenger(pid):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM passenger WHERE passenger_id = %s", (pid,))
        conn.commit()
        if cursor.rowcount > 0:
            flash(f"Passenger ID {pid} successfully deleted!", "success")
        else:
            flash(f"Passenger ID {pid} not found.", "error")
    except mysql.connector.Error as err:
        flash(f"Cannot delete passenger (referenced in active reservations): {err}", "error")
    finally:
        conn.close()
    return redirect("/")

@app.route("/reservation")
def view_reservation():
    res_id = request.args.get("res_id", 1)
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    # 1. First check if a reservation exists with this ID
    res_info = None
    try:
        cursor.execute("""
            SELECT r.reservation_id, p.first_name, p.last_name, p.email_address
            FROM reservation r
            LEFT JOIN passenger p ON r.main_passenger_id = p.passenger_id
            WHERE r.reservation_id = %s
        """, (res_id,))
        res_info = cursor.fetchone()
    except Exception:
        pass

    # 2. Fallback: Check if searching by passenger_id instead
    if not res_info:
        try:
            cursor.execute("""
                SELECT %s AS reservation_id, p.first_name, p.last_name, p.email_address
                FROM passenger p
                WHERE p.passenger_id = %s
            """, (res_id, res_id))
            res_info = cursor.fetchone()
        except Exception:
            pass

    # 3. Query linked legs safely
    legs = []
    try:
        cursor.execute("""
            SELECT fl.flight_leg_id, fl.leg_number
            FROM reservation_leg_link rll
            JOIN flight_leg fl ON rll.flight_leg_id = fl.flight_leg_id
            WHERE rll.reservation_id = %s
        """, (res_id,))
        legs = cursor.fetchall()
    except Exception:
        pass

    # 4. Query linked payments safely
    payments = []
    try:
        cursor.execute("""
            SELECT pay.payment_id, pay.payment_amount, pay.payment_status
            FROM reservation_payment_link rpl
            JOIN payment pay ON rpl.payment_id = pay.payment_id
            WHERE rpl.reservation_id = %s
        """, (res_id,))
        payments = cursor.fetchall()
    except Exception:
        pass
        
    conn.close()
    
    content = f"""
    <div class="card">
        <h2>View Reservation Details</h2>
        <form action="/reservation" method="GET">
            <input type="number" name="res_id" value="{res_id}" placeholder="ID">
            <button type="submit">Search</button>
        </form>
    </div>
    """
    
    if res_info:
        passenger_name = f"{res_info.get('first_name', '')} {res_info.get('last_name', '')}".strip()
        email = res_info.get('email_address', 'N/A')
        
        content += f"""
        <div class="card">
            <h3>Reservation / Record #{res_info['reservation_id']}</h3>
            <p><strong>Passenger:</strong> {passenger_name if passenger_name else 'N/A'} ({email})</p>
            
            <h4>Linked Flight Legs</h4>
            <ul>{"".join([f"<li>Leg #{l.get('leg_number', l['flight_leg_id'])} (ID: {l['flight_leg_id']})</li>" for l in legs]) or "<li>No legs linked</li>"}</ul>
            
            <h4>Linked Payments</h4>
            <ul>{"".join([f"<li>Payment ID {p['payment_id']} - ${p['payment_amount']} ({p['payment_status']})</li>" for p in payments]) or "<li>No payments linked</li>"}</ul>
        </div>
        """
    else:
        content += '<div class="card"><p class="error">Reservation not found.</p></div>'
        
    return render_template_string(BASE_TEMPLATE.replace("{{ content | safe }}", content))

@app.route("/manage-links")
def manage_links():
    content = """
    <div class="card">
        <h2>Unlink Leg from Reservation (Preserves Underlying Records)</h2>
        <form action="/unlink-leg" method="POST">
            <input type="number" name="res_id" placeholder="Reservation ID" required>
            <input type="number" name="leg_id" placeholder="Flight Leg ID" required>
            <button type="submit" class="danger">Unlink Leg</button>
        </form>
    </div>
    """
    return render_template_string(BASE_TEMPLATE.replace("{{ content | safe }}", content))

@app.route("/unlink-leg", methods=["POST"])
def unlink_leg():
    res_id = request.form.get("res_id") or request.form.get("reservation_id")
    leg_id = request.form.get("leg_id") or request.form.get("flight_leg_id")
    
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SHOW COLUMNS FROM reservation_leg_link;")
        cols = [c[0] for c in cursor.fetchall()]
        leg_col = "leg_id" if "leg_id" in cols else "flight_leg_id"
        
        query = f"DELETE FROM reservation_leg_link WHERE reservation_id = %s AND {leg_col} = %s"
        cursor.execute(query, (res_id, leg_id))
        conn.commit()
        
        if cursor.rowcount > 0:
            flash(f"Successfully removed link between Reservation {res_id} and Leg {leg_id}. Original Flight Leg record remains intact!", "success")
        else:
            flash("No matching link found.", "error")
    except Exception as e:
        flash(f"Unlink failed: {e}", "error")
    finally:
        conn.close()
    return redirect("/manage-links")

@app.route("/demo-error")
def demo_error():
    conn = get_db()
    cursor = conn.cursor()
    try:
        # Attempt to insert a child record with a non-existent foreign key to trigger MySQL Error 1452
        cursor.execute("INSERT INTO reservation (reservation_id, main_passenger_id) VALUES (99999, 99999);")
        conn.commit()
        flash("Action succeeded unexpectedly.", "success")
    except Exception as e:
        # Gracefully handle the foreign key exception
        flash(f"Database Error: Foreign key constraint failed ({e})", "error")
    finally:
        conn.close()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True, port=5000)