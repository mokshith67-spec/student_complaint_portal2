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

# Use session to keep login state
if "student_logged_in" not in st.session_state:
    st.session_state.student_logged_in = False
    st.session_state.roll = ""

# Database in temp path
conn = sqlite3.connect("/tmp/complaints.db", check_same_thread=False)
c = conn.cursor()

# Create tables
c.execute("""CREATE TABLE IF NOT EXISTS complaints
             (roll TEXT, title TEXT, description TEXT, category TEXT, status TEXT)""")

c.execute("""CREATE TABLE IF NOT EXISTS students
             (roll TEXT PRIMARY KEY, password TEXT)""")

# Insert students
students_data = [("101", "101"), ("102", "102"), ("103", "103")]
for student in students_data:
    c.execute("INSERT OR IGNORE INTO students VALUES (?, ?)", student)

conn.commit()

# Dashboard
if menu == "Dashboard":
    st.subheader("Complaint Dashboard")
    df = pd.read_sql_query("SELECT status, COUNT(*) as count FROM complaints GROUP BY status", conn)
    if not df.empty:
        st.bar_chart(df.set_index("status"))
    else:
        st.write("No complaints yet")

# Student Login
elif menu == "Student Login":

    if not st.session_state.student_logged_in:
        st.subheader("Student Login")

        roll = st.text_input("Roll Number")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            result = c.execute("SELECT * FROM students WHERE roll=? AND password=?", (roll, password)).fetchone()
            if result:
                st.session_state.student_logged_in = True
                st.session_state.roll = roll
                st.success("Login Successful")
                st.rerun()
            else:
                st.error("Invalid Roll Number or Password")

    else:
        st.success(f"Logged in as {st.session_state.roll}")

        if st.button("Logout"):
            st.session_state.student_logged_in = False
            st.session_state.roll = ""
            st.rerun()

        st.subheader("Submit Complaint")
        title = st.text_input("Complaint Title")
        description = st.text_area("Description")
        category = st.selectbox("Category", ["Hostel", "Food", "Academics", "Transport"])

        if st.button("Submit Complaint"):
            c.execute("INSERT INTO complaints VALUES (?, ?, ?, ?, ?)",
                      (st.session_state.roll, title, description, category, "Pending"))
            conn.commit()
            st.success("Complaint Submitted")

        st.subheader("My Complaints")
        c.execute("SELECT * FROM complaints WHERE roll=?", (st.session_state.roll,))
        data = c.fetchall()
        df = pd.DataFrame(data, columns=["Roll", "Title", "Description", "Category", "Status"])
        st.dataframe(df)

# Admin Login
elif menu == "Admin Login":
    st.subheader("Admin Login")

    admin_id = st.text_input("Admin ID")
    admin_pass = st.text_input("Admin Password", type="password")

    if admin_id == "admin" and admin_pass == "admin123":
        st.success("Admin Login Successful")

        st.subheader("All Complaints")
        df = pd.read_sql_query("SELECT rowid, * FROM complaints", conn)
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
