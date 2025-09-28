import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re

# st.set_option('deprecation.showPyplotGlobalUse', False)

# ===============================
# Load dataset
# ===============================
df = pd.read_csv("SMS AND SID  HAZARD DATA.csv")

st.title("📊 Hazard Analytics Dashboard")

# ===============================
# Helper to extract numbers (H, P, E)
# ===============================
def extract_values(text):
    values = {"H": None, "P": None, "E": None}
    matches = re.findall(r"([HPE])\s*=\s*(\d+)", str(text))
    for k, v in matches:
        values[k] = int(v)
    return values

# Create numeric columns from Probability / Severity / Score
for col, prefix in [("Probability", "Prob"), ("Severity", "Sev"), ("Score (P × S)", "Score")]:
    extracted = df[col].apply(extract_values)
    df[f"{prefix}_H"] = extracted.apply(lambda x: x["H"])
    df[f"{prefix}_P"] = extracted.apply(lambda x: x["P"])
    df[f"{prefix}_E"] = extracted.apply(lambda x: x["E"])

# ===============================
# Sidebar Filters
# ===============================
st.sidebar.header("Filters")
# division_filter = st.sidebar.multiselect("Select Division", df["Division"].unique())
location_filter = st.sidebar.multiselect("Select Location", df["Exact Location"].unique())
category_filter = st.sidebar.multiselect("Select Category", df["Category"].unique())
risk_filter = st.sidebar.multiselect("Select Risk Level", df["Selected Risk Level"].unique())

filtered_df = df.copy()
# if division_filter:
#     filtered_df = filtered_df[filtered_df["Division"].isin(division_filter)]
if category_filter:
    filtered_df = filtered_df[filtered_df["Category"].isin(category_filter)]
if risk_filter:
    filtered_df = filtered_df[filtered_df["Selected Risk Level"].isin(risk_filter)]
if location_filter:
    filtered_df = filtered_df[filtered_df["Exact Location"].isin(location_filter)]

st.subheader("🔎 Dataset Preview")
st.dataframe(filtered_df.head())

# ===============================
# 1. Hazard Distribution
# ===============================
st.subheader("📌 Hazard Count by Category")
st.bar_chart(filtered_df["Category"].value_counts())

st.subheader("📌 Hazard Count by Sub-Category")
st.bar_chart(filtered_df["Sub Category"].value_counts())

# ===============================
# 2. H / P / E Breakdown
# ===============================
# st.subheader("👥 Human / 🏠 Property / 🌱 Environment Affected")

h_count = filtered_df["Type Hazard"].str.contains("H = Y", case=False).sum()
p_count = filtered_df["Type Hazard"].str.contains("P = Y", case=False).sum()
e_count = filtered_df["Type Hazard"].str.contains("E = Y", case=False).sum()

hpe_counts = {"Human": h_count, "Property": p_count, "Environment": e_count}
hpe_sorted = dict(sorted(hpe_counts.items(), key=lambda x: x[1], reverse=True))

# col1, col2, col3 = st.columns(3)
# col1.metric("Human Hazards", h_count)
# col2.metric("Property Hazards", p_count)
# col3.metric("Environment Hazards", e_count)

# st.write("### 🏆 H/P/E Impact Ranking")
# for i, (k, v) in enumerate(hpe_sorted.items(), 1):
#     st.write(f"{i}. **{k}** → {v} hazards")

# fig, ax = plt.subplots()
# ax.bar(hpe_counts.keys(), hpe_counts.values(), color=["red", "blue", "green"])
# ax.set_ylabel("Count")
# ax.set_title("H/P/E Hazard Comparison")
# st.pyplot(fig)

# ===============================
# 3. Risk Levels
# ===============================
st.subheader("⚠️ Selected Risk Level Distribution")
risk_counts = filtered_df["Selected Risk Level"].value_counts()
fig, ax = plt.subplots()
ax.pie(risk_counts, labels=risk_counts.index, autopct="%1.1f%%")
st.pyplot(fig)

# ===============================
# 4. Hazards Over Time
# ===============================
st.subheader("📅 Hazards Reported Over Time")
df_time = pd.to_datetime(filtered_df["Date and Time"], errors="coerce")
time_counts = df_time.value_counts().sort_index()
st.line_chart(time_counts)

# ===============================
# 5. Compliance Tracking
# ===============================
st.subheader("✅ Compliance Status by Date")
comp_counts = filtered_df.groupby("Compliance Date")["Remark"].value_counts().unstack(fill_value=0)
st.bar_chart(comp_counts)

# ===============================
# 6. Location-based Hazards
# ===============================
st.subheader("📍 Hazard Count by Exact Location")
location_counts = filtered_df["Exact Location"].value_counts()
st.bar_chart(location_counts)

