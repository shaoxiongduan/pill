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

def init_page():
    st.session_state['page'] = 'Home'
    st.session_state['searching'] = False

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
            st.session_state['user'] = run_query('SELECT users.id FROM users WHERE users.username = "{0}"'.format(username))
            st.session_state['page'] = 'Home'
            time.sleep(2)
            st.experimental_rerun()
        elif st.session_state['authentication_status'] == False:
            st.error('Username/password is incorrect') 
        elif st.session_state['authentication_status'] == None:
            st.warning('Please enter your username and password')

    if st.session_state['page'] == 'User':
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




def init_menu():
    btn1, btn2, btn3, btn4, btn5 = st.columns([1, 1, 1, 1.5, 1.5])

    
    selected = option_menu(
        menu_title = None,
        options = ["Home", "Login", "Register", "Reset Password", "Forgot Password", "User"],
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
        st.session_state['page'] = "Forgot Password"
    if selected == "User":
        st.session_state['page'] = "User"

def alertbox(prompt):
    with st.form(prompt):
        yes = st.form_submit_button('Yes')
        no = st.form_submit_button('No')
        if yes:
            return True
        if no:
            return False
        

def print_search(data, str):
    cnt = 0
    for post in data:
        cnt += 1
        with st.form(str + "post #{0}".format(cnt)):
            view, submit = st.columns([5, 1])
            with view:
                st.text("medicine: {0}".format(post[1]))
                st.text("quantity available: {0}".format(post[2]))
                st.text("supplier: {0}".format(post[4]))
                st.text("contact: {0}".format(post[5]))
                if post[3] == 'available':
                    st.success("status: {0}".format(post[3]))
                elif post[3] == 'pending':
                    st.warning("status: {0}".format(post[3]))  
                elif post[3] == 'not available':
                    st.error("status: {0}".format(post[3]))

            with submit:             
                
                if st.session_state['authentication_status'] == True:
                    if post[3] == 'available':
                        reserve = st.form_submit_button("Reserve")
                        if reserve:
                            if st.session_state['user'][0][0] == post[0]:
                                st.error("You can't reserve your own post!")
                            else:
                                run_query('UPDATE posts SET posts.status = "pending", posts.to_user_id = {0} WHERE posts.id = {1};'.format(st.session_state['user'][0][0], post[0]))
                                conn.commit()
                                st.success("successfully reserved!")
                                #init_page()
                                st.experimental_rerun()
                    elif post[3] == 'pending' and st.session_state['user'] == run_query('SELECT posts.to_user_id FROM posts WHERE posts.id = {0};'.format(post[0])):
                        unreserve = st.form_submit_button("Unreserve")
                        confirm = st.form_submit_button("Confirm transaction")
                        if unreserve:
                            #if alertbox('Are you sure to unreserve this medicine?'):
                            run_query('UPDATE posts SET posts.status = "available", posts.to_user_id = {0} WHERE posts.id = {1};'.format('NULL' , post[0]))
                            conn.commit()
                            st.success("successfully unreserved!")
                            #init_page()
                            st.experimental_rerun()
                        if confirm:
                            #if alertbox('Are you sure that the transaction is completed?'):
                            run_query('UPDATE posts SET posts.status = "not available" WHERE posts.id = {0};'.format(post[0]))
                            conn.commit()
                            st.success("successfully unreserved!")
                            #init_page()
                            st.experimental_rerun()
                                
                    else:
                        back = st.form_submit_button('back')
                        st.error("This post is already claimed!")
                        
                            #init_page()
                            #st.experimental_rerun()
                else:
                    st.error("You must be logged in to do that!")


def print_offer(data, str):
    cnt = 0
    for post in data:
        cnt += 1
        with st.form(str + "post #{0}".format(cnt)):
            view, submit = st.columns([5, 1])
            with view:
                st.text("medicine: {0}".format(post[1]))
                st.text("quantity available: {0}".format(post[2]))
                st.text("supplier: {0}".format(post[4]))
                st.text("contact: {0}".format(post[5]))
                if post[3] == 'available':
                    st.success("status: {0}".format(post[3]))
                elif post[3] == 'pending':
                    st.warning("status: {0}".format(post[3]))  
                elif post[3] == 'not available':
                    st.error("status: {0}".format(post[3]))

            with submit:             
                
                if st.session_state['authentication_status'] == True:
                    if post[3] == 'available' or post[3] == 'pending':
                        remove = st.form_submit_button("Remove")
                        if remove:
                            run_query('UPDATE posts SET posts.status = "removed" WHERE posts.id = {0};'.format(post[0]))
                            st.success("successfully reserved!")
                            #init_page()
                            conn.commit()
                            st.experimental_rerun()
                    elif post[3] == 'removed':
                        st.form_submit_button('back')
                        st.error('You have removed this post!')           
                    else:
                        back = st.form_submit_button('back')
                        st.error("This post is already claimed!")
                        
                            #init_page()
                            #st.experimental_rerun()
                else:
                    st.error("You must be logged in to do that!")
 
                                



def search_terms(search_term, quantity):
    data_all = run_query('SELECT posts.medicine_name, posts.quantity, posts.status, users.name, users.email FROM posts JOIN users ON posts.from_user_id = users.id;')
    data = run_query('SELECT posts.id, posts.medicine_name, posts.quantity, posts.status, users.name, users.email FROM posts JOIN users ON posts.from_user_id = users.id WHERE posts.medicine_name = "{0}" AND posts.quantity >= {1} ORDER BY posts.quantity;'.format(search_term, quantity))
    #data = run_query('SELECT * FROM posts;'.format(search_term, quantity))
    st.write(data_all)

    st.subheader("Search results:")
    if len(data) == 0:
        st.error("No search matched!")
    else:
        st.success("{0} search matched!".format(len(data)))
        print_search(data, 'Search ')
    


def search_box():
    
    if st.session_state['page'] == "Home":
        #st.subheader("Ho  
        with st.form("my_form"):
            #st.write("Inside the form")
            #slider_val = st.slider("Form slider")
            #checkbox_val = st.checkbox("Form checkbox")

            # Every form must have a submit button.

            nav1, nav2, nav3, nav4 = st.columns([3, 2, 1, 1])

            with nav1:
                name = st.selectbox("select medicine", ["布洛芬", "鸡蛋"])
            with nav2:
                quantity = st.number_input("quantity", 1, 10)
            with nav3:
                st.text("request ")
                submitted = st.form_submit_button("Request")
            with nav4:
                st.text("offer ")
                submitted2 = st.form_submit_button("Offer")   

            if submitted:
                st.success("searched medicine: {0} quantity: {1}".format(name, quantity))
                st.session_state['searching'] = True
            if submitted2:
                
                if st.session_state['authentication_status'] == True:
                    st.success("successfully created medicine: {0} quantity: {1}".format(name, quantity))
                    run_query('INSERT INTO posts (from_user_id, medicine_name, quantity, status) VALUES ({0}, "{1}", {2}, "available");'.format(st.session_state['user'][0][0], name, quantity))
                else:
                    st.error('You must be logged in to do that!')
        with st.container():
            if (st.session_state['searching'] == True):
                search_terms(name, quantity)
                

def show_transactions():
    if st.session_state['page'] == 'User':
        if st.session_state['authentication_status'] == True:
            st.success('Welcome')
            datato = run_query('SELECT posts.id, posts.medicine_name, posts.quantity, posts.status, users.name, users.email FROM posts JOIN users ON posts.from_user_id = users.id WHERE posts.to_user_id = {0} ORDER BY posts.quantity;'.format(st.session_state['user'][0][0]))
            st.subheader('Requests:')
            print_search(datato, 'request ')
            datafrom = run_query('SELECT posts.id, posts.medicine_name, posts.quantity, posts.status, users.name, users.email FROM posts JOIN users ON posts.from_user_id = users.id WHERE posts.from_user_id = {0} ORDER BY posts.quantity;'.format(st.session_state['user'][0][0]))
            st.subheader('Offers:')
            print_offer(datafrom, 'offer ')
        else:
            st.error('You must be logged in to view this!')


def main():


    #st.session_state['page'] = st.selectbox("Menu", menu)

    
    init_sessions()
    init_menu()
    st.title("PILL")
    init_users()
    search_box()
    show_transactions()
    



if __name__ == '__main__':
    main()
