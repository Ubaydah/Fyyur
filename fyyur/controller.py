from datetime import datetime
from flask import render_template, request, flash, redirect, url_for
from sqlalchemy import func
from fyyur import app, db
from fyyur.forms import VenueForm, ArtistForm, ShowForm
from fyyur.model import Artist, Show, Venue
import dateutil.parser
import babel


def format_datetime(value, format='medium'):
    if isinstance(value, str):
        date = dateutil.parser.parse(value)
    else:
        date = value
      
    return babel.dates.format_datetime(date, format, locale='en')
app.jinja_env.filters['datetime'] = format_datetime


# Controllers.
@app.route('/')
def index():
  return render_template('pages/home.html')

@app.route('/venues')
def venues():
  areas = Venue.query.distinct(Venue.city, Venue.state).all()
  data = []

  for area in areas:
    area_venues = Venue.query.filter_by(state=area.state).filter_by(city=area.city).all()
    venue_data = []
    for venue in area_venues:
      venue_data.append({
        "id": venue.id,
        "name": venue.name, 
        "num_upcoming_shows": len(Show.query.filter(Show.venue_id==venue.id).filter(Show.start_time > datetime.now()).all())
      })
    data.append({
      "city": area.city,
      "state": area.state, 
      "venues": venue_data
    })
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])

def search_venues():
  input = request.form.get('search_term', '')
  data = Venue.query.filter(func.lower(Venue.name).contains(func.lower(input))).all()
  response = {
        "count": len(data),
        "data": data
    }
  return render_template('pages/search_venues.html', results=response, search_term=input)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  data = Venue.query.filter_by(id=venue_id).first()

  upcoming_shows = []
  past_shows = []
  try:
    for show in data.show:
      if show.start_time > datetime.now():
        upcoming_shows.append(show)
      else:
        past_shows.append(show)
    data.upcoming_shows = upcoming_shows
    data.past_shows = past_shows
    data.upcoming_shows_count = len(upcoming_shows)
    data.past_shows_count = len(past_shows)

    return render_template('pages/show_venue.html', venue=data)
  except:
    flash("Venue with this id doesn't exist")

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  if request.method == 'POST':
    try:
      venue = Venue(
        name = request.form.get('name'),
        city = request.form.get('city'),
        state = request.form.get('state'),
        address = request.form.get('address'),
        phone = request.form.get('phone'),
        image_link = request.form.get('image_link'),
        genres = request.form.get('genres'),
        facebook_link = request.form.get('facebook_link'),
        website_link = request.form.get('website_link'),
        seeking_talent = request.form.get('seeking_talent'),
        seeking_description = request.form.get('seeking_description'),
      )
      db.session.add(venue)
      db.session.commit()
      flash('Venue ' + venue.name + ' was successfully listed!')
      return render_template('pages/home.html')
    except:
      db.session.rollback()
      flash('An error occurred. Venue ' + venue.name + ' could not be listed.')
    finally:
      db.session.close()

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
  except:
        db.session.rollback()
  finally:
        db.session.close()
  return render_template('pages/home.html')

@app.route('/artists')
def artists():
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  input = request.form.get('search_term', '')
  data = Artist.query.filter(func.lower(Artist.name).contains(func.lower(input))).all()
  response = {
        "count": len(data),
        "data": data
    }
  return render_template('pages/search_artists.html', results=response, search_term=input)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  data = Artist.query.filter_by(id=artist_id).first()

  upcoming_shows = []
  past_shows = []
  try:
    for show in data.show:
      if show.start_time > datetime.now():
        upcoming_shows.append(show)
      else:
        past_shows.append(show)
    data.upcoming_shows = upcoming_shows
    data.past_shows = past_shows
    data.upcoming_shows_count = len(upcoming_shows)
    data.past_shows_count = len(past_shows)
    return render_template('pages/show_artist.html', artist=data)
  except None:
    flash("Artist with this id doesn't exist")

@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  try:
    artist = Artist.query.get(artist_id)
    return render_template('forms/edit_artist.html', form=form, artist=artist)
  except None:
    flash("Artist with this ID doesn't exist")

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  try:
    artist = Artist.query.get(artist_id)
    artist.name = request.form.get("name")
    artist.city = request.form.get('city')
    artist.state = request.form.get('state')
    artist.phone = request.form.get('phone')
    artist.genres = request.form.get('genres')
    artist.facebook_link = request.form.get('facebook_link')
    artist.website_link = request.form.get('website_link')
    artist.image_link = request.form.get('image_link')
    artist.seeking_venue = request.form.get('seeking_venue')
    artist.seeking_description = request.form.get('seeking_description')
    
    db.session.add(artist)
    db.session.commit()
  
  except:
    db.session.rollback()
  finally:
    db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  try:
    venue = Venue.query.get(venue_id)
    return render_template('forms/edit_venue.html', form=form, venue=venue)
  except:
    flash("Venue with this ID doesn't exist")
 
@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  try:
    venue = Venue.query.get(venue_id)
    venue.name = request.form.get("name")
    venue.city = request.form.get('city')
    venue.address = request.form.get('address')
    venue.state = request.form.get('state')
    venue.phone = request.form.get('phone')
    venue.genres = request.form.get('genres')
    venue.facebook_link = request.form.get('facebook_link')
    venue.website_link = request.form.get('website_link')
    venue.image_link = request.form.get('image_link')
    venue.seeking_talent = request.form.get('seeking_talent')
    venue.seeking_description = request.form.get('seeking_description')
    
    db.session.add(venue)
    db.session.commit()
  
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
   if request.method == 'POST':
    try:
      artist = Artist(
        name = request.form.get('name'),
        city = request.form.get('city'),
        state = request.form.get('state'),
        phone = request.form.get('phone'),
        image_link = request.form.get('image_link'),
        genres = request.form.get('genres'),
        facebook_link = request.form.get('facebook_link'),
        website_link = request.form.get('website_link'),
        seeking_venue = request.form.get('seeking_venue'),
        seeking_description = request.form.get('seeking_description'),
      )
      db.session.add(artist)
      db.session.commit()
      flash('Artist ' + artist.name + ' was successfully listed!')
      return render_template('pages/home.html')
    
    except:
      db.session.rollback()
      flash('An error occurred. Artist ' + artist.name + ' could not be listed.')
    finally:
      db.session.close()

@app.route('/shows')
def shows():
  current_time = datetime.now()

  data = []
  allshows = Show.query.all()

  for show in allshows:
    artist = Artist.query.get(show.artist_id)
    venue = Venue.query.get(show.venue_id)

    if show.start_time > current_time:
      data.append({
        "venue_id": show.venue_id,
        "venue_name": venue.name,
        "artist_id": show.artist_id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": show.start_time
      })
 
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  if request.method == 'POST':
    try:
      show = Show(
        artist_id = request.form.get('artist_id'),
        venue_id = request.form.get('venue_id'),
        start_time = request.form.get('start_time')
      )
      db.session.add(show)
      db.session.commit()
      flash('Show was successfully listed!')
      return render_template('pages/home.html')
    except:
      db.session.rollback()
      flash('An error occured while listing Show')
    finally:
      db.session.close()
 
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500
