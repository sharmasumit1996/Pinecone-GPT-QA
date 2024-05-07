from fastapi import FastAPI, HTTPException
from langchain_openai import OpenAIEmbeddings
from pydantic import BaseModel
from pinecone import Pinecone
import openai
from dotenv import load_dotenv
import os
import time
from scripts import extract_metadata, ask_question

load_dotenv(override=True)

app = FastAPI()

# Connect to Pinecone
api_key = os.getenv("PINECONE_API_KEY")
pc = Pinecone(api_key=api_key)

# Define Pinecone index name
index_name = "damg-group3-assignment5-step1"

model_name = 'text-embedding-ada-002'

class Question(BaseModel):
    query: str

@app.post("/search")
async def search(input_json:Question) :
    try:
        question = input_json.query
        # Perform search using Pinecone
        embedres = openai.embeddings.create(
            model=model_name,
            input=question
        )

        embedding_vector = embedres.data[0].embedding


        # # get relevant contexts (including the questions)
        # connect to index
        index = pc.Index(index_name)
        time.sleep(1)
        res = index.query(vector=embedding_vector, top_k=5, include_metadata=True,namespace='TechNote')

        note_metadata = extract_metadata(res)

        notedata = ''
        notes = []
        for data in note_metadata:
            note = data['text']
            notes.append(note)
            notedata += note
        response = ask_question(notedata,question)
        results = response.choices[0].message.content

        return notes,results
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
