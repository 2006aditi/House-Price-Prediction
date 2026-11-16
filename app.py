
import streamlit as st
import pandas as pd
import sqlite3
from pathlib import Path
import plotly.express as px
from backend import predict_house_price

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "chhatrapati_sambhajinagar_house_prices.csv"
MODEL_DIR = BASE_DIR / "models"
DB_PATH = BASE_DIR / "data" / "prediction_history.db"

st.set_page_config(
    page_title="Sambhajinagar House Price Prediction",
    page_icon="🏠",
    layout="wide"
)

# Custom design
st.markdown("""
<style>
.stApp {
    background-color: #f3f6fb;
}
.block-container {
    max-width: 1200px;
    padding-top: 2rem;
}
.hero {
    background: linear-gradient(120deg, #14213d, #315c8c);
    padding: 30px;
    border-radius: 15px;
    color: white;
    margin-bottom: 25px;
}
.hero h1 {
    color: white;
}
div[data-testid="stMetric"] {
    background: white;
    padding: 15px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

# Database functions
def create_database():
    con = sqlite3.connect(DB_PATH)
    con.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            location TEXT,
            area INTEGER,
            bedrooms INTEGER,
            gallery INTEGER,
            predicted_price REAL
        )
    """)
    con.commit()
    con.close()


def save_prediction(details, price):
    con = sqlite3.connect(DB_PATH)

    con.execute("""
        INSERT INTO predictions
        (location, area, bedrooms, gallery, predicted_price)
        VALUES (?, ?, ?, ?, ?)
    """, (
        details["location"],
        details["area_sqft"],
        details["bedrooms"],
        details["gallery"],
        price
    ))

    con.commit()
    con.close()


def get_history():
    con = sqlite3.connect(DB_PATH)

    history = pd.read_sql_query(
        "SELECT * FROM predictions ORDER BY id DESC",
        con
    )

    con.close()
    return history


# Check dataset
if not DATA_PATH.exists():
    st.error("Dataset not found. Run python create_dataset.py")
    st.stop()

df = pd.read_csv(DATA_PATH)
locations = sorted(df["location"].unique())

create_database()

# Header
st.markdown("""
<div class="hero">
    <h1>🏠 Sambhajinagar House Price Prediction</h1>
    
</div>
""", unsafe_allow_html=True)

# Navigation
page = st.sidebar.radio(
    "Navigation",
    [
        "Home",
        "Market Dashboard",
        "Compare Properties",
        "Prediction History",
        "About Project"
    ]
)

# HOME PAGE
if page == "Home":

    st.header("Enter House Details")

    with st.form("prediction_form"):

        col1, col2 = st.columns(2)

        with col1:

            area = st.number_input(
                "Area (Square Feet)",
                300, 6000, 1200, 50
            )

            bedrooms = st.selectbox(
                "Number of Bedrooms",
                [1, 2, 3, 4, 5, 6]
            )

            bathrooms = st.selectbox(
                "Number of Bathrooms",
                [1, 2, 3, 4, 5, 6]
            )

            gallery = st.number_input(
                "Number of Galleries",
                0, 5, 1
            )

            age = st.number_input(
                "Property Age (Years)",
                0, 100, 5
            )

        with col2:

            parking = st.selectbox(
                "Parking Spaces",
                [0, 1, 2, 3]
            )

            floor = st.number_input(
                "Floor Number",
                0, 50, 3
            )

            furnishing = st.selectbox(
                "Furnishing",
                [
                    "Unfurnished",
                    "Semi-Furnished",
                    "Furnished"
                ]
            )

            property_type = st.selectbox(
                "Property Type",
                [
                    "Apartment",
                    "Independent House",
                    "Villa"
                ]
            )

            facing = st.selectbox(
                "Facing Direction",
                ["East", "West", "North", "South"]
            )

        location = st.selectbox(
            "Select Location",
            locations
        )

        submit = st.form_submit_button(
            "🔍 Predict House Price",
            use_container_width=True
        )

    if submit:

        details = {
            "area_sqft": area,
            "bedrooms": bedrooms,
            "bathrooms": bathrooms,
            "age_years": age,
            "parking": parking,
            "gallery": gallery,
            "floor": floor,
            "furnishing": furnishing,
            "property_type": property_type,
            "facing": facing,
            "location": location
        }

        try:
            prediction = predict_house_price(details)

            save_prediction(details, prediction)

            st.success("Prediction completed successfully!")

            st.metric(
                "Estimated House Price",
                f"₹ {prediction:,.0f}"
            )

            st.write(
                f"**Property:** {area} sq.ft. | "
                f"{bedrooms} BHK | {gallery} Galleries | {location}"
            )

            st.info(
                f"Illustrative estimate range: "
                f"₹ {prediction * 0.93:,.0f} – "
                f"₹ {prediction * 1.07:,.0f}"
            )

        except Exception as e:
            st.error(f"Prediction Error: {e}")


