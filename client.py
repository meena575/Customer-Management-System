import streamlit as st
from streamlit_option_menu import option_menu
import methods as md
from mysql.connector import Error
from datetime import datetime,date,timedelta
import bcrypt
import mysql.connector
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from fpdf import FPDF
import base64
from io import BytesIO
import payment_methods as pm
import gmail_service as gs
import sms_note as sms
import invoice_methods as im
import Invoice_send as sn
import pyotp
def user_exists(username, email):
    conn = md.create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

# Function to insert new user into database
def insert_user(fullname, email, username, password, phone_number, address):
    conn = md.create_connection()
    cursor = conn.cursor()
    hashed_password = md.hash_password(password)
    cursor.execute("""
        INSERT INTO users (fullname, email, username, password, phone_number, address, role)
        VALUES (%s, %s, %s, %s, %s, %s, 'client')
    """, (fullname, email, username, hashed_password, phone_number, address))
    conn.commit()
    cursor.close()
    conn.close()
def handle_payment_and_notify(payment_method, amount_paid, client_id, client_email, client_phone, service_name,service_price,service_id):
    amount_unpaid = float(service_price) - amount_paid
    pm.update_subscription_with_payment(client_id, service_id, payment_method, amount_paid, amount_unpaid)
    st.success("Subscription updated with payment details.")
    if client_email:
        subject = "Your Payment Receipt from Our Company"
        message_text = "Please find attached your payment receipt."
        st.write(service_id)
        pdf_bytes = pm.generate_payment_receipt_pdf(client_id, service_id, amount_paid, amount_unpaid, payment_method)
        gs.send_email_with_attachment_bytes(client_email, subject, message_text, pdf_bytes, "payment_receipt.pdf")
        st.success("Payment receipt sent successfully!")
    else:
        st.error("Client email not found!")
    # Send SMS notification
    sms_message = f"Dear {user['fullname']}, your payment of ${amount_paid} for {selected_service_name} has been received. Thank you!"
    sms.send_sms_notification(client_phone, sms_message)
    st.success("Payment notification sent via SMS.")
def handle_payment_and_notify_remianing(payment_method, amount_paid, client_id, client_email, client_phone, service_name,service_price,service_id):
    amount_unpaid=pm.get_unpaid_amount(client_id, service_id)
    pm.update_subscription_remaining_payment(client_id, service_id,amount_paid,amount_unpaid)
    amount_unpaid=pm.get_unpaid_amount(client_id, service_id)
    invoice_date = datetime.now().date()
    due_date = invoice_date  # or set a different due date
    status = "Paid" if amount_unpaid == 0 else "Unpaid"
    total_amount = amount_paid
    if amount_unpaid==0:
        im.create_invoice(client_id, invoice_date, due_date, total_amount, status)
        st.success(f"Service assigned and invoice created for client {client_id} successfully.")
    else:
        st.error("Invoice not created,You have a pending amount")
    st.success("Subscription updated with payment details.")
    if client_email:
        subject = "Your Payment Receipt from Our Company"
        message_text = "Please find attached your payment receipt."
        pdf_bytes = pm.generate_payment_receipt_pdf(client_id, service_id, amount_paid, amount_unpaid, payment_method)
        
        gs.send_email_with_attachment_bytes(client_email, subject, message_text, pdf_bytes, "payment_receipt.pdf")
        st.success("Payment receipt sent successfully!")
    else:
        st.error("Client email not found!")
    # Send SMS notification
    sms_message = f"Dear {user['username']}, your payment of ${amount_paid} for {selected_service_name} has been received. Thank you!"
    sms.send_sms_notification(client_phone, sms_message)
    st.success("Payment notification sent via SMS.")

