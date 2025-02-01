from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy # ORM
from sqlalchemy import func
from sqlalchemy.orm import aliased
import pycountry
import os
from datetime import datetime

# instanciates a Flask application
app = Flask(__name__) 
# updates the application constantly
app.config.from_object(__name__) 

# determines the database system used and path to database relative to the app instance folder
app.config['SQLALCHEMY_DATABASE_URI'] =  f"sqlite:///{os.path.abspath('tennisdb.sqlite')}"
# reduces terminal warnings
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 

# We need: username, password, server location, database name. 

# enablse CORS, the route and leave it open to other origins
CORS(app, resources={r"/*":{'origins':"*"}}) 

# instantiates the database
db = SQLAlchemy(app)


def normalize_values_into_db(field, value):
   
   if field == 'hand':
      hand_mapping_dict = {
         'Derecha': 'R',
         'Izquierda': 'L',
         '-': 'Unknown'
      }
      return hand_mapping_dict.get(value, 'Unknown')
   
   if field in ['height', 'wikidata_id']:
      return value if (value and value != '-') else 'Unknown'
   
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
         print(f'Error converting country: {value}, Error: {e}')
         return 'unknown'

      
   

# Model for table Players
class Players(db.Model):
   player_id = db.Column(db.String(7), primary_key=True)
   name_last = db.Column(db.String(50))
   hand = db.Column(db.String(7))
   birth_date = db.Column(db.Date)
   country = db.Column(db.String(3))
   height = db.Column(db.String(3))
   wikidata_id = db.Column(db.String(15))
   fullname = db.Column(db.String(60))
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
         if hand != 'unknown':  # other values not allowed
            hand = 'unknown'
         return format_unknown(hand)
      
      def format_birth_date(birth_date):
         if birth_date: 
            return birth_date.strftime('%d-%m-%Y') 
         return None
      
      return {
         'player_id': self.player_id,
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



# GET all players route handle
@app.route('/players')
def get_all_players():
   try:
      # Retrieves tuples with player and his best ranking for ALL players
      query = db.session.query(Players, func.min(Rankings.rank).label('best_rank'))\
            .outerjoin(Rankings, Players.player_id == Rankings.player_id)\
            .group_by(Players)\
            .order_by(Players.birth_date.desc())
            
      #query = db.session.query(Players).order_by(Players.birth_date.desc())
      total_players = query.count()
            
      page = int(request.args.get('page', 1))  # page 1 as default
      if page < 1 : page = 1
      
      per_page = int(request.args.get('per_page', 20))   # 20 players per page
      if ((per_page < 1) or (per_page > total_players)) : per_page = 20

      total_pages = (total_players + per_page - 1) // per_page
      if page > total_pages: page = total_pages
      
      # Filters players in page
      players_page = query.offset((page - 1) * per_page).limit(per_page).all()
      players_list_in_page = []
      
      # Composes dict for each player from tuple
      for player, best_rank in players_page:
         player_dict = player.to_dict()
         player_dict['best_ranking'] = best_rank if best_rank is not None else '-'
         
         players_list_in_page.append(player_dict)
      
      
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
      app.logger.error(f"Error retrieving players: {str(e)}", exc_info=True)
      return jsonify({
         'status': 'error', 
         'message': f'Error retrieving players: {str(e)}'
      }), 500
      
      
# GET player by id route handle
@app.route('/players/<string:player_id>', methods=['GET'])
def get_player(player_id):
    try:
        player = Players.query.filter_by(player_id=player_id).first()

        if not player:
            return jsonify({
                'status': 'error',
                'message': f'Player id {player_id} not found in database.'
            }), 404

        return jsonify({
            'status': 'success',
            'player': player.to_dict()
        }), 200

    except Exception as e:
        print(f'Error retrieving player: {str(e)}')
        return jsonify({
            'status': 'error',
            'message': f'Error retrieving player: {str(e)}'
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
      print( f'Error adding new player: {str(e)}')
      return jsonify({
         'status': 'error', 
         'message': f'Error adding new player: {str(e)}'
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
        print(f'Error deleting player: {str(e)}')
        return jsonify({
            'status': 'error',
            'message': f'Error deleting player: {str(e)}'
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
        print(f'Error updating player: {str(e)}')
        return jsonify({
            'status': 'error',
            'message': f'Error updating player: {str(e)}'
        }), 500




   # # Wikidata API endpoint
   # url = "https://www.wikidata.org/w/api.php"

   # # Parámetros de la solicitud
   # params = {
   #    "action": "wbgetentities",
   #    "ids": "Q3494",  # Reemplaza con el wikidata_id
   #    "format": "json",
   #    "languages": "en"
   # }

   # # Realizar la solicitud
   # response = requests.get(url, params=params)

   # # Procesar la respuesta
   # data = response.json()

if __name__ == "__main__":
   app.run(debug=True) #development mode
   