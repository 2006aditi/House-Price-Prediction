
import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

np.random.seed(42)

# Sample locality rates (illustrative, not verified market rates)
locations = {
    "CIDCO": 4800,
    "Garkheda": 5200,
    "Osmanpura": 5800,
    "N-1": 4500,
    "N-2": 4700,
    "N-3": 4900,
    "Satara Parisar": 4200,
    "Beed Bypass": 4600,
    "Waluj": 3200,
    "Seven Hills": 5500,
    "Jyoti Nagar": 6000,
    "Shahnoorwadi": 5300,
    "Ulkanagari": 6200,
    "Padegaon": 3800,
    "Harsul": 3500,
    "Chikalthana": 4000,
    "Railway Station": 5000
}

data = []

for i in range(1500):

    area = np.random.randint(450, 4001)
    bedrooms = np.random.randint(1, 6)
    bathrooms = np.random.randint(1, 5)
    age = np.random.randint(0, 31)
    parking = np.random.randint(0, 4)

    # New gallery feature
    gallery = np.random.randint(0, 6)

    floor = np.random.randint(0, 21)

    furnishing = np.random.choice([
        "Unfurnished",
        "Semi-Furnished",
        "Furnished"
    ])

    property_type = np.random.choice([
        "Apartment",
        "Independent House",
        "Villa"
    ])

    facing = np.random.choice([
        "East", "West", "North", "South"
    ])

    location = np.random.choice(list(locations.keys()))

    price_per_sqft = locations[location]

    furnishing_bonus = {
        "Unfurnished": 0,
        "Semi-Furnished": 150000,
        "Furnished": 300000
    }[furnishing]

    type_bonus = {
        "Apartment": 0,
        "Independent House": 400000,
        "Villa": 900000
    }[property_type]

    price = (
        area * price_per_sqft
        + bedrooms * 80000
        + bathrooms * 50000
        + gallery * 60000
        + parking * 80000
        + floor * 8000
        + furnishing_bonus
        + type_bonus
        - age * 15000
        + np.random.randint(-200000, 200001)
    )

    price = max(price, 400000)

    data.append({
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
        "location": location,
        "price": price
    })

df = pd.DataFrame(data)

file_path = DATA_DIR / "chhatrapati_sambhajinagar_house_prices.csv"
df.to_csv(file_path, index=False)

print("Dataset created successfully!")
print("Total records:", len(df))
print("Saved at:", file_path)
print(df.head())
