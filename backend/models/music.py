from models import db

class Music(db.Model):
    track_id = db.Column(db.Integer, primary_key=True)
    track_name = db.Column(db.String(100), nullable=False)
    track_artist = db.Column(db.String(100), nullable=False)
    track_popularity = db.Column(db.String(100), nullable=False)
    track_album_id = db.Column(db.Integer, nullable=False)
    track_album_name = db.Column(db.String(100), nullable=False)
    playlist_name = db.Column(db.String(100), nullable=False)
    playlist_id = db.Column(db.Integer, nullable=False)
    playlist_genre = db.Column(db.String(100), nullable=False)
    playlist_subgenre = db.Column(db.String(100), nullable=True)
    duration_ms = db.Column(db.Integer, nullable=False)
    soundcloud_link = db.Column(db.String(100), nullable=True)
    
    def __init__(self, track_name, track_artist, track_popularity,
            track_album_id, track_album_name,
            playlist_name, playlist_id, playlist_genre, playlist_subgenre,
            duration_ms, soundcloud_link):
        self.track_name = track_name
        self.track_artist = track_artist
        self.track_popularity = track_popularity
        self.track_album_id = track_album_id
        self.track_album_name = track_album_name
        self.playlist_name = playlist_name
        self.playlist_id = playlist_id
        self.playlist_genre = playlist_genre
        self.playlist_subgenre = playlist_subgenre
        self.duration_ms = duration_ms
        self.soundcloud_link = soundcloud_link