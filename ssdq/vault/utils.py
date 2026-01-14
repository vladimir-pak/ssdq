import requests


class Vault:
    def __init__(self):
        pass

    @staticmethod
    def get_secret_id(url:str, password:str) -> str:
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "password": password
        }
        response = requests.post(url=url, headers=headers, json=data)
        response_json = response.json()
        return response_json['auth']['client_token']
    
    @staticmethod
    def get_token(url:str, role_id:str, secret_id:str) -> str:
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "role_id": role_id,
            "secret_id": secret_id
        }
        response = requests.post(url=url, headers=headers, json=data)
        response_json = response.json()
        return response_json['auth']['client_token']

    @staticmethod
    def get_secret(url:str, token:str) -> dict|str:
        headers = {
            'X-Vault-Token': token,
        }
        response = requests.get(url=url, headers=headers)
        response.raise_for_status()
        return response.json()['data']['data']
    
    @staticmethod
    def create_secret(url:str, token:str, data:dict):
        headers = {
            'X-Vault-Token': token,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        response = requests.post(url=url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    