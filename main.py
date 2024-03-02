import classes
import loadpages
import spotifyAPI

import base64
import flask
import json
import os
import requests
import random
import string

from dotenv import load_dotenv
from flask import Flask, request, render_template
from requests import post, get

variable = 2

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
    return name
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

artistname = data_page()

