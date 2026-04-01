import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="Student Complaint Portal", layout="wide")

st.title("Student Complaint Portal")

menu = st.sidebar.selectbox("Menu", [
    "Dashboard",
    "Student Complaint",
    "Admin Login"
])

# Database
conn = sqlite3.connect("complaints.db")
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS complaints
             (name TEXT, title TEXT, description TEXT, category TEXT, status TEXT)""")
conn.commit()

# Dashboard
if menu == "Dashboard":
    st.subheader("Complaint Dashboard")
    data = pd.read_sql("SELECT status, COUNT(*) as count FROM complaints GROUP BY status", conn)
    if not data.empty:
        st.bar_chart(data.set_index("status"))
    else:
        st.write("No complaints yet")

# Student Complaint
elif menu == "Student Complaint":
    st.subheader("Submit Complaint")

    name = st.text_input("Your Name")
    title = st.text_input("Complaint Title")
    description = st.text_area("Description")
    category = st.selectbox("Category", ["Hostel", "Food", "Academics", "Transport"])

    if st.button("Submit Complaint"):
        c.execute("INSERT INTO complaints VALUES (?, ?, ?, ?, ?)",
                  (name, title, description, category, "Pending"))
        conn.commit()
        st.success("Complaint Submitted Successfully")

# Admin Login
elif menu == "Admin Login":
    st.subheader("Admin Login")

    password = st.text_input("Enter Admin Password", type="password")

    if password == "admin123":
        st.success("Login Successful")

        st.subheader("All Complaints")
        df = pd.read_sql("SELECT rowid, * FROM complaints", conn)
        st.dataframe(df)

        cid = st.number_input("Enter Complaint ID", min_value=1)
        status = st.selectbox("Update Status", ["Pending", "In Progress", "Resolved"])

        if st.button("Update Status"):
            c.execute("UPDATE complaints SET status=? WHERE rowid=?", (status, cid))
            conn.commit()
            st.success("Status Updated")

    elif password != "":
        st.error("Wrong Password")

conn.close()
