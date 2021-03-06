#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import datetime

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    genres = db.Column(db.String(120))
    website = db.Column(db.String())
    seeking_talent = db.Column(db.Boolean(),default=False)
    shows = db.relationship('Show', backref='venue', lazy=True)
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean(),default=False)
    seeking_description = db.Column(db.String())
    shows = db.relationship('Show', backref='artist', lazy=True)
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'),nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'),nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    
      

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format,locale='en_US')

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
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  
  
  data = []
  venue = Venue.query.distinct(Venue.city, Venue.state).all()
  area = []
  for v in venue :
    area.append([v.city,v.state])
  
  for city,state in area:
        list_venues = []
        venue = Venue.query.filter_by( city = city , state = state ).all()
        for v in venue :
          list_venues.append({
            "id": v.id,
            "name":v.name,
            "num_upcoming_shows" : 0,
          })
        data.append({
          "city" : city,
          "state" : state,
          "venues" : list_venues,
        })    
  
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  data = []
  search_term = request.form.get('search_term', None)
  venues = Venue.query.filter(
        Venue.name.ilike("%{}%".format(search_term))).all()
  for v in venues:
    data.append({
      "id": v.id,
      "name": v.name,
    })
    
  count_venues = len(venues)
  response = {
        "count": count_venues,
        "data": data

  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data = []
  past_count,upcoming_count = 0 , 0
  venue = Venue.query.all()
  past_show =[]
  upcoming_show = []
  shows = Show.query.filter_by(venue_id = venue_id).all()
  for s in shows:   
    if s.start_time < datetime.datetime.now() :
          past_count+=1
          past_show.append({
            "artist_id": s.artist.id,
            "artist_name": s.artist.name,
            "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
            "start_time": str(s.start_time)
          })
    elif s.start_time > datetime.datetime.now():
          upcoming_count += 1
          upcoming_show.append({
            "artist_id": s.artist.id,
            "artist_name": s.artist.name,
            "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
            "start_time": str(s.start_time)
          }) 
  for v in venue :
    data.append({
    "id": v.id,
    "name": v.name,
    "genres": v.genres.split(','),
    "address": v.address,
    "city": v.city,
    "state": v.state,
    "phone": v.phone,
    "website": "https://www.themusicalhop.com",
    "facebook_link": v.facebook_link,
    "seeking_talent": v.seeking_talent,
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    
    
    "past_shows": past_show ,
    "upcoming_shows": upcoming_show ,
    "past_shows_count": past_count,
    "upcoming_shows_count": upcoming_count,
      
      
    })
        
  data = list(filter(lambda d: d['id'] == venue_id, data))[0]
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
  # on successful db insert, flash success

  
  venue_form = VenueForm()
  try:
    newVenue = Venue(
    name = venue_form.name.data,
    city =  venue_form.city.data,
    state = venue_form.state.data,
    address = venue_form.address.data,
    phone = venue_form.phone.data,
    genres=','.join(venue_form.genres.data),
    facebook_link = venue_form.facebook_link.data)
    db.session.add(newVenue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except :
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  venue = Venue.query.filter_by(id = venue_id).one()
  venue.delete()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for('venues'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = []
  artists = Artist.query.all()
  for a in artists:
        data.append({
          "id": a.id,
          "name": a.name,
        })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  data = []
  search_term = request.form.get('search_term', None)
  artists= Artist.query.filter(
        Artist.name.ilike("%{}%".format(search_term))).all()
  for a in artists:
    data.append({
      "id": a.id,
      "name": a.name,
    })
    
  count_artists = len(artists)
  response = {
        "count": count_artists,
        "data": data}
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data = []
  past_shows_count,upcoming_shows_count = 0 , 0
  artists = Artist.query.all()
  past_show =[]
  upcoming_show = []
  shows = Show.query.filter_by(artist_id = artist_id).all()
  for s in shows:   
      if s.start_time < datetime.datetime.now() :
          past_shows_count+=1
          past_show.append({
            "venue_id": s.venue.id,
            "venue_name": s.venue.name,
            "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
            "start_time": str(s.start_time)
          })
      elif s.start_time > datetime.datetime.now():
          upcoming_shows_count += 1
          upcoming_show.append({
            "venue_id": s.venue.id,
            "venue_name": s.venue.name,
            "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
            "start_time": str(s.start_time)
          })
  for a in artists :            
        data.append({
            "id": a.id,
            "name": a.name,
            "genres": a.genres.split(','),
            "city": a.city,
            "state": a.state,
            "phone": a.phone,
            "website": "https://www.themusicalhop.com",
            "facebook_link": a.facebook_link,
            "seeking_venue": a.seeking_venue,
            "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
            "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
            "past_shows": past_show,
            "upcoming_shows": upcoming_show,
            "past_shows_count": past_shows_count,
            "upcoming_shows_count": upcoming_shows_count,
        })

  data = list(filter(lambda d: d['id'] == artist_id, data))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.filter_by(id = artist_id).one_or_none()
  
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist_Form = ArtistForm()
  artist = Artist.query.filter_by(id = artist_id).one_or_none()
  artist.name = artist_Form.name.data
  artist.city =  artist_Form.city.data
  artist.state = artist_Form.state.data
  artist.phone = artist_Form.phone.data
  artist.genres=','.join(artist_Form.genres.data)
  artist.facebook_link = artist_Form.facebook_link.data
  db.session.commit()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.filter_by(id = venue_id).one_or_none()
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue = Venue.query.filter_by(id = venue_id).one_or_none()
  venue_form = VenueForm()
  venue.name = venue_form.name.data,
  venue.city =  venue_form.city.data,
  venue.state = venue_form.state.data,
  venue.address = venue_form.address.data,
  venue.phone = venue_form.phone.data,
  venue.genres=','.join(venue_form.genres.data),
  venue.facebook_link = venue_form.facebook_link.data
  db.session.commit()
  return redirect(url_for('show_venue', venue_id=venue_id))

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
  artist_Form = ArtistForm()
  try:
    newArtist = Artist(
    name = artist_Form.name.data,
    city =  artist_Form.city.data,
    state = artist_Form.state.data,
    phone = artist_Form.phone.data,
    genres=','.join(artist_Form.genres.data),
    facebook_link = artist_Form.facebook_link.data)
    db.session.add(newArtist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except :
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  finally:
    return render_template('pages/home.html')



#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  shows = Show.query.all()
  for s in shows:
    data.append({
    "venue_id": s.venue.id,
    "venue_name": s.venue.name,
    "artist_id": s.artist.id,
    "artist_name": s.artist.name,
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": str(s.start_time)
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
  show_form = ShowForm()
  try:
    newShow = Show(
      venue_id = show_form.venue_id.data,
      artist_id = show_form.artist_id.data,
      start_time = show_form.start_time.data
    )
    db.session.add(newShow)
    db.session.commit()
    flash('Show was successfully listed!')
  except :
    flash('An error occurred. Show could not be listed.')
  finally:
    return render_template('pages/home.html')
  # on successful db insert, flash success

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/


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
