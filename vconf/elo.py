#
# November 11, 2021
#
from datetime import date
import cfbd

def get_cfbd_elo_dict(configuration):
    api_instance = cfbd.RatingsApi(cfbd.ApiClient(configuration))
    this_year = date.today().year
    api_response = api_instance.get_elo(year=this_year, season_type='regular')
    retval = { }
    for entry in api_response:
        retval[entry.team] = entry
    return retval

# p that elo1 wins
def p_win_elo(elo1, elo2):
    interior = ((elo2 - elo1) / 400)
    denom = 1 + (10 ** interior)
    prob = 1 / denom
    return prob
