import streamlit as st
from .snowflake_operations import register_new_user, validate_user_credentials

def show_registration_login():
    #st.title("Welcome to the the San Francisco Crime Tracker App")
    if not st.session_state.logged_in:
        # Center align the title using HTML and CSS
        st.markdown("""
            <style>
            .title {
                text-align: center;
            }
            </style>
        """, unsafe_allow_html=True)
        
        st.markdown('<h1 class="title">Welcome to the the San Francisco Crime Tracker App</h1><br></br><h3 align="center">User Registration and Login</h3>', unsafe_allow_html=True)

    with st.container() as form_container:
        #st.markdown("##")
 
            tab1, tab2 = st.tabs(["Login", "Sign Up"])

            with tab1:
                username = st.text_input("Username", key="login_username_input")
                password = st.text_input("Password", type="password", key="login_password_input")
                if st.button("Login", key="login_button"):
                    st.header("Login")
                    if not username or not password:
                        st.error("Please enter username and password.")
                    else:
                        success, user_id = validate_user_credentials(username, password)
                        if success:
                            st.success("Login successful!")
                            st.success(f"Welcome, {username}!")
                            st.session_state.logged_in = True
                            st.session_state.user_id = user_id
                            #st.session_state.user_role = user_role
                        else:
                            st.error("Incorrect username or password.")
                        st.experimental_rerun()
                st.markdown("<hr/>", unsafe_allow_html=True)

 
            with tab2:
                new_username = st.text_input("New Username", key="new_username")
                new_password = st.text_input("New Password", type="password", key="new_password")
                full_name = st.text_input("Full Name", key="full_name")
                email = st.text_input("Email", key="email")
                #role = st.selectbox("Role", ["User", "Admin"], key="role")

                if st.button("Sign Up"):
                    if not new_username or not new_password or not full_name or not email:
                        st.error("Please fill in all fields.")
                    else:
                        success, message = register_new_user(new_username, new_password, full_name, email)
                        if success:
                            st.success(message)
                            st.experimental_rerun()
                        else:
                            st.error(message)
                    pass
 
            st.markdown('</div>', unsafe_allow_html=True)

def log_out():
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.success("Logged out successfully!")
    st.experimental_rerun()

if __name__ == "__main__":
    show_registration_login()
