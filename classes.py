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
