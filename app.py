import pandas as pd
import streamlit as st
from io import BytesIO

# === Load Country Codes from Excel ===
def load_country_codes():
    country_df = pd.read_excel("Book2.xlsx")  # Your uploaded file
    country_df.columns = country_df.columns.str.strip().str.lower()
    code_map = dict(zip(country_df.iloc[:, 0].str.strip(), country_df.iloc[:, 1].str.strip()))
    return code_map

country_codes = load_country_codes()

# === Naming Convention Logic ===
def generate_names(row):
    parts = ["NN"]

    country = str(row.get("Country", "")).strip()
    parts.append(country_codes.get(country, country))  # Lookup or fallback

    jurisdiction_map = {"Yes": "Domestic", "No": "Foreign", "Both": "Global"}
    ae_value = str(row.get("AE in Jurisdiction", "")).strip()
    parts.append(jurisdiction_map.get(ae_value, ""))

    report_type = str(row.get("Report Type", "")).strip().capitalize()
    if report_type in ["Spontaneous", "Solicited", "Clinical trial"]:
        parts.append(report_type)

    serious = str(row.get("Serious", "")).strip()
    if serious == "Yes":
        parts.append("Serious")
    elif serious == "No":
        parts.append("Non-Serious")

    expected = str(row.get("Expected (Listedness)", "")).strip()
    expected_term = {
        "Yes - Listed": "Expected",
        "No - Unlisted": "Unexpected"
    }.get(expected, None)

    names = []

    if row.get("Fatal", "").strip() == "Yes":
        name = parts.copy()
        name.append("Fatal")
        if expected_term:
            name.append(expected_term)
        names.append(" - ".join(name))

    if row.get("Life Threatening", "").strip() == "Yes":
        name = parts.copy()
        name.append("Life threatening")
        if expected_term:
            name.append(expected_term)
        names.append(" - ".join(name))

    if not names:
        name = parts.copy()
        if expected_term:
            name.append(expected_term)
        names.append(" - ".join(name))

    return names

# === Process Uploaded Excel File ===
def process_file(uploaded_file):
    df = pd.read_excel(uploaded_file)
    df["Generated Names"] = df.apply(generate_names, axis=1)
    exploded = df.explode("Generated Names")
    return exploded

# === Convert DataFrame to Excel for Download ===
def convert_df(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return output

# === Streamlit Interface ===
st.title("Excel Naming Convention Generator")

uploaded_file = st.file_uploader("Upload your Excel data file", type=["xlsx"])

if uploaded_file:
    st.success("File uploaded. Processing...")
    result_df = process_file(uploaded_file)

    st.write("### Preview of Generated Output")
    st.dataframe(result_df[["Generated Names"]])

    output_excel = convert_df(result_df)
    st.download_button(
        label="📥 Download Result as Excel",
        data=output_excel,
        file_name="naming_results.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
