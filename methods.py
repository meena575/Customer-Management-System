import streamlit as st
import mysql.connector
from streamlit_option_menu import option_menu
from st_aggrid import AgGrid, JsCode
from st_aggrid.grid_options_builder import GridOptionsBuilder
from mysql.connector import Error
import bcrypt
import pandas as pd
import re
import datetime
def create_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='client_management',
            user='root',
            password='12345678'
        )
    except Error as e:
        st.error(f"Error: {e}")
    return connection


def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def authenticate_user(username,password, role):
    try:
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""SELECT * FROM users
            WHERE username = %s AND role = %s""", (username, role))
        user = cursor.fetchone()
        if user is None:
            return None
        if 'password' not in user:
            return None
        if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            return user
        else:
            return None
    except Error as e:
        return None
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def authenticate_user_admin(username, password):
    return authenticate_user(username, password, 'admin')

def authenticate_user_client(username, password):
    return authenticate_user(username, password,'client')


def authenticate_user_staff(username, password):
    return authenticate_user(username, password, 'user')

def fetch_data(query, params=None):
    conn = create_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result
    return []
def is_valid_contact_number(contact_number):
    pattern = re.compile(r'^\+91\d{10}$')
    
    if pattern.match(contact_number):
        return True
    else:
        return False

def validate_email(email):
    # Regular expression to match email addresses
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None
def get_total_clients():
    query = "SELECT COUNT(*) AS total_clients FROM users WHERE role='client'"
    result = fetch_data(query)
    return result[0]['total_clients'] if result else 0

def get_total_services():
    query = "SELECT COUNT(*) AS total_services FROM services"
    result = fetch_data(query)
    return result[0]['total_services'] if result else 0

def get_total_sales():
    query = "SELECT SUM(total_amount) AS total_sales FROM invoices WHERE status='Paid'"
    result = fetch_data(query)
    return result[0]['total_sales'] if result else 0

def get_total_users():
    query = "SELECT count(id) AS total_users FROM users where role='user'"
    result = fetch_data(query)
    return result[0]['total_users'] if result else 0

def get_total_invoices():
    query = "SELECT count(id) AS total_invoices FROM invoices"
    result = fetch_data(query)
    return result[0]['total_invoices'] if result else 0



def get_services():
    try:
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM services")
        services = cursor.fetchall()
        return services
    except Error as e:
        print(f"Error: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()
def get_services_for_client():
    try:
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM services WHERE status='Active'")
        services = cursor.fetchall()
        return services
    except Error as e:
        print(f"Error: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

def get_service(service_id):
    try:
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM services WHERE id = %s", (service_id,))
        service = cursor.fetchone()
        return service
    except Error as e:
        print(f"Error: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

def create_service(service_name, description, price, status):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute(
            """INSERT INTO services (date_created, service_name,
            description, price, status) VALUES (%s, %s, %s, %s, %s)""",
            (datetime.datetime.now(), service_name, description, price, status)
        )
        connection.commit()
    except Error as e:
        print(f"Error: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

def update_service(service_id, service_name, description, price, status):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE services SET service_name = %s, description = %s, price = %s, status = %s WHERE id = %s",
            (service_name, description, price, status, service_id)
        )
        connection.commit()
    except Error as e:
        print(f"Error: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

def delete_service(service_id):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM services WHERE id = %s", (service_id,))
        connection.commit()
    except Error as e:
        print(f"Error: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

#client list
# Create a new client

def check_existing_entries(email, username):
    connection = create_connection()
    if connection is None:
        return False

    cursor = connection.cursor()

    try:
        

        # Check if email or username already exists in users table
        cursor.execute("SELECT id FROM users WHERE email = %s OR username = %s", (email, username))
        user_exists = cursor.fetchone()

        return user_exists is not None
    except mysql.connector.Error as err:
        st.error(f"Database error while checking existing entries: {err}")
        print(f"Database error: {err}")
        return True
    finally:
        cursor.close()
        connection.close()

def create_client_user(name, email, phone, address, username, password):
    connection = create_connection()
    if connection is None:
        return

    cursor = connection.cursor()
    hashed_password = hash_password(password)

    if check_existing_entries(email, username):
        st.error("Email or username already exists.")
        return

    try:
        connection.start_transaction()

        # Insert into users table with role admin
        user_query = """
            INSERT INTO users (fullname, email, username, password, role, phone_number, address)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        print(f"Executing user query: {user_query} with values: {name, email, username, hashed_password, 'client', phone, address}")
        cursor.execute(user_query, (name, email, username, hashed_password, 'client', phone, address))

        connection.commit()
        st.success("Admin user added successfully!")
    except mysql.connector.Error as err:
        connection.rollback()
        st.error(f"Database error: {err}")
        print(f"Database error: {err}")  # Print the error for debugging
    finally:
        cursor.close()
        connection.close()
