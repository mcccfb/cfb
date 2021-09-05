##
# September 1, 2021
#
# Tools for "virtual conferences" of intramural results
#
import cfbd
from datetime import datetime

MAX_TEAM_LENGTH = 24

# teams = a dictionary of id->team_name of the teams we want in our conference
#
def find_mcc_games(api_instance, teams, cur_year) :
    mcc_games = {}

    for team_id in teams :
        #print("looking for " + teams[team_id])
        all_teams_games = api_instance.get_games(year=cur_year, team = teams[team_id])
        for cur_game in all_teams_games :
            #print(cur_game)
            other_team_id = -1
            if (cur_game.away_id == team_id) :
                other_team_id = cur_game.home_id
            else :
                other_team_id = cur_game.away_id
                if other_team_id in teams :
                    other_team = teams[other_team_id]
                    #print("This was a MCC game " + teams[team_id] + " versus " + other_team)
                    mcc_games[cur_game.id] = cur_game
    return mcc_games


def timesortfunc(mcc_game) :
    fmt = "%Y-%m-%dT%H:%M:%S.%fZ"
    return datetime.strptime(mcc_game.start_date, fmt)

class StandingsRecord:
    def __init__(self, wins, losses, team_name):
        self.wins = wins
        self.losses = losses
        self.ties = 0
        self.team_name = team_name
        
    def __str__(self):
        if (self.ties == 0):
            return self.team_name.ljust(MAX_TEAM_LENGTH) + str(self.wins) + "-" + str(self.losses)
        else:
            return self.team_name.ljust(MAX_TEAM_LENGTH) + str(self.wins) + "-" + str(self.losses) + "-" + str(self.ties)

def build_standings(mcc_games) :
    standings = {}
    for mcc_game_id in mcc_games :
        cur_mcc_game = mcc_games[mcc_game_id]
        if (cur_mcc_game.away_points is None or cur_mcc_game.home_points is None) :
            pass
            # print("This game doesn't have a score")
        elif (cur_mcc_game.away_points == cur_mcc_game.home_points) :
            if (cur_mcc_game.away_id not in standings) :
                standings[cur_mcc_game.away_id] = StandingsRecord(0, 0, cur_mcc_game.away_team)
            if (cur_mcc_game.home_id not in standings) :
                standings[cur_mcc_game.home_id] = StandingsRecord(0, 0, cur_mcc_game.home_team)
            standings[cur_mcc_game.away_id].ties += 1
            standings[cur_mcc_game.home_id].ties += 1
        elif (cur_mcc_game.away_points > cur_mcc_game.home_points) :
            if (cur_mcc_game.away_id in standings) :
                standings[cur_mcc_game.away_id].wins += 1
            else :
                standings[cur_mcc_game.away_id] = StandingsRecord(1, 0, cur_mcc_game.away_team)
            if (cur_mcc_game.home_id in standings) :
                standings[cur_mcc_game.home_id].losses += 1
            else :
                standings[cur_mcc_game.home_id] = StandingsRecord(0, 1, cur_mcc_game.home_team)
        else :
            # home team won
            if (cur_mcc_game.home_id in standings) :
                standings[cur_mcc_game.home_id].wins += 1
            else :
                standings[cur_mcc_game.home_id] = StandingsRecord(1, 0, cur_mcc_game.home_team)
            if (cur_mcc_game.away_id in standings) :
                standings[cur_mcc_game.away_id].losses += 1
            else :
                standings[cur_mcc_game.away_id] = StandingsRecord(0, 1, cur_mcc_game.away_team)
    return standings

def standings_sortfunc(sr) :
    return (sr.wins * 1000 / (sr.losses + sr.wins + sr.ties)) - sr.losses + sr.wins


# enforce win minimum
def check_minimum_wins(ordered_standings) :
    while(True) :
        if (len(ordered_standings) < 1) :
            return False
        first_place = ordered_standings[0];
        if (first_place.wins <= 1) :
            print("disqualifying one win " + first_place.team_name)
            ordered_standings.pop(0)
        else:
            return True


        
# return -1 if team 1 is winner, 1 if team2, 0 if tie    
def head_to_head_winner(team1, team2, all_games):
    retval = 0
    for mcc_game_id in all_games :
        cur_mcc_game = all_games[mcc_game_id]
        if (cur_mcc_game.home_team == team1 and cur_mcc_game.away_team == team2) :
            if (cur_mcc_game.home_points > cur_mcc_game.away_points) :
                # team1 was the home team and home team won
                retval -= 1
            else:
                # team1 was the home team and the home team lost
                retval += 1
        elif (cur_mcc_game.away_team == team1 and cur_mcc_game.home_team == team2) :
            if (cur_mcc_game.away_points > cur_mcc_game.home_points) :
                # team1 was the away team and the away team won
                retval -= 1
            else:
                retval += 1
        else:
            # this game was not head to head
            pass
    return retval

