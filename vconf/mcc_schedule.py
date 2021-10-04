##
# September 1, 2021
#
# Find MCC games
#
import os
import cfbd
from virtualconf import find_vconf_games

configuration = cfbd.Configuration()
configuration.api_key['Authorization'] = os.environ.get('CFBD_API_KEY')
configuration.api_key_prefix['Authorization'] = 'Bearer'

all_ca_teams = {25: 'California', 278: 'Fresno State', 16: 'Sacramento State',
                21: 'San Diego State', 23: 'San José State', 24: 'Stanford',
                302: 'UC Davis', 26: 'UCLA', 30: 'USC',
                1000003: 'Santa Clara', 1000004: 'San Francisco', 1000920: 'Saint Mary\'s',
                1000034: 'Loyola Marymount', 1000044: 'Pacific', 1000867: 'Pepperdine',
                1000007: 'California-Santa Barbara', 1000888: 'San Francisco State',
                1000006: 'Long Beach State', 1000012: 'Cal State Fullerton',
                13: 'Cal Poly',
                1000013: 'Cal State Los Angeles', 1000513: 'Cal Poly-Pomona'
}

for cur_year in range(2021, 2022) :
    find_vconf_games(configuration, teams = all_ca_teams, year = cur_year, verbose = True)
