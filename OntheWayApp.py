import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px
import time

# Set page config for layout and title
st.set_page_config(
    page_title="ON THE WAY ARRIVAL SUMMARY \n Hunza Sugar Unit-1 ",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Global styling
st.markdown("""
    <style>
        /* Styling the title */
        .css-1v0mbdj { 
            font-size: 36px;
            font-weight: bold;
            color: #2F4F4F;
            text-align: center;
        }
        
        /* Sidebar styles */
        .css-1j9dxpz { 
            background-color: #f0f4f8;
        }

        .css-1wa3eu0 { 
            color: #008CBA;
            font-weight: bold;
        }

        /* Custom button styles */
        .stButton button {
            background-color: #008CBA;
            color: white;
            border-radius: 8px;
            font-weight: bold;
            padding: 10px 15px;
        }

        .stButton button:hover {
            background-color: #005F7A;
        }

        /* Footer style */
        .footer {
            position: fixed;
            bottom: 0;
            width: 100%;
            background-color: #333;
            color: white;
            padding: 5px 0;
            text-align: center;
            font-size: 14px;
        }

        .css-2trq6i {
            background-color: #f0f4f8;
            border-radius: 10px;
            padding: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# Streamlit app title
st.title("ON THE WAY ARRIVAL SUMMARY \n Hunza Sugar  Unit-1")
st.write("This Application is Designed for Evaluation of ELP On The Way Vehicles For Hunza Sugar Unit-1.")

# Sidebar for database connection parameters
st.sidebar.header("Database Connection")
server = st.sidebar.text_input("Server", placeholder="10.10.0.51:1433")
database = st.sidebar.text_input("Database", placeholder="ElpWebData")

# Fetch data function
def fetch_data(server, database):
    try:
        conn_str = f"mssql+pyodbc://sa:2avoid%hunzawb@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server+Server&Encrypt=yes&TrustServerCertificate=yes"
        engine = create_engine(conn_str)
        query = """
        SELECT DateofDeparture, LpCode,
               CASE 
                   WHEN LpCode IN ('2401', '2402', '2403', '2404', '2405', '2406', '2407', '2408', '2409') THEN 'AlipurBangla'
                   WHEN LpCode IN ('2410', '2411', '2412', '2413', '2414', '2415', '2416', '2417', '2418', '2419', '2420', '2421', '2422') THEN 'Satiana/Syedwala'
                   WHEN LpCode IN ('2428', '2429', '2430', '2431') THEN 'Shahkot'
                   WHEN LpCode IN ('2423','2424', '2425', '2426', '2427', '2432', '2433', '2434', '2435', '2436', '2437') THEN 'Nankana/Manawala'
                   WHEN LpCode IN ('2449', '2450', '2451', '2452', '2453', '2454', '2455', '2456', '2457', '2458', '2459', '2460', '2461') THEN 'Chiniot'
                   WHEN LpCode IN ('2438', '2439', '2440', '2441', '2442', '2443', '2444', '2445', '2446', '2447', '2448', '2462', '2463') THEN 'Jhumra'
               END AS Zone
        FROM ArrivingVehicles
        """
        data = pd.read_sql(query, engine)
        return data

    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

# Sidebar filters
def apply_filters(data):
    st.sidebar.header("Filters")
    unique_zones = data["Zone"].unique().tolist()
    selected_zones = st.sidebar.multiselect(
        "Select Zones", options=unique_zones, default=unique_zones
    )
    unique_dates = data["DateofDeparture"].unique().tolist()
    selected_dates = st.sidebar.multiselect(
        "Select Dates", options=unique_dates, default=[]
    )

    filtered_data = data[
        (data["Zone"].isin(selected_zones)) &
        (data["DateofDeparture"].isin(selected_dates))
    ]
    
    return filtered_data

# Main visualization
def display_chart(data):
    zone_summary = data.groupby("Zone").size().reset_index(name="Count")
    total_count = zone_summary["Count"].sum()

    chart = px.bar(
        zone_summary,
        x="Zone",
        y="Count",
        color="Zone", 
        title="Area Wise On The Way Statistics",
        labels={"Count": "Number of LP Codes", "Zone": "Zone"},
        text="Count",
        color_discrete_map={
            "AlipurBangla": "#636EFA",
            "Satiana/Syedwala": "#EF553B",
            "Shahkot": "#00CC96",
            "Nankana/Manawala": "#AB63FA",
            "Chiniot": "#FFA15A",
            "Jhumra": "#19D3F3",
        },
    )

    chart.update_layout(
        xaxis_title="Area Name ",
        yaxis_title="Number Of Unit",
        showlegend=False,
        title={'x': 0.5, 'xanchor': 'center', 'font': {'size': 22, 'color': '#333333'}},
        plot_bgcolor="#f7f7f7",
        paper_bgcolor="#ffffff",
        margin=dict(l=30, r=30, t=60, b=40),
        xaxis=dict(tickangle=-45),
    )

    st.plotly_chart(chart, use_container_width=True)
    st.write(f"### Total On The Way: {total_count}")

# Main app logic
if server and database:
    if "data" not in st.session_state:
        st.session_state.data = fetch_data(server, database)

    if st.button("Refresh Data"):
        st.session_state.data = fetch_data(server, database)

    if st.session_state.data is not None:
        filtered_data = apply_filters(st.session_state.data)
        display_chart(filtered_data)
    else:
        st.error("No data to display. Check your database connection.")

# Footer
st.markdown("""
    <div class="footer">
        Powered by Hunza IT Department Unit-1
    </div>
""", unsafe_allow_html=True)
