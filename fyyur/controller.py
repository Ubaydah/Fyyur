from datetime import datetime
from flask import render_template, request, flash, redirect, url_for
from sqlalchemy import func
from fyyur import app, db
from fyyur.forms import VenueForm, ArtistForm, ShowForm
from fyyur.model import Artist, Show, Venue
import dateutil.parser
import babel


def format_datetime(value, format="medium"):
    if isinstance(value, str):
        date = dateutil.parser.parse(value)
    else:
        date = value

    return babel.dates.format_datetime(date, format, locale="en")


app.jinja_env.filters["datetime"] = format_datetime


# Controllers.
@app.route("/")
def index():
    return render_template("pages/home.html")


@app.route("/venues")
def venues():
  areas = Venue.query.distinct(Venue.city, Venue.state).all()
  data = []

  for area in areas:
    area_venues = (
        Venue.query.filter_by(state=area.state).filter_by(city=area.city).all()
    )
    venue_data = []
    for venue in area_venues:
        venue_data.append(
          {
              "id": venue.id,
              "name": venue.name,
              "num_upcoming_shows": len(
                  Show.query.filter(Show.venue_id == venue.id)
                  .filter(Show.start_time > datetime.now())
                  .all()
              ),
          }
        )
    data.append({"city": area.city, "state": area.state, "venues": venue_data})
  return render_template("pages/venues.html", areas=data)


@app.route("/venues/search", methods=["POST"])
def search_venues():
  search_term = request.form.get("search_term", "")


  query = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
  results = {
    "count": len(query),
    "data": query
  }
    
  return render_template(
        "pages/search_venues.html", results=results, search_term=search_term
    )


@app.route("/venues/<int:venue_id>")
def show_venue(venue_id):
  data = Venue.query.filter_by(id=venue_id).first()

  upcoming_shows = []
  past_shows = []
  
  for show in data.show:
    show_detail = {
        "artist_id": show.artist_id, 
        "artist_name": show.artist.name, 
        "artist_image_link": show.artist.image_link, 
        "start_time": show.start_time
      }
    if show.start_time > datetime.now():
        upcoming_shows.append(show_detail)
    else:
        past_shows.append(show_detail)
  data.upcoming_shows = upcoming_shows
  data.past_shows = past_shows
  data.upcoming_shows_count = len(upcoming_shows)
  data.past_shows_count = len(past_shows)
  return render_template("pages/show_venue.html", venue=data)

  # except:
  #   flash("Venue with this id doesn't exist")
  

@app.route("/venues/create", methods=["GET"])
def create_venue_form():
    form = VenueForm()
    return render_template("forms/new_venue.html", form=form)


@app.route("/venues/create", methods=["POST"])
def create_venue_submission():
  form = VenueForm(request.form)
  if request.method == "POST":
    try:
      venue = Venue(
          name=form.name.data,
          city=form.city.data,
          state=form.state.data,
          address=form.address.data,
          phone=form.phone.data,
          image_link=form.image_link.data,
          genres=form.genres.data,
          facebook_link=form.facebook_link.data,
          website_link=form.website_link.data,
          seeking_talent=form.seeking_talent.data,
          seeking_description=form.seeking_description.data,
      )
      db.session.add(venue)
      db.session.commit()
      flash("Venue " + form.name.data + " was successfully listed!")
    except Exception as e:
      print(e)
      db.session.rollback()
      flash(
          "An error occurred. Venue " + form.name.data + " could not be listed."
      )
    finally:
        db.session.close()

  return render_template("pages/home.html")


@app.route("/venues/<venue_id>", methods=["DELETE"])
def delete_venue(venue_id):
  try:
      venue = Venue.query.get(venue_id)
      db.session.delete(venue)
      db.session.commit()
  except:
      db.session.rollback()
  finally:
      db.session.close()
  return render_template("pages/home.html")


@app.route("/artists")
def artists():
  data = Artist.query.all()
  return render_template("pages/artists.html", artists=data)


@app.route("/artists/search", methods=["POST"])
def search_artists():
  search_term = request.form.get("search_term", "")


  query = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
  results = {
    "count": len(query),
    "data": query
  }

  return render_template(
        "pages/search_artists.html", results=results, search_term=search_term
    )


@app.route("/artists/<int:artist_id>")
def show_artist(artist_id):
  data = Artist.query.filter_by(id=artist_id).first()

  upcoming_shows = []
  past_shows = []
  
  for show in data.show:
    show_detail = {
        "venue_id": show.venue_id, 
        "venue_name": show.venue.name, 
        "venue_image_link": show.venue.image_link, 
        "start_time": show.start_time
      }
    if show.start_time > datetime.now():
        upcoming_shows.append(show_detail)
    else:
        past_shows.append(show_detail)
  data.upcoming_shows = upcoming_shows
  data.past_shows = past_shows
  data.upcoming_shows_count = len(upcoming_shows)
  data.past_shows_count = len(past_shows)
  return render_template("pages/show_artist.html", artist=data)


