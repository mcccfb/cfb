#
# November 16, 2021
#
import secrets
from elo import p_win_elo
from elo import get_cfbd_elo_dict


class MC_Predictor:

    def predict_game(self, game):
        pass

    def __str__(self):
        return "abstract predictor"
    
    def random_decimal(self):
        three_digit = secrets.randbelow(1000)
        return (three_digit / 1000)


class Home_Team_Predictor(MC_Predictor):

    def predict_game(self, game):
        raw_p = self.random_decimal()
        if (raw_p > .550):
            game.home_points = 21
            game.away_points = 24
        else:
            game.home_points = 24
            game.away_points = 21

    def __str__(self):
        return "Home Team Predictor"

# based on 10 years of MCC game data
#
class Sampled_Margin_Predictor(MC_Predictor):

    @staticmethod
    def random_score():
        real_life_data = [[7, 35], [48, 14], [33, 18], [35, 37], [35, 0], [28, 14], \
                          [14, 48], [21, 36], [30, 9], [27, 24], [28, 35], [3, 57], \
                          [19, 45], [28, 31], [17, 27], [14, 31], [56, 48], [0, 50], \
                          [17, 43], [21, 3], [40, 52], [38, 34], [17, 20], [14, 21], \
                          [24, 27], [28, 38], [35, 17], [9, 27], [62, 28], [35, 28], \
                          [34, 30], [52, 62], [13, 34], [10, 24], [13, 63], [10, 37], \
                          [17, 20], [35, 14], [36, 34], [38, 17], [13, 24], [24, 38], \
                          [7, 38], [13, 10], [20, 38], [31, 10], [13, 52], [30, 38], \
                          [7, 35], [27, 21], [7, 21], [23, 49], [30, 7], [35, 56], \
                          [22, 35], [22, 41], [24, 40], [41, 31], [21, 40], [45, 31], \
                          [10, 36], [17, 3], [16, 14], [40, 45], [3, 42], [10, 27], \
                          [22, 13], [36, 14], [24, 45], [30, 20], [17, 20], [27, 3], \
                          [27, 10], [52, 7], [34, 58], [14, 17], [27, 30], [24, 42], \
                          [23, 28], [28, 31], [30, 7], [23, 13], [14, 23], [13, 31], \
                          [13, 16], [10, 31], [3, 17], [38, 14], [27, 34], [49, 42], \
                          [15, 14], [41, 17], [7, 17], [27, 17], [16, 17], [34, 16], \
                          [24, 20], [23, 14], [28, 18], [23, 31], [20, 45], [35, 52], \
                          [24, 23], [28, 17], [10, 34], [43, 38], [48, 47], [30, 20], \
                          [19, 13], [35, 24], [40, 37], [7, 30], [42, 28], [62, 33], \
                          [41, 11], [40, 9]]
        return secrets.choice(real_life_data)
        
    def predict_game(self, game):
        sample_margin = self.random_score();
        game.away_points = sample_margin[0]
        game.home_points = sample_margin[1]

    def __str__(self):
        return "Sampled Home Margin Predictor"


class Elo_Predictor(MC_Predictor):

    def __init__(self, configuration):
        self.elo_dict = get_cfbd_elo_dict(configuration)

    def predict_game(self, game):
        if game.home_team not in self.elo_dict:
            home_elo = 1400
        else:
            home_elo_entry = self.elo_dict[game.home_team]
            home_elo = home_elo_entry.elo
        if game.away_team not in self.elo_dict:
            away_elo = 1400
        else:
            away_elo_entry = self.elo_dict[game.away_team]
            away_elo = away_elo_entry.elo
        p_home_win = p_win_elo(home_elo, away_elo)
        raw_p = self.random_decimal()
        sample_margin = Sampled_Margin_Predictor.random_score();
        if (sample_margin[0] > sample_margin[1]):
            winning_score = sample_margin[0]
            losing_score = sample_margin[1]
        else:
            losing_score = sample_margin[0]
            winning_score = sample_margin[1]
        if (raw_p < p_home_win):
            game.home_points = winning_score
            game.away_points = losing_score
        else:
            game.home_points = losing_score
            game.away_points = winning_score

    def __str__(self):
        return "Elo Predictor"
