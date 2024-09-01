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

    return json_data

def prompt_template(question):

    system_prompt = """
    You are a bank specialist and recieve a bank statement from a PDF in text.
    You can easily extract transactions from the PDF and list them in JSON thanks your IT team.
    Your goal is to find the elements of the transactions from TEXT and return them in json format.
    For example if the user asks:
    Return the following data from the bank statement text:
    ```
    {
        "year": "year of the transaction in format YYYY",
        "month": "month of the transaction in format MM",
        "date": "the full date of the transaction in format YYYY-MM-DD",
        "description": "description of the transaction",
        "amount": "float specifiying the amount of the transaction",
        "currency": "currency on which was made the transaction"
    }
    ```
    Make sure to return a json with the list of corresponding values
    Output json:
    ```json
    {
        "transactions": [
        {"year": 2024, "month": 8, "date": "2024-08-15", "descrition": "description1", "amount": 100, "currency": "USD"},
        {"year": 2024, "month": 8, "date": "2024-08-16", "descrition": "description1", "amount": 110, "currency": "USD"},
        {"year": 2024, "month": 8, "date": "2024-08-17", "descrition": "description1", "amount": 120, "currency": "USD"}
        ]
    }
    ```

    if the user asks for others fields that are not part of an specific transaction:
    For example, User asks: Return the following elements:
    ```
    {
        "product": "id or number of the product (credit card or account)",
        "total_debt:": "total settlement amount",
        "number_of_transactions": "number of transactions in the statement",
        "transactions": [
        {
            "year": "year of the transaction in format YYYY",
            "month": "month of the transaction in format MM",
            "date": "the full date of the transaction in format YYYY-MM-DD",
            "description": "description of the transaction",
            "amount": "float specifiying the amount of the transaction",
            "currency": "currency on which was made the transaction"
        }
        ]
    }
    ```
    Make sure to return a json with only those fields
    ```json
    {
        "product": "****-7899",
        "total_debt:": 330,
        "number_of_transactions": 3,
        "transactions": [
        {"year": 2024, "month": 8, "date": "2024-08-15", "descrition": "description1", "amount": 100, "currency": "USD"},
        {"year": 2024, "month": 8, "date": "2024-08-16", "descrition": "description1", "amount": 110, "currency": "USD"},
        {"year": 2024, "month": 8, "date": "2024-08-17", "descrition": "description1", "amount": 120, "currency": "USD"}
        ]
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
            "date": "The date of the statement in format 2024-01-13",
            "total_debt": "The Settlement amount for the month",
            "number_of_transactions": "The number of transactions in the statement",
            "transactions": [
            {{
                "date": "The date of the transaction in format 2024-01-13",
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