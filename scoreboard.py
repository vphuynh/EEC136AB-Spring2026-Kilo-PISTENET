from colorama import Fore, init
import time

# initialize colorama
init(autoreset=True)


class Scoreboard:

    def __init__(self, bout_type="pool"):
        # pool = first to 5, de = first to 15
        self.bout_type = bout_type.lower()

        if self.bout_type == "de":
            self.winning_score = 15
        else:
            self.bout_type = "pool"
            self.winning_score = 5

        self.player_1_score = 0
        self.player_2_score = 0

        self.match_over = False
        self.winner = None

        self.counted_hits = set()
        self.event_history = []

        # timing / lockout system
        self.last_hit_time = None
        self.last_hit_player = None
        self.lockout_window = 0.3  # 300 ms

    def update_score(self, parsed_packet):

        if parsed_packet is None:
            print(Fore.RED + "Invalid packet - score not updated")
            return

        player_id = parsed_packet["player_id"]
        hit_type = parsed_packet["hit_type"]
        time_stamp = parsed_packet["time"]

        # if match already ended
        if self.match_over:
            event_text = f"{player_id} {hit_type} at {time_stamp} (ignored: match already ended)"
            self.event_history.append(event_text)
            print(Fore.MAGENTA + "Match already ended, score not updated")
            return

        # log event
        event_text = f"{player_id} {hit_type} at {time_stamp}"
        self.event_history.append(event_text)

        if hit_type != "hit":
            print(Fore.YELLOW + "No score change because event was not a hit")
            return

        hit_key = (player_id, hit_type, time_stamp)

        if hit_key in self.counted_hits:
            print(Fore.YELLOW + "Duplicate hit packet detected, score not updated")
            return

        self.counted_hits.add(hit_key)

        current_time = time.time()

        # check timing window
        if self.last_hit_time is not None:
            time_difference = current_time - self.last_hit_time

            if time_difference < self.lockout_window:

                # different players → simultaneous hit
                if player_id != self.last_hit_player:
                    print(Fore.YELLOW + "Simultaneous hit detected")

                    if player_id == "P1":
                        self.player_1_score += 1
                        print(Fore.GREEN + "Point awarded to Player 1")

                    elif player_id == "P2":
                        self.player_2_score += 1
                        print(Fore.RED + "Point awarded to Player 2")

                    self.check_winner()
                    return

                # same player spam → ignore
                else:
                    print(Fore.YELLOW + "Hit ignored (same player inside lockout window)")
                    return

        # normal hit (outside lockout)
        self.last_hit_time = current_time
        self.last_hit_player = player_id

        if player_id == "P1":
            self.player_1_score += 1
            print(Fore.GREEN + "Point awarded to Player 1")

        elif player_id == "P2":
            self.player_2_score += 1
            print(Fore.RED + "Point awarded to Player 2")

        else:
            print("Unknown player id, score not updated")
            return

        self.check_winner()

    def check_winner(self):
        if self.player_1_score >= self.winning_score:
            self.match_over = True
            self.winner = "Player 1"

        elif self.player_2_score >= self.winning_score:
            self.match_over = True
            self.winner = "Player 2"

    def print_scoreboard(self):
        print(Fore.CYAN + "======================")
        print(Fore.CYAN + "   FENCING SCOREBOARD")
        print(Fore.GREEN + f"   Player 1: {self.player_1_score}")
        print(Fore.RED + f"   Player 2: {self.player_2_score}")
        print(Fore.CYAN + "======================")

        if self.match_over:
            print(Fore.YELLOW + "***** MATCH OVER *****")
            print(Fore.YELLOW + f"Winner: {self.winner}")
            print(Fore.CYAN + "======================")

    def print_match_history(self):
        print("\n===== MATCH HISTORY =====")

        for i, event in enumerate(self.event_history, start=1):
            print(f"{i}. {event}")

        print("========================")
        print(f"Final Score: {self.player_1_score} - {self.player_2_score}")

        if self.winner:
            print("Winner:", self.winner)

        print("========================")

    def save_match_history(self, filename="match_result.txt"):
        with open(filename, "w") as file:
            file.write("===== MATCH HISTORY =====\n")

            for i, event in enumerate(self.event_history, start=1):
                file.write(f"{i}. {event}\n")

            file.write("========================\n")
            file.write(f"Final Score: {self.player_1_score} - {self.player_2_score}\n")

            if self.winner:
                file.write(f"Winner: {self.winner}\n")

            file.write("========================\n")

        print(Fore.CYAN + f"Match history saved to {filename}")

    def reset_match(self):
        self.player_1_score = 0
        self.player_2_score = 0
        self.match_over = False
        self.winner = None
        self.counted_hits.clear()
        self.event_history = []
        self.last_hit_time = None
        self.last_hit_player = None

