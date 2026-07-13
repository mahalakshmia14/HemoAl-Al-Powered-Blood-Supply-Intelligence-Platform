import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import joblib

df = pd.read_csv("dataset/blood_inventory.csv")

X = df[[
    "Emergency_Requests",
    "Daily_Usage",
    "Units_Available"
]]

y = df["Future_Demand"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = RandomForestRegressor()

model.fit(X_train, y_train)

joblib.dump(
    model,
    "blood_demand_model.pkl"
)

print("Model Created")