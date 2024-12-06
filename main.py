import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
from config import DATABASE_CONFIG

# Add custom CSS for colors, styling, and animations
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
            font-family: 'Verdana', sans-serif; /* Changed font to Verdana */
        }
        h2, h3 {
            color: #2e8b57;
        }
        .css-1yoh8k0 {
            background-color: #3cb371;
        }
        .css-1p0d5p5 {
            color: #ff7f50;
        }
        .css-ffhzg2 {
            color: #8a2be2;
        }
        .streamlit-expanderHeader {
            color: #d2691e;
        }
        .css-1emrehy {
            background-color: #ff6347;
            color: white;
        }
        .animated {
            animation-duration: 1.5s;
            animation-fill-mode: both;
        }
        .fadeIn {
            animation-name: fadeIn;
        }
        @keyframes fadeIn {
            0% { opacity: 0; }
            100% { opacity: 1; }
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

def calculate_team_performance():
    query = """
    SELECT 
        EXTRACT(YEAR FROM date) AS year, 
        home_team AS team, 
        CASE WHEN home_score > away_score THEN 1 ELSE 0 END AS win
    FROM results
    UNION ALL
    SELECT 
        EXTRACT(YEAR FROM date) AS year, 
        away_team AS team, 
        CASE WHEN away_score > home_score THEN 1 ELSE 0 END AS win
    FROM results
    """
    
    data = execute_query(query)
    
    if data is not None:
        df = pd.DataFrame(data)
        # Group by team and year, then calculate the winning percentage
        team_performance = df.groupby(['year', 'team'])['win'].agg(['sum', 'count'])
        team_performance['win_percentage'] = (team_performance['sum'] / team_performance['count']) * 100
        team_performance.reset_index(inplace=True)
        
        return team_performance
    else:
        return None

def plot_team_performance(team_performance, team_name):
    team_data = team_performance[team_performance['team'] == team_name]
    fig = px.line(team_data, x='year', y='win_percentage', title=f"{team_name} Performance - Winning Percentage Over the Years",
                  labels={"win_percentage": "Winning Percentage", "year": "Year"})
    st.plotly_chart(fig)

def main():
    # Top Navigation Menu
    menu = st.selectbox(
        "Navigation",
        ["Dashboard", "Data Operations", "Statistics and Trends", "Advanced Querying"],
        index=0
    )

    # Display Image on Landing Page
    st.markdown('<h1 style="position: absolute; top: 10px; left: 10px;">Welcome to the International Football Database Portal</h1>', unsafe_allow_html=True)
    image_path = "/Users/shreyansh/PycharmProjects/pythonProject/imago1002614356h.jpg"  # Adjust this path based on where you place the image
    st.image(image_path, caption="Football Image", use_column_width=True)

    if menu == "Dashboard":
        st.subheader("Welcome to the International Football Database Portal")
        
    elif menu == "Statistics and Trends":
        st.subheader("Explore Statistics and Trends")
        trend_option = st.selectbox(
            "Choose Analysis",
            ["Top Scoring Teams", "Penalty Shootout Matches", "High-Scoring Matches", "Winning Teams", "Team Performance"]
        )

        if trend_option == "Top Scoring Teams":
            query = """
            SELECT team, SUM(goals) AS total_goals
            FROM (
                SELECT home_team AS team, home_score AS goals FROM results
                UNION ALL
                SELECT away_team AS team, away_score AS goals FROM results
            ) AS combined_scores
            GROUP BY team
            ORDER BY total_goals DESC
            LIMIT 10;
            """
            data = execute_query(query)
            if data is not None:
                st.dataframe(data)

        elif trend_option == "Penalty Shootout Matches":
            query = """
            SELECT * FROM shootouts
            ORDER BY date DESC
            LIMIT 10;
            """
            data = execute_query(query)
            if data is not None:
                st.dataframe(data)

        elif trend_option == "High-Scoring Matches":
            query = """
            SELECT date, home_team, away_team, home_score, away_score
            FROM results
            WHERE (home_score + away_score) > 10
            ORDER BY (home_score + away_score) DESC
            LIMIT 10;
            """
            data = execute_query(query)
            if data is not None:
                st.dataframe(data)

        elif trend_option == "Winning Teams":
            query = """
            SELECT team, COUNT(*) AS wins
            FROM (
                SELECT home_team AS team FROM results WHERE home_score > away_score
                UNION ALL
                SELECT away_team AS team FROM results WHERE away_score > home_score
            ) AS winners
            GROUP BY team
            ORDER BY wins DESC
            LIMIT 10;
            """
            data = execute_query(query)
            if data is not None:
                st.dataframe(data)

        elif trend_option == "Team Performance":
            st.subheader("Team Performance: Winning Percentage Over the Years")
            team_performance = calculate_team_performance()
            if team_performance is not None:
                # Get the list of unique teams for selection
                teams = team_performance['team'].unique()
                selected_team = st.selectbox("Select Team", teams)
                plot_team_performance(team_performance, selected_team)
            else:
                st.error("Error fetching team performance data.")

    elif menu == "Advanced Querying":
        st.subheader("Custom SQL Queries")
        custom_query = st.text_area("Enter your SQL query here:")
        if st.button("Run Query"):
            data = execute_query(custom_query)
            if data is not None:
                st.dataframe(data)

if __name__ == "__main__":
    main()

