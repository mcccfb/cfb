#
# November 16, 2021
#
# Use our pool of games to calculate home field advantage stats
#
import os
import cfbd
from datetime import date
from virtualconf import remove_fcs_teams
from virtualconf import find_mcc_games
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

this_year = date.today().year

parser = argparse.ArgumentParser()
parser.add_argument('--verbose', '-v', action = 'store_true')
parser.add_argument('--start', '-s', type = int, default = this_year, help = "First year of range")
parser.add_argument('--end', '-e', type = int, default = this_year, help = "Last year of range")
args = parser.parse_args()

#api_instance = cfbd.GamesApi(cfbd.ApiClient(configuration))

wins = 0
losses = 0
ties = 0

master_margins = []

def get_vconf_games(year, configuration):
    curyear_teams = all_ca_teams.copy()
    remove_fcs_teams(configuration, curyear_teams, cur_year)
    api_instance = cfbd.GamesApi(cfbd.ApiClient(configuration))
    return find_mcc_games(api_instance, curyear_teams, cur_year)

def get_conf_games(year, configuration):
    api_instance = cfbd.GamesApi(cfbd.ApiClient(configuration))
    all_conf_games = api_instance.get_games(year=cur_year, conference = 'SEC')
    conf_only = { }
    for cur_game in all_conf_games:
        if (not cur_game.conference_game):
            conf_only[cur_game.id] = cur_game
    return conf_only

for cur_year in range(args.start, args.end + 1) :
    #vconf_games = get_vconf_games(cur_year, configuration)
    vconf_games = get_conf_games(cur_year, configuration)
    year_wins = 0
    year_losses = 0
    year_ties = 0
    for cur_mcc_game in vconf_games.values():
        if (cur_mcc_game.neutral_site):
            continue
        #print("sanity check " + cur_mcc_game.away_team + " at " + cur_mcc_game.home_team)
        if (cur_mcc_game.away_points is None or cur_mcc_game.home_points is None) :
            pass
        else :
            master_margins.append([cur_mcc_game.away_points, cur_mcc_game.home_points])
            if (cur_mcc_game.home_points > cur_mcc_game.away_points) :
                year_wins += 1
            elif (cur_mcc_game.away_points > cur_mcc_game.home_points) :
                year_losses += 1
            else:
                year_ties += 1
    print("totals for year " + str(cur_year) + " home team is " + str(year_wins) + "-" + str(year_losses) + "-" + str(year_ties))
    wins += year_wins
    losses += year_losses
    ties += year_ties

pct = (wins + (ties / 2)) / (wins + losses + ties)

if (args.verbose):
    print(master_margins)
print("overall: " + str(wins) + "-" + str(losses) + "-" + str(ties))
print("{:.3f}".format(pct))
