# scoreboard.py

# this class keeps track of the current score
class Scoreboard:

    def __init__(self):
        # start both players at 0
        self.player_1_score = 0
        self.player_2_score = 0

        # this set stores hit packets we already counted
        # so we do not count the same hit twice
        self.processed_hits = set()

        # this tells us if the match already ended
        self.match_over = False

        # store winner once someone wins
        self.winner = None

        # first player to this score wins
        self.winning_score = 5

    # this function updates score based on a parsed packet
    def update_score(self, parsed_packet):

        # if the match is already over, do not change score
        if self.match_over:
            print("Match already ended, score not updated")
            return

        # if packet is invalid, do nothing
        if parsed_packet is None:
            print("Scoreboard not updated because packet was invalid")
            return

        # get values from parsed packet
        player_id = parsed_packet["player_id"]
        hit_type = parsed_packet["hit_type"]
        time = parsed_packet["time"]

        # only real hit events should change score
        if hit_type != "hit":
            print("No score change because event was not a hit")
            return

        # make a unique key for this hit packet
        packet_key = (player_id, hit_type, time)

        # if we already counted this exact hit, ignore it
        if packet_key in self.processed_hits:
            print("Duplicate hit packet detected, score not updated")
            return

        # mark this hit as already processed
        self.processed_hits.add(packet_key)

        # update correct player
        if player_id == "P1":
            self.player_1_score += 1
            print("Point awarded to Player 1")

        elif player_id == "P2":
            self.player_2_score += 1
            print("Point awarded to Player 2")

        else:
            print("Unknown player id, score not updated")
            return

        # check if someone won after updating score
        self.check_winner()

    # this function checks if someone reached the winning score
    def check_winner(self):

        if self.player_1_score >= self.winning_score:
            self.match_over = True
            self.winner = "Player 1"

        elif self.player_2_score >= self.winning_score:
            self.match_over = True
            self.winner = "Player 2"

    # this function prints scoreboard in a cleaner display style
    def print_scoreboard(self):
        print("======================")
        print("   FENCING SCOREBOARD")
        print(f"   Player 1: {self.player_1_score}")
        print(f"   Player 2: {self.player_2_score}")
        print("======================")

        # if match ended, show winner too
        if self.match_over:
            print("***** MATCH OVER *****")
            print("Winner:", self.winner)
            print("======================")