# return -1 if team 1 is winner, 1 if team2, 0 if tie    
def common_opp_margin(team1, team2, all_games):
    oppos = {}
    gross_margin_team1 = 0
    
    # first find all team1's margins
    for mcc_game_id in all_games :
        cur_mcc_game = all_games[mcc_game_id]
        if (cur_mcc_game.home_team == team1) :
            oppos[cur_mcc_game.away_id] = (cur_mcc_game.home_points - cur_mcc_game.away_points)
        elif (cur_mcc_game.away_team == team1) :
            oppos[cur_mcc_game.home_id] = (cur_mcc_game.away_points - cur_mcc_game.home_points)
        else:
            # team1 was not involved in this game
            pass
    # now we have all team1's margins organized by opponent
    print("oppo check for " + team1 + " and " + team2)
    #print(oppos)
    for mcc_game_id in all_games :
        cur_mcc_game = all_games[mcc_game_id]
        if (cur_mcc_game.home_team == team2) :
            if (cur_mcc_game.away_id in oppos):
                # this is a common opponent with team2 as home team
                this_team2_margin = (cur_mcc_game.home_points - cur_mcc_game.away_points)
                gross_margin_team1 += (oppos[cur_mcc_game.away_id] - this_team2_margin)
                #print("common oppo detected with " + cur_mcc_game.away_team + " gross team1 margin " + str(gross_margin_team1))
            else:
                # team1 didn't play them
                # print(team1 + " didn't play " + cur_mcc_game.away_id);
                pass
        elif (cur_mcc_game.away_team == team2) :
            if (cur_mcc_game.home_id in oppos):
                # this is a common opponent with team2 as away team
                this_team2_margin = (cur_mcc_game.away_points - cur_mcc_game.home_points)
                gross_margin_team1 += (oppos[cur_mcc_game.home_id] - this_team2_margin)
                #print("common oppo detected with " + cur_mcc_game.home_team + " gross team1 margin " + str(gross_margin_team1))
            else:
                # team1 didn't play them
                # print(team1 + " didn't play " + cur_mcc_game.home_id);
                pass
        else:
            # print(cur_mcc_game.home_team + " vs " + cur_mcc_game.away_team + " is not relevant")
            # this is not a team2 game
            pass

    if (gross_margin_team1 < 0):
        return 1
    elif (gross_margin_team1 > 0):
        return -1
    else:
        return 0

# return True if we could break the tie
#
def break_ties(ordered_standings, mcc_games):
    if (len(ordered_standings) > 2 and standings_sortfunc(ordered_standings[0]) == standings_sortfunc(ordered_standings[1])) :
        print("looks like a tie for the cup")
        # find head to head
        h2h = head_to_head_winner(ordered_standings[0].team_name,
                                  ordered_standings[1].team_name, mcc_games)
        if (h2h < 0) :
            print("Tie broken by head-to-head")
            # proper team is in first
            return True
        elif (h2h > 0) :
            print("Tie broken by head-to-head")
            # promote second
            improper = ordered_standings.pop(0)
            ordered_standings.insert(1, improper)
            return True
        else:
            print("head to head didn't resolve anything")
            oppo_check = common_opp_margin(ordered_standings[0].team_name,
                                           ordered_standings[1].team_name,
                                           mcc_games)
            if (oppo_check < 0) :
                # proper team is in first
                return True
            elif (oppo_check > 0) :
                # promote second
                improper = ordered_standings.pop(0)
                ordered_standings.insert(1, improper)
                return True
            else:
                print("common opponent margin didn't resolve anything")
                return False
    else:
        return True

def find_vconf_games(configuration, teams, year, verbose):
    
    api_instance = cfbd.GamesApi(cfbd.ApiClient(configuration))
    
    today = datetime.utcnow()

    mcc_games = find_mcc_games(api_instance, teams, year)
    time_ordered_games = sorted(mcc_games.values(), reverse = False, key = timesortfunc)
    if (verbose):
        fmt = "%Y-%m-%dT%H:%M:%S.%fZ"
        for cur_mcc_game in time_ordered_games:
            game_time = datetime.strptime(cur_mcc_game.start_date, fmt)
            pretty_date = datetime.strftime(game_time, "%b %d, %Y")
            if (game_time > today) :
                print (cur_mcc_game.away_team + " at " +
                       cur_mcc_game.home_team + " on " +
                       pretty_date)
            else :
                print (cur_mcc_game.away_team + " " + str(cur_mcc_game.away_points) + " at " +
                       cur_mcc_game.home_team + " " + str(cur_mcc_game.home_points) + " on " +
                       pretty_date)

    standings = build_standings(mcc_games)
    if (len(standings) == 0):
        if (verbose):
            print("There are no standings, possibly because no games were completed.")
        return False
        
    ordered_standings = sorted(standings.values(), reverse = True, key = standings_sortfunc)
    if not check_minimum_wins(ordered_standings):
        print("No team has enough wins")
        return False
    if (verbose) :
        for line in ordered_standings:
            print(line)

    if (break_ties(ordered_standings, mcc_games)) :
        if (verbose) :
            print()
            print(str(year) + " ordered standings")
            print()
            for line in ordered_standings:
                print(line)
            print()

        print(str(year) + " MCC winner is " + ordered_standings[0].team_name + " (" +
              str(ordered_standings[0].wins) + "-" + str(ordered_standings[0].losses) + ")")
        return True
    else:
        print("could not resolve a winner for " + str(year))
        return False
