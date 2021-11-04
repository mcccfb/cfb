##
# September 1, 2021
#
# Tools for "virtual conferences" of intramural results
#
import sys
import cfbd
import copy
from datetime import datetime
from datetime import timedelta
from datetime import timezone

MAX_TEAM_LENGTH = 24

# knocks out the non-FBS teams for the given year from
# the byref param teams
def remove_fcs_teams(configuration, teams, cur_year):
    api_instance = cfbd.TeamsApi(cfbd.ApiClient(configuration))
    year = cur_year
    fcs_teams = []

    fbs_teams = api_instance.get_fbs_teams(year=year)
    for team_id in teams:
        found = False
        for cur_team in fbs_teams:
            if (cur_team.id == team_id) :
                found = True
                break
        if (not found) :
            fcs_teams.append(team_id)
            #print(teams[team_id] + " is an FCS team")

    for fcs_team in fcs_teams :
        del teams[fcs_team]



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

# returns a dictionary of team name -> StandingsRecord
#
def build_standings(mcc_games) :
    standings = {}
    for cur_mcc_game in mcc_games :
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
            print("disqualifying insufficient wins (" + str(first_place.wins) +
                  ") from "  + first_place.team_name, file = sys.stderr)
            ordered_standings.pop(0)
        else:
            return True


        
# return -1 if team 1 is winner, 1 if team2, 0 if tie    
def head_to_head_winner(team1, team2, all_games):
    retval = 0
    for cur_mcc_game in all_games :
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
    for cur_mcc_game in all_games :
        if (cur_mcc_game.home_team == team1) :
            oppos[cur_mcc_game.away_id] = (cur_mcc_game.home_points - cur_mcc_game.away_points)
        elif (cur_mcc_game.away_team == team1) :
            oppos[cur_mcc_game.home_id] = (cur_mcc_game.away_points - cur_mcc_game.home_points)
        else:
            # team1 was not involved in this game
            pass
    # now we have all team1's margins organized by opponent
    print("oppo check for " + team1 + " and " + team2, file = sys.stderr)
    #print(oppos)
    for cur_mcc_game in all_games :
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

# return -1 if team 1 is winner, 1 if team2, 0 if tie
def total_margin(team1, team2, all_games):
    team1_margin = 0
    team2_margin = 0

    # first find all team1's margins
    for cur_mcc_game in all_games :
        if (cur_mcc_game.home_team == team1) :
            team1_margin += (cur_mcc_game.home_points - cur_mcc_game.away_points)
        elif (cur_mcc_game.away_team == team1) :
            team1_margin += (cur_mcc_game.away_points - cur_mcc_game.home_points)
        else:
            # team1 was not involved in this game
            pass

        if (cur_mcc_game.home_team == team2) :
            team2_margin += (cur_mcc_game.home_points - cur_mcc_game.away_points)
        elif (cur_mcc_game.away_team == team2) :
            team2_margin += (cur_mcc_game.away_points - cur_mcc_game.home_points)
        else:
            # team2 was not involved in this game
            pass

    if (team1_margin > team2_margin) :
        return -1
    elif (team2_margin > team1_margin) :
        return 1
    else:
        return 0


# return True if we could break the tie
#
def break_ties(ordered_standings, mcc_games):
    if (len(ordered_standings) > 2 and standings_sortfunc(ordered_standings[0]) == standings_sortfunc(ordered_standings[1])) :
        print("looks like a tie for the cup", file = sys.stderr)
        # find head to head
        h2h = head_to_head_winner(ordered_standings[0].team_name,
                                  ordered_standings[1].team_name, mcc_games)
        if (h2h < 0) :
            print("Tie broken by head-to-head", file = sys.stderr)
            # proper team is in first
            return True
        elif (h2h > 0) :
            print("Tie broken by head-to-head", file = sys.stderr)
            # promote second
            improper = ordered_standings.pop(0)
            ordered_standings.insert(1, improper)
            return True
        else:
            print("head to head didn't resolve anything", file = sys.stderr)
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
                print("common opponent margin didn't resolve anything", file = sys.stderr)

                total_check = total_margin(ordered_standings[0].team_name,
                                           ordered_standings[1].team_name,
                                           mcc_games)
                if (total_check < 0) :
                    return True
                elif (total_check > 0) :
                    improper = ordered_standings.pop(0)
                    ordered_standings.insert(1, improper)
                    return True
                else:
                    print("total margin didn't resolve anything", file = sys.stderr)
                    return False
    else:
        return True


class PossibilityScoreboard:
    def __init__(self, name):
        self.name = name
        self.teams = {}
        self.total_trials = 0

    def record_winner(self, winning_team):
        if (winning_team in self.teams):
            self.teams[winning_team] += 1
        else:
            self.teams[winning_team] = 1
        self.total_trials += 1

    def __str__(self):
        s = self.name + " Simulation:\n"
        for team in self.teams :
            pct_win = self.teams[team] * 100 // self.total_trials
            s += team + " " + str(self.teams[team]) + " [" + str(pct_win) + "%]\n"
        return s
    
