import requests
from requests.exceptions import HTTPError, RequestException
from datetime import datetime

def get_wikidata_property(wikidata_id, property):
   
   # Validates arguments
   arguments = [wikidata_id, property]
   for argument in arguments:
      if not argument:
         print(f'WikidataServices Error in get_property: empty {argument}')
         return None
   
   # Connection parameters
   wiki_api_url = 'https://www.wikidata.org/w/api.php'
   params = {
      'action': 'wbgetclaims',
      'format': 'json',
      'entity': wikidata_id,
      'property': property
   }
   
   try:
      
      # Requests Wikidata API
      res = requests.get(
         wiki_api_url, 
         params=params, 
         timeout=10
      )
      
      # Raises HTTPError when response status is 4XX or 5XX
      res.raise_for_status()
      
      data = res.json()
      
      # Empty response
      if not property in data.get('claims', {}): 
         print(f'WikidataServices Warning from get_property: Property {property} does not exist for wikidata id {wikidata_id}')   
         return None
      
      # Extracts property array
      return data['claims'][property]
      
   except HTTPError as e:
      print(f'WikidataServices Error in get_wikidata_property: HTTPError - {e}')
      return None
   except RequestException as e:
      print(f'WikidataServices Error in get_wikidata_property: HTTP Request Error - {e}')
      return None
   except Exception as e:
      print(f'WikidataServices Error in get_wikidata_property: {e}')
      return None


def is_tennis_player(wikidata_id):
   
   try:
      # Validates argument
      if not wikidata_id.strip():
         print('WikidataServices Error in is_tennis_player: empty wikidata_id.')
         return None
      
      # Requests Wikidata API
      jobs_claim = get_wikidata_property(wikidata_id, 'P31')
      
      # Empty response
      if not jobs_claim or len(jobs_claim) == 0:
         print(f'WikidataServices Warning from is_tennis_player: wikidata_id {wikidata_id} has not been validated as a tennis player because there is no property P31.')
         return False
      
      # Loops claim array
      for job in jobs_claim:
         
         # Extracts job
         job_id = job['mainsnak']['datavalue']['value']['id']
         
         # Not a tennis player
         if job_id not in ['Q10833314', 'Q13382460', 'Q15100009']:
            print(f'WikidataServices Warning from is_tennis_player: wikidata_id {wikidata_id} has not been validated as a tennis player')
            return False
         
         # Validated tennis player
         print(f'WikidataServices Info from is_tennis_player: wikidata_id {wikidata_id} has been validated as a tennis player.')
         return True
      
   except Exception as e:
      print(f'WikidataServices Error in is_tennis_player: {str(e)}')
      return False




def get_wikidata_id(player_name):
   

   # Validates argument
   if not player_name.strip():
      print('WikidataServices Error in get_wikidata_id: empty player name.')
      return None

   # Connection parameters            
   wiki_api_url = f'https://www.wikidata.org/w/api.php'
   params = {
      'action': 'wbsearchentities',
      'format': 'json',
      'language': 'en',
      'search': player_name,
      'type': 'item',
      'limit': 1,
      'props': 'id'
   }

   try: 
      # Requests Wikidata API
      res = requests.get(
         wiki_api_url, 
         params=params, 
         timeout=10
      )
      
      # Raises HTTPError when response status is 4XX or 5XX
      res.raise_for_status()
      
      data = res.json()
      
      # Empty response
      if not data.get('search'):
         print(f'WikidataServices Warning from get_wikidata_id: No wikidata id has been found for player {player_name}')
         return None
      
      wikidata_id = data['search'][0]['id']
      
      # Empty response or not validated tennis player
      if not wikidata_id or not is_tennis_player(wikidata_id):
         print(f'WikidataServices Warning from get_wikidata_id: No wikidata id has been found for player {player_name}')
         return None
      
      # Validated wikidata_id found
      print(f'WikidataServices Info from get_wikidata_id: wikidata id {wikidata_id} has been found for player {player_name}')
      return wikidata_id
   
   except HTTPError as e:
      print(f'WikidataServices Error in get_wikidata_id: HTTPError - {e}')
      return None
   except RequestException as e:
      print(f'WikidataServices Error in get_wikidata_id: HTTP Request Error - {e}')
      return None
   except Exception as e:
      print(f'WikidataServices Error in get_wikidata_id: {e}')
      return None
   

   
