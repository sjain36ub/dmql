import streamlit as st
import pandas as pd
import psycopg2
from config import DATABASE_CONFIG

st.markdown("""
    <style>
        body {
            background-color: #f0f8ff;
            color: #333333;
            font-family: 'Arial', sans-serif;
        }
        h1 {
            color: #2e8b57;
            font-size: 45px;
            font-weight: bold;
            font-family: 'Verdana', sans-serif;
        }
        h2, h3 {
            color: #2e8b57;
        }
    </style>
""", unsafe_allow_html=True)

def connect_to_db():
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        return conn
    except Exception as e:
        st.error(f"Error connecting to the database: {e}")
        return None

def execute_query(query, params=None):
    conn = connect_to_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            if query.strip().upper().startswith("SELECT"):
                results = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                df = pd.DataFrame(results, columns=columns)
                return df
            conn.commit()
        except Exception as e:
            st.error(f"Error executing query: {e}")
        finally:
            cursor.close()
            conn.close()

def main():
    menu = st.selectbox(
        "Navigation",
        ["Dashboard", "Statistics and Trends", "Advanced Querying"],
        index=0
    )

    if menu == "Dashboard":
        st.title("Welcome to the International Football Database Portal")
        st.subheader("Explore football data and trends.")
        st.image("imago1002614356h.jpg", caption="Football Image", use_column_width=True)

    elif menu == "Statistics and Trends":
        st.subheader("Explore Statistics and Trends")

    elif menu == "Advanced Querying":
        st.subheader("Custom SQL Queries")
        custom_query = st.text_area("Enter your SQL query here:")
        if st.button("Run Query"):
            data = execute_query(custom_query)
            if data is not None:
                st.dataframe(data)

if __name__ == "__main__":
    main()
