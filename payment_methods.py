
import methods as md
import streamlit as st
import pandas as pd
from decimal import Decimal
import time
import re
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

def generate_payment_receipt_pdf(client_id, service_id, amount_paid, amount_unpaid, payment_method):
    client_details = md.get_client(client_id)
    service_details = md.get_service(service_id)

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.drawString(100, 750, "Payment Receipt")
    p.drawString(100, 735, f"Client Name: {client_details[1]}")
    p.drawString(100, 720, f"Service: {service_details['service_name']}")
    p.drawString(100, 705, f"Amount Paid: ${amount_paid:.2f}")
    p.drawString(100, 690, f"Amount Unpaid: ${amount_unpaid:.2f}")
    p.drawString(100, 675, f"Payment Method: {payment_method}")
    p.drawString(100, 660, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    p.showPage()
    p.save()

    buffer.seek(0)
    return buffer.getvalue()

def collect_credit_card_details():
    st.subheader("Credit Card Payment")
    card_number = st.text_input("Card Number")
    card_holder_name = st.text_input("Card Holder Name")
    expiration_date = st.text_input("Expiration Date (MM/YY)")
    cvv = st.text_input("CVV", type="password")

    return {
        "card_number": card_number,
        "card_holder_name": card_holder_name,
        "expiration_date": expiration_date,
        "cvv": cvv
    }
def collect_debit_card_details():
    st.subheader("Debit Card Payment")
    card_number = st.text_input("Card Number")
    card_holder_name = st.text_input("Card Holder Name")
    expiration_date = st.text_input("Expiration Date (MM/YY)")
    cvv = st.text_input("CVV", type="password")

    return {
        "card_number": card_number,
        "card_holder_name": card_holder_name,
        "expiration_date": expiration_date,
        "cvv": cvv
    }

def collect_paypal_details():
    st.subheader("PayPal Payment")
    paypal_email = st.text_input("PayPal Email")

    return {
        "paypal_email": paypal_email
    }

def collect_bank_transfer_details():
    st.subheader("Bank Transfer Payment")
    account_number = st.text_input("Account Number")
    bank_name = st.text_input("Bank Name")
    routing_number = st.text_input("Routing Number")

    return {
        "account_number": account_number,
        "bank_name": bank_name,
        "routing_number": routing_number
    }
def validate_credit_card_details(details):
    card_number_pattern = re.compile(r"^\d{16}$")
    expiration_date_pattern = re.compile(r"^(0[1-9]|1[0-2])\/?([0-9]{2})$")
    cvv_pattern = re.compile(r"^\d{3}$")

    if not card_number_pattern.match(details["card_number"]):
        st.error("Invalid card number")
        return False

    if not expiration_date_pattern.match(details["expiration_date"]):
        st.error("Invalid expiration date")
        return False

    if not cvv_pattern.match(details["cvv"]):
        st.error("Invalid CVV")
        return False

    return True
def validate_debit_card_details(details):
    return validate_credit_card_details(details)  # Same validation as credit card

def validate_paypal_details(details):
    paypal_email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    if not paypal_email_pattern.match(details["paypal_email"]):
        st.error("Invalid PayPal email address")
        return False

    return True

def validate_bank_transfer_details(details):
    account_number_pattern = re.compile(r"^\d{10,12}$")
    routing_number_pattern = re.compile(r"^\d{9}$")

    if not account_number_pattern.match(details["account_number"]):
        st.error("Invalid account number")
        return False

    if not routing_number_pattern.match(details["routing_number"]):
        st.error("Invalid routing number")
        return False

    return True
def process_payment(details, amount, payment_method):
    st.info("Processing payment...")
    time.sleep(2)  # Simulate payment processing delay
    st.success(f"Payment successful with {payment_method}!")

def process_credit_card_payment(details, amount):
    st.info("Processing payment...")
    time.sleep(2)  # Simulate payment processing delay
    st.success("Payment successful!")
def get_service_price(service_id):
    connection = md.create_connection()
    cursor = connection.cursor()
    query = "SELECT price FROM services WHERE id = %s"
    cursor.execute(query, (service_id,))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    return result[0] if result else 0.0
def get_services_for_client(user_id):
    try:
        # Establish a database connection
        connection = md.create_connection()

        cursor = connection.cursor(dictionary=True)

        # Query to get services available for the client
        query = """
        SELECT id, service_name, price
        FROM services
        WHERE status = 'active'  
        ORDER BY service_name
        """
        cursor.execute(query)
        services = cursor.fetchall()

        return services

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
def update_subscription_remaining_payment(client_id, service_id, amount_paid,amount_unpaid):
    
    connection = md.create_connection()
    cursor = connection.cursor(dictionary=True)

    # Update subscription table
    update_query = """UPDATE subscriptions_table
                SET amount_paid = amount_paid + %s,
                amount_unpaid = amount_unpaid - %s WHERE user_id = %s AND service_id = %s"""
    cursor.execute(update_query, (amount_paid, amount_paid, client_id, service_id))
    connection.commit()
    cursor.close()
    connection.close()
    assign_service_to_client(client_id, service_id)
    st.success(f"Service assigned to client {client_id} successfully.")

    
def get_unpaid_amount(client_id, service_id):
    
    # Establish a database connection
    connection = md.create_connection()
    cursor = connection.cursor(dictionary=True)

    # Query to get the subscription details
    query = """
    SELECT amount_unpaid
    FROM subscriptions_table
    WHERE user_id = %s AND service_id = %s
    """
    cursor.execute(query, (client_id, service_id))
    subscription = cursor.fetchone()

    return subscription
    
    cursor.close()
    connection.close()
def update_subscription_with_payment(client_id, service_id, payment_method, amount_paid, amount_unpaid):
    connection = md.create_connection()
    cursor = connection.cursor()

    query = """
    INSERT INTO subscriptions_table (user_id, service_id, payment_method, amount_paid, amount_unpaid,status )
    VALUES (%s, %s, %s, %s, %s, 'active')
    """
    cursor.execute(query, (client_id, service_id, payment_method, amount_paid, amount_unpaid))
    connection.commit()
    cursor.close()
    connection.close()
    assign_service_to_client(client_id, service_id)
    st.success(f"Service assigned to client {client_id} successfully.")

    invoice_date = datetime.now().date()
    due_date = invoice_date  # or set a different due date
    status = "Paid" if amount_unpaid == 0 else "Unpaid"
    total_amount = amount_paid
    
    if amount_unpaid==0:
        create_invoice(client_id, invoice_date, due_date, total_amount, status)
        st.success(f"Service assigned and invoice created for client {client_id} successfully.")
    else:
        st.error("Invoice not created,You have a pending amount")
def create_invoice(user_id, invoice_date, due_date, total_amount, status):
    conn = md.create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO invoices (user_id, invoice_date, due_date, total_amount, status)
        VALUES (%s, %s, %s, %s, %s)
    """, (user_id, invoice_date, due_date, total_amount, status))
    conn.commit()
    invoice_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return invoice_id
def assign_service_to_client(client_id, service_id):
    
    connection = md.create_connection()

    cursor = connection.cursor()

    # Check if the service is already assigned to the client
    query = "SELECT COUNT(*) FROM client_services WHERE user_id = %s AND service_id = %s"
    cursor.execute(query, (client_id, service_id))
    result = cursor.fetchone()

    if result[0] == 0:
        # Service is not assigned yet, insert into client_services table
        insert_query = "INSERT INTO client_services (user_id, service_id) VALUES (%s, %s)"
        cursor.execute(insert_query, (client_id, service_id))
        connection.commit()
        print("Service assigned to client successfully.")
    else:
        print("Service already assigned to client.")


        cursor.close()
        connection.close()
def get_subscription(client_id, service_id):
    
    # Establish a database connection
    connection = md.create_connection()
    cursor = connection.cursor(dictionary=True)

    # Query to get the subscription details
    query = """
    SELECT *
    FROM subscriptions_table
    WHERE user_id = %s AND service_id = %s
    """
    cursor.execute(query, (client_id, service_id))
    subscription = cursor.fetchone()

    return subscription
    
    cursor.close()
    connection.close()

