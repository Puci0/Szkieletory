import string
from collections import OrderedDict
import requests
from urllib.parse import urlencode
from django.conf import settings


API_KEY = settings.API_KEY

def memoize(func):
    """
    Dekorator do zapamiętywania wyników funkcji (memoization).
    """
    cache = {}
    def memoized_func(*args):
        key = str(args)
        if key not in cache:
            cache[key] = func(*args)
        return cache[key]
    return memoized_func


@memoize
def get_sorted_list_and_legs(start_loc: str, loc_list: list, mode: str ='walking') -> tuple:
    """
    Pobiera posortowaną listę lokalizacji i informacje o odcinkach trasy.

    :param start_loc: Lokalizacja początkowa
    :param loc_list: Lista lokalizacji
    :param mode: Tryb podróży (domyślnie 'walking')
    :return: Krotka zawierająca posortowaną listę lokalizacji i informacje o odcinkach trasy
    """
    start_loc = "Warszawa " + start_loc
    name_list = ["Warszawa " + loc.nazwa_atrakcji for loc in loc_list]

    PATH_URL = 'https://maps.googleapis.com/maps/api/directions/json'

    PATH_PARAMS = {
        'key': API_KEY,
        'origin': start_loc,
        'destination': start_loc,
        'mode': mode,
        'waypoints': "optimize:true|" + "|".join(name_list),
    }

    response = requests.get(url=PATH_URL, params=PATH_PARAMS).json()
    waypoint_order = response['routes'][0]['waypoint_order']
    sorted_loc_list = [loc_list[i] for i in waypoint_order]
    legs = response['routes'][0]['legs'][:-1]

    return sorted_loc_list, legs


def generate_static_map(start_loc: str, loc_list: list, mode: str ='walking') -> tuple:
    """
    Generuje statyczną mapę z zaznaczoną trasą zwiedzania.

    :param start_loc: Lokalizacja początkowa
    :param loc_list: Lista lokalizacji
    :param mode: Tryb podróży (domyślnie 'walking')
    :return: Krotka zawierająca URL obrazu mapy i miejsca na trasie
    """
    loc_list = sorted(loc_list, key=lambda obj: obj.nazwa_atrakcji)
    sorted_loc_list, legs = get_sorted_list_and_legs(start_loc, loc_list, mode)

    IMAGE_URL = 'https://maps.googleapis.com/maps/api/staticmap?'
    COLORS = ['0x0C9DEFff', '0xEFA40Cff', '0x0BD55Aff']

    paths = []
    for leg in legs:
        path = []
        path.append(f"{leg['start_location']['lat']},{leg['start_location']['lng']}")

        for step in leg['steps']:
            path.append(f"{step['end_location']['lat']},{step['end_location']['lng']}")

        paths.append(path)

    IMAGE_PARAMS = {
        'key': API_KEY,
        'size': '640x640',
        'scale': '2',
        'markers': [f"color:0x9933FF|label:S|{paths[0][0]}"],
        'path': [],
    }

    for i, path in enumerate(paths):
        x = f"color:{COLORS[i % len(COLORS)]}|weight:3|"
        x += "|".join(path)
        IMAGE_PARAMS['path'].append(x)
        IMAGE_PARAMS['markers'].append(f"color:0x3333FF|label:{string.ascii_uppercase[i]}|{path[-1]}")

    URL = IMAGE_URL + urlencode(IMAGE_PARAMS, True)
    places = OrderedDict()

    for i in range(len(IMAGE_PARAMS['markers'])):
        if i == 0:
            places['S'] = start_loc
        else:
            places[f'{string.ascii_uppercase[i - 1]}'] = sorted_loc_list[i - 1].nazwa_atrakcji

    return URL, places


def generate_interactive_map(start_loc: str, loc_list: list, mode: str ='walking') -> str:
    """
    Generuje interaktywną mapę z zaznaczoną trasą zwiedzania.

    :param start_loc: Lokalizacja początkowa
    :param loc_list: Lista lokalizacji
    :param mode: Tryb podróży (domyślnie 'walking')
    :return: URL interaktywnej mapy
    """
    loc_list = sorted(loc_list, key=lambda obj: obj.nazwa_atrakcji)
    sorted_loc_list, _ = get_sorted_list_and_legs(start_loc, loc_list, mode)

    BASE_URL = 'https://www.google.com/maps/embed/v1/directions?'

    PARAMS = {
        'origin': "Warszawa " + start_loc,
        'destination': sorted_loc_list[-1].nazwa_atrakcji,
        'mode': mode,
        'waypoints': "|".join(["Warszawa " + loc.nazwa_atrakcji for loc in sorted_loc_list[:-1]]) if len(sorted_loc_list) > 1 else None,
        'key': API_KEY
    }

    if PARAMS['waypoints'] is None:
        del PARAMS['waypoints']

    URL = BASE_URL + urlencode(PARAMS)
    return URL
