from openai import OpenAI
## parse the res of RAG return
def extract_metadata(response):
    # Initialize a list to store all extracted metadata as dictionaries
    extracted_data = []

    # Check if the response contains any matches
    if response and response.get('matches'):
        # Iterate over each match found in the response
        for match in response['matches']:
            # Retrieve the metadata dictionary from the current match
            metadata = match.get('metadata', {})

            # Extract the LOS, Note, and text from the metadata
            # Provide default values if any key is not found
            los = metadata.get('LOS', 'No LOS provided')
            note = metadata.get('Note', 'No Note provided')
            text = metadata.get('text', 'No text provided')

            # Create a dictionary with the extracted data
            data_dict = {
                'LOS': los,
                'Note': note,
                'text': text
            }

            # Add the dictionary to the list of extracted data
            extracted_data.append(data_dict)
    else:
        print("No matches found in the response.")

    # Return the list containing dictionaries of the extracted data
    return extracted_data

def ask_question(notedata, question):

    client = OpenAI()
    response = client.chat.completions.create(
    model="gpt-3.5-turbo-0125",
    messages=[
            {"role": "system", "content": f"Use the background knowledge here: {notedata}"},
            {"role": "user", "content": f"Answer the question base on the system content I provide: {question}"}
        ]
    )
    # print(response.choices[0].message.content)
    return response
