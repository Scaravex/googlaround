##help place: https://developers.google.com/places/web-service/search
##download googleplaces here --> https://github.com/slimkrazy/python-google-places
#installed: googleplaces, gmaps
from googleplaces import GooglePlaces, types, lang
import json
import pandas as pd
import numpy as np

def create_dictionary (place):
    '''
    create a dictionary with information from a googleMaps place
    '''
    info = {}
    info ['_id']           = place.place_id
    info ['name']          = place.name
    info ['address']       = place.formatted_address
#   info ['PLZ']           = place.details['address_components'][7]['long_name']
    try: info ['geo_location']  = place.geo_location
    except: pass

    try: info ['opening_hours'] = place.details['opening_hours']['weekday_text']
    except: pass

    try: info ['rating']        = float(place.rating)
    except: pass
    
    try: info ['viewport']      = place.details['geometry']['viewport']
    except: pass

    try: info ['types']         = place.details['types']
    except: pass
    
    try: info ['url']           = place.url
    except: pass

    try: info ['website']       = place.website
    except: pass

    return info


def saver_queries (saved_places, query_result):
    '''
    save all the queries from the ones extracted from gmaps searches API
    '''
    for place in query_result.places:
        # Returned places from a query are place summaries.
        print (place.name)
        print (place.geo_location)
        print (place.place_id)
        # The following method has to make a further API call.
        place.get_details()
        # Referencing any of the attributes below, prior to making a call to
        # get_details() will raise a googleplaces.GooglePlacesAttributeError.
        print (place.details) # A dict matching the JSON response from Google.
        print (place.local_phone_number) # print (place.international_phone_number)
        print (place.website)
        print (place.url)
        tempDict = create_dictionary(place)
        saved_places.append(tempDict)

    return saved_places
