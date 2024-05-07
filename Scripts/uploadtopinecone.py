from pinecone import Pinecone
import hashlib
import csv
import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
import openai
from time import sleep
from tqdm.autonotebook import tqdm
from pinecone import ServerlessSpec

load_dotenv()
 
spec = ServerlessSpec(
    cloud="aws", region="us-east-1"
)
 
# Initialize Pinecone
pinecone_api_key: str | None = os.getenv('PINECONE_API_KEY')
pc = Pinecone(api_key=pinecone_api_key)
questions_namespace = 'questions'
answers_namespace = 'answers'
index_name = 'setb-final'
 
# Function to embed text using OpenAI model
def embed_text(text):
    # Initialize OpenAI Embeddings
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    model_name = 'text-embedding-ada-002'
    embed = OpenAIEmbeddings(model=model_name, openai_api_key=OPENAI_API_KEY) #type: ignore
    # Embed the text
    return embed.embed_documents([text])[0]
 
 
# Function to read data from CSV file and process it
def read_and_process_csv(file_path):
    data = []
    with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for i, row in enumerate(reader, 1):  # Start enumeration from 1
 
            # combine the question, options, answer and explanation
            values = row['Question'] + row['Option A'] + row['Option B'] + row['Option C'] + row['Option D'] + row['Question'] + row['Explanation']
            vector_values = embed_text(values)
 
            # Generate ID based on question number
            question_id = f"question_{i}"
 
            # Append data to list
            data.append({"id": question_id, "values": vector_values, "metadata": {
                "question": row['Question'],
                "options": [row[option] for option in ['Option A', 'Option B', 'Option C', 'Option D']],
                "correct_answer": row['Correct Answer'],
                "explanation": row['Explanation']
            }})
 
    return data
 
def create_index():
    existing_indexes = [
        index_info["name"] for index_info in pc.list_indexes()
    ]
    if index_name not in existing_indexes:
        # if does not exist, create index
        pc.create_index(
            index_name,
            dimension=1536,  # dimensionality of ada 002
            metric='dotproduct',
            spec=spec
        )
        # wait for index to be initialized
        while not pc.describe_index(index_name).status['ready']:
            sleep(1)
 
 
def upload_the_data():
    """return index for query"""
    # connect to index
    index = pc.Index(index_name)
    sleep(1)
 
    # Path to your CSV file
    csv_file_path = "./data/qna_data_setb.csv"
    
    # Read and process data from CSV
    data = read_and_process_csv(csv_file_path)
    
    # Upsert data into the index with separate namespaces for questions and answers
    index.upsert(vectors=data,namespace=questions_namespace)  # Upsert questions data
    index.upsert(vectors=data,namespace=answers_namespace)    # Upsert answers data
 
    return index

def main():
    index = upload_the_data()

if __name__ == "__main__":
    main()