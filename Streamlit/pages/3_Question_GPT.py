import streamlit as st
import os
import requests

st.set_page_config(layout="wide")

def main():
    st.title("Pinecone Search Base ON Tech Note")
    question = st.text_input("Enter your question:")  # Capture user input

    if st.button("Search"):  # Button to trigger search
        if question:  # Check if question is not empty
            with st.spinner("Loading..."):  # Loading spinner
                try:
                    question = {
                        'query': question
                    }
                    response = requests.post("http://fastapi:8000/search", json=question)
                    response.raise_for_status()  # Check for HTTP errors, which raises an exception if the status code is not OK
                    results = response.json()  
                    st.write(f"Results: {results[1]}")  # Display results
                except requests.exceptions.HTTPError as err:
                    error_detail = err.response.json().get('detail', 'Unknown error')
                    st.error(f"HTTP Error: {error_detail}")  # Display HTTP error details
                except requests.exceptions.ConnectionError:
                    st.error("Failed to connect to the server. Please check if the FastAPI service is running.")
                except requests.exceptions.Timeout:
                    st.error("Request timed out. Please check your network connection and try again.")
                except requests.exceptions.RequestException as e:
                    st.error(f"An error occurred: {e}")  # Catch all other request-related errors
                except Exception as e:
                    st.error(f"An unexpected error occurred: {e}")  # Catch all other exceptions
        else:
            st.warning("Please enter a question before searching.")  # Warning if no question is entered

if __name__ == "__main__":
    main()
