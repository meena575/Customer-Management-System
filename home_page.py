import streamlit as st
def app():
    st.markdown("<h1 style='text-align: center;'>Customer Management System</h1>", unsafe_allow_html=True)
    image="https://www.shutterstock.com/image-photo/businessman-show-crm-customer-relationship-600nw-2322768263.jpg"
    image_width = 500
        
        # Calculate the left margin to center the image
        #left_margin = (st.sidebar.columns[0].width - image_width) / 2
        
        # Center the image using Streamlit layout options
    st.markdown(
        f'<div style="text-align:center;">'
        f'<img src="{image}" style="width:100%;">'
        '</div>',
        unsafe_allow_html=True
        )
        #st.image("https://global-uploads.webflow.com/625d567276661e857102867d/63cd55af57b94e9886e36427_A%20Beginners%20Guide%20to%20Employee%20Management%20System.png",width=400)
    
    st.markdown("<p style='text-align: center;'> This kind of project can be very valuable for businesses to provide their clients with a convenient and informative interface to manage their services, view invoices, and access other relevant information.</h1>", unsafe_allow_html=True)
