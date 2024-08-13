import mysql.connector
from datetime import date
import gmail_service as gs
import methods as md
from email.message import EmailMessage
import base64
def get_due_invoices():
    # Database connection
    db = md.create_connection()
    cursor = db.cursor(dictionary=True)

    # Query to get invoices with due date as today
    today = date.today()
    query = """SELECT u.email, u.fullname, i.due_date,
            i.total_amount FROM invoices i
            JOIN users u ON i.user_id = u.id
            WHERE i.due_date = %s AND i.status = 'Unpaid'"""
    cursor.execute(query, (today,))

    results = cursor.fetchall()

    cursor.close()
    db.close()

    return results
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email_due_reminder(to_email, client_name, due_date, total_amount):
    # Authenticate with Gmail
    service = gs.authenticate_gmail()

    # Email subject and body
    subject = "Payment Due Reminder"
    body = f"Dear {client_name},\n\nThis is a reminder that your payment of ${total_amount} is due today ({due_date}). Please make the payment at your earliest convenience.\n\nThank you."

    # Create the email message
    new_mail = EmailMessage()
    new_mail['To'] = to_email
    new_mail['From'] = 'reddimpalli575@gmail.com'  # Replace with your email address
    new_mail['Subject'] = subject
    new_mail.set_content(body)

    raw = base64.urlsafe_b64encode(new_mail.as_bytes()).decode()
    final_mail = {'raw': raw}

    # Send the email
    service.users().messages().send(userId='me', body=final_mail).execute()

def send_due_date_reminders():
    due_invoices = get_due_invoices()
    for invoice in due_invoices:
        send_email_due_reminder(invoice['email'], invoice['fullname'], , invoice['total_amount'])
    #send_email_due_reminder('aagna527575@gmail.com', 'Meena', '2024-07-06', 100)

if __name__ == "__main__":
    send_due_date_reminders()