def get_clients():
    try:
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)  
        cursor.execute("SELECT id,fullname ,email,phone_number,address,username FROM users WHERE role='client'")
        clients = cursor.fetchall()
        return clients
    except Error as e:
        print(f"Error: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

def get_client(client_id):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id = %s", (client_id,))
        client = cursor.fetchone()
        return client
    except Error as e:
        print(f"Error: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

def get_user_id(username):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        user_id = cursor.fetchone()
        return user_id
    except Error as e:
        print(f"Error: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

# Update a client
def update_client(id, client_name, email, phone_number, address,username):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE users
            SET fullname = %s, email = %s, phone_number = %s, address = %s,username=%s
            WHERE id = %s
        """, (client_name, email, phone_number, address,username ,id))
        connection.commit()
    except Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        connection.close()
def delete_client(client_id):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        
        # Delete dependent records in client_services table
        cursor.execute("DELETE FROM client_services WHERE user_id = %s", (client_id,))
        
        cursor.execute("DELETE FROM invoices WHERE user_id = %s", (client_id,))

        cursor.execute("DELETE FROM users WHERE id = %s", (client_id,))
        
        connection.commit()
    except Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        connection.close()
def create_invoice(user_id, invoice_date, due_date, total_amount, status):
    try:
        connection = create_connection()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO invoices (client_id, invoice_date, due_date, total_amount, status)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, invoice_date, due_date, total_amount, status))
        
        connection.commit()
        return cursor.lastrowid  

    except mysql.connector.Error as e:
        print(f"MySQL Error: {e}")
    except Exception as ex:
        print(f"Error: {ex}")
    finally:
        cursor.close()
        connection.close()
def calculate_total_amount(client_id):
    try:
        connection = create_connection()
        cursor = connection.cursor()

        # Fetch prices of services for the given client
        cursor.execute("""
            SELECT s.price
            FROM client_services cs
            JOIN services s ON cs.service_id = s.id
            WHERE cs.client_id = %s
        """, (client_id,))
        
        prices = cursor.fetchall()
        total_amount = sum(price[0] for price in prices)
        return total_amount

    except mysql.connector.Error as e:
        print(f"MySQL Error: {e}")
    except Exception as ex:
        print(f"Error: {ex}")
    finally:
        cursor.close()
        connection.close()

def get_invoice(invoice_id):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM invoices WHERE id = %s", (invoice_id,))
        invoice = cursor.fetchone()
        return invoice
    except Error as e:
        print(f"Error: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

def update_invoice(invoice_id, status):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE invoices
            SET  status = %s
            WHERE id = %s
        """, ( status, invoice_id))
        connection.commit()
    except Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        connection.close()

def delete_invoice(invoice_id):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM invoices WHERE id = %s", (invoice_id,))
        connection.commit()
    except Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        connection.close()

#staff list



#Assign services to client
def get_assigned_services(client_id):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        query = """
            SELECT services.id, services.service_name,services.price
            FROM client_services
            JOIN services ON client_services.service_id = services.id
            WHERE client_services.client_id = %s
        """
        cursor.execute(query, (client_id,))
        assigned_services = cursor.fetchall()
        return [{'id': row[0], 'service_name': row[1],'price':row[2]} for row in assigned_services]
    except Error as e:
        print(f"Error: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def delete_assigned_service(client_id, service_id):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        query = "DELETE FROM client_services WHERE client_id = %s AND service_id = %s"
        cursor.execute(query, (client_id, service_id))
        connection.commit()
        cursor.close() 
        connection.close() 
    except Error as e:
        print(f"Error: {e}")

def assign_service_to_client(client_id, service_id):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        query = "INSERT INTO client_services (user_id, service_id) VALUES (%s, %s)"
        values = (client_id, service_id)

        cursor.execute(query, values)
        connection.commit()
    except Error as e:
        print(f"Error: {e}")



def update_password(password,username):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    connection = create_connection()
    cursor = connection.cursor()
    query = "UPDATE users SET password = %s WHERE username = %s"
    cursor.execute(query, (hashed_password.decode('utf-8'), username))
    connection.commit()
    cursor.close()
    connection.close()

def get_user_details(username):
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)  
    query = "SELECT EmployeeName, email FROM users WHERE username = %s"
    cursor.execute(query, (username,))
    user_details = cursor.fetchone()
    cursor.close()
    connection.close()
    return user_details


# Function to update user details based on username
def update_user_details(username, name, email):
    connection = create_connection()
    cursor = connection.cursor()
    query = "UPDATE users SET EmployeeName = %s, email = %s WHERE username = %s"
    cursor.execute(query, (name, email, username))
    connection.commit()
    cursor.close()
    connection.close()


def get_invoices_print():
    try:
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("""SELECT i.id,u.id AS Client Id,u.fullname,
            email,phone_number,address,invoice_date,i.total_amount,status
            FROM users AS u JOIN invoices AS i ON c.id=i.client_id""")
        invoices = cursor.fetchall()
        return invoices
    except Error as e:
        print(f"Error fetching invoices: {e}") 
        return None  
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()
            

def get_invoice_details(invoice_id):
    invoices = get_invoices_print()
    if invoices:
        for invoice in invoices:
            if invoice["id"] == invoice_id:
                return invoice
    return None
def client_assigned_services(client_id):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        
        query = """
            SELECT s.id, s.service_name, s.price
            FROM client_services cs
            JOIN services s ON cs.service_id = s.id
            WHERE cs.client_id = %s
        """
        cursor.execute(query, (client_id,))
        services = cursor.fetchall()
        
        service_list = []
        for service in services:
            service_list.append({
                'id': service[0],
                'service_name': service[1],
                'price': service[2]
            })
        
        return service_list
    except mysql.connector.Error as e:
        print(f"MySQL Error: {e}")
    except Exception as ex:
        print(f"Error: {ex}")
    finally:
        cursor.close()
        connection.close()

def calculate_total_amount(client_id):
    try:
        connection = create_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT s.price
            FROM client_services cs
            JOIN services s ON cs.service_id = s.id
            WHERE cs.client_id = %s
        """, (client_id,))
        
        prices = cursor.fetchall()
        total_amount = sum(price[0] for price in prices)
        return total_amount

    except mysql.connector.Error as e:
        print(f"MySQL Error: {e}")
    except Exception as ex:
        print(f"Error: {ex}")
    finally:
        cursor.close()
        connection.close()

def get_total_sales_dash():
    query = """
    SELECT client_id, SUM(total_amount) AS total_sales
    FROM invoices
    WHERE status = 'Paid'
    GROUP BY client_id
    """
    
    return fetch_data(query)

def get_total_services_dash():
    query = """
    SELECT cs.client_id,sum(price) as total_services
    FROM client_services cs JOIN invoices i ON
    cs.client_id=i.client_id JOIN services s ON
    cs.service_id=s.id where i.status="Paid" group by cs.client_id;

    """
    return fetch_data(query)

def get_invoices_dash():
    query = """
    SELECT client_id, total_amount, status
    FROM invoices
    """
    return fetch_data(query)
def get_subscription_list_for_client(username):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True) 

    try:
        cursor.execute("""
            SELECT st.id AS Subscription_ID, user.id as Client_ID,
            user.fullname AS Client_Name,user.username AS Username,
            services.service_name, st.status
            FROM subscriptions_table as st
            JOIN users  ON st.user_id = users.id
            JOIN services ON st.service_id = services.id
            WHERE users.username = %s AND st.status = 'active'
        """,(username,))
        subscription_details = cursor.fetchall()
        return subscription_details
    except mysql.connector.Error as err:
        print(f"Error fetching subscription details: {err}")
        return None
    finally:
        cursor.close()
        conn.close()
def get_active_subscriptions_for_client(username):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True) 
    try:
        cursor.execute("""
            SELECT
            u.id AS Client_ID,
            u.fullname AS Client_Name,
            s.id AS Service_ID,
            s.service_name,
            s.description,
            st.status AS Subscription_Status,
            st.subscription_date,
            st.expiration_date
            FROM
                subscriptions_table st
            JOIN
                users u ON st.user_id = u.id
            JOIN
                services s ON st.service_id = s.id
            WHERE
                u.username = %s AND
                st.status = 'active'
        """, (username,))
        subscriptions = cursor.fetchall()
        return subscriptions
    except mysql.connector.Error as err:
        print(f"Error fetching active subscriptions: {err}")
        return None
    finally:
        cursor.close()
        conn.close()

def cancel_subscription(subscription_id):
    conn = create_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("UPDATE subscriptions_table SET status = 'cancelled' WHERE id = %s", (subscription_id,))
        conn.commit()
        return True, "Subscription cancelled successfully."
    except mysql.connector.Error as err:
        
        conn.rollback()
        return False, f"Error cancelling subscription: {err}"
    finally:
        cursor.close()
        conn.close()
def get_subscription_details():
    conn = create_connection()
    cursor = conn.cursor(dictionary=True) 

    try:
        cursor.execute("""
            SELECT subscriptions_table.id AS Subscription_ID,
            clients.id as Client_ID,clients.client_name AS Client_Name,
            clients.username AS Username, services.service_name, subscriptions_table.status
            FROM subscriptions_table
            JOIN clients ON subscriptions_table.client_id = clients.id
            JOIN services ON subscriptions_table.service_id = services.id
        """)
        subscription_details = cursor.fetchall()
        return subscription_details
    except mysql.connector.Error as err:
        print(f"Error fetching subscription details: {err}")
        return None
    finally:
        cursor.close()
        conn.close()

def update_subscription_status(subscription_id, new_status):
    conn = create_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("UPDATE subscriptions SET status = %s WHERE id = %s", (new_status, subscription_id))
        conn.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Error updating subscription status: {err}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()
def get_invoices_for_client(client_id):
    try:
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM invoices WHERE client_id=%s",(client_id,))
        invoices = cursor.fetchall()
        return invoices
    except Error as e:
        print(f"Error: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

def get_client_id(username):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id
    FROM clients
    WHERE username = %s""",(username,))
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

def get_client_id_dashboard(username):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id
        FROM clients
        WHERE username = %s""", (username,))
    result = cursor.fetchone() 
    cursor.close()
    conn.close()
    return result[0] if result else None

def get_services_data():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM services")
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result
def get_clients_data():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""SELECT id, fullname, email, phone_number, address,
                   username, created_at FROM users where role='client'""")
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result
def get_invoices_data():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM invoices WHERE status='Paid' or status='Unpaid'")
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result
def get_users_data():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result
def get_client_services(client_id):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)  
    query = "SELECT * FROM client_services WHERE user_id = %s"
    cursor.execute(query, (client_id,))
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

