import streamlit as st
from streamlit_option_menu import option_menu
import methods as md
from mysql.connector import Error
from datetime import date,timedelta
import bcrypt
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from fpdf import FPDF
import base64
import pyotp
import time
from io import BytesIO
import gmail_service as gs
import invoice_methods as im
import Invoice_send as ins
import sms_note as sms
import due_reminder_mail as drm
def admin():
    
    if 'user' not in st.session_state:
        st.session_state['user'] = None
    if 'otp_verified' not in st.session_state:
        st.session_state['otp_verified'] = False
    if 'otp_secret' not in st.session_state:
        st.session_state['otp_secret'] = None
    
    logged_user = st.session_state['user']
    otp_verified = st.session_state['otp_verified']

    if logged_user is None:
        st.title("Admin Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user = md.authenticate_user_admin(username, password)
            if user:
                # Generate a new OTP secret for the user session
                otp_secret = pyotp.random_base32()
                st.session_state['otp_secret'] = otp_secret
                st.session_state['user'] = user
                st.session_state['otp_verified'] = False
                st.success("Login successful. Please verify the OTP sent to your phone.")
                
                # Create TOTP object
                totp = pyotp.TOTP(otp_secret)
                otp = totp.now()
                
                body = f"Your OTP code is: {otp}"
                #sms.send_sms_notification(user['phone_number'], body)
                st.rerun()
            else:
                st.error("Invalid username or password")
        """elif not otp_verified:
        st.title("Two-Factor Authentication")
        otp_enter = st.text_input("Enter the OTP sent to your phone", type="password")
        if st.button("Verify OTP"):
            if st.session_state['otp_secret'] and otp_enter:
                totp = pyotp.TOTP(st.session_state['otp_secret'])
                if totp.verify(otp_enter):
                    st.session_state['otp_verified'] = True
                    st.success("OTP verification successful")
                    st.rerun()
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
                menu_title="ADMIN",
                options=["Dashboard", "Clients List", "Invoices", "Services List", "Staff List", "Profile","Settings"],
                icons=["bar-chart", "person-circle", "receipt", "list", "people-fill","person-lines-fill", "gear"],
                menu_icon="person-circle",
                default_index=0,
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
            st.subheader("Welcome to Admin Client Management System Dashboard")

            col1, col2, col3, col4, col5 = st.columns(5)

            custom_css = """
            <style>
            .metric-container {
                display: flex;
                align-items: center;
                justify-content: center;
                flex-direction: column;
                background-color: black;
                border-radius: 5px;
                padding: 0px;
                margin: 3px;
                box-shadow: 0 0px 0px rgba(0, 0, 0, 0.2);
            }

            .metric-icon {
                font-size: 40px;
                margin-bottom: 5px;
            }

            .metric-label {
                font-size: 20px;
                font-weight: bold;
                color: #fff;
            }

            .metric-value {
                font-size: 30px;
                color: #007bff;
            }
            </style>
            """

            st.markdown(custom_css, unsafe_allow_html=True)

            with col1:
                st.markdown("""
                <div class="metric-container">
                    <div class="metric-icon" style="color: #ffff;">&#x1F4C3;</div>
                    <div class="metric-label">Services</div>
                    <div class="metric-value">{}</div>
                </div>
                """.format(md.get_total_services()), unsafe_allow_html=True)

            with col2:
                st.markdown("""
                <div class="metric-container">
                    <div class="metric-icon" style="color: #00bff;">&#x1F465;</div>
                    <div class="metric-label">Clients</div>
                    <div class="metric-value">{}</div>
                </div>
                """.format(md.get_total_clients()), unsafe_allow_html=True)

            with col3:
                st.markdown("""
                <div class="metric-container">
                    <div class="metric-icon" style="color: #007bff;">&#x1F4B8;</div>
                    <div class="metric-label">Invoices</div>
                    <div class="metric-value">{}</div>
                </div>
                """.format(md.get_total_invoices()), unsafe_allow_html=True)

            with col4:
                st.markdown("""
                <div class="metric-container">
                    <div class="metric-icon" style="color: #007bff;">&#x1F465;</div>
                    <div class="metric-label">Users</div>
                    <div class="metric-value">{}</div>
                </div>
                """.format(md.get_total_users()), unsafe_allow_html=True)

            with col5:
                st.markdown("""
                <div class="metric-container">
                    <div class="metric-icon" style="color: #007bff;">&#x1F4B0;</div>
                    <div class="metric-label">Total Sales</div>
                    <div class="metric-value">${}</div>
                </div>
                """.format(md.get_total_sales()), unsafe_allow_html=True)
            
            services_data = md.get_services_data()
            clients_data = md.get_clients_data()
            invoices_data = md.get_invoices_data()
            users_data = md.get_users_data()

            col1, col2 = st.columns(2)
    
            with col1:
                # Visualizing Services
                st.subheader("Services Overview")
                services_df = pd.DataFrame(services_data, columns=['id', 'date_created', 'service_name', 'description', 'price', 'status'])

                # Define custom colors for each status
                custom_colors = {
                    'active': '#1f77b4',  # blue
                    'inactive': '#d62728'  # ORANGE
                }

                # Create the pie chart with custom colors
                services_chart = px.pie(
                    services_df, 
                    names='status', 
                    title='Services Status Distribution', 
                    hole=0.4,
                    color='status',
                    color_discrete_map=custom_colors
                )

                st.plotly_chart(services_chart, use_container_width=True)

            with col2:
                # Visualizing Clients
                st.subheader("Clients Overview")
                clients_df = pd.DataFrame(clients_data, columns=['id', 'fullname', 'email', 'phone_number', 'address', 'username', 'created_at'])
                clients_df['created_at'] = pd.to_datetime(clients_df['created_at'])
                clients_chart = px.histogram(clients_df, x='created_at', title='Clients Registered Over Time', nbins=20)
                clients_chart.update_xaxes(title_text='Registration Date')
                clients_chart.update_yaxes(title_text='Number of Clients')
                st.plotly_chart(clients_chart, use_container_width=True)
            
            st.subheader("Invoices Overview")
            col3, col4 = st.columns(2)

            with col3:
                # Visualizing Invoices Issued Over Time
                invoices_df = pd.DataFrame(invoices_data, columns=['id', 'client_id', 'invoice_date', 'due_date', 'total_amount', 'status'])
                invoices_df['invoice_date'] = pd.to_datetime(invoices_df['invoice_date'])
                invoices_chart = px.histogram(invoices_df, x='invoice_date', title='Invoices Issued Over Time', nbins=20)
                invoices_chart.update_xaxes(title_text='Invoice Date')
                invoices_chart.update_yaxes(title_text='Number of Invoices')
                st.plotly_chart(invoices_chart, use_container_width=True)

            with col4:
                # Visualizing Invoices Status Distribution
                invoices_df['status'] = invoices_df['status'].str.lower().str.strip()
                invoices_status_chart = px.pie(invoices_df, names='status', title='Invoices Status Distribution', hole=0.3)
                st.plotly_chart(invoices_status_chart, use_container_width=True)
            
            st.subheader("Users Overview")
            col5, col6 = st.columns(2)

            with col5:
                # Visualizing Users Registered Over Time
                users_df = pd.DataFrame(users_data, columns=['id', 'fullname', 'email', 'username', 'password', 'role', 'created_at', 'phone_number', 'address'])
                users_df['created_at'] = pd.to_datetime(users_df['created_at'])
                users_chart = px.histogram(users_df, x='created_at', title='Users Registered Over Time', nbins=20)
                users_chart.update_xaxes(title_text='Registration Date')
                users_chart.update_yaxes(title_text='Number of Users')
                st.plotly_chart(users_chart, use_container_width=True)

            with col6:
                # Visualizing Users Role Distribution
                users_role_chart = px.pie(users_df, names='role', title='Users Role Distribution', hole=0.3)
                st.plotly_chart(users_role_chart, use_container_width=True)
            
        elif selection == "Clients List":
            selected = option_menu(
                menu_title="Customer Details:",  
                options=["View Clients","Add Client", "Edit Client", "Delete Client","Unpaid Clients List"],  
                icons=["house", "person-circle", "person","person-fill"],  
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
            clients = md.get_clients()
            if selected == "View Clients":
                st.subheader("Clients List")
                if clients:
                    df = pd.DataFrame(clients)  # Convert the list to a DataFrame
                    styled_df = df.style.set_properties(**{'background-color': 'white', 'color': 'black', 'border-color': 'black', 'border-width': '1px', 'border-style': 'solid'}).set_table_styles([
                        {'selector': 'th', 'props': [('font-size', '12px'), ('font-weight', 'bold')]},
                        {'selector': 'td', 'props': [('font-size', '12px')]}
                    ])
                    st.write(styled_df.to_html(), unsafe_allow_html=True)
                else:
                    st.write("No clients found.")
            if 'client_added' not in st.session_state:
                st.session_state.client_added = False
            elif selected =="Add Client":
                st.subheader("Add a New Client")
                new_name = st.text_input("Client Name")
                new_email = st.text_input("Email")
                new_phone = st.text_input("Phone Number(including Contuntry code(Ex:+91)")
                new_address = st.text_input("Address")
                new_username = st.text_input("Username")
                new_password = st.text_input("Password", type="password")

                if st.button("Add Client"):
                    if all([new_name, new_email, new_phone, new_address, new_username, new_password]):
                        if md.validate_email(new_email) and md.is_valid_contact_number(new_phone):
                            md.create_client_user(new_name, new_email, new_phone, new_address, new_username, new_password)
                            #md.create_user(new_name,new_email,new_username,new_password)
                            st.session_state.client_added = True
                            st.experimental_rerun()
                        else:
                            st.error("Please enter a valid email address and phone number.")
                    else:
                        st.error("Please enter all details.")
                if st.session_state.client_added:
                    st.success("Client added successfully.")
                    st.session_state.client_added = False
            if 'client_edited' not in st.session_state:
                st.session_state.client_edited = False
            elif selected =="Edit Client":
                clients = md.get_clients()
                st.subheader("Update a Client")
                client_ids = [client['id'] for client in clients]
                client_id = st.selectbox("Select Client to Update", client_ids, key="select_client_id")
                selected_client = md.get_client(client_id)
                if selected_client:
                    updated_name = st.text_input("Update Client Name", value=selected_client[1], key=f"update_client_name_{client_id}")
                    updated_email = st.text_input("Update Email", value=selected_client[2], key=f"update_client_email_{client_id}")
                    updated_phone = st.text_input("Update Phone Number", value=selected_client[7], key=f"update_client_phone_{client_id}")
                    updated_address = st.text_input("Update Address", value=selected_client[8], key=f"update_client_address_{client_id}")
                    updated_username= st.text_input("Update Username", value=selected_client[3], key=f"update_client_username_{client_id}")
                    #updated_password = st.text_input("New Password")

                    if st.button("Update Client", key=f"update_client_button_{client_id}"):
                        if md.validate_email(updated_email) and md.is_valid_contact_number(updated_phone):
                            md.update_client( client_id,updated_name, updated_email, updated_phone, updated_address, updated_username)
                            st.session_state.client_edited = True
                            st.experimental_rerun()
                if st.session_state.client_edited:
                    st.success("Client Updated successfully.")
                    st.session_state.client_edited = False
            if 'client_delete' not in st.session_state:
                st.session_state.client_delete = False
            elif selected =="Delete Client":
                clients = md.get_clients()
                st.subheader("Delete a Client")
                client_ids = [client['id'] for client in clients]
                client_id = st.selectbox("Select Client to Delete", client_ids, key="select_client_id")
                selected_client = md.get_client(client_id)
                if selected_client:
                    st.write(f"Name: {selected_client[1]}")
                    st.write(f"Email: {selected_client[2]}")
                    st.write(f"Phone: {selected_client[7]}")
                    st.write(f"Address: {selected_client[8]}")
                    st.write(f"Username: {selected_client[3]}")
                    
                    if st.button("Delete Client", key=f"delete_client_button_{client_id}"):
                        md.delete_client(client_id)
                        st.session_state.client_delete = True
                        st.rerun()
                if st.session_state.client_delete:
                    st.success("Client Delete successfully.")
                    st.session_state.client_delete = False
            elif selected =="Unpaid Clients List":
                unpaid_invoices = md.get_unpaid_invoices_with_user_details()
                st.subheader("Unpaid Clients Details")
                if unpaid_invoices:
                    df = pd.DataFrame(unpaid_invoices)  # Convert the list to a DataFrame
                    styled_df = df.style.set_properties(**{'background-color': 'white', 'color': 'black', 'border-color': 'black', 'border-width': '1px', 'border-style': 'solid'}).set_table_styles([
                        {'selector': 'th', 'props': [('font-size', '12px'), ('font-weight', 'bold')]},
                        {'selector': 'td', 'props': [('font-size', '12px')]}
                    ])
                    st.write(styled_df.to_html(), unsafe_allow_html=True)
                else:
                    st.write("No clients found.")
                st.write(" ")
                if st.button("Send Payment Remainder Mail"):
                    drm.send_due_date_reminders()
            
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

                # Fetch client details for filtering
                client_details = im.fetch_client_names()

                # Debug print to verify the structure of client_details
                #st.write("Client Details:", client_details)

                client_options = {f"{client['fullname']} ({client['email']})": client for client in client_details}
                selected_client = st.selectbox("Select Client", client_options.keys(),index=None)

                start_date = st.date_input("From Date")
                end_date = st.date_input("To Date")

                if selected_client:
                    client_id = client_options[selected_client]["id"]
                    client_email = client_options[selected_client]["email"]
                    client_service_details = im.fetch_clients_and_services_by_name_and_date(client_id, start_date, end_date)
                    
                    if client_service_details:
                        st.success("Invoices generated successfully!")
                        total_amount = sum(detail[4] for detail in client_service_details)  # Sum of all service prices
                        invoice_date = date.today()
                        due_date = invoice_date + timedelta(days=30)
                        invoice_id = client_service_details[0][6]

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
                            styled_df = df.style.set_properties(
                                **{'background-color': 'white', 'color': 'black', 'border-color': 'black', 'border-width': '1px', 'border-style': 'solid'}
                            ).set_table_styles([
                                {'selector': 'th', 'props': [('font-size', '12px'), ('font-weight', 'bold')]},
                                {'selector': 'td', 'props': [('font-size', '12px')]}
                            ])
                            st.write(styled_df.to_html(), unsafe_allow_html=True)
                        else:
                            st.write("No Subscriptions found.")
                        st.write(" ")

                        pdf_filename = im.generate_invoice_pdf(client_service_details, invoice_id, invoice_date, due_date, total_amount)

                        with open(pdf_filename, "rb") as file:
                            st.download_button(label="Download Invoice PDF", data=file, file_name=pdf_filename, mime='application/pdf')

                        if st.button("Send Invoice to Client_Email"):
                            pdf_file = im.generate_invoice_pdf(client_service_details, invoice_id, invoice_date, due_date, total_amount)

                            # Authenticate with Gmail API
                            service = im.authenticate_gmail()

                            # Send email with attachment
                            ins.send_email_with_attachment(service, client_email, 'Invoice from Your Company', 'Please find attached your invoice.', pdf_file)

                            st.success(f'Invoice sent successfully to {client_email}.')
                        
                        st.subheader("Email Options")
                        email_option = st.selectbox("Select Email Option", ["To", "CC", "BCC"])
                        email_addresses = st.text_input(f"{email_option} (comma separated emails)")

                        if st.button("Send Invoice to Email"):
                            pdf_file = im.generate_invoice_pdf(client_service_details, invoice_id, invoice_date, due_date, total_amount)

                            # Authenticate with Gmail API
                            service = ins.authenticate_gmail()

                            # Convert comma-separated emails to list
                            email_list = [email.strip() for email in email_addresses.split(",")] if email_addresses else []

                            # Determine email recipients based on the selected option
                            to_list = email_list if email_option == "To" else []
                            cc_list = email_list if email_option == "CC" else []
                            bcc_list = email_list if email_option == "BCC" else []

                            # Send email with attachment
                            ins.send_email_with_attachment_to_cc_bcc(service, to_list, 'Invoice from Your Company', 'Please find attached your invoice.', pdf_file, cc_list, bcc_list)

                            st.success(f'Invoice sent successfully to {", ".join(email_list)}.')

                    else:
                        st.warning("No services found for the specified date range and client.")

            
        elif selection == "Services List":
            selected = option_menu(
                menu_title="Service Details:",  # required
                options=["All Services","Add Service", "Edit Service", "Delete Service"],  # required
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
            if selected=="All Services":
                st.subheader("Services List")

                services = md.get_services()
                if services:
                    df = pd.DataFrame(services)  # Convert the list to a DataFrame
                    styled_df = df.style.set_properties(**{'background-color': 'white', 'color': 'black', 'border-color': 'black', 'border-width': '1px', 'border-style': 'solid'}).set_table_styles([
                        {'selector': 'th', 'props': [('font-size', '12px'), ('font-weight', 'bold')]},
                        {'selector': 'td', 'props': [('font-size', '12px')]}
                    ])
                    st.write(styled_df.to_html(), unsafe_allow_html=True)
                    #st.table(services)
                else:
                    st.write("No Services found.")
            if 'add_service' not in st.session_state:
                st.session_state.add_service = False
            elif selected =="Add Service":
                st.subheader("Add a New Service")
                new_service_name = st.text_input("Service Name")
                new_description = st.text_input("Description")
                new_price = st.number_input("Price", min_value=0.0, format="%.2f")
                new_status = st.selectbox("Status", ["Active", "Inactive"])
                if st.button("Add Service"):
                    if new_service_name!="" and new_description!="" and new_price!="" and new_status!="":
                        md.create_service(new_service_name, new_description, new_price, new_status)
                        numbers_list=md.get_all_client_phone_numbers()
                        message_text = f"Dear customer, we are excited to announce that a new service '{new_service_name}' has been added to our website! Visit our site to learn more."

                        sms.send_sms_notification_multi(numbers_list,message_text)
                        st.session_state.add_service = True
                        st.experimental_rerun()
                    else:
                        st.error("Enter all details.")
                if st.session_state.add_service:
                    st.success("Service Added Successfully")
                    st.session_state.add_service = False
            if 'edit_service' not in st.session_state:
                st.session_state.edit_service = False
            elif selected =="Edit Service":
                services = md.get_services()
                st.subheader("Update a Service")
                service_ids = [service["id"] for service in services]
                service_id = st.selectbox("Select Service to Update/Delete", service_ids, key="select_service_id")
                selected_service = md.get_service(service_id)
                if selected_service:
                    updated_service_name = st.text_input("Update Service Name", value=selected_service["service_name"], key=f"update_service_name_{service_id}")
                    updated_description = st.text_input("Update Description", value=selected_service["description"], key=f"update_description_{service_id}")
                    updated_price = st.number_input("Update Price", value=float(selected_service["price"]), min_value=0.0, format="%.2f", key=f"update_price_{service_id}")
                    updated_status = st.selectbox("Update Status", ["Active", "Inactive"], index=["Active", "Inactive"].index(selected_service["status"]), key=f"update_status_{service_id}")
                    if st.button("Update Service", key=f"update_service_button_{service_id}"):
                        md.update_service(service_id, updated_service_name, updated_description, updated_price, updated_status)
                        st.session_state.edit_service = True
                        st.experimental_rerun()
                    if st.session_state.edit_service:
                        st.success("Updated Successfully")
                        st.session_state.edit_service = False
            if 'delete_service' not in st.session_state:
                st.session_state.delete_service = False
            elif selected =="Delete Service":
                services = md.get_services()
                st.subheader("Delete a Service")
                service_ids = [service["id"] for service in services]
                service_id = st.selectbox("Select Service to Delete", service_ids, key="select_service_id")
                selected_service = md.get_service(service_id)
                if selected_service:
                    st.write(f"**Service_ID:** {selected_service['id']}")
                    st.write(f"**Service_Name:** {selected_service['service_name']}")
                    st.write(f"**Description:** {selected_service['description']}")
                    st.write(f"**Price:** {selected_service['price']}")
                    st.write(f"**Status:** {selected_service['status']}")
                    if st.button("Delete Service", key=f"delete_service_button_{service_id}"):
                        md.delete_service(service_id)
                        st.session_state.delete_service = True
                        st.experimental_rerun()
                    if st.session_state.delete_service:
                        st.success("Deleted Successfully")
                        st.session_state.delete_service = False
            
            
        elif selection == "Staff List":
            
            selected = option_menu(
                menu_title="Staff Management:",
                options=["View Staff List", "Add Staff", "Edit Staff", "Delete Staff"],
                icons=["eye", "person-plus", "pencil-square", "trash"],
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

            if selected == "View Staff List":
                md.view_staff_list()
            elif selected == "Add Staff":
                md.add_staff_form()
            elif selected == "Edit Staff":
                md.edit_staff_form()
            elif selected == "Delete Staff":
                md.delete_staff_form()
        elif selection == "Profile":
            md.show_profile_admin(logged_user)
            
        elif selection == "Settings":
            md.change_password(logged_user)
        
            

def create_admin_user(name, email, phone, address, username, password):
    connection = md.create_connection()
    if connection is None:
        return

    cursor = connection.cursor()
    hashed_password = md.hash_password(password)

    if md.check_existing_entries(email, username):
        st.error("Email or username already exists.")
        return

    try:
        connection.start_transaction()

        # Insert into users table with role admin
        user_query = """
            INSERT INTO users (EmployeeName, email, username, password, role, phone_number, address)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        print(f"Executing user query: {user_query} with values: {name, email, username, hashed_password, 'admin', phone, address}")
        cursor.execute(user_query, (name, email, username, hashed_password, 'admin', phone, address))

        connection.commit()
        st.success("Admin user added successfully!")
    except mysql.connector.Error as err:
        connection.rollback()
        st.error(f"Database error: {err}")
        print(f"Database error: {err}")  # Print the error for debugging
    finally:
        cursor.close()
        connection.close()

#create_admin_user("Vasudeva","vasu@gmail.com","9676058805","hyderabad","vasu123","vasu123")
