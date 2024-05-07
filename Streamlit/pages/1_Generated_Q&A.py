import streamlit as st
import requests
import pandas as pd

st.set_page_config(layout="wide")

def read_csv_file(file_path):
    try:
        df = pd.read_csv(file_path)
        return df
    except FileNotFoundError:
        st.error(f"File '{file_path}' not found.")

# App title
st.title("Generated Q&A Data Viewer")

# Read qna_a.csv
st.header("Data from Q&A Set A")
qna_a_file_path = "data/qna_data_seta.csv"
qna_a_df = read_csv_file(qna_a_file_path)

if qna_a_df is not None:
    st.write(qna_a_df)

# Read qna_b.csv
st.header("Data from Q&A Set B")
qna_b_file_path = "data/qna_data_setb.csv"
qna_b_df = read_csv_file(qna_b_file_path)

if qna_b_df is not None:
    st.write(qna_b_df)