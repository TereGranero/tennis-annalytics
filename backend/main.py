from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy # ORM
from sqlalchemy import func, select, desc
import pycountry
import os
from datetime import datetime

from Services.wikidata_services import get_wikidata_id,\
                                       get_wikidata_country,\
                                       get_wikidata_birth_date, \
                                       get_wikidata_height, \
                                       get_wikidata_weight, \
                                       get_wikidata_hand

# -------------------------- CONFIGURATION ---------------------------------- #

# instanciates a Flask application
app = Flask(__name__) 
# updates the application constantly
app.config.from_object(__name__) 

# determines the database system used 
# and path to database relative to the app instance folder
app.config['SQLALCHEMY_DATABASE_URI'] =  f"sqlite:///{os.path.abspath('tennisdb.sqlite')}"
# reduces terminal warnings
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 

# We need: username, password, server location, database name. 

# enablse CORS, the route and leave it open to other origins
CORS(app, resources={r"/*":{'origins':"*"}}) 

# instantiates the database
db = SQLAlchemy(app)

# -------------------------- AUX FUNCTIONS ---------------------------------- #

def normalize_values_into_db(field, value):
   
   if field == 'hand':
      hand_mapping_dict = {
         'Derecha': 'R',
         'Izquierda': 'L',
         '-': 'unknown'
      }
      return hand_mapping_dict.get(value, 'unknown')
   
   if field in ['height', 'wikidata_id']:
      return value if (value and value != '-') else 'unknown'
   
   if field == 'birth_date':
      return datetime.strptime(value, '%Y-%m-%d').date() if value else None
   
   if field == 'country':
      try:
         if value and len(value) == 3:
            country = pycountry.countries.get(alpha_3=value)
            return country.alpha_2.lower() if country else 'unknown'
         if value and len(value) == 2:
            return value.lower()
         return 'unknown'
      
      except Exception as e:
         error_msg = f'Error converting country {value}: {str(e)}'
         app.logger.error(error_msg, exc_info=True)
         
         return 'unknown'

      
   
# ---------------------------- DATA MODELS ---------------------------------- #

# Model for table Players
class Players(db.Model):
   player_id = db.Column(db.String(7), primary_key=True)
   name_first = db.Column(db.String(50))
   name_last = db.Column(db.String(50))
   hand = db.Column(db.String(7))
   birth_date = db.Column(db.Date)
   country = db.Column(db.String(3))
   height = db.Column(db.String(3))
   wikidata_id = db.Column(db.String(15))
   fullname = db.Column(db.String(60))
   instagram = db.Column(db.String(100))
   facebook = db.Column(db.String(100))
   x_twitter = db.Column(db.String(100))
   rankings = db.relationship('Rankings', backref='player', lazy='dynamic')
   
   def to_dict(self):
      # Converts registers to dict and normalizes some values according to frontend
      
      def format_unknown(value):
         return value if value != 'unknown' else '-'
      
      def normalize_country(country):
         try:
            if country and len(country) == 3:
               country = pycountry.countries.get(alpha_3=country)
               return country.alpha_2.lower() if country else 'unknown'
            if country and len(country) == 2:
               return country.lower()
            return 'unknown'
         
         except Exception as e:
            print(f'Error converting country: {country}, Error: {e}')
            return 'unknown'   
      
      def normalize_hand(hand):
         if hand == 'R':
            return 'Derecha'
         if hand == 'L':
            return 'Izquierda'
         if hand != 'unknown':  # not allowed values
            hand = 'unknown'
         return format_unknown(hand)
      
      def format_birth_date(birth_date):
         if birth_date: 
            return birth_date.strftime('%d-%m-%Y') 
         return None
      
      return {
         'player_id': self.player_id,
         'name_first': format_unknown(self.name_first),
         'name_last': self.name_last,
         'hand': normalize_hand(self.hand),
         'birth_date': format_birth_date(self.birth_date),
         'country': normalize_country(self.country),
         'height': format_unknown(self.height),
         'wikidata_id': format_unknown(self.wikidata_id),
         'fullname': self.fullname
      }

   def get_best_ranking(self):
      return self.rankings.order_by(Rankings.rank.asc()).first()
   
      
