import streamlit as st
import requests

import streamlit as st
import os

st.set_page_config(layout="wide")

def main():
    st.title("Display Markdown File Content")
    if st.button("Load Markdown"):
        # Define the path to the markdown file
        file_path = "data/LOS_summary.md"

        # Check if the file exists
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as file:
                markdown_content = file.read()
                st.markdown(markdown_content, unsafe_allow_html=True)
        else:
            st.error("The file does not exist.")

if __name__ == "__main__":
    main()

