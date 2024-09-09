import os.path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

import pandas as pd
from dotenv import load_dotenv
from pathlib import Path
import json

from groq import Groq
from openai import OpenAI

from elasticsearch import Elasticsearch



def get_json_from_text(text):
    dotenv_path = Path('magic/.env')
    load_dotenv(dotenv_path)

    GROQ_API_KEY = os.getenv('GROQ_API_KEY')

    client = Groq(
        api_key=GROQ_API_KEY,
    )

    model_name = "llama-3.1-70b-versatile"

    result = get_answer(client, model_name, text)
    
    final_result = result.split('```json')[1].split('```')[0]
    json_data = json.loads(final_result)
    json_string = json.dumps(json_data)

    return json_string

def get_json_from_text_oa(text):
    dotenv_path = Path('magic/.env')
    load_dotenv(dotenv_path)

    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

    client = OpenAI(api_key=OPENAI_API_KEY)

    model_name = "gpt-4o-mini"

    result = get_answer(client, model_name, text)
    
    final_result = result.split('```json')[1].split('```')[0]
    json_data = json.loads(final_result)
    json_string = json.dumps(json_data)

    return json_string

def prompt_template(question):

    system_prompt = """
    You are a bank specialist and received a bank statement from a PDF in text.
    Your goal is to find the elements of each the transactions from TEXT and return them in json format.
    For example, User asks: Return the following elements:
    ```
    {
        "bank_statement":{
            "year": "year of the transaction in format YYYY",
            "month": "month of the transaction in format MM",
            "date": "the full date of the transaction in format YYYY-MM-DD",
            "transactions": [
              {
                  "year": "year of the transaction in format YYYY",
                  "month": "month of the transaction in format MM",
                  "date": "the full date of the transaction in format YYYY-MM-DD",
                  "description": "description of the transaction",
                  "amount": "float specifiying the amount of the transaction",
                  "currency": "currency on which was made the transaction DOP or USD"
              }
            ]
    }
    ```
    Make sure to return a json with only those fields
    ```json
    {
        "bank_statement":{
            "year": 2024,
            "month": 8,
            "date": "2024-08-20",
            "transactions": [
              {"year": 2024, "month": 8, "date": "2024-08-15", "descrition": "description1", "amount": 100, "currency": "USD"},
              {"year": 2024, "month": 8, "date": "2024-08-16", "descrition": "description1", "amount": 110, "currency": "DOP"},
              {"year": 2024, "month": 8, "date": "2024-08-17", "descrition": "description1", "amount": 120, "currency": "USD"}
            ]
        }
    }
    ```
    """

    prompt = f"""
    From the TEXT you recieve, extract and responde with the JSON file with the following structure:

    ```json
    {{
        "bank_statement":{{
            "year": "The year of the statement",
            "month": "The month of the statement",
            "date": "The date of the statement in format YYYY-MM-DD (e.g. 2024-01-13)",
            "transactions": [
            {{
                "date": "The date of the transaction in format YYYY-MM-DD (e.g. 2024-01-13)",
                "description": "The description of the transaction",
                "amount": "The amount of the transaction",
                "type": "The type of the transaction if debit or credit",
                "category": "The category of the transaction, for example if it is from ONLINE SHOPING, GROCERY, SUPERMARKET, RESTAURANT, COFFEE SHOP, SERVICE PAYMENT, CARD PAYMENT, etc.",
                "currency": "The currency of the transaction, DOP or USD",
            }}
            ]
        }}
    }}
    ```

    TEXT: {question}

    Output json:
    """

    return system_prompt, prompt

def get_answer(client, model_name, question):
    system_prompt, prompt = prompt_template(question)
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model=model_name,
        # model="llama-3.1-70b-versatile",
    )
    return  chat_completion.choices[0].message.content

def elastic_search_knn(field, vector):
    es_client = Elasticsearch('http://elasticsearch:9200', request_timeout=500) 
    index_name = "categories"
    knn = {
        "field": field,
        "query_vector": vector,
        "k": 2,
        "num_candidates": 10000,
    }

    search_query = {
        "knn": knn,
        "_source": ["id", "description", "category"]
    }

    es_results = es_client.search(
        index=index_name,
        body=search_query
    )
    
    result_docs = []
    print(es_results['hits']['hits'])
    
    for hit in es_results['hits']['hits']:
        result_docs.append(hit['_source'])

    return result_docs

def description_search(desc):
    model_name = 'all-MiniLM-L6-v2'
    embedding_model = SentenceTransformer(model_name)
    v_desc = embedding_model.encode(desc)
    return elastic_search_knn('description_vector', v_desc)

def build_category_prompts(desc, search_results):
    system_prompt = """You are a transactions experts and you determine the exact CATEGORY from the transaction description.
    For example if the user asks:

    Provide the category for this transaction description:
    ```json
    {
        "description": "SUPERMERCADO BRAVO"
    }
    ```
    Using this REFERENCES:
    description: LA SIRENA VENEZUELA
    category: SUPERMARKET

    description: SM NACIONAL AV SAN VICENTE
    category: SUPERMARKET
    
    You respond the following category in json:
    The final category is:
    ```json
    {{
        "category": "SUPERMARKET"
    }}
    ```
    """
    prompt_template = """
    Provide the category for this transaction description:
    ```json
    {{
        "description": "{descrip}"
    }}
    ```
    Using this REFERENCES:
    {references}
    
    The final CATEGORY is:
    """

    reference = ""
    for doc in search_results:
        reference = reference + f"description: {doc['description']}\ncategory: {doc['category']}\n\n"

    user_prompt = prompt_template.format(descrip=desc, references=reference).strip()

    return system_prompt, user_prompt

def get_category(client, model_name, description):
    search_results = description_search(description)
    system_prompt, prompt = build_category_prompts(description, search_results)
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model=model_name,
        # model="llama-3.1-70b-versatile",
    )
    return  chat_completion.choices[0].message.content

def get_json_from_description_oa(description):
    dotenv_path = Path('magic/.env')
    load_dotenv(dotenv_path)

    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

    client = OpenAI(api_key=OPENAI_API_KEY)

    model_name = "gpt-4o-mini"

    result = get_category(client, model_name, description)
    
    final_result = result.split('```json')[1].split('```')[0]
    json_data = json.loads(final_result)
    json_string = json.dumps(json_data)
    
    return json_data['category']


def get_credentials():
    creds = None
    SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']
    absolute_path = os.path.abspath(__file__)
    print(absolute_path)
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print('yay')
            print('loading credentials.json')
            flow = InstalledAppFlow.from_client_secrets_file('../credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def list_files_in_folder(folder_id):
    service = build('drive', 'v3', credentials=get_credentials())

    query = f"'{folder_id}' in parents"
    results = service.files().list(q=query, fields="files(id, name, size)").execute()
    items = results.get('files', [])

    if not items:
        print('No files found.')
    else:
        print('Files:')
        files = []
        for item in items:
            file_size_kb = int(item.get('size', 0)) / 1024  # Convert bytes to KB
            print(f"{item['name']} ({item['id']}): {file_size_kb:.2f} KB")
            file = {'file_name': item['name'], 'size': file_size_kb, 'id': item['id']}
            files.append(file)
        return pd.DataFrame(files)



def get_gd_folder_files(folder_id):
    return list_files_in_folder(folder_id)