def get_client_invoices(client_id):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM invoices WHERE user_id = %s"
    cursor.execute(query, (client_id,))
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

def get_all_staff():
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""SELECT id as User_ID ,fullname as Name,email as Email_ID,
    username as Username,phone_number as Contact_Number,address as Address
    FROM users WHERE role = 'user'""")
    staff = cursor.fetchall()
    cursor.close()
    conn.close()
    return staff

# Function to add new staff
def add_staff(fullname, email, username, password, phone_number, address):
    conn = create_connection()
    cursor = conn.cursor()
    hashed_password = hash_password(password)
    cursor.execute("""
        INSERT INTO users (fullname, email, username, password, phone_number, address, role)
        VALUES (%s, %s, %s, %s, %s, %s, 'user')
    """, (fullname, email, username, hashed_password, phone_number, address))
    conn.commit()
    cursor.close()
    conn.close()

# Function to get a single staff by ID
def get_staff_by_id(staff_id):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (staff_id,))
    staff = cursor.fetchone()
    cursor.close()
    conn.close()
    return staff

# Function to update staff details
def update_staff(staff_id, fullname, email, username, phone_number, address):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users SET fullname = %s, email = %s, username = %s, phone_number = %s, address = %s
        WHERE id = %s
    """, (fullname, email, username, phone_number, address, staff_id))
    conn.commit()
    cursor.close()
    conn.close()

