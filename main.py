import base64
from typing_extensions import dataclass_transform
import connection
import flask
import json
import os
import requests
import random
import string

from connection import token
from dotenv import load_dotenv
from flask import Flask, request, render_template, session, redirect, url_for
from requests import post, get
from spotipy.oauth2 import SpotifyClientCredentials
from connection import get_auth_header


# return JSON object for Spotify artist data
def get_artist_data(token, artistname):
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
def get_artists_songs(token, artist_id):
  url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=GB"
  headers = get_auth_header(token)
  result = get(url, headers=headers)
  json_result = json.loads(result.content)["tracks"]
  return json_result


#get related artist function
def get_related_artists(token, artist_id):
  api_url = "https://api.spotify.com/v1/artists/"
  api_url2 = "/related-artists"
  finalurl = api_url + artist_id + api_url2

  headers = get_auth_header(token)
  result = get(finalurl, headers=headers)
  json_result = json.loads(result.content)
  return json_result


#return JSON object for Spotify track data
def get_song_data(token, songname):
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


# CLASSES ---------------------------------------------------------------------
class Artist_class ():
  def __init__(self, name, genre, followers, imgurl):
    self.name = str(name)
    self.genre = str(genre)
    self.followers = int(followers)
    self.toptracks = [""]*10
    # self.relatedartists = [relatedartists]*5
    self.imgurl = str(imgurl)

  #setter methods

  def set_name(self, target_artist):
    self.name = target_artist
    return self.name

  def set_genre(self, a_result):
    if len(a_result["genres"])==0:
      self.genre = "No genre found"
    else:
      self.genre = a_result["genres"][0]
    return self.genre

  def set_followers(self, a_result):
    self.followers=a_result["followers"]["total"]
    return self.followers

  def set_toptracks(self,songs):
    for idx, songs in enumerate(songs):
      self.toptracks [idx] = (songs['name'])
    return self.toptracks

  # def set_relatedartists(self, relatedartists):
  #   if len(relatedartists["artists"]) == 0:
  #     self.relatedartists="No related artists found"
  #   else:
  #     for i in range (10):
  #       relatedartists = relatedartists["artists"][i]["name"]
  #   return self.relatedartists

  def set_profile_image (self, a_result):
    self.imgurl = a_result["images"][0]["url"]
    return self.imgurl

  def sort_followers (self, a1, a2, a3, a4, a5):
    artists = [a1, a2, a3, a4, a5]
    length = len(artists)
    for x in range(length):
      for y in range(0, length - x - 1):
        if artists[y]["followers"]["total"] < artists[y + 1]["followers"]["total"]:
          artists[y], artists[y + 1] = artists[y + 1], artists[y]
        for i in range(5):
          return artists[i]["name"], artists[i]["followers"]["total"]

        


#RENDER FLASK TEMPLATES/ FLASK CODE ----------
app = Flask(  # Create a flask app
  __name__,
  template_folder='templates',  # Name of html file folder
  static_folder='static'  # Name of directory for static files
)

app.secret_key = "ayabyabab"

ok_chars = string.ascii_letters + string.digits

@app.route('/check_session')
def check_session():
  if 'user_id' in session:
    return 'Session is active'
  else:
    return 'Session is not active'
    
#render landing page (home)
@app.route('/')
def base_page():
  random_num = random.randint(1, 100000) 
  return render_template(
    'index.html',
    random_number=random_num 
)

#render find data page
@app.route('/finddata', methods =["GET", "POST"])
def data_page():
  return render_template(
    'finddata.html'
  )

@app.route('/storeartistresult', methods =["GET", "POST"])
def store_result():
  if request.method == 'POST':
    data = request.form['artistname']
    session['data'] = data
  return redirect('/results/artistresult')

#render artist result page
@app.route('/results/artistresult', methods =["GET", "POST"])
def aresult_page():
  target_artist = session.get('data')
  print(target_artist)
  a_result = get_artist_data(token, target_artist)
  artist_id = (a_result["id"])
  songs= get_artists_songs(token, artist_id)
  artistobject = Artist_class("Name", "Genre", 0, "Image URL")
  name= artistobject.set_name(target_artist)
  genre= artistobject.set_genre(a_result)
  followers= artistobject.set_followers(a_result)
  tracks= artistobject.set_toptracks(songs)
  image= artistobject.set_profile_image(a_result)
  return render_template(
    '/results/artistresult.html',
  name=name,
  genre=genre,
  followers=followers,
  image=image,
  tracks=tracks,
  )

#render song result page
@app.route('/results/songresult')  
def sresult_page():
  return render_template(
    '/results/songresult.html'
  )

#render suggestions page
@app.route('/suggestions')  
def suggestions_page():
  return render_template(
    'suggestions.html'
  )

#render compare page
@app.route('/compare')  
def compare_page():
  return render_template(
    'compare.html'
  )

#render home page again
@app.route('/index')  # What happens when the user visits the site
def home_page():
  return render_template(
    'index.html',  # Template file path, starting from the templates folder. 
  )



#render artist suggestions page
@app.route('/results/suggestresult')  
def asuggest_page():
  return render_template(
    '/results/suggestresult.html'
  )

#render artist comparison page
@app.route('/results/artistcompare')  
def acompare_page():
  return render_template(
    '/results/artistcompare.html'
  )

#render song comparison page
@app.route('/results/songcompare')  
def scompare_page():
  return render_template(
    '/results/songcompare.html'
  )

#running the app ----------
if __name__ == "__main__":  # Makes sure this is the main process
  app.debug = True
  app.run( # Starts the site
    host='0.0.0.0',  # EStablishes the host, required for repl to detect the site
    port=3000 
  )


