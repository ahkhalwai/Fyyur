#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (
  Flask,
  render_template,
  request,
  Response,
  flash,
  redirect,
  url_for
  )
from markupsafe import Markup
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import collections
import collections.abc
collections.Callable = collections.abc.Callable
from flask_migrate import Migrate
from collections import defaultdict
from sqlalchemy import or_
import sys
from models import db, Venue, Artist, Show
from datetime import datetime


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)



#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  
  v_data = Venue.query.all()

  grouped_venues = defaultdict(lambda: {"venues": []})

  for venue in v_data:
      key = (venue.city, venue.state)
      grouped_venues[key]["city"] = venue.city
      grouped_venues[key]["state"] = venue.state
      grouped_venues[key]["venues"].append({
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": 0 
      })

  data = list(grouped_venues.values())         
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')

  results = Venue.query.filter(or_(Venue.name.ilike(f'%{search_term}%'))).all()

  response={
    "count": len(results),
    "data": [{
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": 0,
    } for venue in results]
  }
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)

  if not venue:
      flash('Venue not found')
      return redirect(url_for('index'))

  past_shows = Show.query.join(Artist).filter(Show.venue_id == venue_id, Show.start_time < datetime.now()).all()
  upcoming_shows = Show.query.join(Artist).filter(Show.venue_id == venue_id, Show.start_time >= datetime.now()).all()    

  data ={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": [{
      "artist_id": show.artist.id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
    } for show in past_shows],
    "upcoming_shows": [{
      "artist_id": show.artist.id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
    } for show in upcoming_shows],
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = VenueForm(request.form)

  if form.validate():
        venue = Venue(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            address=form.address.data,
            phone=form.phone.data,
            genres=form.genres.data,
            facebook_link=form.facebook_link.data,
            image_link=form.image_link.data,
            website=form.website_link.data,
            seeking_talent=form.seeking_talent.data,
            seeking_description=form.seeking_description.data
        )
        try:
            db.session.add(venue)
            db.session.commit()
            # on successful db insert, flash success
            flash('Venue ' + request.form['name'] + ' was successfully listed!')
        except Exception as e:
            # TODO: on unsuccessful db insert, flash an error instead.
            db.session.rollback()
            flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
            print(e)
        finally:
            db.session.close()
            return render_template('pages/home.html')

  else:
        message = []
        for field, err in form.errors.items():
            message.append(field + ' ' + '|'.join(err))
        flash('An error occurred. Venue ' + form.name.data + ' , '.join(message))
        form = VenueForm()
        
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  
  error = False
  try:
      venue = Venue.query.get(venue_id)
      venueName = venue.name
      venue.delete()
  except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()      
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage    
  if error:
      flash(f"{venueName} venue could not be deleted.")
  else:
      flash(f"{venueName} venue has been successfully deleted.")
  return render_template("pages/home.html")


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists = Artist.query.all()

  data = []
  for artist in artists:
      data.append({
          "id": artist.id,
          "name": artist.name,
      })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')

  artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()

  response={
    "count": len(artists),
    "data": [{
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": 0,
    } for artist in artists]
  }
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  
  artist_found = Artist.query.get(artist_id)
  

  # same concept like show_venue join and easy for me :) 
  past_shows = Show.query.join(Venue).filter(Show.artist_id == artist_id, Show.start_time < datetime.now()).all()
  upcoming_shows = Show.query.join(Venue).filter(Show.artist_id == artist_id, Show.start_time >= datetime.now()).all()
  
  past_shows_data = [{
      "venue_id": show.venue.id,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
  } for show in past_shows]
  upcoming_shows_data = [{
      "venue_id": show.venue.id,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
  } for show in upcoming_shows]

  data = vars(artist_found)
  data['past_shows'] = past_shows_data
  data['upcoming_shows'] = upcoming_shows_data
  data['past_shows_count'] = len(past_shows_data)
  data['upcoming_shows_count'] = len(upcoming_shows_data)
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  
  # TODO: populate form with fields from artist with ID <artist_id>
  artist_found = Artist.query.get(artist_id)
  if not artist_found:
    return render_template('errors/404.html')

  form.name.data = artist_found.name
  form.city.data = artist_found.city
  form.state.data = artist_found.state
  form.phone.data = artist_found.phone
  form.genres.data = artist_found.genres
  form.facebook_link.data = artist_found.facebook_link
  form.image_link.data = artist_found.image_link
  form.website_link.data = artist_found.website
  form.seeking_venue.data = artist_found.seeking_venue
  form.seeking_description.data = artist_found.seeking_description

  return render_template('forms/edit_artist.html', form=form, artist=artist_found)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  artist_found = Artist.query.get(artist_id)
  artist_form = ArtistForm(request.form)
  genresList = request.form.getlist("genres")
  try:
    artist_found.name = artist_form.name.data
    artist_found.city = artist_form.city.data
    artist_found.state = artist_form.state.data
    artist_found.phone = artist_form.phone.data
    artist_found.genres = ",".join(genresList)
    artist_found.facebook_link = artist_form.facebook_link.data
    artist_found.image_link = artist_form.image_link.data
    artist_found.website_link = artist_form.website_link.data
    artist_found.seeking_venue = artist_form.seeking_venue.data
    artist_found.seeking_description = artist_form.seeking_description.data

    db.session.commit()
    # on successful db update, flash success
    flash("Artist: " + artist_form.name.data + " has been successfully updated!")
  except:
    db.session.rollback()
    print(sys.exc_info())
    # Done: on unsuccessful db update, flash an error instead.
    flash(
      "An error occurred. Artist "
      + artist_form.name.data
      + " could not be updated."
      )
  finally:
    db.session.close()
  return redirect(url_for("show_artist", artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue_found = Venue.query.get(venue_id)

  # check if venue exists
  if not venue_found:
    return render_template('errors/404.html')

  form.name.data = venue_found.name
  form.city.data = venue_found.city
  form.state.data = venue_found.state
  form.address.data = venue_found.address
  form.phone.data = venue_found.phone
  form.genres.data = venue_found.genres
  form.facebook_link.data = venue_found.facebook_link
  form.image_link.data = venue_found.image_link
  form.website_link.data = venue_found.website
  form.seeking_talent.data = venue_found.seeking_talent
  form.seeking_description.data = venue_found.seeking_description

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue_found)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue = Venue.query.get(venue_id)
  venue_form = VenueForm(request.form)
  genresList = request.form.getlist("genres")
  try:
      venue.name = venue_form.name.data
      venue.city = venue_form.city.data
      venue.state = venue_form.state.data
      venue.address = venue_form.address.data
      venue.phone = venue_form.phone.data
      venue.genres = ",".join(genresList)
      venue.facebook_link = venue_form.facebook_link.data
      venue.image_link = venue_form.image_link.data
      venue.website_link = venue_form.website_link.data
      venue.seeking_talent = venue_form.seeking_talent.data
      venue.seeking_description = venue_form.seeking_description.data

      db.session.commit()
      # on successful db update, flash success
      flash("Venue: " + venue_form.name.data + " has been successfully updated!")
  except:
      db.session.rollback()
      print(sys.exc_info())
      # Done: on unsuccessful db update, flash an error instead.
      flash(
        "An error occurred. Venue " + venue_form.name.data + " could not be updated."
      )
  finally:
      db.session.close()
  return redirect(url_for("show_venue", venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = ArtistForm(request.form)

  if form.validate():
        artist = Artist(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            phone=form.phone.data,
            genres=form.genres.data,
            facebook_link=form.facebook_link.data,
            image_link=form.image_link.data,
            website=form.website_link.data,
            seeking_venue=form.seeking_venue.data,
            seeking_description=form.seeking_description.data
        )
        try:
            db.session.add(artist)
            db.session.commit()
            # on successful db insert, flash success
            flash('Artist ' + request.form['name'] + ' was successfully listed!')
        except Exception as e:
            # TODO: on unsuccessful db insert, flash an error instead.
            db.session.rollback()
            flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
            print(e)
        finally:
            db.session.close()
            return render_template('pages/home.html')

  else:
        message = []
        for field, err in form.errors.items():
            message.append(field + ' ' + '|'.join(err))
        flash('An error occurred. Artist ' + form.name.data + ' , '.join(message))
        form = ArtistForm()
        return render_template('forms/new_artist.html', form=form)

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.

  shows = (
      db.session.query(Show, Artist, Venue)
      .join(Artist, Show.artist_id == Artist.id)
      .join(Venue, Show.venue_id == Venue.id)
      .filter(Show.start_time > datetime.now())
      .all()
    )
  data = []
  for show, artist, venue in shows:
      data.append({
          "venue_id": venue.id,
          "venue_name": venue.name,
          "artist_id": artist.id,
          "artist_name": artist.name,
          "artist_image_link": artist.image_link,
          "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S"),
        })    
  

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form = ShowForm(request.form, meta={'csrf': False})
  if form.validate():
    show = Show(venue_id=form.venue_id.data, artist_id=form.artist_id.data, start_time=form.start_time.data)
    try:
      db.session.add(show)
      db.session.commit()
    except:
      db.session.rollback()
    finally:
      # on successful db insert, flash success
      flash('Show was successfully listed!')
      db.session.close()
      return render_template('pages/home.html')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  else:
    message = []
    for field, err in form.errors.items():
      message.append(field + ' ' + '|'.join(err))
    flash('An error occurred. Show could not be listed. ' + ', '.join(message))
    form = ShowForm()
  return render_template('forms/new_show.html', form=form) 
  

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