# MARKET DASHBOARD
elif page == "Market Dashboard":

    st.header("📊 Property Market Dashboard")

    c1, c2, c3 = st.columns(3)

    c1.metric("Total Properties", len(df))

    c2.metric(
        "Average Sample Price",
        f"₹ {df['price'].mean():,.0f}"
    )

    c3.metric(
        "Average Area",
        f"{df['area_sqft'].mean():,.0f} sq.ft."
    )

    location_prices = (
        df.groupby("location")["price"]
        .mean()
        .reset_index()
        .sort_values("price", ascending=False)
    )

    fig = px.bar(
        location_prices,
        x="location",
        y="price",
        title="Average Generated House Price by Location",
        labels={
            "location": "Location",
            "price": "Average Price (₹)"
        }
    )

    fig.update_layout(xaxis_tickangle=-45)

    st.plotly_chart(fig, use_container_width=True)

    fig2 = px.scatter(
        df,
        x="area_sqft",
        y="price",
        color="property_type",
        hover_data=["location", "bedrooms", "gallery"],
        title="Area vs House Price"
    )

    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Explore Dataset")

    selected_location = st.selectbox(
        "Filter by Location",
        ["All"] + locations
    )

    if selected_location == "All":
        filtered_df = df
    else:
        filtered_df = df[
            df["location"] == selected_location
        ]

    st.dataframe(filtered_df, use_container_width=True)

    st.download_button(
        "Download Dataset CSV",
        filtered_df.to_csv(index=False),
        "sambhajinagar_properties.csv",
        "text/csv"
    )


# PROPERTY COMPARISON
elif page == "Compare Properties":

    st.header("⚖️ Compare Two Properties")

    col1, col2 = st.columns(2)

    def property_form(column, number):
        with column:
            st.subheader(f"Property {number}")

            loc = st.selectbox(
                f"Location {number}",
                locations,
                key=f"loc{number}"
            )

            area = st.number_input(
                f"Area {number} (sq.ft.)",
                300, 6000, 1200,
                key=f"area{number}"
            )

            bedrooms = st.selectbox(
                f"Bedrooms {number}",
                [1, 2, 3, 4, 5, 6],
                key=f"bed{number}"
            )

            bathrooms = st.selectbox(
                f"Bathrooms {number}",
                [1, 2, 3, 4, 5, 6],
                key=f"bath{number}"
            )

            gallery = st.number_input(
                f"Galleries {number}",
                0, 5, 1,
                key=f"gallery{number}"
            )

            age = st.number_input(
                f"Property Age {number}",
                0, 100, 5,
                key=f"age{number}"
            )

            parking = st.selectbox(
                f"Parking {number}",
                [0, 1, 2, 3],
                key=f"parking{number}"
            )

            floor = st.number_input(
                f"Floor {number}",
                0, 50, 3,
                key=f"floor{number}"
            )

            furnishing = st.selectbox(
                f"Furnishing {number}",
                ["Unfurnished", "Semi-Furnished", "Furnished"],
                key=f"furn{number}"
            )

            property_type = st.selectbox(
                f"Property Type {number}",
                ["Apartment", "Independent House", "Villa"],
                key=f"type{number}"
            )

            facing = st.selectbox(
                f"Facing {number}",
                ["East", "West", "North", "South"],
                key=f"face{number}"
            )

            return {
                "area_sqft": area,
                "bedrooms": bedrooms,
                "bathrooms": bathrooms,
                "age_years": age,
                "parking": parking,
                "gallery": gallery,
                "floor": floor,
                "furnishing": furnishing,
                "property_type": property_type,
                "facing": facing,
                "location": loc
            }

    property1 = property_form(col1, 1)
    property2 = property_form(col2, 2)

    if st.button("Compare Prices", use_container_width=True):

        try:
            price1 = predict_house_price(property1)
            price2 = predict_house_price(property2)

            c1, c2 = st.columns(2)

            c1.metric("Property 1 Price", f"₹ {price1:,.0f}")
            c2.metric("Property 2 Price", f"₹ {price2:,.0f}")

            st.info(
                f"Estimated price difference: "
                f"₹ {abs(price1 - price2):,.0f}"
            )

        except Exception as e:
            st.error(f"Comparison Error: {e}")


# PREDICTION HISTORY
elif page == "Prediction History":

    st.header("🧾 Prediction History")

    history = get_history()

    if history.empty:
        st.info("No prediction history available yet.")

    else:
        st.metric("Total Predictions", len(history))

        st.dataframe(
            history,
            use_container_width=True
        )

        st.download_button(
            "Download Prediction History",
            history.to_csv(index=False),
            "prediction_history.csv",
            "text/csv"
        )

        if st.button("Clear History"):
            con = sqlite3.connect(DB_PATH)
            con.execute("DELETE FROM predictions")
            con.commit()
            con.close()
            st.success("Prediction history cleared.")
            st.rerun()


# ABOUT PROJECT
elif page == "About Project":

    st.header("About This Project")

    st.write("""
    This project predicts house prices in Chhatrapati Sambhajinagar
    using Machine Learning.

    Main Algorithm:
    - Linear Regression

    Additional Model:
    - Random Forest Regression

    Features:
    1. Area
    2. Bedrooms
    3. Bathrooms
    4. Number of Galleries
    5. Property Age
    6. Parking
    7. Floor
    8. Furnishing
    9. Property Type
    10. Facing Direction
    11. Location

    Evaluation Metrics:
    - MAE
    - RMSE
    - R2 Score

    Dataset Split:
    - 80% Training
    - 20% Testing
    """)

    metrics_path = MODEL_DIR / "model_metrics.csv"

    if metrics_path.exists():
        st.subheader("Model Comparison")
        metrics = pd.read_csv(metrics_path)
        st.dataframe(metrics, use_container_width=True)

    st.warning(
        "This project uses synthetic educational data. "
        "Its predictions are not verified real-estate valuations."
    )

st.divider()

st.markdown(
    "<center>Chhatrapati Sambhajinagar House Price Prediction | "
    "B.Tech CSE Machine Learning Project</center>",
    unsafe_allow_html=True
)
