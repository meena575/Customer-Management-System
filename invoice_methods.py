import streamlit as st
import mysql.connector
from datetime import date, timedelta
from fpdf import FPDF

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.message import EmailMessage
import base64
import methods as md

# Function to create a new invoice in the database
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

# Function to fetch client and service details for the given date range
def fetch_clients_and_services(start_date, end_date,user_id):
    conn = md.create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.id,u.fullname, u.email, s.service_name, s.price, cs.assigned_date,i.id as invoice_id
        FROM users u
        JOIN client_services cs ON u.id = cs.user_id
        JOIN services s ON cs.service_id = s.id
        JOIN invoices i ON i.user_id=u.id
        WHERE u.id = %s AND i.invoice_date BETWEEN %s AND %s

    """, (user_id,start_date, end_date))
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result


# Function to generate a PDF invoice
# Function to generate a PDF invoice
def generate_invoice_pdf(client_service_details, invoice_id, invoice_date, due_date, total_amount):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Adding a title
    pdf.cell(200, 10, txt="Invoice Details", ln=True, align='C')
    pdf.ln(10)

    # Adding client and service details
    for detail in client_service_details:
        fullname, email, service_name, price, assigned_date = detail[1], detail[2], detail[3], detail[4], detail[5]
        pdf.cell(200, 10, txt=f"Invoice ID: {invoice_id}", ln=True)
        pdf.cell(200, 10, txt=f"Client Name: {fullname}", ln=True)
        pdf.cell(200, 10, txt=f"Client Email: {email}", ln=True)
        pdf.cell(200, 10, txt=f"Service Name: {service_name}", ln=True)
        pdf.cell(200, 10, txt=f"Service Price: {price:.2f}", ln=True)
        pdf.cell(200, 10, txt=f"Service Assigned Date: {assigned_date}", ln=True)
        pdf.cell(200, 10, txt=f"Invoice Date: {invoice_date}", ln=True)
        pdf.cell(200, 10, txt=f"Due Date: {due_date}", ln=True)
        pdf.cell(200, 10, txt="-"*40, ln=True)

    # Adding total amount
    pdf.cell(200, 10, txt=f"Total Amount: {total_amount:.2f}", ln=True)

    pdf_filename = f"invoice_{invoice_id}.pdf"
    pdf.output(pdf_filename)
    
    return pdf_filename
def authenticate_gmail():
    f = InstalledAppFlow.from_client_secrets_file('key.json', ['https://mail.google.com/'])
    cred = f.run_local_server(port=0)
    service = build('gmail', 'v1', credentials=cred)
    return service


def send_invoice_to_email(email, pdf_filename, invoice_id):
    service = authenticate_gmail()
    if not email:
        return False, "Email address not provided."
    subject = "Your Invoice from Our Company"
    message_text = "Please find attached your invoice."
    new_mail = EmailMessage()
    new_mail['To'] = to_email
    new_mail['Subject'] = subject
    new_mail.set_content(message_text)
    with open('pdf_filename.pdf','rb') as f:
    #main type for 
        newmail.add_attachment(f.read(),maintype='document',subtype='.pdf',filename="Invoice.pdf")
    
    b=newmail3.as_bytes()
    d=base64.urlsafe_b64encode(b)
    data=d.decode()
    finalmail={'raw':data}
    
    service.users().messages().send(userId='reddimpalli575@gmail.com', body=final_mail).execute()

def fetch_clients_and_services_by_name_and_date(user_id, start_date, end_date):
    conn = md.create_connection()
    cursor = conn.cursor()

    query = """
    SELECT u.id,u.fullname, u.email, s.service_name, s.price, i.invoice_date,i.id as invoice_id
        FROM users u
        JOIN client_services cs ON u.id = cs.user_id
        JOIN services s ON cs.service_id = s.id
        JOIN invoices i ON i.user_id=u.id
        WHERE u.id = %s AND i.invoice_date BETWEEN %s AND %s
    """
    cursor.execute(query, (user_id, start_date, end_date))

    client_service_details = cursor.fetchall()

    cursor.close()
    conn.close()

    return client_service_details
def fetch_client_names():
    conn = md.create_connection()
    cursor = conn.cursor()

    # Select the id, fullname, and email of clients
    cursor.execute("SELECT id, fullname, email FROM users WHERE role='client'")

    # Fetch all rows and store them in a list of dictionaries
    client_details = [{"id": row[0], "fullname": row[1], "email": row[2]} for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    return client_details



   
