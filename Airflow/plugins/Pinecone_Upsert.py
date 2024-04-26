from pinecone import Pinecone
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
import hashlib
import glob
import time
from tqdm.auto import tqdm


# Function to chunk text using RecursiveCharacterTextSplitter
def chunk_text(text):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    return text_splitter.split_text(text)

# Function to read text files and process them
def read_and_process_text_files(data_folder):

    # Initialize OpenAI model
    load_dotenv(override=True)
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    model_name = 'text-embedding-ada-002'
    embed = OpenAIEmbeddings(
        model=model_name,
        openai_api_key=OPENAI_API_KEY  # type: ignore
    )


    data = []
    txt_files = glob.glob(os.path.join(data_folder, '*.txt'))
    for i, txt_file in enumerate(txt_files, 1):
        print('testing:----:', txt_file)
        with open(txt_file, 'r', encoding='utf-8') as file:
            text = file.read()
            # Chunk the text
            text_chunks = chunk_text(text)
            # Embed each chunk
            for chunk in text_chunks:
                # Embed the chunk
                vector_values = embed.embed_documents([chunk])[0]
                # Generate ID based on file name and chunk
                file_name_hash = hashlib.sha256(txt_file.encode()).hexdigest()[:8]
                chunk_hash = hashlib.sha256(chunk.encode()).hexdigest()[:8]
                chunk_id = f"law_{file_name_hash}_{chunk_hash}"
                # Include text content in metadata
                metadata = {"file_name": txt_file, "chunk_text": chunk}
                data.append({"id": chunk_id, "values": vector_values, "metadata": metadata})
    return data

# Function to upload data to the index in batches
def upload_data_to_index_in_batches(data, batch_size=100):

    #init pc
    load_dotenv(override=True)
    # Initialize Pinecone
    pinecone_api_key = os.getenv('PINECONE_API_KEY')
    pc = Pinecone(api_key=pinecone_api_key)
    index_name = os.getenv('PINECONE_INDEX')

    # Connect to the index
    if index_name is not None:
        index = pc.Index(index_name) 
        print(index.describe_index_stats())
        print(len(data))
        # Upsert data into the index in batches
        for i in range(0, len(data), batch_size):
            batch = data[i:i+batch_size]
            index.upsert(vectors=batch, namespace='TextChunks')

def upload_pinecone():

    #init path
    load_dotenv(override=True)
    airflow_file_path = os.getenv('AIRFLOW_FILES_PATH')
    data_folder = airflow_file_path

    # Read and process text files
    data = read_and_process_text_files(data_folder)
    # Upload data to the index in batches
    upload_data_to_index_in_batches(data, batch_size=100)
    print("Data uploaded successfully!")
