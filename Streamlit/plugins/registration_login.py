import streamlit as st
import re
from .snowflake_operations import register_new_user, validate_user_credentials

# Get the absolute path to the plugins directory

def show_registration_login():
    if not st.session_state.logged_in:
        st.title("User Registration and Login")
        col1, col2 = st.columns(2)

        with col1:
            st.header("User Registration")
            new_username = st.text_input("New Username")
            new_password = st.text_input("New Password", type="password")
            full_name = st.text_input("Full Name")
            email = st.text_input("Email")
            role = st.selectbox("Role", ["User", "Admin"])

            if st.button("Sign Up"):
                if not new_username or not new_password or not full_name or not email:
                    st.error("Please fill in all fields.")
                else:
                    success, message = register_new_user(new_username, new_password, full_name, email, role)
                    if success:
                        st.success(message)
                        st.experimental_rerun()
                    else:
                        st.error(message)
            st.markdown("<hr/>", unsafe_allow_html=True)

        with col2:
            st.header("Login")
            username = st.text_input("Username", key="login_username_input")
            password = st.text_input("Password", type="password", key="login_password_input")
            
            if st.button("Login", key="login_button"):
                if not username or not password:
                    st.error("Please enter username and password.")
                else:
                    success, user_id, user_role = validate_user_credentials(username, password)
                    if success:
                        st.success("Login successful!")
                        st.success(f"Welcome, {username} ({user_role})!")
                        st.session_state.logged_in = True
                        st.session_state.user_id = user_id
                        st.session_state.user_role = user_role
                    else:
                        st.error("Incorrect username or password.")
                    st.experimental_rerun()
            st.markdown("<hr/>", unsafe_allow_html=True)

if __name__ == "__main__":
    show_registration_login()
