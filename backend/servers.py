from flask import Flask, render_template, redirect, url_for, request, jsonify
import requests
import sys
import random
import pandas as pd
# from flask_oauthlib.client import OAuth
from models import db
from models.admins import Admin
from models.admin_candidates import Candidates
from models.music import Music
from datetime import datetime
from werkzeug.middleware.profiler import ProfilerMiddleware
from sqlalchemy.exc import IntegrityError

from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flask_caching import Cache
import spotipy
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

app_admin = Flask(__name__)

# config section

client_id = 'f8eb39f738654c94945537405e6ebad1'
client_secret = '27e1646b17d24a32b34cfaf6504a84b1'
redirect_uri = 'http://localhost:5000/admin/callback'

sp_oauth = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope='user-library-read'  # Add the required scopes for your application   
)

cache = Cache(app_admin, config={'CACHE_TYPE': 'simple', 'CACHE_DEFAULT_TIMEOUT': 60})


login_manager = LoginManager(app_admin)
login_manager.login_view = 'unauthorized'

app_admin.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///admin_manager.db'
app_admin.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app_admin.config['SECRET_KEY'] = 'Moriarty'
app_admin.config["CACHE_DEFAULT_TIMEOUT"] = 60  # Set the cache timeout in seconds
db.init_app(app_admin)

# Create tables if not already created
with app_admin.app_context():
    db.create_all()
    # Commit the changes to the database
    db.session.commit()
    print("TABLES CREATED")
    
    if not Admin.query.first():
        # If no records, create an initial admin
        initial_admin = Admin(name='Super Admin', email='sAdmin@admin.com', username='sAdmin', password='sPassword', datetime=datetime.now(), priority=True)
        db.session.add(initial_admin)
        db.session.commit()
        
        
# app_admin.wsgi_app = ProfilerMiddleware(app_admin.wsgi_app, profile_dir='./server_status')

@app_admin.route('/')
def index():
    return redirect(url_for('admin_login'))


@app_admin.route('/admin/')
@login_required
def admin():
    admin_name = current_user.name
    return render_template('index.html', admin_name=admin_name)

@app_admin.route('/admin/profile')
@login_required
def admin_profile():
    current_admin = current_user
    return render_template('users-profile.html', admin=current_admin)

@app_admin.route('/admin/register')
def admin_register():
    return render_template('pages-register.html')

@app_admin.route('/admin/register/candidate', methods=['POST'])
@login_required
def create_admin():
    name = request.form.get('name')
    email = request.form.get('email')
    username = request.form.get('username')
    password = request.form.get('password') 
    current_date = datetime.now()
    # priority = False
    
    # new_admin = Admin(name, email, username, password, current_date, priority)
    new_candidates = Candidates(name, email, username, password, current_date, status='waiting')
    # db.session.add(new_admin)
    db.session.add(new_candidates)
    db.session.commit()
    
    print('Done Creating Admin')
    return redirect(url_for('show_admin_data'))

@app_admin.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        admin = Admin.query.filter_by(username=username, password=password).first()
        if admin:
            login_user(admin)
            return redirect(url_for('admin'))
        else:
            return render_template('pages-unauthorized.html')
        
    return render_template('pages-login.html')


@login_manager.user_loader
def load_admin(admin_id):
    return Admin.query.get(int(admin_id))

@app_admin.errorhandler(404)
def page_error_404(error):
    return render_template('pages-error-404.html'), 404

@app_admin.route('/admin/music_archive')
@login_required
def music_archive():
    return '<h1>Music Archive</h1>'

@cache.memoize()
def get_existing_track(track_name, track_artist):
    return Music.query.filter_by(track_name=track_name, track_artist=track_artist).first()

@app_admin.route('/admin/music_archive/transfer')
def transfer_to_database():
    music_data = 'raw_music_data/Spotify_Songs_Links.xlsx'
    track_df = pd.read_excel(music_data)

    for index, row in track_df.iterrows():
        track_name = row['track_name']
        track_artist = row['track_artist']

        # Check if a track with the same name already exists using caching
        existing_track = get_existing_track(track_name, track_artist)

        if existing_track is None:
            music_object = Music(
                track_name=row['track_name'],
                track_artist=row['track_artist'],
                track_popularity=row['track_popularity'],
                track_album_id=row['track_album_id'],
                track_album_name=row['track_album_name'],
                playlist_name=row['playlist_name'],
                playlist_id=row['playlist_id'],
                playlist_genre=row['playlist_genre'],
                playlist_subgenre=row['playlist_subgenre'],
                duration_ms=row['duration_ms'],
                soundcloud_link=row['links']
            )

            try:
                # Print the memory usage
                memory_usage = sys.getsizeof(music_object)
                print(f"Memory usage of Music object: {memory_usage} bytes")
                db.session.add(music_object)
                db.session.commit()
                print("Database operation successful!")
            except IntegrityError as e:
                db.session.rollback()
                print(f"IntegrityError: {str(e)}")
            except Exception as e:
                db.session.rollback()
                print(f"An error occurred: {str(e)}")
        else:
            print(f"Track with the name '{track_name}-{track_artist}' already exists. Not adding duplicate.")

    db.session.commit()
    
    tracks = Music.query.all()

    return render_template('pages-track.html', tracks=tracks)

