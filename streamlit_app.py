
# streamlit_app.py

import streamlit as st
from streamlit_option_menu import option_menu
import streamlit_authenticator as stauth
import mysql.connector
import pandas as pd
import numpy as np
import time
import yaml


@st.experimental_singleton
def init_database_connection():
    return mysql.connector.connect(**st.secrets["mysql"])

conn = init_database_connection()

def run_query(query):
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()

def init_sessions():
    if 'page' not in st.session_state:
        st.session_state['page'] = 'Home'
    if 'user' not in st.session_state:
        st.session_state['user'] = None
    if 'searching' not in st.session_state:
        st.session_state['searching'] = False

def logged_in():
    st.error("Already logged in!")
    st.session_state['page'] = 'Home'
    time.sleep(2)
    st.experimental_rerun()



def init_users():

    #hashed_passwords = stauth.Hasher(['123', '456']).generate()


    with open('./config.yaml') as file:
        config = yaml.load(file, Loader=yaml.SafeLoader)

    users = run_query("SELECT * FROM users;")
    usernames = [user[1] for user in users]
    names = [user[2] for user in users]
    emails = [user[3] for user in users]
    passwords = [user[4] for user in users]
    
    st.text(users)

    credentials = {"usernames": {}}
    for un, name, em, pw in zip(usernames, names, emails, passwords):
        user_dict = {"name": name, "email": em, "password":  pw}
        credentials["usernames"].update({un: user_dict})
    
    st.text(credentials)
    credentials_init = credentials
    authenticator = stauth.Authenticate(
        credentials,
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized']
    )

    #st.text(config["credentials"])
    
  
    if st.session_state['page'] == 'Login':
        if st.session_state['authentication_status'] == True:
            logged_in()

        name, authentication_status, username = authenticator.login('Login', 'main')
        if st.session_state['authentication_status'] == True:
            st.success("successfully logged in")
            st.session_state['user'] = username
            st.session_state['page'] = 'Home'
            time.sleep(2)
            st.experimental_rerun()
        elif st.session_state['authentication_status'] == False:
            st.text("test")
            st.error('Username/password is incorrect') 
        elif st.session_state['authentication_status'] == None:
            st.warning('Please enter your username and password')

    
    if st.session_state['authentication_status'] == True:
        authenticator.logout('Logout', 'main')
        if st.session_state['authentication_status'] == None:
            st.success("Logged out!")
        st.write(f"Welcome *{st.session_state['user']}*")
        #st.title('Some content')
    
    
    if st.session_state['page'] == "Reset Password":
        if st.session_state['authentication_status'] == True:
            try:
                if authenticator.reset_password(st.session_state['user'], 'Reset password'):
                    st.success('Password modified successfully')
            except Exception as e:
                st.error(e)
        else:
            st.error("Must be logged in first!")
    
    if st.session_state['page'] == "Register":
        if st.session_state['authentication_status'] == True:
            logged_in()
        try:
            if authenticator.register_user('Register user', preauthorization=False):
                st.success('User registered successfully')
        except Exception as e:
            st.error(e)
    
    if st.session_state['page'] == "Forgot Password":
        if st.session_state['authentication_status'] == True:
            logged_in()
        if not (st.session_state['authentication_status'] == True):
            try:
                username_forgot_pw, email_forgot_password, random_password = authenticator.forgot_password('Forgot password')
                if username_forgot_pw:
                    st.success('New password sent securely')
                    # Random password to be transferred to user securely
                elif username_forgot_pw == False:
                    st.error('Username not found')
            except Exception as e:
                st.error(e)
        else:
            st.error("already logged in!")

    
    #st.text(credentials)
    for user in credentials['usernames']:
        
        if not (user in usernames):
            cmd = 'INSERT INTO users (username, name, email, password) VALUES ("{0}", "{1}", "{2}", "{3}");'.format(user, credentials['usernames'][user]['name'], credentials['usernames'][user]['email'], credentials['usernames'][user]['password'])
            st.success(cmd)
            run_query(cmd)
            conn.commit()
    st.text("done!")



def init_menu():
    btn1, btn2, btn3, btn4, btn5 = st.columns([1, 1, 1, 1.5, 1.5])

    
    selected = option_menu(
        menu_title = None,
        options = ["Home", "Login", "Register", "Reset Password", "Forgot Password"],
        default_index = 0,
        orientation = "horizontal"
    )

       
    if selected == "Home":
        st.session_state['page'] = "Home"
    if selected == "Login":
        st.session_state['page'] = "Login"
    if selected == "Register":
        st.session_state['page'] = "Register"
    if selected == "Reset Password":
        st.session_state['page'] = "Reset Password"
    if selected == "Forgot Password":
        st.session_state['page'] = "Fowrgot Password"

def print_search(data):
    cnt = 0
    for post in data:
        cnt += 1
        with st.form("post #{0}".format(cnt)):
            view, submit = st.columns([5, 1])
            with view:
                st.text("medicine: {0}".format(post[0]))
                st.text("quantity available: {0}".format(post[1]))
                st.text("status: {0}".format(post[2]))
                st.text("supplier: {0}".format(post[3]))
                st.text("contact: {0}".format(post[4]))
            with submit:
                reserve = st.form_submit_button("Reserve")



def search_terms(search_term, quantity):
    data_all = run_query('SELECT posts.medicine_name, posts.quantity, posts.status, users.name, users.email FROM posts JOIN users ON posts.from_user_id = users.id;')
    data = run_query('SELECT posts.medicine_name, posts.quantity, posts.status, users.name, users.email FROM posts JOIN users ON posts.from_user_id = users.id WHERE posts.medicine_name = "{0}" AND posts.status = "available" AND posts.quantity >= {1} ORDER BY posts.quantity;'.format(search_term, quantity))
    #data = run_query('SELECT * FROM posts;'.format(search_term, quantity))
    st.write(data_all)

    st.subheader("Search results:")
    if len(data) == 0:
        st.error("No search matched!")
    else:
        st.success("{0} search matched!".format(len(data)))
        print_search(data)
    


def search_box():
    if st.session_state['page'] == "Home":
        #st.subheader("Ho  
        with st.form("my_form"):
            #st.write("Inside the form")
            #slider_val = st.slider("Form slider")
            #checkbox_val = st.checkbox("Form checkbox")

            # Every form must have a submit button.

            nav1, nav2, nav3 = st.columns([3, 2, 1])

            with nav1:
                name = st.selectbox("select medicine", ["布洛芬", "鸡蛋"])
            with nav2:
                quantity = st.number_input("quantity", 1, 10)
            with nav3:
                st.text("search ")
                submitted = st.form_submit_button("Search")

            if submitted:
                st.success("searched medicine: {0} quantity: {1}".format(name, quantity))
                st.session_state['searching'] = True
        with st.container():
            if (st.session_state['searching'] == True):
                search_terms(name, quantity)
                


def main():
    menu = ["Home", "Login", "Register", "Forgot Password", "Reset Password"]

    #st.session_state['page'] = st.selectbox("Menu", menu)

    
    init_sessions()
    init_menu()
    st.title("PILL")
    init_users()
    search_box()

    



if __name__ == '__main__':
    main()
