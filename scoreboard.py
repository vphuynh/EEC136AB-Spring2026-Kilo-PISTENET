from colorama import Fore, init
import time
import threading

init(autoreset=True)


class Scoreboard:

    def __init__(self, bout_type="pool"):
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
        self.match_start_time = time.time()

        self.counted_hits = set()
        self.event_history = []
        self.last_hit_display = "None"

        self.valid_packets = 0
        self.invalid_packets = 0
        self.duplicate_hits = 0
        self.simultaneous_hits = 0

        self.device_status = {
            "Fencing_P1": "not connected",
            "Fencing_P2": "not connected"
        }

        self.last_hit_time = None
        self.last_hit_player = None
        self.weapon_mode = "epee"
        self.lockout_window = 0.045

        self.timer_seconds = 180
        self.timer_running = False
        self.timer_thread_started = False

    def update_score(self, parsed_packet):

        if parsed_packet is None:
            self.invalid_packets += 1
            print(Fore.RED + "Invalid packet - score not updated")
            return

        self.valid_packets += 1

        player_id = parsed_packet["player_id"]
        hit_type = parsed_packet["hit_type"]
        time_stamp = parsed_packet["time"]

        self.last_hit_display = f"{player_id} {hit_type} ({time_stamp})"

        if self.match_over:
            event_text = f"[{time_stamp}] {player_id} {hit_type} ignored because match already ended"
            self.event_history.append(event_text)
            print(Fore.MAGENTA + "Match already ended, score not updated")
            return

        event_text = f"[{time_stamp}] {player_id} {hit_type}"
        self.event_history.append(event_text)

        if hit_type != "hit":
            print(Fore.YELLOW + "No score change because event was not a hit")
            return

        hit_key = (player_id, hit_type, time_stamp)

        if hit_key in self.counted_hits:
            self.duplicate_hits += 1
            print(Fore.YELLOW + "Duplicate hit packet detected, score not updated")
            return

        self.counted_hits.add(hit_key)

        current_time = time.time()

        if self.last_hit_time is not None:
            time_difference = current_time - self.last_hit_time

            if time_difference < self.lockout_window:

                if player_id != self.last_hit_player:
                    self.simultaneous_hits += 1
                    print(Fore.YELLOW + "Simultaneous hit detected")

                    if player_id == "P1":
                        self.player_1_score += 1
                        print(Fore.GREEN + "Point awarded to Player 1")

                    elif player_id == "P2":
                        self.player_2_score += 1
                        print(Fore.RED + "Point awarded to Player 2")

                    self.check_winner()
                    return

                else:
                    print(Fore.YELLOW + "Hit ignored, same player inside lockout window")
                    return

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

        if self.match_over:
            self.save_match_history()

    def print_scoreboard(self):

        elapsed_time = round(time.time() - self.match_start_time, 1)

        print(Fore.CYAN + "\n======================")
        print(Fore.CYAN + "   FENCING SCOREBOARD")
        print(Fore.CYAN + f"   Mode: {self.bout_type.upper()} | First to {self.winning_score}")
        print(Fore.CYAN + f"   Match Time: {elapsed_time}s")
        print(Fore.CYAN + "----------------------")
        print(Fore.GREEN + f"   Player 1: {self.player_1_score}")
        print(Fore.RED + f"   Player 2: {self.player_2_score}")
        print(Fore.CYAN + "----------------------")
        print(Fore.CYAN + f"   Valid Packets: {self.valid_packets}")
        print(Fore.CYAN + f"   Invalid Packets: {self.invalid_packets}")
        print(Fore.CYAN + f"   Duplicate Hits Ignored: {self.duplicate_hits}")
        print(Fore.CYAN + f"   Simultaneous Hits: {self.simultaneous_hits}")
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

    def start_timer(self):

        self.timer_running = True

        if not self.timer_thread_started:
            self.timer_thread_started = True
            threading.Thread(target=self.run_timer, daemon=True).start()

    def pause_timer(self):

        self.timer_running = False

    def reset_timer(self):

        self.timer_seconds = 180
        self.timer_running = False

    def run_timer(self):

        while True:
            if self.timer_running and self.timer_seconds > 0 and not self.match_over:
                time.sleep(1)
                self.timer_seconds -= 1

                if self.timer_seconds <= 0:
                    self.timer_seconds = 0
                    self.timer_running = False
                    self.event_history.append("Timer expired")
                    self.last_hit_display = "Timer expired"
            else:
                time.sleep(0.2)

    def get_timer_display(self):

        minutes = self.timer_seconds // 60
        seconds = self.timer_seconds % 60

        return f"{minutes}:{seconds:02d}"

    def get_state(self):

        elapsed_time = round(time.time() - self.match_start_time, 1)

        return {
            "bout_type": self.bout_type,
            "winning_score": self.winning_score,
            "weapon_mode": self.weapon_mode,
            "lockout_window": self.lockout_window,
            "player_1_score": self.player_1_score,
            "player_2_score": self.player_2_score,
            "last_hit": self.last_hit_display,
            "match_time": elapsed_time,
            "timer_display": self.get_timer_display(),
            "timer_running": self.timer_running,
            "match_over": self.match_over,
            "winner": self.winner,
            "valid_packets": self.valid_packets,
            "invalid_packets": self.invalid_packets,
            "duplicate_hits": self.duplicate_hits,
            "simultaneous_hits": self.simultaneous_hits,
            "event_history": self.event_history[-8:],
            "device_status": self.device_status
        }

    def manual_score(self, player_id, amount):

        if player_id == "P1":
            self.player_1_score += amount

            if self.player_1_score < 0:
                self.player_1_score = 0

        elif player_id == "P2":
            self.player_2_score += amount

            if self.player_2_score < 0:
                self.player_2_score = 0

        else:
            return

        event_text = f"Manual score change: {player_id} {amount:+d}"
        self.event_history.append(event_text)
        self.last_hit_display = event_text

        self.check_winner()

    def set_weapon(self, weapon_mode):

        self.weapon_mode = weapon_mode.lower()

        if self.weapon_mode == "epee":
            self.lockout_window = 0.045

        elif self.weapon_mode == "foil":
            self.lockout_window = 0.300

        elif self.weapon_mode == "saber":
            self.lockout_window = 0.120

        else:
            self.weapon_mode = "epee"
            self.lockout_window = 0.045

        event_text = f"Weapon mode changed to {self.weapon_mode.upper()}"
        self.event_history.append(event_text)
        self.last_hit_display = event_text

    def set_mode(self, bout_type):

        self.bout_type = bout_type.lower()

        if self.bout_type == "de":
            self.winning_score = 15
        else:
            self.bout_type = "pool"
            self.winning_score = 5

        self.reset_match()

    def reset_match(self):

        self.player_1_score = 0
        self.player_2_score = 0

        self.match_over = False
        self.winner = None

        self.counted_hits.clear()
        self.event_history = []
        self.last_hit_display = "None"

        self.valid_packets = 0
        self.invalid_packets = 0
        self.duplicate_hits = 0
        self.simultaneous_hits = 0

        self.last_hit_time = None
        self.last_hit_player = None
        self.match_start_time = time.time()

        self.reset_timer()

        print(Fore.CYAN + "Match reset complete")