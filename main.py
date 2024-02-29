#IMPORTS ----------
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


#RENDER FLASK TEMPLATES/ FLASK CODE ----------
app = Flask(  # Create a flask app
  __name__,
  template_folder='templates',  # Name of html file folder
  static_folder='static'  # Name of directory for static files
)

ok_chars = string.ascii_letters + string.digits

#render landing page (home)
@app.route('/')  
def base_page():
  random_num = random.randint(1, 100000) 
  return render_template(
    'index.html',
    random_number=random_num  
)

#render find data page
@app.route('/finddata.html', methods =["GET", "POST"])
def data_page():
  if request.method == "POST":
    name = request.form.get("artistname")
    print (name)
  return render_template(
    'finddata.html'
  )
  
#render suggestions page
@app.route('/suggestions.html')  
def suggestions_page():
  return render_template(
    'suggestions.html'
  )

#render compare page
@app.route('/compare.html')  
def compare_page():
  return render_template(
    'compare.html'
  )

#render home page again
@app.route('/index.html')  # What happens when the user visits the site
def home_page():
  return render_template(
    'index.html',  # Template file path, starting from the templates folder. 
  )

#running the app ----------
if __name__ == "__main__":  # Makes sure this is the main process
  app.debug = True
  app.run( # Starts the site
    host='0.0.0.0',  # EStablishes the host, required for repl to detect the site
    port=random.randint(2000, 9000)  # Randomly select the port the machine hosts on.
  )

#INITIALISING VARIABLES ----------
artistname = str()
song = str()

#CLASSES ----------
class artist ():
  def __init__(self, name, imgurl, followers, toptracks):
    self.name = str(name)
    self.imgurl = str(imgurl)
    self.followers = int(followers)
    self.toptracks = str(toptracks)

class track ():
  def __init__(self, artist, album, albumurl, duration, popularity):
    self.artist = str(artist)
    album = str(album)
    self.albumurl = str(albumurl)
    self.duration = str(duration)
    self.popularity = int(popularity)

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


targetartist = request.form["artistname"]
targets = request.form["songname"]


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

#find artists song using artist ID
def find_song_by_artist (token, artist_id):
  url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=GB"
  headers = get_auth_header(token)
  result = get(url, headers=headers)
  json_result = json.loads(result.content)["tracks"]
  return json_result

#DESERIALISING JSON OBJECT INTO CLASS OBJECTS ----------

#create artist object and deserialise JSON object into "artist" class
artist_obj = artist(
  name = result["name"],
  imgurl = result["images"][0]["url"],
  followers = result["followers"]["total"],
  toptracks = str(songs)
)

#create song object and deserialise JSON object into "song" class
tracks_obj = []
for song in songs:
  new_track_obj = track(
  artist = song["artists"][0]["name"],
  album = song["album"]["name"],
  albumurl = song["album"]["images"][0]["url"],
  duration = song["duration_ms"],
  popularity = song["popularity"]
  )

  tracks_obj.append(new_track_obj)