@app.route("/artists/<int:artist_id>/edit", methods=["GET"])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
 
  if artist:
      form = ArtistForm(artist=artist)
  else:
      flash("Artist with this ID doesn't exist")

  return render_template("forms/edit_artist.html", form=form, artist=artist)


@app.route("/artists/<int:artist_id>/edit", methods=["POST"])
def edit_artist_submission(artist_id):
  form = ArtistForm(request.form)
  artist = Artist.query.get(artist_id)
  if request.method == "POST":
    try:

      artist.name=form.name.data,
      artist.city=form.city.data,
      artist.state=form.state.data,
      artist.phone=form.phone.data,
      artist.image_link=form.image_link.data,
      artist.genres=form.genres.data,
      artist.facebook_link=form.facebook_link.data,
      artist.website_link=form.website_link.data,
      artist.seeking_venue=form.seeking_venue.data,
      artist.seeking_description=form.seeking_description.data,
  
      db.session.add(artist)
      db.session.commit()
      flash("Artist " + form.name.data + " was successfully edited!")
    except Exception as e:
      print(e)
      db.session.rollback()
      flash(
          "An error occurred. Artist " + form.name.data + " could not be edited."
      )
    finally:
        db.session.close()

  return redirect(url_for("show_artist", artist_id=artist_id))


@app.route("/venues/<int:venue_id>/edit", methods=["GET"])
def edit_venue(venue_id):
  form = VenueForm()
  try:
      venue = Venue.query.get(venue_id)
      return render_template("forms/edit_venue.html", form=form, venue=venue)
  except:
      flash("Venue with this ID doesn't exist")


@app.route("/venues/<int:venue_id>/edit", methods=["POST"])
def edit_venue_submission(venue_id):
  try:
      venue = Venue.query.get(venue_id)
      venue.name = request.form.get("name")
      venue.city = request.form.get("city")
      venue.address = request.form.get("address")
      venue.state = request.form.get("state")
      venue.phone = request.form.get("phone")
      venue.genres = request.form.get("genres")
      venue.facebook_link = request.form.get("facebook_link")
      venue.website_link = request.form.get("website_link")
      venue.image_link = request.form.get("image_link")
      venue.seeking_talent = request.form.get("seeking_talent")
      venue.seeking_description = request.form.get("seeking_description")

      db.session.add(venue)
      db.session.commit()

  except:
      db.session.rollback()
  finally:
      db.session.close()
  return redirect(url_for("show_venue", venue_id=venue_id))


@app.route("/artists/create", methods=["GET"])
def create_artist_form():
  form = ArtistForm()
  return render_template("forms/new_artist.html", form=form)


@app.route("/artists/create", methods=["POST"])
def create_artist_submission():
  form = ArtistForm(request.form)
  if request.method == "POST":
    try:
      artist = Artist(
          name=form.name.data,
          city=form.city.data,
          state=form.state.data,
          phone=form.phone.data,
          image_link=form.image_link.data,
          genres=form.genres.data,
          facebook_link=form.facebook_link.data,
          website_link=form.website_link.data,
          seeking_venue=form.seeking_venue.data,
          seeking_description=form.seeking_description.data,
      )
      db.session.add(artist)
      db.session.commit()
      flash("Artist " + form.name.data + " was successfully listed!")
    except Exception as e:
      print(e)
      db.session.rollback()
      flash(
          "An error occurred. Artist " + form.name.data + " could not be listed."
      )
    finally:
        db.session.close()

  return render_template("pages/home.html")


@app.route("/shows")
def shows():
  current_time = datetime.now()

  data = []
  allshows = Show.query.all()

  for show in allshows:
    artist = Artist.query.get(show.artist_id)
    venue = Venue.query.get(show.venue_id)

    if show.start_time > current_time:
      data.append(
        {
          "venue_id": show.venue_id,
          "venue_name": venue.name,
          "artist_id": show.artist_id,
          "artist_name": artist.name,
          "artist_image_link": artist.image_link,
          "start_time": show.start_time,
        }
      )

    return render_template("pages/shows.html", shows=data)


@app.route("/shows/create")
def create_shows():
    form = ShowForm()
    return render_template("forms/new_show.html", form=form)


@app.route("/shows/create", methods=["POST"])
def create_show_submission():
  form = ShowForm(request.form)
  if request.method == "POST":
    try:
      show = Show(
          artist_id=form.artist_id.data,
          venue_id=form.venue_id.data,
          start_time=form.start_time.data,
      )
      db.session.add(show)
      db.session.commit()
      flash("Show was successfully listed!")
          
    except:
      db.session.rollback()
      flash("An error occured while listing Show")
    finally:
      db.session.close()
  return render_template("pages/home.html")


@app.errorhandler(404)
def not_found_error(error):
  return render_template("errors/404.html"), 404

@app.errorhandler(500)
def server_error(error):
  return render_template("errors/500.html"), 500
