from . import states_and_cities
from django.http import JsonResponse

def get_cities(request, state):
    # You can replace this with your logic to fetch cities based on the state
    city_data = states_and_cities.states_and_cities

    # Getting the list of cities for the given state
    cities = city_data.get(state, [])

    # I am returning the cities in JSON format
    return JsonResponse({'cities': cities})