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
from classes import artist, track

#CONNECTING TO SPOTIFY WEB API ----------

# loading Spotify credentials
cid = os.environ['CID']
secret = os.environ['SECRET']

# creating Spotify client credentials manager  
client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

url = "https://api.spotify.com"
response = requests.get(url)

# check spotify web API is connected using response status code
if (response.status_code)==200:
  print("response status code is 200, API is working")

# get token access
def get_token():
  auth_string = cid + ":" + secret
  auth_bytes = auth_string.encode("utf-8")
  auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

  url = "https://accounts.spotify.com/api/token"
  headers = {
    "Authorization" : "Basic " + auth_base64, 
    "Content-type" : "application/x-www-form-urlencoded"
  }

  data = {"grant_type": "client_credentials"}
  result = post(url, headers=headers, data=data)
  json_result = json.loads(result.content)
  token = json_result["access_token"]
  return token

def get_auth_header(token):
  return {"Authorization": "Bearer " + token}



# RETREIVING SPOTIFY WEB API DATA ----------

# return JSON object for Spotify artist data
def search_artist(token, artistname):
  url = "https://api.spotify.com/v1/search"
  headers = get_auth_header(token)
  query = f"?q={artistname}&type=artist&limit=1"

  query_url = url + query
  result = get(query_url, headers=headers)
  json_result = json.loads(result.content)["artists"]["items"]
  if len(json_result) == 0:
    print("No artist found...")
    return None
  return json_result[0]

#return JSON object for Spotify track data
def search_song(token, songname):
  url = "https://api.spotify.com/v1/search"
  headers = get_auth_header(token)
  query = f"?q={songname}&type=track&limit=1"

  query_url = url + query
  result = get(query_url, headers=headers)
  json_result = json.loads(result.content)["tracks"]["items"]
  if len(json_result) == 0:
    print("No song found...")
    return None
  return json_result[0]


#find artists song using artist ID
def find_song_by_artist (token, artist_id):
  url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=GB"
  headers = get_auth_header(token)
  result = get(url, headers=headers)
  json_result = json.loads(result.content)["tracks"]
  return json_result
  
#find artists follower count using artist_id


#DESERIALISING JSON OBJECT INTO CLASS OBJECTS ----------

#MAIN PROGRAM ----------

token = get_token()
target_song = str(input("Enter the name of the song you wish to search for:"))
target_artist = str(input("Enter the name of the artist you wish to search for:"))


a_result = search_artist(token, target_artist)
s_result = search_song(token, target_song)
artist_id=(a_result["id"])
songs = find_song_by_artist(token, artist_id)


#SONG OUTPUTS ----------

string = target_song + " information"
box_char = '='
print(box_char*(len(string)+4))
print(box_char,string,box_char)
print(box_char*(len(string)+4))

print ("\n Artist name:", s_result["artists"][0]["name"])

if s_result["album"]["album_type"]=="single":
  print ("\n Album name:", " n/a, this song is a single")
else:
  print ("\n Album name:", s_result["album"]["name"])

print ("\n Album image url:", s_result["album"]["images"][0]["url"])

mill_sec= s_result["duration_ms"]
total_sec = mill_sec / 1000
min = int(total_sec // 60)
sec = int(total_sec % 60)

print ("\n Duration:", min, "min", sec, "sec")

if s_result["explicit"] == True:
  print ("\n Explicit: Yes")
else:
  print ("\n Explicit: No")



print ("\n")

#ARTIST OUTPUTS ----------

string = a_result["name"] + " information"
box_char = '='
print(box_char*(len(string)+4))
print(box_char,string,box_char)
print(box_char*(len(string)+4))

print ("\n Top songs:")

for idx, song in enumerate(songs):
  print (f"{idx +1}. {song['name']}")

print ("\n Follower count:", a_result["followers"]["total"],)

if len(a_result["genres"])==0:
  print ("\n Top genre: None found")
else:
  print("\n Top genre:", a_result["genres"][0])

print ("\n Image URL:", a_result["images"][0]["url"])

print ("\n")