# ===============================
# 7. Probability & Severity (H, P, E)
# ===============================
st.subheader("🎯 Probability & Severity (H, P, E)")
prob_sev_cols = ["Prob_H", "Prob_P", "Prob_E", "Sev_H", "Sev_P", "Sev_E"]
st.dataframe(filtered_df[["Hazard Identified"] + prob_sev_cols].head())

avg_prob = filtered_df[["Prob_H", "Prob_P", "Prob_E"]].mean()
avg_sev = filtered_df[["Sev_H", "Sev_P", "Sev_E"]].mean()

col1, col2 = st.columns(2)
col1.bar_chart(avg_prob, height=300)
col1.write("Avg Probability (1-5)")
col2.bar_chart(avg_sev, height=300)
col2.write("Avg Severity (1-5)")

# ===============================
# 8. Risk Score Analysis
# ===============================
# st.subheader("📈 Risk Score Analysis (Probability × Severity)")
# score_cols = ["Score_H", "Score_P", "Score_E"]
# st.dataframe(filtered_df[["Hazard Identified"] + score_cols + ["Risk Level"]].head())

# avg_scores = filtered_df[score_cols].mean()
# st.bar_chart(avg_scores, height=300)

# st.write("### 🏆 Highest Risk Hazards")
# st.dataframe(filtered_df.nlargest(5, ["Score_H", "Score_P", "Score_E"])[
#     ["Hazard Identified", "Score_H", "Score_P", "Score_E", "Risk Level"]
# ])

# st.write("### 🛡️ Lowest Risk Hazards")
# st.dataframe(filtered_df.nsmallest(5, ["Score_H", "Score_P", "Score_E"])[
#     ["Hazard Identified", "Score_H", "Score_P", "Score_E", "Risk Level"]
# ])

# st.subheader("🔥 Probability vs Severity Heatmaps")

# col1, col2, col3 = st.columns(3)

# with col1:
#     st.write("Human")
#     heatmap_data = filtered_df.groupby(["Prob_H", "Sev_H"]).size().unstack(fill_value=0)
#     fig, ax = plt.subplots()
#     sns.heatmap(heatmap_data, annot=True, cmap="Reds", ax=ax)
#     st.pyplot(fig)

# with col2:
#     st.write("Property")
#     heatmap_data = filtered_df.groupby(["Prob_P", "Sev_P"]).size().unstack(fill_value=0)
#     fig, ax = plt.subplots()
#     sns.heatmap(heatmap_data, annot=True, cmap="Blues", ax=ax)
#     st.pyplot(fig)

# with col3:
#     st.write("Environment")
#     heatmap_data = filtered_df.groupby(["Prob_E", "Sev_E"]).size().unstack(fill_value=0)
#     fig, ax = plt.subplots()
#     sns.heatmap(heatmap_data, annot=True, cmap="Greens", ax=ax)
#     st.pyplot(fig)


# ===============================
# Calculate risk scores (Probability × Severity) AFTER extracting H/P/E values
df["Risk_H"] = df["Prob_H"] * df["Sev_H"]
df["Risk_P"] = df["Prob_P"] * df["Sev_P"]
df["Risk_E"] = df["Prob_E"] * df["Sev_E"]

st.subheader("🔍 Hazard Drill-Down Analysis")

# Let user pick a specific hazard
hazard_list = df["Hazard Identified"].unique()
selected_hazard = st.selectbox("Select a Hazard to Analyze", hazard_list)

if selected_hazard:
    hazard_data = df[df["Hazard Identified"] == selected_hazard]

    st.write(f"### 📌 Details for Hazard: **{selected_hazard}**")

    # Show probability, severity, risk score for H, P, E
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Human Probability", int(hazard_data["Prob_H"].values[0]))
        st.metric("Human Severity", int(hazard_data["Sev_H"].values[0]))
        st.metric("Human Risk Score", int(hazard_data["Risk_H"].values[0]))

    with col2:
        st.metric("Property Probability", int(hazard_data["Prob_P"].values[0]))
        st.metric("Property Severity", int(hazard_data["Sev_P"].values[0]))
        st.metric("Property Risk Score", int(hazard_data["Risk_P"].values[0]))

    with col3:
        st.metric("Environment Probability", int(hazard_data["Prob_E"].values[0]))
        st.metric("Environment Severity", int(hazard_data["Sev_E"].values[0]))
        st.metric("Environment Risk Score", int(hazard_data["Risk_E"].values[0]))

    # Show location & date if available
    cols_to_show = [c for c in ["Exact Location", "Date and Time"] if c in hazard_data.columns]
    if cols_to_show:
        st.write("### 📍 Location & Date")
        st.table(hazard_data[cols_to_show])
    else:
        st.info("No location/date columns found in dataset.")



st.success("✅ Full Dashboard Ready: includes original + extended analytics")