# Model for table Rankings
class Rankings(db.Model):
   player_id = db.Column(db.String(7), db.ForeignKey('players.player_id'), primary_key=True)
   ranking_date = db.Column(db.Date, primary_key=True)
   points = db.Column(db.String(7))
   rank = db.Column(db.Integer)

   def to_dict(self):
      # Converts registers to dict and normalizes some values according to frontend
      
      def format_unknown(value):
         return value if value != "unknown" else "-"
            
      def normalize_points(points):
         return format_unknown(points)
      
      def format_ranking_date(ranking_date):
         if ranking_date: 
            return ranking_date.strftime('%d-%m-%Y') 
         return None
      
      return {
         'player_id': self.player_id,
         'ranking_date': format_ranking_date(self.ranking_date),
         'points': normalize_points(self.points),
         'rank': self.rank
      }


# ------------------------------- ROUTES ------------------------------------ #

# GET all players route handle
@app.route('/players', methods=['GET'])
def get_players():
   try:
      
      # Gets and validates arguments
      page = int(request.args.get('page', 1))     
      per_page = int(request.args.get('per_page', 10))
      search_name_last = request.args.get('search_name_last', '').strip()
      
      if page < 1 : 
         page = 1
      
      if (per_page < 1 or per_page > 30): 
         per_page = 10
      
      # Retrieves all players in database
      base_query = db.session.query(Players)

      # Filters by search_name_last if provided
      if search_name_last:
         base_query = base_query.filter(Players.name_last.ilike(f'%{search_name_last}%'))

      # Calculates number of filtered players
      total_players = base_query.count()
      
      # Calculates number of pages for all filtered players
      total_pages = (total_players + per_page - 1) // per_page
      
      if page > total_pages: 
         page = total_pages if total_pages > 0 else 1
     
      # Retrieves filtered players for current page
      query = (
         base_query
         .order_by(desc(Players.birth_date))
         .offset((page - 1) * per_page)
         .limit(per_page)
      )

      # Query: retrieves players with their best_rank for current page
      # query = (
      #    select(Players, func.min(Rankings.rank).label('best_rank'))
      #    .outerjoin(Rankings, Players.player_id == Rankings.player_id)
      #    .filter(Players.player_id.in_(subquery))
      #    .group_by(Players)
      #    .order_by((Players.birth_date))
      # )
      
      # List of players objects
      players_objects_list = query.all()
      
      # Converts to list of dicts
      players_list_in_page = []
      
      # Composes dict for each player and searches missings in Wikidata
      #for player, best_rank in players_page:
      for player_object in players_objects_list:
         
         player = player_object.to_dict()         
         
         # Controls if commit is needed
         update_flag = False    

         # Gets wikidata id
         if player['wikidata_id'] == '-':
            
            # Composes complete player name
            if player['name_first'] == '-':
               player_name = player['name_last'].strip()
            else:
               player_name = player['name_first'].strip() + ' ' + player['name_last'].strip()
               
            wikidata_id = get_wikidata_id(player_name)
            if wikidata_id:
               player['wikidata_id'] = wikidata_id
               player_object.wikidata_id = wikidata_id 
               update_flag = True
         
         # Gets country
         if player['wikidata_id'] != '-' and player['country'] == 'unknown':
            
            country = get_wikidata_country(player['wikidata_id'])
            if country: 
               player['country'] = country
               player_object.country = country
               update_flag = True
               
         # Gets birth_date
         if player['wikidata_id'] != '-' and \
            ( player['birth_date'] == None or player['birth_date'] == '' or player['birth_date'] == '01-01-1800'):
            
            birth_date = get_wikidata_birth_date(player['wikidata_id'])
            if birth_date: 
               player['birth_date'] = birth_date.strftime('%d-%m-%Y') 
               player_object.birth_date = birth_date
               update_flag = True
            
         players_list_in_page.append(player)
         
         # Commits changes into database
         if update_flag:
            db.session.commit()
               
      
      response_object = {
         'status':'success',
         'message': 'Players have been retrieved successfully!',
         'players': players_list_in_page,
         'total_players': total_players, 
         'page': page,
         'pages': total_pages
      } 
      
      return jsonify(response_object), 200
   
   except Exception as e:
      error_msg = f'Error retrieving players: {str(e)}'
      app.logger.error(error_msg, exc_info=True)
      return jsonify({
         'status': 'error', 
         'message': error_msg
      }), 500
      
      
