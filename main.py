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
class Artist_class():

  def __init__(self, name, genre, followers, toptracks, relatedartists,
               imgurl):
    self.name = str(name)
    self.genre = str(genre)
    self.followers = int(followers)
    self.toptracks = [""] * 10
    self.relatedartists = [""] * 10
    self.imgurl = str(imgurl)

  #setter methods

  def set_name(self, target_artist):
    self.name = target_artist
    return self.name

  def set_genre(self, a_result):
    if len(a_result["genres"]) == 0:
      self.genre = "No genre found"
    else:
      self.genre = a_result["genres"][0]
    return self.genre

  def set_followers(self, a_result):
    self.followers = a_result["followers"]["total"]
    return self.followers

  def set_toptracks(self, songs):
    for idx, songs in enumerate(songs):
      self.toptracks[idx] = (songs['name'])
    return self.toptracks

  def set_relatedartists(self, relatedartists):
    if len(relatedartists["artists"]) == 0:
      self.relatedartists = "No related artists found"
    else:
      for i in range(10):
        self.relatedartists[i] = relatedartists["artists"][i]["name"]
    return self.relatedartists

  def set_profile_image(self, a_result):
    self.imgurl = a_result["images"][0]["url"]
    return self.imgurl

  def sort_followers(self, a1, a2, a3, a4, a5):
    artists = [a1, a2, a3, a4, a5]
    list=[""]*5
    length = len(artists)
    for x in range(length):
      for y in range(0, length - x - 1):
        if artists[y]["followers"]["total"] < artists[y + 1]["followers"]["total"]:
          artists[y], artists[y + 1] = artists[y + 1], artists[y]
        for i in range(5):
          list[i] = artists[i]["name"] + "  (follower count:" + str(artists[i]["followers"]["total"]) + ")"
    return list


