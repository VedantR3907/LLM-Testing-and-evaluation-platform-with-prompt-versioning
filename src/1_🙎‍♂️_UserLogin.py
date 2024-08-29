import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
import os
from streamlit_server_state import server_state
import re

load_dotenv()
# Supabase credentials
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Streamlit page setup
st.set_page_config(page_title="App", page_icon="🔒")

# Initialize session state variables
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'email' not in st.session_state:
    st.session_state.email = ''

def validate_password(password):
    # Password should contain at least one capital letter, one number, and one special character
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    if not re.search(r"[!@#$%^&*]", password):
        return False
    return True

def check_user_exists(email):
    try:
        response = supabase.table("users").select("id").eq("email", email).execute()
        if response.data:
            return True
        return False
    except Exception as e:
        st.error(f"Error checking user: {e}")
        return False

def sign_up(email, password):
    if check_user_exists(email):
        st.error("This email is already registered. Please sign in instead.")
        return
    
    if not validate_password(password):
        st.error("Password should contain at least one capital letter, one number, and one special character.")
        return

    try:
        user = supabase.auth.sign_up({  # noqa: F841
            'email': email,
            'password': password,
        })
        st.success("Sign-up successful! Please check your email to confirm your account.")
        
    except Exception as e:
        st.error(f"Error: {e}")

def sign_in(email, password):
    try:
        user = supabase.auth.sign_in_with_password({
            'email': email,
            'password': password,
        })
        st.session_state.logged_in_count = 0
        st.session_state.email = email
        server_state['session'] = user
    except Exception as e:
        st.error(f"Error: {e}")

if 'session' in server_state and server_state['session']:
    st.switch_page('./pages/2_🌍_Main.py')

else:
    
    # Creating columns for layout
    col1, col2, col3 = st.columns([1,3,1])  # Adjust the numbers to change the width of the columns

    with col2:
        # Creating tabs for Sign In and Sign Up
        tab1, tab2 = st.tabs(["Sign In", "Sign Up"])

        with tab1:
            st.markdown("<h1 style='text-align: center;'>Sign In</h1>", unsafe_allow_html=True)
            email = st.text_input("Email", key='login_email')
            password = st.text_input("Password", type="password", key='login_pass')
            if st.button("Sign In"):
                if email and password:
                    sign_in(email, password)
                else:
                    st.error("Please provide both email and password.")

        with tab2:
            st.markdown("<h1 style='text-align: center;'>Sign Up</h1>", unsafe_allow_html=True)
            email = st.text_input("Email", key='signup_email')
            password = st.text_input("Password", type="password")
            if st.button("Sign Up"):
                if email and password:
                    sign_up(email, password)
                else:
                    st.error("Please provide both email and password.")