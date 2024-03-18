import base64
import flask
import json
import os
import requests
import random
import spotipy
import string

from dotenv import load_dotenv
from flask import Flask, request, render_template
from requests import post, get
from spotipy.oauth2 import SpotifyClientCredentials

#CONNECTING TO SPOTIFY WEB API ----------

# loading Spotify credentials
cid = os.environ['CID']
secret = os.environ['SECRET']

# creating Spotify client credentials manager
client_credentials_manager = SpotifyClientCredentials(client_id=cid,
                                                      client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

url = "https://api.spotify.com"
response = requests.get(url)

# check spotify web API is connected using response status code
if (response.status_code) == 200:
  print("response status code is 200, API is working")


# get token access
def get_token():
  auth_string = cid + ":" + secret
  auth_bytes = auth_string.encode("utf-8")
  auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

  url = "https://accounts.spotify.com/api/token"
  headers = {
      "Authorization": "Basic " + auth_base64,
      "Content-type": "application/x-www-form-urlencoded"
  }

  data = {"grant_type": "client_credentials"}
  result = post(url, headers=headers, data=data)
  json_result = json.loads(result.content)
  token = json_result["access_token"]
  return token


def get_auth_header(token):
  return {"Authorization": "Bearer " + token}


token = get_token()