@app_admin.route('/admin/music_archive/track')
def show_track():
    # Get the total number of Music objects in the database
    total_tracks = Music.query.count()
    fraction_to_fetch = 0.01
    num_tracks_to_fetch = int(total_tracks * fraction_to_fetch)
    tracks = Music.query.filter(Music.track_id <= num_tracks_to_fetch).all()

    return render_template('pages-track.html', tracks=tracks)
@app_admin.route('/admin/spotify/callback')
def callback():
    # After authorizing, the user is redirected to this route with the authorization code
    auth_code = request.args.get('code')
    # Get the access token using the authorization code
    token_info = sp_oauth.get_access_token(auth_code)
    # Use the access token to make requests to the Spotify Web API
    sp = Spotify(auth=token_info['access_token'])
    # Example: Get the current user's playlists
    user_playlists = sp.current_user_playlists()
    # Print the playlists to the console (for testing purposes)
    print(user_playlists)
    # You can now use 'sp' to interact with the Spotify API in your Flask application
    # Add your application logic here
    
    return 'Authorization successful. You can close this window.'


@app_admin.route('/admin/spotify/spotify_auth')
def spotify_auth():
    auth_url = sp_oauth.get_authorize_url()
    
    # Redirect the user to the Spotify authorization page
    return redirect(auth_url)


# user section

@app_admin.route('/admin/customer_contact')   
@login_required
def show_customer_contact():
    return render_template('pages-contact.html')

@app_admin.route('/admin/user_data')
@login_required
def show_user_data():
    return '<h1>User Data</h1>'

# admin data section

@app_admin.route('/admin/admin_data')
@login_required
@cache.cached(timeout=300)
def show_admin_data():
    admins = Admin.query.all()
    candidates = Candidates.query.all();
    return render_template('pages-admins.html', admins = admins, candidates = candidates)

@app_admin.route('/admin/admin_data/candidate_approve', methods = ['POST'])
@login_required
def candidate_approve():
    try:
        data = request.get_json()      
        candidate_id = data.get('id')
        print(candidate_id);
        candidate = Candidates.query.get(candidate_id)
        candidate.status = 'approved'
        
        new_admin = Admin(candidate.name, candidate.email, candidate.username, candidate.password, candidate.date, priority=False)
        db.session.add(new_admin)
        
        db.session.commit()
        return redirect('/admin/admin_data')

    except Exception as e:
        # Handle errors appropriately (logging, error response, etc.)
        print(f"Error: {e}")
        return jsonify({'error': 'An error occurred'}), 500
    
@app_admin.route('/admin/admin_data/candidate_deny', methods=['POST'])
@login_required
def candidate_deny():
    try:
        data = request.get_json()
        candidate_id = data.get('id')
        print(candidate_id)
        
        # Use filter_by to get the candidate by ID and then delete it
        candidate = Candidates.query.filter_by(id=candidate_id).first()
        
        if candidate:
            db.session.delete(candidate)
            db.session.commit()
            return redirect('/admin/admin_data')
        else:
            return jsonify({'error': 'Candidate not found'}), 404

    except Exception as e:
        # Handle errors appropriately (logging, error response, etc.)
        print(f"Error: {e}")
        return jsonify({'error': 'An error occurred'}), 500


@app_admin.route('/admin/raw_data')
def show_admin_raw_data():
    admins = Admin.query.all()
    return render_template('samples-admin.html', admins=admins)

#unauthorized section

@app_admin.route('/admin/unauthorized')
def unauthorized():
    return render_template('pages-unauthorized.html')


@app_admin.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('index'))


#spotify section
@app_admin.route('/admin/spotify', methods=['GET'])
def get_spotify():
    auth_code = request.args.get('code')
    token_info = sp_oauth.get_access_token(auth_code)
    sp = Spotify(auth=token_info['access_token'])
    user_playlists = sp.current_user_playlists()
    return render_template('pages-spotify.html', playlists=user_playlists)

if __name__ == '__main__':
    app_admin.run(debug=True, port=5000)
