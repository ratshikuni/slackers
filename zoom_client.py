import requests
import json 
import base64
import hmac
import hashlib
from datetime import timedelta, datetime
import time
class ZoomClient:

    def __init__(self, account_id, client_id, client_secret, time_delta=60) -> None:
        self.account_id = account_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.time_delta = time_delta
        self.token_generated = None
        self.meetingNumber= None
        self.access_token = self.get_access_token()
 
        self.token_value = None

    def get_access_token(self):
        data = {
            "grant_type": "account_credentials",
            "account_id": self.account_id,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        try:
            response = requests.post("https://zoom.us/oauth/token", data=data)
            response.raise_for_status()  # Raise an error for non-200 responses
            token_data = response.json()
            return token_data.get("access_token", None)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching access token: {e}")
            return None

    def get_meetings(self):
        if not self.access_token:
            print("No access token available.")
            return None
        
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        params = {"type": "upcoming"}

        url = "https://api.zoom.us/v2/users/me/meetings"

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()  # Raise an error for HTTP errors
            
            data = response.json()
            
            if "meetings" in data:
                return data["meetings"]
            else:
                print("Unexpected response format:", data)
                return None

        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error: {e}")
        except requests.exceptions.RequestException as e:
            print(f"Request Error: {e}")
        except ValueError:
            print("Error decoding JSON response.")
        
        return None

    
    def get_recordings(self):
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }

        url = f"https://api.zoom.us/v2/users/me/recordings"

        return requests.get(url, headers=headers).json()
    
    def get_download_url(self, meeting_id):
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        url = f"https://api.zoom.us/v2/meetings/{meeting_id}/recordings"

        r = requests.get(url, headers=headers).json()
        
        url = [i['download_url'] for i in r['recording_files'] if i['recording_type'] == 'audio_only'][0]
        download_link = f'{url}?access_token={self.access_token}&playback_access_token={r["password"]}'
        return download_link
    


    @property
    def token(self):
        """
        This property returns a JWT token for Zoom.

        :return: JWT token for Zoom.
        """
        # Check if time stamp of current token is close to expiring before generating a new one
        if (self.get_time() - self.token_generated) > (self.time_delta - 10):
            self.token_value = self.generate_token()
            return self.token_value
        else:
            return self.token_value



    def generate_token(self):
   
        # Current time and expiration in seconds
        iat = int(time.time()) - 30  # issued at (30 seconds before now)
        exp = iat + 60 * 60 * 2     # expires in 2 hours
        token_exp = exp               # token expiration timestamp

        # Header and Payload
        header = {
            "alg": "HS256",
            "typ": "JWT"
        }
        secret  = self.client_id

        payload = {
            "sdkKey": self.client_id,
            "appKey": self.client_id,
            "mn": self.meetingNumber,
            "role": 0,
            "iat": iat,
            "exp": exp,
            "tokenExp": token_exp
        }

        # Base64Url encode function
        def base64_url_encode(data):
            return base64.urlsafe_b64encode(data.encode('utf-8')).decode('utf-8').rstrip('=')

        # Create the message to sign (header + payload)
        message = f"{base64_url_encode(json.dumps(header))}.{base64_url_encode(json.dumps(payload))}"

        # Generate the HMACSHA256 signature
        signature = hmac.new(secret.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).hexdigest()

        # Return the JWT
        return f"{message}{signature}"