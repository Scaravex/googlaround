##help place: https://developers.google.com/places/web-service/search
##download googleplaces here --> https://github.com/slimkrazy/python-google-places
#installed: googleplaces, gmaps

import json
import pandas as pd
import numpy as np
import csv
import codecs
from time import sleep

from googleplaces import GooglePlaces
# import of internal files
from config import API_KEY
from config import SEARCH_KEY  #e.g. restaurant, supermarket, bar
from config import LOCATION_KEY # good idea is to have a list of U-bahn station, save every search and eliminate duplicated results
from config import PICKLE_FILE_PATH

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


def query_gmaps(api_key=API_KEY, search_key=SEARCH_KEY, location_key=LOCATION_KEY):
    '''
    function which performs the query of stores
    '''
    saved_shops = []
    google_places = GooglePlaces(api_key)
    # Maybe can be preferred to use the text_search API, instead.
    query_result = google_places.nearby_search(
                                               location = location_key, keyword = search_key,
                                               radius = 20000,
                                               rankby = "distance")#,pagetoken='nextPageToken')
    ##  pagetoken=x -->  Returns the next 20 results from a previously run search.
    ##  Setting a pagetoken parameter will execute a search with the same parameters
    ##  used previously — all parameters other than pagetoken will be ignored.

    if query_result.has_attributions:
        print(query_result.html_attributions)

    saved_shops = saver_queries(saved_shops, query_result)
    # Are there any additional pages of results?
    print(len(saved_shops))
    temporary_search = query_result
    max_iter=0
    while temporary_search.has_next_page_token & max_iter<1:
        max_iter+=1
        try:
            query_result_next_page = google_places.nearby_search(pagetoken = temporary_search.next_page_token)
            saved_shops = saver_queries(saved_shops,query_result_next_page)
            temporary_search = query_result_next_page
        except:
            pass

    return saved_shops


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


def new_query_checker(good_shops, df, api_key=API_KEY, search_key=SEARCH_KEY, location_key=LOCATION_KEY):
    '''
    check if the values in the new query are in the current database
    '''
    saved_shops = query_gmaps(api_key, search_key, location_key)

    ## to be smarter, check in the database and save into database directly
    #s  = pd.Series(df['address']) --> faster
    count = 0
    for shops in saved_shops:
        if any(df._id == shops['_id']):
            pass
        else:
            count+=1
            good_shops.append(shops)
    print("There were in total these new items:")
    print(count)

    return good_shops

##to be very smart: create a matrix of data points in Berlin,
## convert into addresses and then only select the unique results
# from_csv('total_shops.csv', encoding='latin_1')
with codecs.open('locations.csv', 'r', encoding='utf-8', errors='ignore') as fdata:
    reader = csv.reader(fdata)
    locations = []
    for row in reader:
        locations.append(row)

good_shops = query_gmaps()
locations  = pd.DataFrame(locations, columns = ['Places'])


def find_good_shops(good_shops, locations = locations):
    '''identify only the good_shops'''
    for location in locations:
        try:
            good_shops = new_query_checker(good_shops, df=pd.DataFrame(good_shops), location_key=location)
            print(len(good_shops))
            print("going to sleep")
            sleep(45)  # trick to avoid google maps troubles
            print('I slept 45 secondds, zzz: already saved {} good shops'.format(len(good_shops)))
        except:
            break
        
    return good_shops
