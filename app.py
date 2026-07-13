
import streamlit as st
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib

st.set_page_config(page_title="HemoAI Premium", page_icon="🩸", layout="wide")

df = pd.read_csv("dataset/blood_inventory.csv")
model = joblib.load("blood_demand_model.pkl")

st.markdown("""
<style>
.main{background:#f4f7fb;}
.hero{
background:linear-gradient(135deg,#7f0000,#b71c1c,#e53935);
padding:55px;border-radius:30px;color:white;margin-bottom:25px;
}
.metric{
background:white;padding:25px;border-radius:20px;
box-shadow:0 4px 16px rgba(0,0,0,.08);text-align:center;
}
.result{
background:linear-gradient(135deg,#8b0000,#d62828);
padding:25px;border-radius:20px;color:white;margin-bottom:15px;
}
.alert{
background:#fff1f1;border-left:8px solid red;
padding:20px;border-radius:15px;margin-bottom:10px;
}
</style>
""", unsafe_allow_html=True)

page = st.sidebar.radio(
    "🩸 Navigation",
    ["🏠 Home","🔍 Search","📊 Analytics","🚨 Emergency","ℹ️ About"]
)

if page=="🏠 Home":
    st.markdown('<div class="hero"><h1>🩸 HemoAI</h1><h3>AI Powered Blood Supply Intelligence Platform</h3></div>', unsafe_allow_html=True)

    c1,c2,c3=st.columns(3)
    with c1:
        st.markdown(f'<div class="metric"><h1>{len(df[df["Type"]=="Hospital"])}</h1><p>Hospitals</p></div>',unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric"><h1>{len(df[df["Type"]=="Blood Bank"])}</h1><p>Blood Banks</p></div>',unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric"><h1>{len(df[df["Units_Available"]<10])}</h1><p>Critical Alerts</p></div>',unsafe_allow_html=True)

    st.subheader("Top Available Blood Sources")
    for _,row in df.sort_values("Units_Available",ascending=False).head(5).iterrows():
        st.markdown(f'<div class="result"><h3>{row["Name"]}</h3><p>{row["City"]} | {row["Blood_Group"]}</p><h2>{row["Units_Available"]} Units</h2></div>',unsafe_allow_html=True)

elif page=="🔍 Search":
    city=st.selectbox("City",sorted(df["City"].unique()))
    bg=st.selectbox("Blood Group",sorted(df["Blood_Group"].unique()))
    if st.button("Search"):
        res=df[(df["City"]==city)&(df["Blood_Group"]==bg)].sort_values("Units_Available",ascending=False)
        for _,row in res.iterrows():
            st.markdown(f'<div class="result"><h2>{row["Name"]}</h2><p>📍 {row["City"]}</p><p>🩸 {row["Blood_Group"]}</p><h3>{row["Units_Available"]} Units Available</h3></div>',unsafe_allow_html=True)

elif page=="📊 Analytics":

    st.title("🎯 AI Blood Demand Forecast")

    city_data = df.groupby(
        ["City","Blood_Group"]
    ).agg({
        "Emergency_Requests":"sum",
        "Daily_Usage":"sum",
        "Units_Available":"sum"
    }).reset_index()
    city_data["Predicted_Demand"] = model.predict(
    city_data[
        [
            "Emergency_Requests",
            "Daily_Usage",
            "Units_Available"
        ]
    ]
)
    city_data["Expected_Shortage"] = (
        city_data["Predicted_Demand"]
        - city_data["Units_Available"]
    )

    city_data = city_data.sort_values(
        "Expected_Shortage",
        ascending=False
    )

    st.markdown("### 🚨 Upcoming High Demand Zones")

    for _, row in city_data.head(8).iterrows():

        shortage = int(row["Expected_Shortage"])

        if shortage <= 0:
            continue

        if shortage > 50:
            risk = "🔴 CRITICAL"
            border = "#dc2626"

        elif shortage > 20:
            risk = "🟠 HIGH"
            border = "#f97316"

        else:
            risk = "🟡 MODERATE"
            border = "#eab308"

        donor_candidates = df[
            (df["Blood_Group"] == row["Blood_Group"]) &
            (df["Units_Available"] > 40)
        ].sort_values(
            "Units_Available",
            ascending=False
        )

        source = "No Source Found"

        if len(donor_candidates) > 0:
            source = donor_candidates.iloc[0]["City"]

        st.markdown(f"""
        <div style="
        background:white;
        border-radius:25px;
        padding:25px;
        margin-bottom:18px;
        border-left:8px solid {border};
        box-shadow:0 8px 20px rgba(0,0,0,.08);
        ">

        <h2>{risk}</h2>

        <h3>📍 {row['City']}</h3>

        <p>🩸 Blood Group :
        <b>{row['Blood_Group']}</b></p>

        <p>📦 Current Stock :
        <b>{int(row['Units_Available'])}</b></p>

        <p>📈 Predicted Demand :
        <b>{int(row['Predicted_Demand'])}</b></p>

        <p>⚠ Expected Shortage :
        <b>{shortage} Units</b></p>

        <p>🚚 Recommended Transfer Source :
        <b>{source}</b></p>

        </div>
        """,
        unsafe_allow_html=True)
elif page=="🚨 Emergency":

    st.title("🚨 Emergency Priority Center")

    critical = df[
        df["Units_Available"] < 10
    ].sort_values(
        "Units_Available",
        ascending=True
    )

    for _, row in critical.iterrows():

        units = row["Units_Available"]

        if units <= 2:
            priority = "🔴 EXTREME"

        elif units <= 5:
            priority = "🟠 HIGH"

        else:
            priority = "🟡 MEDIUM"

        st.markdown(f"""
        <div style="
        background:white;
        padding:25px;
        border-radius:20px;
        margin-bottom:15px;
        box-shadow:0 6px 15px rgba(0,0,0,.1);
        border-left:8px solid #d62828;
        ">

        <h2>{priority}</h2>

        <h3>🏥 {row['Name']}</h3>

        <p>📍 {row['City']}</p>

        <p>🩸 {row['Blood_Group']}</p>

        <p>
        ⚠ Remaining Units:
        <b>{units}</b>
        </p>

        </div>
        """,
        unsafe_allow_html=True)
else:
    st.write("Smart Blood Supply Intelligence Platform with AI based recommendations.")
