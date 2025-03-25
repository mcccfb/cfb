import os
import sys
import cfbd
from punts import sadness_score
from punts import print_punt

# This code assumes you set your secrey key in the env variable CFBD_API_KEY
# example for bash shells
# export CFBD_API_KEY='my_long_secret_here'
#

configuration = cfbd.Configuration(
    access_token = os.environ.get('CFBD_API_KEY')
)

year = 2024
top_n = 20

# Initialize API instances
api_instance = cfbd.PlaysApi(cfbd.ApiClient(configuration))
games_api = cfbd.GamesApi(cfbd.ApiClient(configuration))

# Lists to store all punts and game dates
all_punts = []
game_dates = {}

# Collect punts and games from all weeks
for week in range(1, 16):
    print(f"Fetching week {week}...", file=sys.stderr)
    
    # Get games for this week
    games = games_api.get_games(
        year=year,
        week=week,
        season_type='regular',
        classification='fbs'
    )
    
    # Add game dates to our lookup
    for game in games:
        game_dates[game.id] = game.start_date
    
    # Get punts for this week
    week_punts = api_instance.get_plays(
        year=year,
        week=week,
        play_type='PUNT',
        season_type='regular',
        classification='fbs'
    )
    
    all_punts.extend(week_punts)



# Sort all punts by sadness score
sad_rank = sorted(all_punts, reverse=True, key=sadness_score)

print(f"The {top_n} worst punts of {year} out of {len(sad_rank)} total punts:")
print()

# Print the top N worst punts
for i, cur_punt in enumerate(sad_rank[:top_n], 1):
    print(f"{i}. {sadness_score(cur_punt):.3f} " + print_punt(cur_punt, game_dates))
