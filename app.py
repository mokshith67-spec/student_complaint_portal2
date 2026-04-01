import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="Student Complaint Portal", layout="wide")

st.title("Student Complaint Management System")

menu = st.sidebar.selectbox("Menu", [
    "Dashboard",
    "Student Login",
    "Admin Login"
])

# Database
conn = sqlite3.connect("complaints.db")
c = conn.cursor()

# Tables
c.execute("""CREATE TABLE IF NOT EXISTS complaints
             (roll TEXT, title TEXT, description TEXT, category TEXT, status TEXT)""")

c.execute("""CREATE TABLE IF NOT EXISTS students
             (roll TEXT, password TEXT)""")

# Insert demo students
students_data = [("101", "101"), ("102", "102"), ("103", "103")]
c.executemany("INSERT OR IGNORE INTO students VALUES (?, ?)", students_data)

conn.commit()

# Dashboard
if menu == "Dashboard":
    st.subheader("Complaint Dashboard")
    data = pd.read_sql("SELECT status, COUNT(*) as count FROM complaints GROUP BY status", conn)
    if not data.empty:
        st.bar_chart(data.set_index("status"))
    else:
        st.write("No complaints yet")

# Student Login
elif menu == "Student Login":
    st.subheader("Student Login")

    roll = st.text_input("Roll Number")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        result = c.execute("SELECT * FROM students WHERE roll=? AND password=?", (roll, password)).fetchone()
        if result:
            st.success("Login Successful")

            st.subheader("Submit Complaint")
            title = st.text_input("Complaint Title")
            description = st.text_area("Description")
            category = st.selectbox("Category", ["Hostel", "Food", "Academics", "Transport"])

            if st.button("Submit Complaint"):
                c.execute("INSERT INTO complaints VALUES (?, ?, ?, ?, ?)",
                          (roll, title, description, category, "Pending"))
                conn.commit()
                st.success("Complaint Submitted")

            st.subheader("My Complaints")
            df = pd.read_sql(f"SELECT * FROM complaints WHERE roll='{roll}'", conn)
            st.dataframe(df)

        else:
            st.error("Invalid Roll Number or Password")

# Admin Login
elif menu == "Admin Login":
    st.subheader("Admin Login")

    admin_id = st.text_input("Admin ID")
    admin_pass = st.text_input("Admin Password", type="password")

    if admin_id == "admin" and admin_pass == "admin123":
        st.success("Admin Login Successful")

        st.subheader("All Complaints")
        df = pd.read_sql("SELECT rowid, * FROM complaints", conn)
        st.dataframe(df)

        cid = st.number_input("Enter Complaint ID", min_value=1)
        status = st.selectbox("Update Status", ["Pending", "In Progress", "Resolved"])

        if st.button("Update Status"):
            c.execute("UPDATE complaints SET status=? WHERE rowid=?", (status, cid))
            conn.commit()
            st.success("Status Updated")

    elif admin_id != "":
        st.error("Wrong Admin ID or Password")

conn.close()