def recursive_schedule_fill(time_sorted_games, cur_index, scoreboard):
    if (cur_index >= len(time_sorted_games)) :
        # every time we get to the end of the recursion calculate a winner and
        # add it to the scoreboard
        standings = build_standings(time_sorted_games)
        ordered_standings = sorted(standings.values(), reverse = True, key = standings_sortfunc)
        break_ties(ordered_standings, time_sorted_games)
        scoreboard.record_winner(ordered_standings[0].team_name)
    else :
        # jump to the node in question and first fill in a home team win
        cur_mcc_game = time_sorted_games[cur_index]
        cur_mcc_game.away_points = 4
        cur_mcc_game.home_points = 55
        recursive_schedule_fill(time_sorted_games, cur_index + 1, scoreboard)
        # then do a road team win
        cur_mcc_game.away_points = 55
        cur_mcc_game.home_points = 4
        recursive_schedule_fill(time_sorted_games, cur_index + 1, scoreboard)
            
def find_possibilities(time_sorted_games):
    cur_index = 0
    future_index_start = -1
    local_games_copy = []
    for cur_mcc_game in time_sorted_games:
        if (cur_mcc_game.away_points is None) :
            if (future_index_start == -1):
                future_index_start = cur_index
        local_games_copy.append(copy.copy(cur_mcc_game))
        cur_index += 1
        
    scoreboard = PossibilityScoreboard("Full Enumeration")
    recursive_schedule_fill(local_games_copy, future_index_start, scoreboard)
    print()
    print(str(scoreboard))

def find_vconf_games(configuration, teams, year, verbose):

    curyear_teams = teams.copy()
    remove_fcs_teams(configuration, curyear_teams, year)
    
    api_instance = cfbd.GamesApi(cfbd.ApiClient(configuration))
    
    today = datetime.utcnow()

    pac_timez = timezone(timedelta(hours = -8))
    utc_timez = timezone(timedelta(hours = 0))

    mcc_games = find_mcc_games(api_instance, curyear_teams, year)
    time_ordered_games = sorted(mcc_games.values(), reverse = False, key = timesortfunc)
    fmt = "%Y-%m-%dT%H:%M:%S.%fZ"
    any_games_in_future = False
    for cur_mcc_game in time_ordered_games:
        game_time = datetime.strptime(cur_mcc_game.start_date, fmt)
        # the printed stamp is in UTC but strptime reads it as local, so we need to
        # surgically replace it at first and then re-interpret as local.
        #
        pac_game_time = game_time.replace(tzinfo = utc_timez).astimezone(pac_timez)
        pretty_date = datetime.strftime(pac_game_time, "%b %d, %Y")
        if (game_time > today) :
            any_games_in_future = True
            if (verbose) :
                print (cur_mcc_game.away_team + " at " +
                       cur_mcc_game.home_team + " on " +
                       pretty_date)
        else :
            if (verbose) :
                print (cur_mcc_game.away_team + " " + str(cur_mcc_game.away_points) + " at " +
                       cur_mcc_game.home_team + " " + str(cur_mcc_game.home_points) + " on " +
                       pretty_date)
    if (verbose) :
        print()

    if (verbose and any_games_in_future):
        find_possibilities(time_ordered_games)
        
    standings = build_standings(mcc_games.values())
    if (len(standings) == 0):
        print("There are no standings, possibly because no games were completed.", file = sys.stderr)
        print(str(year) + ", " + str(len(mcc_games)) + ", ,")
        return False

    ordered_standings = sorted(standings.values(), reverse = True, key = standings_sortfunc)
    if (any_games_in_future) :
        if (verbose) :
            for line in ordered_standings:
                print(line)
        print(str(year) + ", " + str(len(mcc_games)) + ", ,")
        return False

    if not check_minimum_wins(ordered_standings):
        print("No team has enough wins", file = sys.stderr)
        print(str(year) + ", " + str(len(mcc_games)) + ", ,")
        return False

    if (break_ties(ordered_standings, mcc_games.values())) :
        if (verbose) :
            print(str(year) + " final standings")
            print()
            for line in ordered_standings:
                print(line)
            print()

        print(str(year) + ", " + str(len(mcc_games)) + ", " + ordered_standings[0].team_name + ", " +
              str(ordered_standings[0].wins) + "-" + str(ordered_standings[0].losses))
        return True
    else:
        print("could not resolve a winner for " + str(year), file = sys.stderr)
        print(str(year) + ", " + str(len(mcc_games)) + ", ,")
        return False