def get_wikidata_country(wikidata_id):
   
   try:
      # Validates argument
      if not wikidata_id.strip():
         print('WikidataServices Error in get_wikidata_country: empty wikidata_id.')
         return None

      # Requests Wikidata API
      country_claim = get_wikidata_property(wikidata_id, 'P27')

      # Empty response
      if not country_claim or len(country_claim) == 0:
         print(f'WikidataServices Warning from get_wikidata_country: No country id has been found for wikidata_id {wikidata_id}')
         return None
      
      # Extracts entity country id
      country_id = country_claim[0]['mainsnak']['datavalue']['value']['id']
      
      # Empty response
      if not country_id:
         print(f'WikidataServices Warning from get_wikidata_country: No country id has been found for wikidata_id {wikidata_id}')
         return None
      
      # Requests Wikidata API for country ISO-3166-1 alpha-2
      alpha2_claim = get_wikidata_property(country_id, 'P297')
      
      # Empty response
      if not alpha2_claim or len(alpha2_claim) == 0:
         print(f'WikidataServices Warning from get_wikidata_country: No alpha2 code has been found for country_id {country_id}')
         return None
         
      # Extracts alpha2   
      country_alpha2 = alpha2_claim[0]["mainsnak"]["datavalue"]["value"] 
      
      # Empty response
      if not country_alpha2:
         print(f'WikidataServices Warning from get_wikidata_country: No alpha2 code has been found for wikidata id {wikidata_id} country id {country_id}')
         return None
      
      # Country found      
      print(f'WikidataServices Info from get_wikidata_country: alpha2 code has been found for wikidata id {wikidata_id} country id {country_id}')
      return country_alpha2.lower()

   except Exception as e:
      print(f'WikidataServices Error in get_wikidata_country: {str(e)}')
      return None
   

def get_wikidata_birth_date(wikidata_id):

   try:
      # Validates argument
      if not wikidata_id.strip():
         print( 'WikidataServices Error in get_wikidata_birth_date: empty wikidata_id.')
         return None

      # Requests Wikidata API
      birth_date_claim = get_wikidata_property(wikidata_id, 'P569')

      # Empty response
      if not birth_date_claim or len(birth_date_claim) == 0:
         print(f'WikidataServices Warning from get_wikidata_birth_date: No birth_date has been found for wikidata_id {wikidata_id}')
         return None
      
      # Extracts birth date
      birth_date = birth_date_claim[0]['mainsnak']['datavalue']['value']['time']
      
      # Empty response
      if not birth_date:
         print(f'WikidataServices Warning from get_wikidata_birth_date: No birth_date has been found for wikidata_id {wikidata_id}')
         return None

      # Formats birth date found
      birth_date = birth_date[1:-1]  # format +2007-10-01T00:00:00Z
      formatted_birth_date = datetime.strptime(birth_date, "%Y-%m-%dT%H:%M:%S").date()
      print(f'WikidataServices Info from get_wikidata_birth_date: birth date {formatted_birth_date} has been found for wikidata id {wikidata_id}')
      return formatted_birth_date
            
   except Exception as e:
      print(f'WikidataServices Error in get_wikidata_birth_date: {str(e)}')
      return None
   

def get_wikidata_height(wikidata_id):

   try:
      # Validates argument 
      if not wikidata_id.strip():
         print('WikidataServices Error in get_wikidata_height: empty wikidata_id.')
         return None

      # Requests Wikidata API
      height_claim = get_wikidata_property(wikidata_id, 'P2048')

      # Empty response
      if not height_claim or len(height_claim) == 0:
         print(f'WikidataServices Warning from get_wikidata_height: No height has been found for wikidata_id {wikidata_id}')
         return None
      
      # Extracts height value and unit
      height = height_claim[0]['mainsnak']['datavalue']['value']['amount'] # +1.85
      unit = height_claim[0]['mainsnak']['datavalue']['value']['unit'] #http://www.wikidata.org/entity/Q11573
      
      # Empty response
      if not height or not unit:
         print(f'WikidataServices Warning from get_wikidata_height: No height has been found for wikidata_id {wikidata_id}')
         return None      
      
      # Conversion to cm 
      units_dict = {
         'Q11573': 100,    # m
         'Q174728': 1,     # cm
         'Q3710': 30.48,   # feet
         'Q218593': 2.54,  # inches
      }

      # Clean value and unit
      clean_height = float(height.lstrip('+'))
      clean_unit = unit.split('/')[-1]
            
      # Unknown units      
      if clean_unit not in units_dict:
         print(f'WikidataServices Warning from get_wikidata_height: No height has been found for wikidata_id {wikidata_id}')
         return None
      
      # Converts to cm
      height_in_cm = round( clean_height * units_dict[clean_unit], 1)
   
      print(f'WikidataServices Info from get_wikidata_height: height {height_in_cm} cm has been found for wikidata id {wikidata_id}')
      return height_in_cm   
      
   except Exception as e:
      print(f'WikidataServices Error in get_wikidata_height: {str(e)}')
      return None
   

