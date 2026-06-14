import streamlit as st
import re
import sqlite3
import pandas as pd
from datetime import datetime

# ==========================
# DATABASE CONNECTION
# ==========================

conn = sqlite3.connect("nayepankh.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS applicants(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    phone TEXT,
    internship TEXT,
    college TEXT,
    applied_date TEXT
)
""")

conn.commit()

# ==========================
# PAGE CONFIG
# ==========================

st.set_page_config(
    page_title="NayePankh Foundation",
    page_icon="🎓",
    layout="wide"
)

# ==========================
# CUSTOM HEADER
# ==========================

st.markdown("""
# 🎓 NayePankh Foundation
### Internship Application Management System
---
""")

# ==========================
# SIDEBAR
# ==========================

st.sidebar.image(
    "https://img.icons8.com/color/96/student-center.png",
    width=80
)

st.sidebar.title("🌱 NayePankh Foundation")

menu = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Add Applicant",
        "View Applicants",
        "Reports"
    ]
)

# ==========================
# DASHBOARD
# ==========================

if menu == "Dashboard":

    total = cursor.execute(
        "SELECT COUNT(*) FROM applicants"
    ).fetchone()[0]

    python_count = cursor.execute(
        "SELECT COUNT(*) FROM applicants WHERE internship='Python Development'"
    ).fetchone()[0]

    ai_count = cursor.execute(
        "SELECT COUNT(*) FROM applicants WHERE internship='Artificial Intelligence'"
    ).fetchone()[0]

    ml_count = cursor.execute(
        "SELECT COUNT(*) FROM applicants WHERE internship='Machine Learning'"
    ).fetchone()[0]

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("👥 Total Applicants", total)
    c2.metric("🐍 Python", python_count)
    c3.metric("🤖 AI", ai_count)
    c4.metric("🧠 ML", ml_count)

    st.divider()

    st.subheader("📊 Internship Statistics")

    chart_data = pd.DataFrame({
        "Internship": [
            "Python",
            "AI",
            "Machine Learning"
        ],
        "Applicants": [
            python_count,
            ai_count,
            ml_count
        ]
    })

    st.bar_chart(
        chart_data.set_index("Internship")
    )

# ==========================
# ADD APPLICANT
# ==========================

elif menu == "Add Applicant":

    st.header("➕ Add New Applicant")

    with st.form("application_form"):

        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("Full Name *")
            email = st.text_input("Email *", placeholder="example@gmail.com")

        with col2:
            phone = st.text_input("Phone Number *", placeholder="10 digit mobile number")
            college = st.text_input("College Name *")

        internship = st.selectbox(
            "Internship Domain",
            [
                "Python Development",
                "Artificial Intelligence",
                "Machine Learning",
                "Data Analytics",
                "Web Development",
                "Java Development"
            ]
        )

        submit = st.form_submit_button(
            "Submit Application"
        )

        if submit:
            if not name.strip():
                st.error("Name is required")
            elif not email.strip():
                st.error("Email is required")
            elif not phone.strip():
                st.error("Phone number is required")
            elif not college.strip():
                st.error("College Name is required")
            elif not re.match(r'^[a-zA-Z0-9._%+-]+@gmail\.com$',email):
                st.error("Enter a valid gmail address(example@gmail.com)")
            elif not phone.isdigit():
                st.error("Phone number must contain exactly 10 digits")
            existing=cursor.execute( "SELECT * FROM applicants WHERE email=?",
        (email,)).fetchone()
            if existing:
                st.error("This email is alread registered")

            

            else:

                cursor.execute("""
                INSERT INTO applicants(
                    name,
                    email,
                    phone,
                    internship,
                    college,
                    applied_date
                )
                VALUES(?,?,?,?,?,?)
                """, (
                    name,
                    email,
                    phone,
                    internship,
                    college,
                    datetime.now().strftime("%d-%m-%Y")
                ))

                conn.commit()

                st.success(
                    "✅ Applicant Added Successfully"
                )

                st.rerun()

# ==========================
# VIEW APPLICANTS
# ==========================

elif menu == "View Applicants":

    st.header("📋 Applicants")

    col1, col2 = st.columns(2)

    with col1:
        search = st.text_input(
            "🔍 Search Applicant"
        )

    with col2:
        internship_filter = st.selectbox(
            "Filter Internship",
            [
                "All",
                "Python Development",
                "Artificial Intelligence",
                "Machine Learning",
                "Data Analytics",
                "Web Development",
                "Java Development"
            ]
        )

    query = "SELECT * FROM applicants WHERE 1=1"

    if search:
        query += f" AND name LIKE '%{search}%'"

    if internship_filter != "All":
        query += f" AND internship='{internship_filter}'"

    data = pd.read_sql_query(
        query,
        conn
    )

    st.dataframe(
        data,
        use_container_width=True
    )

    st.divider()

    st.subheader("🗑️ Delete Applicant")

    if not data.empty:

        applicant_options = {
            f"{row['id']} - {row['name']}": row['id']
            for _, row in data.iterrows()
        }

        selected_applicant = st.selectbox(
            "Select Applicant",
            list(applicant_options.keys())
        )

        if st.button(
            "Delete Applicant",
            type="primary"
        ):

            selected_id = applicant_options[
                selected_applicant
            ]

            cursor.execute(
                "DELETE FROM applicants WHERE id=?",
                (selected_id,)
            )

            conn.commit()

            st.success(
                f"✅ {selected_applicant} deleted successfully!"
            )

            st.rerun()

    else:
        st.info(
            "No applicants found."
        )

# ==========================
# REPORTS
# ==========================

elif menu == "Reports":

    st.header("📈 Reports")

    data = pd.read_sql_query(
        "SELECT * FROM applicants",
        conn
    )

    st.dataframe(
        data,
        use_container_width=True
    )

    st.subheader("📊 Quick Summary")

    st.write(
        f"Total Applicants: {len(data)}"
    )

    csv = data.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="⬇ Download CSV Report",
        data=csv,
        file_name="Applicants_Report.csv",
        mime="text/csv"
    )

    st.success(
        "Report ready for download."
    )