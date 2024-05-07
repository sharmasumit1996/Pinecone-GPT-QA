import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

def compare_answers(output_file, openai_file):
    # Read the CSV files
    output_df = pd.read_csv(output_file)
    openai_df = pd.read_csv(openai_file)

    # Compare Correct Answer and AIAnswer from output.csv
    output_matches = (output_df['Correct Answer'] == output_df['AIAnswer']).sum()

    # Compare Correct Answer (Set B) and Correct Answer (OpenAI) from openai_answers.csv
    openai_matches = (openai_df['Correct Answer (Set B)'] == openai_df['Correct Answer (OpenAI)']).sum()

    return output_matches, openai_matches

def main():
    st.title('Comparison of Correct Answers')

    # Load data and compare answers
    output_file = 'data/output.csv'
    openai_file = 'data/openai_answers.csv'
    output_matches, openai_matches = compare_answers(output_file, openai_file)

    # Read the CSV files
    output_df = pd.read_csv(output_file)
    openai_df = pd.read_csv(openai_file)

    col1, col2 = st.columns(2)

    # Display bar charts
    with col1:
        st.subheader('Comparison of Correct Answers for Part 3')
        fig_openai, ax_openai = plt.subplots()
        ax_openai.bar(['Matches', 'Non-Matches'], [openai_matches, len(openai_df) - openai_matches], color=['blue', 'red'])
        ax_openai.set_ylabel('Count')
        st.pyplot(fig_openai)

    with col2:
        st.subheader('Comparison of Correct Answers for Part 4')
        fig_output, ax_output = plt.subplots()
        ax_output.bar(['Matches', 'Non-Matches'], [output_matches, len(output_df) - output_matches], color=['blue', 'red'])
        ax_output.set_ylabel('Count')
        st.pyplot(fig_output)

if __name__ == '__main__':
    main()
