import streamlit as st
from streamlit_option_menu import option_menu
import admin
import staff
import base64
import streamlit as st
#import plotly.express as px
import staff
import client
import home_page
import due_reminder_mail as drm
from datetime import date
import gmail_service as gs
import methods as md
from email.message import EmailMessage
import base64
class MultiApp:
    def __init__(self):
        self.apps = []
    
    

    def run(self):
       
        # Check if user is logged in
        if 'user' not in st.session_state or st.session_state['user'] is None:
            # Display the option menu only if no user is logged in
            selected = option_menu(
                menu_title="CUSTOMER MANAGEMENT SYSTEM",  # required
                options=["Home", "ADMIN", "CUSTOMER","STAFF"],  # required
                icons=["house", "person-circle", "person","person-fill"],  # optional
                menu_icon="people-fill",  # optional
                default_index=0,  # optional
                orientation="horizontal",
                styles={
                    "container": {"padding": "0!important", "background-color": "#fafafa"},
                    "icon": {"color": "orange", "font-size": "15px"},
                    "nav-link": {
                        "font-size": "15px",
                        "text-align": "left",
                        "margin": "0px",
                        "--hover-color": "#eee",
                    },
                    "nav-link-selected": {"background-color": "green"},
                },
            )

            if selected == "ADMIN":
                admin.admin()
            elif selected == "CUSTOMER":
                client.client()
            elif selected == "STAFF":
                staff.staff()
            else:
                home_page.app()
        else:
            # User is logged in, display the appropriate dashboard
            user_role = st.session_state['user']['role']
            if user_role == 'admin':
                admin.admin()
            elif user_role == 'client':
                client.client()
            elif user_role == 'user':
                staff.staff()
            else:
                home_page.app()

if __name__ == "__main__":
    app = MultiApp()
    app.run()
    