def get_wikidata_weight(wikidata_id):

   try:
      # Validates argument
      if not wikidata_id.strip():
         print('WikidataServices Error in get_wikidata_weight: empty wikidata_id.')
         return None

      # Requests Wikidata API
      weight_claim = get_wikidata_property(wikidata_id, 'P2067')

      # Empty response
      if not weight_claim or len(weight_claim) == 0:
         print(f'WikidataServices Warning from get_wikidata_weight: No weight has been found for wikidata_id {wikidata_id}')
         return None
      
      # Extracts weight value and unit
      weight = weight_claim[0]['mainsnak']['datavalue']['value']['amount'] # +80
      unit = weight_claim[0]['mainsnak']['datavalue']['value']['unit'] # http://www.wikidata.org/entity/Q11570
      
      # Empty response
      if not weight or not unit:
         print(f'WikidataServices Warning from get_wikidata_weight: No weight has been found for wikidata_id {wikidata_id}')
         return None    
      
      # Conversion to kg
      units_dict = {
         'Q11570': 1,      # kg
         'Q19908': 0.4536, # lbs to kg
      }

      # Clean value and unit
      clean_weight = float(weight.lstrip('+'))
      clean_unit = unit.split('/')[-1]
      
      # Unknown units  
      if clean_unit not in units_dict:
         print(f'WikidataServices Warning from get_wikidata_weight: No weight has been found for wikidata_id {wikidata_id}')
         return None
      
      # Converts to kg
      weight_in_kg = round(clean_weight * units_dict[clean_unit], 1)
         
      print(f'WikidataServices Info from get_wikidata_weigth: weight {weight_in_kg} kg has been found for wikidata id {wikidata_id}')
      return weight_in_kg
      
   except Exception as e:
      print(f'WikidataServices Error in get_wikidata_weight: {str(e)}')
      return None
   
   
def get_wikidata_hand(wikidata_id):

   try:
      # Validates argument 
      if not wikidata_id.strip():
         print('WikidataServices Error in get_wikidata_hand: empty wikidata_id.')
         return None
      
      # Requests Wikidata API
      hand_claim = get_wikidata_property(wikidata_id, 'P552')

      # Empty response
      if not hand_claim or len(hand_claim) == 0:
         print(f'WikidataServices Warning from get_wikidata_hand: No hand has been found for wikidata_id {wikidata_id}')
         return None
      
      # Extracts entinty hand id
      hand = hand_claim[0]['mainsnak']['datavalue']['value']['amount']
      
      hand_dict = {
         'Q1310443': 'Derecha',
         'Q3029952': 'Izquierda',
      }
      
      # Empty or unknown hand
      if not hand or (not hand in hand_dict):
         print(f'WikidataServices Warning from get_wikidata_hand: No hand has been found for wikidata_id {wikidata_id}')
         return None
      
      # Format hand   
      formatted_hand = hand_dict[hand]
               
      print(f'WikidataServices: hand {formatted_hand} has been found for wikidata id {wikidata_id}')
      return formatted_hand # HAY QUE NORMALIZARLA PARA METERLA EN LA DB
      
   except Exception as e:
      print(f'WikidataServices Error in get_wikidata_hand: {str(e)}')
      return None
   
   
def get_wikidata_networks(wikidata_id):
   
   try:
      # Validates argument
      if not wikidata_id.strip():
         print('WikidataServices Error in get_wikidata_networks: empty wikidata_id.')
         return None

      # Wikidata properties for networks
      properties = {
         'instagram': 'P2003',
         'facebook': 'P2013',
         'x_twitter': 'P2002'
      }

      # Return object
      networks = {}

      # Loops networks
      for network, prop in properties.items():
         
         # Requests Wikidata API
         username_claim = get_wikidata_property(wikidata_id, prop)

         # Empty response
         if not username_claim or len(username_claim) == 0:
            print(f'WikidataServices Warning from get_wikidata_networks: No {network} username has been found for wikidata_id {wikidata_id}')
            networks[network] = '-'
            
         else:
            # Extracts username
            username = username_claim[0]['mainsnak']['datavalue']['value']
            
            # Empty response
            if not username:
               print(f'WikidataServices Warning from get_wikidata_networks: No {network} username has been found for wikidata_id {wikidata_id}')
               networks[network] = '-'
               
            else:
               # Composes URLs
               if network == 'instagram':
                  networks[network] = f'https://www.instagram.com/{username}'
               elif network == 'facebook':
                  networks[network] = f'https://www.facebook.com/{username}'
               elif network == 'x_twitter':
                  networks[network] = f'https://x.com/{username}'

      return networks  # HAY QUE NORMALIZAR ANTES DE METER EN DB !!
   
   except Exception as e:
      print(f'WikidataServices Error in get_wikidata_networks: {str(e)}')
      return None
   
def get_wikidata_pro_since(wikidata_id):
   
   try:
      # Validates argument 
      if not wikidata_id.strip():
         print('WikidataServices Error in get_wikidata_pro_since: empty wikidata_id.')
         return None

      # Requests Wikidata API
      pro_since_claim = get_wikidata_property(wikidata_id, 'P2031')

      # Empty response
      if not pro_since_claim or len(pro_since_claim) == 0:
         print(f'WikidataServices Warning in get_wikidata_pro_since: No pro_since year found for wikidata_id {wikidata_id}')
         return None

      # Extracts pro_since date
      pro_since = pro_since_claim[0]['mainsnak']['datavalue']['value']['time']
      
      # Empty response      
      if not pro_since:
         print(f'WikidataServices Warning in get_wikidata_pro_since: No pro_since year found for wikidata_id {wikidata_id}')
         return None

      # Extracts year
      pro_since_year = int(pro_since[1:5]) # "+2005-04-30T00:00:00Z"

      return pro_since_year

   except Exception as e:
      print(f'WikidataServices Error in get_wikidata_pro_since: {str(e)}')
      return None