# Client page
def client():
    if 'user' not in st.session_state:
        st.session_state['user'] = None
    if 'otp_verified' not in st.session_state:
        st.session_state['otp_verified'] = False
    if 'otp_secret' not in st.session_state:
        st.session_state['otp_secret'] = None

    logged_user = st.session_state['user']
    otp_verified = st.session_state['otp_verified']
    if st.session_state['user'] is None:
        with st.sidebar:
            login_select = option_menu(
                menu_title="CLIENT",
                options=["Login", "Sign Up"],
                icons=["bar-chart", "list"],
                menu_icon="person-circle",
                default_index=0,
                key="admin_menu1",
                styles={
                    "container": {"padding": "5!important", "background-color": '#0A0808'},
                    "icon": {"color": "white", "font-size": "20px"},
                    "nav-link": {"color": "white", "font-size": "20px",
                                 "text-align": "left", "margin": "0px",
                                 "--hover-color": "blue"},
                    "nav-link-selected": {"background-color": "#02ab21"},
                    "menu-title": {"color": "white"},
                }
                
            )
        
        if login_select == "Login":
            st.title("Customer Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("Login"):
                user = md.authenticate_user_client(username, password)
                if user:
                    # Generate a new OTP secret for the user session
                    otp_secret = pyotp.random_base32()
                    st.session_state['otp_secret'] = otp_secret
                    st.session_state['user'] = user
                    st.session_state['otp_verified'] = False
                    st.success("Login successful. Please verify the OTP sent to your phone.")
                    # Generate OTP
                    totp = pyotp.TOTP(otp_secret)
                    otp = totp.now()
                 
                    
                    st.success("Login successful. Please verify the OTP sent to your email or phone.")
                    
                    # Send OTP via SMS (example)
                    #sms.send_sms_notification(user['phone_number'], f"Your OTP code is: {otp}")
                    
                    st.experimental_rerun()
                else:
                    st.error("Invalid username or password")
        elif login_select == "Sign Up":
            st.title("Client Sign-Up")
            fullname = st.text_input("Full Name")
            email = st.text_input("Email")
            phone_number = st.text_input("Phone Number(include Country code +19)")
            address = st.text_input("Address")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")

            if st.button("Sign Up"):
                if fullname and email and phone_number and address and username and password:
                    if user_exists(username, email):
                        st.error("A user with this username or email already exists.")
                    else:
                        insert_user(fullname, email, username, password, phone_number, address)
                        st.success("Sign-up successful! Please log in.")
                else:
                    st.error("Please fill in all fields.")
                   
        """elif not otp_verified:
        st.title("Two-Factor Authentication")
        otp_enter = st.text_input("Enter the OTP sent to your email or phone", type="password")
        if st.button("Verify OTP"):
            # Check if otp has been initialized and entered by the user
            if st.session_state['otp_secret'] and otp_enter:
                totp = pyotp.TOTP(st.session_state['otp_secret'])
                if totp.verify(otp_enter):
                    st.session_state['otp_verified'] = True
                    st.success("OTP verification successful")
                    st.experimental_rerun()
                else:
                    st.error("Invalid OTP. Please try again.")
            else:
                st.error("Please wait for OTP to be sent and enter it.")"""

    else:
        user = st.session_state['user']
        st.sidebar.markdown(
            """
            <div style="text-align: center;">
                <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQcKC2u1xrmlYviutXR9p-IM-AYHr-Se-viOg&s" width="100">
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.sidebar.title(f"Welcome, {user['username']}")
        sidebar_button_clicked = st.sidebar.button("Logout🔒")
        if sidebar_button_clicked:
            st.session_state['user'] = None
            st.experimental_rerun()
        with st.sidebar:
            selection = option_menu(
                menu_title="CLIENT",
                options=["Dashboard", "Services", "Invoices","Profile","Settings"],
                icons=["bar-chart", "list", "receipt","person-lines-fill", "gear"],
                menu_icon="person-circle",
                default_index=0,
                key="admin_menu1",
                styles={
                    "container": {"padding": "5!important", "background-color": '#0A0808'},
                    "icon": {"color": "white", "font-size": "20px"},
                    "nav-link": {"color": "white", "font-size": "20px",
                                 "text-align": "left", "margin": "0px",
                                 "--hover-color": "blue"},
                    "nav-link-selected": {"background-color": "#02ab21"},
                    "menu-title": {"color": "white"},
                }
                
            )

        if selection == "Dashboard":
            st.markdown("<h2 style='text-align: center;'>Welcome to Customer Dashboard</h2>", unsafe_allow_html=True)
            image="https://www.shutterstock.com/image-photo/analyst-uses-computer-dashboard-data-600nw-2285412737.jpg"    
            image_width = 500
            st.markdown(
                    f'<div style="text-align:center;">'
                    f'<img src="{image}" style="width:500px">'
                    '</div>',
                    unsafe_allow_html=True
                )
            
            st.markdown("<p style='text-align: center;'> This kind of project can be very valuable for businesses to provide their clients with a convenient and informative interface to manage their services, view invoices, and access other relevant information.</h1>", unsafe_allow_html=True)

            client_services_data = md.get_client_services_data(logged_user['id'])
            invoices_data = md.get_client_invoices_data(logged_user['id'])

            st.title("Client Dashboard")

            # Create columns for a better layout
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Services Subscribed")
                client_services_df = pd.DataFrame(client_services_data, columns=['user_id', 'service_id', 'assigned_date', 'service_name', 'status'])
                invalid_dates = client_services_df[~client_services_df['assigned_date'].apply(lambda x: pd.to_datetime(x, errors='coerce')).notnull()]

                if not invalid_dates.empty:
                    st.error("There are invalid date entries in the data. Please check the 'assigned_date' column.")
                    st.write(invalid_dates)
                else:
                    client_services_df['assigned_date'] = pd.to_datetime(client_services_df['assigned_date'])
                    services_subscribed_chart = px.histogram(client_services_df, x='assigned_date', title='Services Subscribed Over Time', nbins=20)
                    services_subscribed_chart.update_xaxes(title_text='Subscription Date')
                    services_subscribed_chart.update_yaxes(title_text='Number of Subscriptions')
                    st.plotly_chart(services_subscribed_chart, use_container_width=True)

            with col2:
                st.subheader("Invoices Overview")
                invoices_df = pd.DataFrame(invoices_data, columns=['id', 'client_id', 'invoice_date', 'due_date', 'total_amount', 'status'])
                invoices_df['invoice_date'] = pd.to_datetime(invoices_df['invoice_date'])
                invoices_chart = px.histogram(invoices_df, x='invoice_date', title='Invoices Issued Over Time', nbins=20)
                invoices_chart.update_xaxes(title_text='Invoice Date')
                invoices_chart.update_yaxes(title_text='Number of Invoices')
                st.plotly_chart(invoices_chart, use_container_width=True)

                invoices_status_chart = px.pie(invoices_df, names='status', title='Invoices Status Distribution', hole=0.3)
                st.plotly_chart(invoices_status_chart, use_container_width=True)

            st.subheader("Client Services Status")
            service_status_chart = px.pie(client_services_df, names='status', title='Service Status Distribution', hole=0.2)
            st.plotly_chart(service_status_chart, use_container_width=True)


        elif selection == "Services":
            selection = option_menu(
                menu_title="Service Details:",  
                options=["Subscription for Services","Subscription List"],  # required
                icons=["house", "person-circle", "person","person-fill"],  # optional
                menu_icon="people-fill", 
                default_index=0,  
                orientation="horizontal",
                styles={
                    "container": {"padding": "0!important", "background-color": "#fafafa"},
                    "icon": {"color": "orange", "font-size": "15px"},
                    "nav-link": {
                        "font-size": "10px",
                        "text-align": "left",
                        "margin": "0px",
                        "--hover-color": "#eee",
                    },
                    "nav-link-selected": {"background-color": "green"},
                },
            )

            if selection == "Subscription for Services":
                st.subheader("Subscription for Services")
                services = pm.get_services_for_client(user['id'])
                if services:
                    df = pd.DataFrame(services)
                    styled_df = df.style.set_properties(**{'background-color': 'white', 'color': 'black', 'border-color': 'black', 'border-width': '1px', 'border-style': 'solid'}).set_table_styles([
                        {'selector': 'th', 'props': [('font-size', '12px'), ('font-weight', 'bold')]},
                        {'selector': 'td', 'props': [('font-size', '12px')]}
                    ])
                    st.write(styled_df.to_html(), unsafe_allow_html=True)

                    service_names = [service['service_name'] for service in services]
                    service_prices = {service['service_name']: service['price'] for service in services}

                    selected_service_name = st.selectbox("Select Service", service_names)

                    # Automatically fill service ID and amount paid based on selected service name
                    if selected_service_name in service_prices:
                        service_id = services[service_names.index(selected_service_name)]['id']
                        service_price = service_prices[selected_service_name]

                        # Check for existing subscription and pending payments
                        subscription = pm.get_subscription(client_id=user['id'], service_id=service_id)
                        if subscription:
                            if subscription['amount_unpaid'] > 0:
                                st.warning(f"You have a pending amount of ${subscription['amount_unpaid']} for {selected_service_name}.")
                                st.subheader("Pay Remaining Amount")
                                payment_method = st.selectbox("Select Payment Method", ["cash", "credit_card", "debit_card", "paypal", "bank_transfer"])
                                amount_paid = st.number_input("Enter Amount Paid", min_value=0.0, step=0.01, format="%.2f", value=float(subscription['amount_unpaid']))
                                client_email = user['email']
                                client_phone = user['phone_number']

                                if payment_method == "credit_card":
                                    credit_card_details = pm.collect_credit_card_details()
                                    if st.button("Submit Payment"):
                                        if pm.validate_credit_card_details(credit_card_details):
                                            pm.process_credit_card_payment(credit_card_details, amount=amount_paid)
                                            handle_payment_and_notify_remianing(payment_method, amount_paid, user['id'], client_email, client_phone, selected_service_name,service_price,service_id)
                                elif payment_method == "debit_card":
                                    debit_card_details = pm.collect_debit_card_details()
                                    if st.button("Submit Payment"):
                                        if pm.validate_debit_card_details(debit_card_details):
                                            pm.process_payment(debit_card_details, amount=amount_paid, payment_method=payment_method)
                                            handle_payment_and_notify_remianing(payment_method, amount_paid, user['id'], client_email, client_phone, selected_service_name,service_price,service_id)
                                elif payment_method == "paypal":
                                    paypal_details = pm.collect_paypal_details()
                                    if st.button("Submit Payment"):
                                        if pm.validate_paypal_details(paypal_details):
                                            pm.process_payment(paypal_details, amount=amount_paid, payment_method=payment_method)
                                            handle_payment_and_notify_remianing(payment_method, amount_paid, user['id'], client_email, client_phone, selected_service_name,service_price,service_id)
                                elif payment_method == "bank_transfer":
                                    bank_transfer_details = pm.collect_bank_transfer_details()
                                    if st.button("Submit Payment"):
                                        if pm.validate_bank_transfer_details(bank_transfer_details):
                                            pm.process_payment(bank_transfer_details, amount=amount_paid, payment_method=payment_method)
                                            handle_payment_and_notify_remianing(payment_method, amount_paid, user['id'], client_email, client_phone, selected_service_name,service_price,service_id)
                                elif payment_method == "cash":
                                    if st.button("Confirm Payment"):
                                        handle_payment_and_notify_remianing(payment_method, amount_paid, user['id'], client_email, client_phone, selected_service_name,service_price,service_id)
                            else:
                                st.info(f"You have already subscribed to {selected_service_name}.")
                        else:
                            payment_method = st.selectbox("Select Payment Method", ["cash", "credit_card", "debit_card", "paypal", "bank_transfer"])
                            amount_paid = st.number_input("Enter Amount Paid", min_value=0.0, step=0.01, format="%.2f", value=float(service_price))

                            client_id = user['id']
                            client_email = user['email']
                            client_phone = user['phone_number']

                            if payment_method == "credit_card":
                                credit_card_details = pm.collect_credit_card_details()
                                if st.button("Submit Payment"):
                                    if pm.validate_credit_card_details(credit_card_details):
                                        pm.process_credit_card_payment(credit_card_details, amount=amount_paid)
                                        handle_payment_and_notify(payment_method, amount_paid, client_id, client_email, client_phone, selected_service_name,service_price,service_id)
                            elif payment_method == "debit_card":
                                debit_card_details = pm.collect_debit_card_details()
                                if st.button("Submit Payment"):
                                    if pm.validate_debit_card_details(debit_card_details):
                                        pm.process_payment(debit_card_details, amount=amount_paid, payment_method=payment_method)
                                        handle_payment_and_notify(payment_method, amount_paid, client_id, client_email, client_phone, selected_service_name,service_price,service_id)
                            elif payment_method == "paypal":
                                paypal_details = pm.collect_paypal_details()
                                if st.button("Submit Payment"):
                                    if pm.validate_paypal_details(paypal_details):
                                        pm.process_payment(paypal_details, amount=amount_paid, payment_method=payment_method)
                                        handle_payment_and_notify(payment_method, amount_paid, client_id, client_email, client_phone, selected_service_name,service_price,service_id)
                            elif payment_method == "bank_transfer":
                                bank_transfer_details = pm.collect_bank_transfer_details()
                                if st.button("Submit Payment"):
                                    if pm.validate_bank_transfer_details(bank_transfer_details):
                                        pm.process_payment(bank_transfer_details, amount=amount_paid, payment_method=payment_method)
                                        handle_payment_and_notify(payment_method, amount_paid, client_id, client_email, client_phone, selected_service_name,service_price,service_id)
                            elif payment_method == "cash":
                                if st.button("Confirm Subscription"):
                                    handle_payment_and_notify(payment_method, amount_paid, client_id, client_email, client_phone, selected_service_name,service_price,service_id)
                else:
                    st.write("No Services found.")

            if selection == "Subscription List":
                username = user["username"]
                active_subscriptions = md.get_active_subscriptions_for_client(username)
                if active_subscriptions:
                    df = pd.DataFrame(active_subscriptions)  # Convert the list to a DataFrame
                    styled_df = df.style.set_properties(**{'background-color': 'white', 'color': 'black', 'border-color': 'black', 'border-width': '1px', 'border-style': 'solid'}).set_table_styles([
                        {'selector': 'th', 'props': [('font-size', '12px'), ('font-weight', 'bold')]},
                        {'selector': 'td', 'props': [('font-size', '12px')]}
                    ])
                    st.write(styled_df.to_html(), unsafe_allow_html=True)
                    
                else:
                    st.write("No Subscriptions found.")
                
        elif selection == "Invoices":
            selected = option_menu(
                menu_title="Customer Details:",  # required
                options=["Generate Invoices"],  # required
                icons=["house", "person-circle", "person","person-fill"],  # optional
                menu_icon="people-fill",  # optional
                default_index=0,  # optional
                orientation="horizontal",
                styles={
                    "container": {"padding": "0!important", "background-color": "#fafafa"},
                    "icon": {"color": "orange", "font-size": "15px"},
                    "nav-link": {
                        "font-size": "10px",
                        "text-align": "left",
                        "margin": "0px",
                        "--hover-color": "#eee",
                    },
                    "nav-link-selected": {"background-color": "green"},
                },
            )
            
            if selected == "Generate Invoices":
                st.subheader("Generate Invoice for Services Bought Between Dates")

                start_date = st.date_input("Start Date", value=date.today() - timedelta(days=30))
                end_date = st.date_input("End Date", value=date.today())
            
               
                client_service_details = im.fetch_clients_and_services(start_date, end_date,user['id'])
                if client_service_details:
                    st.success("Invoices generated successfully!")
                    total_amount = sum(detail[4] for detail in client_service_details)  # Sum of all service prices
                    invoice_date = date.today()
                    due_date = invoice_date + timedelta(days=30)
                    user_id = client_service_details[0][0]# Assuming one invoice per client for simplicity
                    invoice_id=client_service_details[0][6]
                    st.subheader("Invoice Details")
                    st.write(f"Invoice ID: {invoice_id}")
                    st.write(f"Invoice Date: {invoice_date}")
                    st.write(f"Due Date: {due_date}")
                    st.write(f"Total Amount: {total_amount:.2f}")

                    # Display client services table
                    st.subheader("Services Bought by Client")
                    service_table = []
                    for detail in client_service_details:
                        service_table.append({
                            "Client Name": detail[1],
                            "Client Email": detail[2],
                            "Service Name": detail[3],
                            "Service Price": detail[4],
                            "Assigned Date": detail[5]
                        })
                    if service_table:
                        df = pd.DataFrame(service_table)  # Convert the list to a DataFrame
                        styled_df = df.style.set_properties(**{'background-color': 'white', 'color': 'black', 'border-color': 'black', 'border-width': '1px', 'border-style': 'solid'}).set_table_styles([
                            {'selector': 'th', 'props': [('font-size', '12px'), ('font-weight', 'bold')]},
                            {'selector': 'td', 'props': [('font-size', '12px')]}
                        ])
                        st.write(styled_df.to_html(), unsafe_allow_html=True)
                        
                    else:
                        st.write("No Subscriptions found.")
                    pdf_filename = im.generate_invoice_pdf(client_service_details, invoice_id, invoice_date, due_date,total_amount)

                    with open(pdf_filename, "rb") as file:
                        st.download_button(label="Download Invoice PDF", data=file, file_name=pdf_filename, mime='application/pdf')
                
                    if st.button("Send Invoice to Email"):
                        pdf_file = sn.generate_invoice_pdf(client_service_details, invoice_id, invoice_date, due_date, total_amount)

                        # Authenticate with Gmail API
                        service = sn.authenticate_gmail()

                        # Send email with attachment
                        sn.send_email_with_attachment(service,user['email'] , 'Invoice from Your Company', 'Please find attached your invoice.', pdf_file)

                        st.success(f'Invoice sent successfully to client.')
                else:
                    st.warning("No services found for the specified date range.")
                        

                
        elif selection == "Profile":
            md.show_profile_admin(logged_user)
            
        elif selection == "Settings":
            md.change_password(logged_user)
def change_password(username, current_password, new_password):
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    connection = md.create_connection()
    cursor = connection.cursor()
    query = "UPDATE clients SET password = %s WHERE username = %s"
    cursor.execute(query, (hashed_password.decode('utf-8'), username))
    connection.commit()
    cursor.close()
    connection.close()
def update_client_details(name,email, phone_number,Address,username):
    connection = md.create_connection()
    cursor = connection.cursor()
    query = "UPDATE clients SET client_name = %s, email = %s,phone_number=%s,address=%s WHERE username = %s"
    cursor.execute(query, (name,email, phone_number,Address,username))
    connection.commit()
    cursor.close()
    connection.close()

def get_client_details(username):
    connection = md.create_connection()
    cursor = connection.cursor()
    query = " SELECT * FROM clients WHERE username=%s"
    cursor.execute(query, (username,))
    client_details = cursor.fetchall()
    return client_details
def show_settings(logged_user):
    st.header("Settings")
    
    # Fetch client details
    user_details = logged_user
    username = user_details['username']
    client_details=get_client_details(username)
    if client_details:
        st.subheader("Update Details")
        # Form for updating profile details
        with st.form("update_profile_form"):
            name = st.text_input("Name", value=client_details[0][1])
            email = st.text_input("Email", value=client_details[0][2])
            phone_number = st.text_input("Phone Number", value=client_details[0][3])
            address = st.text_input("Address", value=client_details[0][4])
            update_profile_submit = st.form_submit_button("Update Profile")

        if update_profile_submit:
            update_client_details(name, email, phone_number, address, username)
            st.success("Profile updated successfully!")

        st.subheader("Change Password")
        # Form for changing password
        with st.form("change_password_form"):
            current_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")
            change_password_submit = st.form_submit_button("Change Password")

        if change_password_submit:
            if new_password == confirm_password:
                change_password(username, current_password, new_password)
                st.success("Password changed successfully!")
            else:
                st.error("New passwords do not match. Please try again.")
    else:
        st.warning("No client found in the database.")


