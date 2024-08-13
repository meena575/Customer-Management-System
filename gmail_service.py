
from fpdf import FPDF
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.message import EmailMessage
import base64

# Authenticate Gmail function
def authenticate_gmail():
    f = InstalledAppFlow.from_client_secrets_file('key.json', ['https://mail.google.com/'])
    cred = f.run_local_server(port=0)
    service = build('gmail', 'v1', credentials=cred)
    return service

# Send email with attachment bytes function
def send_email_with_attachment_bytes(to_email, subject, message_text, file_bytes, file_name):
    service = authenticate_gmail()
    
    new_mail = EmailMessage()
    new_mail['To'] = to_email
    new_mail['Subject'] = subject
    new_mail.set_content(message_text)
    
    # Add the attachment with bytes
    new_mail.add_attachment(file_bytes, maintype='application', subtype='pdf', filename=file_name)
    
    # Encode the email in base64
    raw = base64.urlsafe_b64encode(new_mail.as_bytes()).decode()
    final_mail = {'raw': raw}
    
    service.users().messages().send(userId='reddimpalli575@gmail.com', body=final_mail).execute()

def create_pdf(invoice_details, total_amount, services_details):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Add the invoice details
    pdf.cell(200, 10, txt="Invoice Details", ln=1, align="C")
    pdf.ln(10)
    pdf.cell(100, 10, txt="Invoice ID:", ln=0, align="L")
    pdf.cell(100, 10, txt=str(invoice_details['id']), ln=1, align="L")
    pdf.cell(100, 10, txt="Invoice Date:", ln=0, align="L")
    pdf.cell(100, 10, txt=str(invoice_details['invoice_date']), ln=1, align="L")
    pdf.cell(100, 10, txt="Client Name:", ln=0, align="L")
    pdf.cell(100, 10, txt=str(invoice_details['client_name']), ln=1, align="L")
    pdf.cell(100, 10, txt="Email ID:", ln=0, align="L")
    pdf.cell(100, 10, txt=str(invoice_details['email']), ln=1, align="L")
    pdf.cell(100, 10, txt="Phone Number:", ln=0, align="L")
    pdf.cell(100, 10, txt=str(invoice_details['phone_number']), ln=1, align="L")
    pdf.cell(100, 10, txt="Address:", ln=0, align="L")
    pdf.cell(100, 10, txt=str(invoice_details['address']), ln=1, align="L")
    pdf.cell(100, 10, txt="Status:", ln=0, align="L")
    pdf.cell(100, 10, txt=str(invoice_details['status']), ln=1, align="L")
    
    # Add the service details
    pdf.ln(10)
    pdf.cell(200, 10, txt="Service Details", ln=1, align="C")
    pdf.ln(10)
    for i in range(len(services_details["Service ID"])):
        pdf.cell(100, 10, txt=f"Service ID: {services_details['Service ID'][i]}", ln=1, align="L")
        pdf.cell(100, 10, txt=f"Service Name: {services_details['Service Name'][i]}", ln=1, align="L")
        pdf.cell(100, 10, txt=f"Price: {services_details['Price'][i]}", ln=1, align="L")
        pdf.ln(5)
    
    pdf.cell(100, 10, txt="Total Amount:", ln=0, align="L")
    pdf.cell(100, 10, txt=str(total_amount), ln=1, align="L")
    
    return pdf.output(dest="S").encode("latin-1")




















































































