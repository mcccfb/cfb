import os
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

year = 2022
week = 2
top_n = 20

# note that week and year are required for the API
api_instance = cfbd.PlaysApi(cfbd.ApiClient(configuration))
#all_punts = api_instance.get_plays(year = year, week = week, team = 'Stanford', play_type = 52)
all_punts = api_instance.get_plays(year=year, week=week, play_type=52, season_type='regular')
#year_punts = api_instance.get_plays(year = year, week = week, play_type = 52)

#all_punts = []
#for cur_week in range(1, 16):
#    week_punts = api_instance.get_plays(year = year, week = cur_week, team = 'UCLA', play_type = 52)
#    all_punts += week_punts


#for cur_punt in all_punts:
#    print(print_punt(cur_punt))
#    print("sadness score " + "{:.3f}".format(sadness_score(cur_punt)))

sad_rank = sorted(all_punts, reverse = True, key = sadness_score)

print("the " + str(top_n) + " worst punts out of " + str(len(sad_rank)))

i = 0
for cur_punt in sad_rank:
    if (i >= top_n) :
        break
    i += 1
    print("{:.3f}".format(sadness_score(cur_punt)) + " " + print_punt(cur_punt))