# GET player by id route handle
@app.route('/players/<string:player_id>', methods=['GET'])
def get_player(player_id):
    try:
        player = Players.query.filter_by(player_id=player_id).first()

        if not player:
            error_msg = f'Player id {player_id} not found in database.'
            print(error_msg)
            return jsonify({
                'status': 'error',
                'message': error_msg
            }), 404

        return jsonify({
            'status': 'success',
            'player': player.to_dict()
        }), 200

    except Exception as e:
         error_msg = f'Error retrieving player: {str(e)}'
         app.logger.error(error_msg, exc_info=True)
         
         return jsonify({
               'status': 'error',
               'message': error_msg
         }), 500


# POST player route handle
@app.route('/players', methods=['POST'])
def add_player():
   try:
      data = request.get_json()
      
      # Comprobar que los valores son válidos

      # Creates new instance of model
      new_player = Players(
         player_id=data.get('player_id'),
         name_first=data.get('name_first'),
         name_last=data.get('name_last'),
         hand=normalize_values_into_db('hand', data.get('hand')),
         birth_date=normalize_values_into_db('birth_date', data.get('birth_date')),
         country=data.get('country'),
         height=normalize_values_into_db('height', data.get('height')),
         wikidata_id=normalize_values_into_db('wikidata_id', data.get('wikidata_id')),
         fullname=data.get('fullname')
      )
      
      # Adds player
      db.session.add(new_player)
      
      # Commits changes into database
      db.session.commit()
      
      return jsonify({
         'status': 'success', 
         'message': 'New player has been added successfully!'
      }), 201
   
   except Exception as e:
      db.session.rollback()
      error_msg = f'Error adding new player: {str(e)}'
      app.logger.error(error_msg, exc_info=True)
      
      return jsonify({
         'status': 'error', 
         'message': error_msg
      }), 500
      
# DELETE player route handle
@app.route('/players/<string:player_id>', methods=['DELETE'])
def delete_player(player_id):
    try:
        player = Players.query.filter_by(player_id=player_id).first()
        
        if not player:
            return jsonify({
                'status': 'error',
                'message': f'Player id {player_id} not found in database.'
            }), 404

        # Deletes player
        db.session.delete(player)
        
        # Commits changes into database
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': f'Player id {player_id} has been successfully deleted.'
        }), 200

    except Exception as e:
        error_msg = f'Error deleting player: {str(e)}'
        app.logger.error(error_msg, exc_info=True)
        
        return jsonify({
            'status': 'error',
            'message': error_msg
        }), 500

# PUT player by id route handle
@app.route('/players/<string:player_id>', methods=['PUT'])
def update_player(player_id):
   try:
      player = Players.query.filter_by(player_id=player_id).first()

      if not player:
         return jsonify({
               'status': 'error',
               'message': f'Player id {player_id} not found in database.'
         }), 404

      data = request.get_json()

      # Updates player
      if 'name_first' in data:
         player.name_first = data['name_first']
      if 'name_last' in data:
         player.name_last = data['name_last']
      if 'hand' in data:
         player.hand = normalize_values_into_db('hand', data['hand'])
      if 'birth_date' in data:
         player.birth_date = normalize_values_into_db('birth_date', data['birth_date'])
      if 'country' in data:
         player.country = data['country']
      if 'height' in data:
         player.height = normalize_values_into_db('height', data['height'])
      if 'wikidata_id' in data:
         player.wikidata_id = normalize_values_into_db('wikidata_id', data['wikidata_id'])
      if 'fullname' in data:
         player.fullname = data['fullname']

      # Commits changes into database
      db.session.commit()

      return jsonify({
         'status': 'success',
         'message': f'Player id {player_id} has been successfully updated.'
      }), 200

   except Exception as e:
      db.session.rollback()
      error_msg = f'Error updating player: {str(e)}'
      app.logger.error(error_msg, exc_info=True)
      
      return jsonify({
         'status': 'error',
         'message': error_msg
      }), 500


if __name__ == "__main__":
   app.run(debug=True) #development mode
   