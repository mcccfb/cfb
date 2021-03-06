##
# September 1, 2021
#
# Find MCC games
#
import os
import cfbd
from datetime import date
from virtualconf import find_vconf_games
import argparse

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

all_tx_teams = {249: 'North Texas', 2628: 'TCU', 251: 'Texas', 245: 'Texas A&M',
                2641: 'Texas Tech', 2638: 'UTEP', 2636: 'UT San Antonio',
                239: 'Baylor', 248: 'Houston', 2567: 'SMU', 2534: 'Sam Houston State',
                326: 'Texas State', 242: 'Rice'
                }

this_year = date.today().year

parser = argparse.ArgumentParser()
parser.add_argument('--verbose', '-v', action = 'store_true')
parser.add_argument('--start', '-s', type = int, default = this_year, help = "First year of range")
parser.add_argument('--end', '-e', type = int, default = this_year, help = "Last year of range")
args = parser.parse_args()

for cur_year in range(args.start, args.end + 1) :
    find_vconf_games(configuration, teams = all_ca_teams, year = cur_year, verbose = args.verbose)
