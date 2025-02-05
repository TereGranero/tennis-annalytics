@app.route('/players', methods=['GET'])
def get_players():
   try:
      # Calculates number of players in database      
      total_players = db.session.query(Players).count()
      
      # Gets and validates arguments
      page = int(request.args.get('page', 1))     
      per_page = int(request.args.get('per_page', 10))
      if page < 1 : 
         page = 1
      
      if (per_page < 1 or per_page > total_players or per_page > 30): 
         per_page = 10
      
      # Calculates number of pages for all players in database
      total_pages = (total_players + per_page - 1) // per_page
      
      if page > total_pages: page = total_pages
     
      # Subquery: retrieves player_id for current page players
      query = (
         select(Players)
         .order_by(desc(Players.birth_date))
         .offset((page - 1) * per_page)
         .limit(per_page)
      )

      # Players in current page as tuples (Player object,)
      players_tuples = db.session.execute(query).all()
      
      # List of players objects
      players_objects_list = [player[0] for player in players_tuples]

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