import os
from pinecone import Pinecone
import snowflake.connector
import openai
import spacy
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
import csv
import hashlib
import itertools


# Load environment variables from .env file
load_dotenv()

nlp = spacy.load("en_core_web_md")

# Function to connect to Snowflake and retrieve data
def retrieve_data_from_snowflake():
    SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNTID")
    SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
    SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASS")
    SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE")
    SNOWFLAKE_DATABASE = os.getenv("SNOWFLAKE_DATABASE")
    SNOWFLAKE_SCHEMA = os.getenv("SNOWFLAKE_SCHEMA")

    # Connect to Snowflake
    conn = snowflake.connector.connect(
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        account=SNOWFLAKE_ACCOUNT,
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA
    )

    # Execute query to retrieve data
    cursor = conn.cursor()
    cursor.execute("SELECT summary FROM cfa_courses")

    # Fetch data
    data = cursor.fetchall()
    return [row[0] for row in data]

# Function to divide text into chunks based on character length
def divide_text_into_chunks(text, chunk_size=4000, overlap=20):
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunks.append(text[i:i + chunk_size])
    return chunks

# Function to generate questions with answer options using OpenAI API
def generate_qna_with_openai(data_chunks, context_chunks, num_questions):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    qna = []

    data_context_combinations = itertools.product(data_chunks, context_chunks)
    questions_generated = 0
    for data_chunk, context_chunk in data_context_combinations:
        if questions_generated >= num_questions:
            break

        # Generate question
        prompt = f"""You are a helpful assistant tasked with generating multiple-choice questions along with their answers and explanations based on the provided data. Your goal is to create questions that test understanding and knowledge of the subject matter contained in the data, tailored for a financial analyst with an MBA interest. Each question should have four options (A, B, C, D), with one correct answer among them, derived strictly from the provided data. The incorrect answers should also be related to the questions, although there will eventually be just one correct answer. Please ensure that the questions, options, correct answers, and explanations are all formatted consistently.
        Instructions to Strictly Follow:
        Data: Use the provided {data_chunk}.
        Context: Consider the {context_chunk} to understand the complexity and type of questions, answers, options, and explanations needed, framing them as relevant for a financial analyst with an MBA interest.
        Question Format: Start each question with "Question:" followed by the question text.
        Option Format: Provide four options labeled as "Option A:", "Option B:", "Option C:", and "Option D:" respectively.
        Correct Answer: Indicate the correct answer with the format "Correct Answer: Option X", where X represents the correct option (A, B, C, or D).
        Explanation: Follow the correct answer with an explanation formatted as "Explanation: " followed by the explanation text.

        Remember strictly: Each question SHOULD have four options (A, B, C, D) to choose from, and the answers and explanations should be directly related to the provided data and context. There should be NO blank fields(for example: question or options or Correct Answer or Explanation should not and cannot be blank. )"""
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                    {"role": "system", "content": "You are a helpful assistant to generate questions, answers and explanation for the correct answer."},
                    {"role": "user", "content": prompt}
            ]
        )
        # Extract question and answer options
        question = ""
        options = []
        correct_answer = None
        explanation = ""

        message_content = response.choices[0].message.content
        if message_content is not None:
            lines = message_content.split("\n")
            print(lines)

            # Initialize variables for storing question and options
            question = ""
            options = []
            correct_answer = None
            explanation = ""

            for line in lines:
                line = line.strip()
                if line.startswith("Question:"):
                    if question:  # Check if a question is already present
                        # Append the current question to qna
                        qna.append((question, options, correct_answer, explanation))
                        questions_generated += 1
                        # Check if the required number of questions has been generated
                        if questions_generated >= num_questions:
                            break  # Exit the loop if enough questions have been generated
                        # Reset variables for the new question
                        question = ""
                        options = []
                        correct_answer = None
                        explanation = ""
                    # Extract the new question
                    question = line[len("Question: "):]
                elif line.startswith("Correct Answer:"):
                    correct_answer = line[len("Correct Answer: "):]
                elif line.startswith("Explanation:"):
                    explanation = line[len("Explanation: "):]
                elif line.startswith("Option "):  # Check if the line starts with "Option"
                    options.append(line)  # Append option text

            # Append the last question to qna if it exists
            if question:
                qna.append((question, options, correct_answer, explanation))
                questions_generated += 1

    return qna

# Function to save Q&A data to a CSV file
def save_qna_to_csv(qna, filename):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Question', 'Option A', 'Option B', 'Option C', 'Option D', 'Correct Answer', 'Explanation'])
        for question, options, correct_answer, explanation in qna:
            writer.writerow([question] + options + [correct_answer, explanation])
    

def main():
    # Retrieve data from Snowflake
    data = retrieve_data_from_snowflake()
    context_chunks = []
    
    # Read and chunk the context text file
    context_file_path = "/home/sumitsharma/DAMG7245-Spring24/Assignment05/data/sample-level-i-questions_text.txt"
    with open(context_file_path, "r") as file:
        text = file.read()
        context_chunks = divide_text_into_chunks(text)

    # Chunk the data from Snowflake
    data_chunks = [divide_text_into_chunks(chunk) for chunk in data]

    # Generate questions and answers using OpenAI API
    qna = generate_qna_with_openai(data_chunks, context_chunks, num_questions=5)

    # Save the Q&A data to a CSV file
    save_qna_to_csv(qna, 'qna_data.csv')

if __name__ == "__main__":
    main()