class Song_class():

  def __init__(self, artist, album, albumurl, mins, secs, explicit):
    self.artist = str(artist)
    self.album = str(album)
    self.albumurl = str(albumurl)
    self.mins = int(mins)
    self.secs = int(secs)
    self.explicit = str(explicit)

  def get_artist_name(self, s_result):
    self.artist = s_result["artists"][0]["name"]
    return self.artist

  def get_album_name(self, s_result):
    if s_result["album"]["album_type"] == "single":
      self.album = "N/A, this song is a single"
    else:
      self.album = s_result["album"]["name"]
    return self.album

  def get_album_url(self, s_result):
    self.albumurl = s_result["album"]["images"][0]["url"]
    return self.albumurl

  def get_duration(self, s_result):
    mill_sec = s_result["duration_ms"]
    total_sec = mill_sec / 1000
    self.mins = int(total_sec // 60)
    self.secs = int(total_sec % 60)
    return self.mins, self.secs

  def get_rating(self, s_result):
    if s_result["explicit"] == True:
      self.explicit = "Yes"
    else:
      self.explicit = "No"
    return self.explicit

  def sort_popularity(self, s1, s2, s3, s4, s5):
    songs = [s1, s2, s3, s4, s5]
    list=[""]*5
    length = len(songs)
    for x in range(length):
      for y in range(0, length - x - 1):
        if songs[y]["popularity"] < songs[y + 1]["popularity"]:
          songs[y], songs[y + 1] = songs[y + 1], songs[y]
          for i in range(5):
            list[i] = songs[i]["name"] + "  (popularity score:" + str(songs[i]["popularity"]) + ")"
    return list


#RENDER FLASK TEMPLATES/ FLASK CODE ----------
app = Flask(  # Create a flask app
    __name__,
    template_folder='templates',  # Name of html file folder
    static_folder='static'  # Name of directory for static files
)

app.secret_key = "ayabyabab"

ok_chars = string.ascii_letters + string.digits



#render landing page (home)
@app.route('/')
def base_page():
  random_num = random.randint(1, 100000)
  return render_template('index.html', random_number=random_num)


#render find data page
@app.route('/finddata', methods=["GET", "POST"])
def data_page():
  return render_template('finddata.html')


@app.route('/storeartistresult', methods=["GET", "POST"])
def store_aresult():
  if request.method == 'POST':
    a_data = request.form['artistname']
    session['a_data'] = a_data
  return redirect('/results/artistresult')


@app.route('/storesongresult', methods=["GET", "POST"])
def store_sresult():
  if request.method == 'POST':
    s_data = request.form['songname']
    session['s_data'] = s_data
  return redirect('/results/songresult')


#render artist result page
@app.route('/results/artistresult', methods=["GET", "POST"])
def aresult_page():
  target_artist = session.get('a_data')
  a_result = get_artist_data(token, target_artist)
  artist_id = (a_result["id"])
  songs = get_artists_songs(token, artist_id)
  artistobject = Artist_class("Name", "Genre", 0, "tracks", "related",
                              "Image URL")
  name = artistobject.set_name(target_artist)
  genre = artistobject.set_genre(a_result)
  followers = artistobject.set_followers(a_result)
  tracks = artistobject.set_toptracks(songs)
  image = artistobject.set_profile_image(a_result)
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
  target_song = session.get('s_data')
  s_result = get_song_data(token, target_song)
  songobject = Song_class("Artist", "album", "url link", 0, 0, "rating here")
  name = target_song
  artistname = songobject.get_artist_name(s_result)
  album = songobject.get_album_name(s_result)
  albumphoto = songobject.get_album_url(s_result)
  mins, secs = songobject.get_duration(s_result)
  rating = songobject.get_rating(s_result)
  return render_template(
      '/results/songresult.html',
      name=name,
      artistname=artistname,
      album=album,
      albumphoto=albumphoto,
      mins=mins,
      secs=secs,
      rating=rating,
  )


#render suggestions page
@app.route('/suggestions')
def suggestions_page():
  return render_template('suggestions.html')


@app.route('/store_suggestion', methods=["GET", "POST"])
def store_suggest_result():
  if request.method == 'POST':
    artist = request.form['name']
    session['artist'] = artist
  return redirect('/results/suggestresult')


#render artist suggestions page
@app.route('/results/suggestresult')
def suggest_page():
  artist = session.get('artist')
  name = artist
  a_result = get_artist_data(token, artist)
  artist_id = (a_result["id"])
  artists = get_related_artists(token, artist_id)
  artistobject = Artist_class("Name", "Genre", 0, "tracks", "related",
                              "Image URL")
  image = artistobject.set_profile_image(a_result)
  newartists = artistobject.set_relatedartists(artists)
  get_related_artists(token, artist_id)
  return render_template(
      '/results/artistsuggest.html',
      name=name,
      image=image,
      newartists=newartists,
  )


#render compare page
@app.route('/compare')
def compare_page():
  return render_template('/compare.html')

@app.route('/artist_compare', methods=["GET", "POST"])
def store_artist_compare():
  if request.method == 'POST':
    session['a1'] = request.form['name1']
    session['a2'] = request.form['name2']
    session['a3'] = request.form['name3']
    session['a4'] = request.form['name4']
    session['a5'] = request.form['name5']
  return redirect('/results/artistcompare',)

@app.route('/song_compare', methods=["GET", "POST"])
def store_song_compare():
  if request.method == 'POST':
    session['s1'] = request.form['song1']
    session['s2'] = request.form['song2']
    session['s3'] = request.form['song3']
    session['s4'] = request.form['song4']
    session['s5'] = request.form['song5']
    return redirect('/results/songcompare',)

#render artist comparison page
@app.route('/results/artistcompare')
def acompare_page():
  a=[]*5
  a1 = session.get('a1')
  a2 = session.get('a2')
  a3 = session.get('a3')
  a4 = session.get('a4')
  a5 = session.get('a5')
  a1 = get_artist_data(token, a1)
  a2 = get_artist_data(token, a2)
  a3 = get_artist_data(token, a3)
  a4 = get_artist_data(token, a4)
  a5 = get_artist_data(token, a5)
  artistobject = Artist_class("Name", "Genre", 0, "tracks", "related",
    "Image URL")
  a = artistobject.sort_followers(a1, a2, a3, a4, a5)
  return render_template('/results/artistcompare.html',
                        a=a
                        )

#render song comparison page
@app.route('/results/songcompare')
def scompare_page():
  s=[]*5
  s1 = session.get('s1')
  s2 = session.get('s2')
  s3 = session.get('s3')
  s4 = session.get('s4')
  s5 = session.get('s5')
  s1 = get_song_data(token, s1)
  s2 = get_song_data(token, s2)
  s3 = get_song_data(token, s3)
  s4 = get_song_data(token, s4)
  s5 = get_song_data(token, s5)
  songobject = Song_class("Artist", "album", "url link", 0, 0, "rating here")
  s = songobject.sort_popularity(s1, s2, s3, s4, s5)
  return render_template('/results/songcompare.html',
                        s=s)

#render home page again
@app.route('/index')  # What happens when the user visits the site
def home_page():
  return render_template(
    'index.html',  # Template file path, starting from the templates folder. 
    )

  
#running the app ----------
if __name__ == "__main__":  # Makes sure this is the main process
  app.debug = True
  app.run(  # Starts the site
      host=
      '0.0.0.0',  # EStablishes the host, required for repl to detect the site
      port=3000)
