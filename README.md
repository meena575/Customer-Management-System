# Customer Management System
## Overview
This project is a comprehensive Customer Management System (CMS) built with a focus on streamlining client, service, invoice, and staff management for businesses. The system includes features for both admins and staff, with role-specific functionalities and an easy-to-use interface. The backend is powered by MySQL and Python, and the frontend is built using Streamlit.

## Table of Contents
- Features
- Technologies Used
- Database Schema
- Installation
- Usage
- Project Structure
- Screenshots
- Contributing
- License
## Features
Common Features for Admin and Staff
1. **Dashboard**

- Overview of clients, users, services, total sales amount, and invoices.
- Graphical representation of clients, users, invoices, and services.
2. **Client Management**

- Add, view, update, and delete clients.
- View unpaid clients and send payment reminders.
  Note: Staff cannot delete clients.
3. **Service Management**

- CRUD operations for services.
- Send SMS notifications to clients when new services are added.
  Note: Staff cannot delete services.
4. **Invoice Management**

- Generate, filter, and manage invoices.
- Download or send invoice PDFs via email with options for TO, CC, BCC.
5. **Profile Management**

- Update logged-in admin/staff details.
6. **Settings**
- Update admin/staff password securely.
## Additional Admin-Only Features
1. **Staff Management**
  - CRUD operations for staff members.
## Client Features
1. **User Authentication**
    - Sign-up with one-factor or two-factor authentication (2FA).
    - 2FA via SMS for additional security.
2. **Dashboard**

Visual overview of subscribed services, invoices, and service status.
Services List

Browse and subscribe to available services.
Select payment methods and receive payment receipts via email and SMS.
Manage partial payments and service subscriptions.
Invoice Management

View, download, and email invoices.
Profile Management

Update personal details.
Settings

Update password securely.
Technologies Used
Backend: MySQL, SQL, Python
Frontend: Streamlit
Others: Twilio (for SMS notifications), Google API (for email services), ReportLab (for PDF generation)
Database Schema
The project uses the following MySQL schema:

services
users
invoices
client_services
subscriptions_table
See the schema.sql file for detailed table definitions and relationships.

Installation
Clone the repository:

bash
Copy code
git clone https://github.com/yourusername/customer-management-system.git
cd customer-management-system
Set up the virtual environment:

bash
Copy code
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install dependencies:

bash
Copy code
pip install -r requirements.txt
Set up the MySQL database:

Create the database using the provided schema.sql file.
Update the database connection settings in the project configuration file.
Run the application:

bash
Copy code
streamlit run app.py
Usage
Admin and Staff:

Access the dashboard, manage clients, services, invoices, and staff.
Update profiles and change passwords.
Clients:

Sign up, subscribe to services, manage payments, and view invoices.
Update personal profiles and change passwords.
Project Structure
plaintext
Copy code
customer-management-system/
│
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation
├── schema.sql             # MySQL database schema
├── methods.py             # Common methods used across the project
├── admin/                 # Admin-related functionality
├── staff/                 # Staff-related functionality
├── client/                # Client-related functionality
├── templates/             # HTML templates (if any)
└── static/                # Static files (CSS, JS, images)
Screenshots
Include screenshots or GIFs of your application here.

Contributing
If you would like to contribute to this project, please fork the repository and submit a pull request.

License
This project is licensed under the MIT License - see the LICENSE file for details.

