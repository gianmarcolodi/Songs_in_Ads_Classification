import base64
import datetime
from urllib.parse import quote
import requests

class SpotifyAPI(object):

    def __init__(self, client_id, client_secret, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_id = client_id
        self.client_secret = client_secret
        self.perform_auth()
    
    def get_client_credentials(self):
        client_creds = f"{self.client_id}:{self.client_secret}"
        client_creds_b64 = base64.b64encode(client_creds.encode())
        return client_creds_b64.decode()
    
    def get_token_data(self):
        return {
            "grant_type": "client_credentials"
        } 
    
    def get_token_headers(self):
        client_creds_b64 = self.get_client_credentials()
        return {
            "Authorization": f"Basic {client_creds_b64}"
        }
    
    def perform_auth(self):
        token_url = "https://accounts.spotify.com/api/token"
        token_data = self.get_token_data()
        token_headers = self.get_token_headers()
        r = requests.post(token_url, data = token_data, headers = token_headers)
        if r.status_code not in range(200, 299):
            raise Exception("Authentication Error")
        data = r.json()
        now = datetime.datetime.now()
        access_token = data['access_token']
        expires_in = data['expires_in']
        expires = now + datetime.timedelta(seconds = expires_in)
        self.access_token = access_token
        self.access_token_expires = expires
        return
    
    def get_access_token(self):
        token = self.access_token
        expires = self.access_token_expires
        now = datetime.datetime.now()
        if expires < now:
            self.perform_auth()
            return self.get_access_token()
        return token
    
    def get_resource_header(self):
        access_token = self.get_access_token()
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        return headers

    def get_track(self, _id):
        headers = self.get_resource_header()
        endpoint = f"https://api.spotify.com/v1/tracks/{_id}"
        r = requests.get(endpoint, headers=headers)
        if r.status_code not in range(200, 299):
            return {}
        return r.json()
    
    def get_features(self, ids):
        if isinstance(ids, list):
            if len(ids) > 100:
                raise Exception("Too many IDs. 100 max")
            ids = "%2C".join(ids)
        headers = self.get_resource_header()
        endpoint = f"https://api.spotify.com/v1/audio-features?ids={ids}"
        r = requests.get(endpoint, headers=headers)
        if r.status_code not in range(200, 299):
            return {}
        return r.json()
    
    def search(self, query, search_type = 'track', limit = 1):
        headers = self.get_resource_header()
        query = quote(query)
        endpoint = f"https://api.spotify.com/v1/search?q={query}&type={search_type}&limit={str(limit)}"
        r = requests.get(endpoint, headers=headers)
        if r.status_code not in range(200, 299):  
            return {}
        return r.json()