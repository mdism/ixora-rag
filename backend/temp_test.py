import requests
import json


BASE_URL = 'http://localhost:8000/api'

# API endpoint
LOGIN_API_URL = BASE_URL + "/login/" 
RAG_API_URL =  BASE_URL + "/rag/query/"
CUSTOMER_URL = BASE_URL + "/customers/"
SERVICES_URL = BASE_URL + "/tags/"
token= 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzU4OTM5NjU4LCJpYXQiOjE3NTg4NTMyNTgsImp0aSI6IjUwY2EzMDlmYTJiODQ2N2NiZTU4ZmZjNzRlOTI3YjNhIiwidXNlcl9pZCI6IjEifQ.33GY2OmP0P_b7i1KPfMVWH2M9tGwjTwp5Zw4BjX7py8'



def load_customers(token:str):
    result = []
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.request("GET", CUSTOMER_URL, headers=headers, data=[])
    for customer in json.loads(response.text):
        result.append({"id":customer.get('id',None), 'name': customer.get('name', None)})
    return result

def load_services(token:str):
    result = []
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.request("GET", SERVICES_URL, headers=headers, data=[])
    for tags in json.loads(response.text):
        result.append({"id":tags.get('id',None), 'name': tags.get('name', None)})
    return result

def format_value(object:dict, id:int):
    object.get(id, "Unknown")


