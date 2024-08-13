import streamlit as st
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from fpdf import FPDF
import base64
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
import pyotp
import time
# Main Streamlit app code
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
def send_email_with_attachment_to_cc_bcc(service, to_emails, subject, message_text, pdf_file_path, cc_emails=[], bcc_emails=[]):
    message = MIMEMultipart()
    message['to'] = ", ".join(to_emails)
    message['cc'] = ", ".join(cc_emails)
    message['bcc'] = ", ".join(bcc_emails)
    message['subject'] = subject

    # Attach the message body
    message.attach(MIMEText(message_text))

    # Attach the PDF file
    with open(pdf_file_path, "rb") as f:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(pdf_file_path))
    message.attach(part)

    # Convert to raw string for sending
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    # Send the email
    service.users().messages().send(userId="me", body={'raw': raw_message}).execute()




def send_email_with_attachment(service, to_email, subject, message_text, file_path):
    message = MIMEMultipart()
    message['to'] = to_email
    message['from'] = 'reddimpalli575@gmail.com'  # Replace with your own email address
    message['subject'] = subject

    msg = MIMEText(message_text)
    message.attach(msg)

    attachment = MIMEBase('application', 'pdf')
    with open(file_path, 'rb') as f:
        attachment.set_payload(f.read())
    encoders.encode_base64(attachment)
    attachment.add_header('Content-Disposition', f'attachment; filename={file_path}')
    message.attach(attachment)

    raw_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
    try:
        message = service.users().messages().send(userId='reddimpalli575@gmail.com', body=raw_message).execute()
        print('Message Id: %s' % message['id'])
        return message
    except Exception as error:
        print(f'An error occurred: {error}')

def authenticate_gmail():
    flow = InstalledAppFlow.from_client_secrets_file('key.json', scopes=['https://www.googleapis.com/auth/gmail.send'])
    credentials = flow.run_local_server(port=0)
    service = build('gmail', 'v1', credentials=credentials)
    return service


def generate_invoice_pdf(client_service_details, invoice_id, invoice_date, due_date, total_amount):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Adding a title
    pdf.cell(200, 10, txt="Invoice Details", ln=True, align='C')
    pdf.ln(10)

    # Adding client and service details
    for detail in client_service_details:
        try:
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
        except IndexError as e:
            print(f"Error processing detail: {detail}. IndexError: {e}")
            continue  # Skip this detail tuple and proceed with the next one

    # Adding total amount
    pdf.cell(200, 10, txt=f"Total Amount: {total_amount:.2f}", ln=True)

    pdf_filename = f"invoice_{invoice_id}.pdf"
    pdf.output(pdf_filename)

    return pdf_filename

