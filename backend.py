
from pathlib import Path
import joblib
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = (
    BASE_DIR / "models" / "house_price_model.joblib"
)

def predict_house_price(property_details):

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            "Model not found. Run python train_model.py first."
        )

    model = joblib.load(MODEL_PATH)

    input_data = pd.DataFrame([property_details])

    prediction = model.predict(input_data)[0]

    return float(prediction)
