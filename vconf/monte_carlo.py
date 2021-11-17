#
# November 16, 2021
#
import secrets

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

    def predict_game(self, game):
        real_life_data = [-45, -35, -34, -34, -24, -24, -24, -23, -23, -22, -21, \
                          -21, -21, -21, -18, -18, -18, -17, -15, -14, -14, -14, \
                          -14, -11, -11, -10, -10, -10, -10, -10, -10, -9, -9, -8, \
                          -7, -7, -6, -6, -5, -4, -4, -4, -3, -3, -3, -2, -2, -1, \
                          -1, -1, 1, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 5, 5, 7, 7, 7, \
                          8, 8, 9, 10, 10, 10, 10, 11, 12, 13, 14, 14, 14, 14, 15, \
                          16, 17, 17, 17, 18, 18, 18, 18, 19, 19, 21, 21, 21, 21, \
                          23, 24, 24, 25, 26, 26, 26, 26, 27, 28, 28, 31, 34, 39, \
                          39, 50, 50, 54]
        sample_margin = secrets.choice(real_life_data)
        if (sample_margin > 0) :
            # home team won.
            game.away_points = 10
            game.home_points = 10 + sample_margin
        else:
            game.home_points = 10
            game.away_points = 10 + (-sample_margin)

    def __str__(self):
        return "Sampled Home Margin Predictor"