# Function to delete staff
def delete_staff(staff_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = %s", (staff_id,))
    conn.commit()
    cursor.close()
    conn.close()

def view_staff_list():
    st.title("Staff List")
    staff = get_all_staff()
    if staff:
        df = pd.DataFrame(staff)  # Convert the list to a DataFrame
        styled_df = df.style.set_properties(**{'background-color': 'white', 'color': 'black', 'border-color': 'black', 'border-width': '1px', 'border-style': 'solid'}).set_table_styles([
            {'selector': 'th', 'props': [('font-size', '12px'), ('font-weight', 'bold')]},
            {'selector': 'td', 'props': [('font-size', '12px')]}
        ])
        st.write(styled_df.to_html(), unsafe_allow_html=True)
    else:
        st.write("No staff found.")

def add_staff_form():
    st.title("Add Staff")
    fullname = st.text_input("Full Name")
    email = st.text_input("Email")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    phone_number = st.text_input("Phone Number")
    address = st.text_input("Address")
    if st.button("Add Staff"):
        if fullname and email and username and password and phone_number and address:
            add_staff(fullname, email, username, password, phone_number, address)
            st.success("Staff added successfully!")
        else:
            st.error("Please fill in all fields.")

def edit_staff_form():
    st.title("Edit Staff")
    # Fetch all staff members
    staff = get_all_staff()
    staff_dict = {f"{person['Name']} ({person['User_ID']})": person['User_ID'] for person in staff}
    
    if staff_dict:
        selected_staff = st.selectbox("Select Staff to Edit", options=list(staff_dict.keys()))
        staff_id = staff_dict[selected_staff]
        
        if st.button("Load Staff"):
            staff = get_staff_by_id(staff_id)
            if staff:
                fullname = st.text_input("Full Name", value=staff['fullname'])
                email = st.text_input("Email", value=staff['email'])
                username = st.text_input("Username", value=staff['username'])
                phone_number = st.text_input("Phone Number", value=staff['phone_number'])
                address = st.text_input("Address", value=staff['address'])
                if st.button("Update Staff"):
                    if fullname and email and username and phone_number and address:
                        update_staff(staff_id, fullname, email, username, phone_number, address)
                        st.success("Staff updated successfully!")
                    else:
                        st.error("Please fill in all fields.")
            else:
                st.error("Staff not found.")
    else:
        st.write("No staff members available to edit.")




def delete_staff_form():
    st.title("Delete Staff")
    # Fetch all staff members
    staff = get_all_staff()
    staff_dict = {f"{person['Name']} ({person['User_ID']})": person['User_ID'] for person in staff}
    
    if staff_dict:
        selected_staff = st.selectbox("Select Staff to Delete", options=list(staff_dict.keys()))
        staff_id = staff_dict[selected_staff]
        
        if st.button("Delete Staff"):
            delete_staff(staff_id)
            st.success("Staff deleted successfully!")
    else:
        st.write("No staff members available to delete.")
def show_profile_admin(user):
    st.subheader("Profile")
    st.write("Update your profile details below:")
    
    fullname = st.text_input("Full Name", value=user['fullname'])
    email = st.text_input("Email", value=user['email'])
    username = st.text_input("Username", value=user['username'])
    phone_number = st.text_input("Phone Number", value=user['phone_number'])
    address = st.text_input("Address", value=user['address'])

    if st.button("Update Profile"):
        if fullname and email and username and phone_number and address:
            update_staff(user['id'], fullname, email, username, phone_number, address)
            st.success("Profile updated successfully!")
        else:
            st.error("Please fill in all fields.")
import streamlit as st
import bcrypt

# Assuming hash_password function is defined as shown above

def change_password(user):
    st.title("Change Password")
    st.write("Enter your current password and new password to change your password:")
    
    current_password = st.text_input("Current Password", type="password")
    new_password = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm New Password", type="password")
    
    if st.button("Change Password"):
        if current_password and new_password and confirm_password:
            if new_password == confirm_password:
                # Authenticate the current password
                authenticated_user = authenticate_user_password(user['username'], current_password)
                if authenticated_user:
                    # Update the password
                    hashed_password = hash_password(new_password)
                    conn = create_connection()
                    cursor = conn.cursor()
                    cursor.execute("UPDATE users SET password = %s WHERE id = %s", (hashed_password, user['id']))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    st.success("Password changed successfully!")
                else:
                    st.error("Current password is incorrect.")
            else:
                st.error("New password and confirmation do not match.")
        else:
            st.error("Please fill in all fields.")

def authenticate_user_password(username, password):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Query to fetch hashed password for the given username
    cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
    result = cursor.fetchone()
    
    if result:
        hashed_password = result['password']
        # Verify the provided password against the stored hashed password
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
            # Passwords match, fetch user details
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
        else:
            user = None
    else:
        user = None
    
    cursor.close()
    conn.close()
    
    return user


def get_client_services_data(user_id):
    connection = create_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT cs.user_id, cs.service_id, cs.assigned_date, s.service_name, s.status
                FROM client_services cs
                JOIN services s ON cs.service_id = s.id
                WHERE cs.user_id = %s
            """
            cursor.execute(sql, (user_id,))
            result = cursor.fetchall()
            return result
    finally:
        connection.close()

def get_client_invoices_data(user_id):
    connection = create_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT i.id, i.user_id, i.invoice_date, i.due_date, i.total_amount, i.status
                FROM invoices i
                WHERE i.user_id = %s and status='Paid' or 'Unpaid'
            """
            cursor.execute(sql, (user_id,))
            result = cursor.fetchall()
            return result
    finally:
        connection.close()
def get_unpaid_invoices_with_user_details():

    connection = create_connection()
    cursor = connection.cursor(dictionary=True)

    # Query to fetch unpaid invoices with user details
    query = """
    SELECT c.fullname, c.email, c.phone_number, i.due_date, i.total_amount, i.status
    FROM invoices i
    JOIN users c ON i.user_id = c.id
    WHERE i.status = 'Unpaid'
    """
    cursor.execute(query)
    unpaid_invoices = cursor.fetchall()

    return unpaid_invoices


    cursor.close()
    connection.close()
def get_all_client_phone_numbers():
    
        # Establish a connection to the database
    connection = create_connection()
    cursor = connection.cursor()

    # Query to fetch all phone numbers from clients table
    query = "SELECT phone_number FROM users WHERE role='client'"
    cursor.execute(query)
    phone_numbers = cursor.fetchall()

    # Extract phone numbers from the query result
    phone_number_list = [phone[0] for phone in phone_numbers]

    return phone_number_list

    cursor.close()
    connection.close()




































