from colorama import Fore, init
import time
import threading

init(autoreset=True)


class Scoreboard:

    def __init__(self, bout_type="pool"):
        self.lock = threading.Lock()

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
        self.match_number = 1

        self.counted_hits = set()
        self.event_history = []
        self.last_hit_display = "None"
        self.last_packet_received_time = None

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
        self.timer_start_seconds = 180
        self.timer_running = False
        self.timer_thread_started = False

        self.player_1_cards = []
        self.player_2_cards = []

    def add_event(self, event_text):
        self.event_history.append(event_text)

        if len(self.event_history) > 200:
            self.event_history.pop(0)

    def add_system_event(self, event_text):

        with self.lock:

            self.add_event("[SYSTEM] " + event_text)
            self.last_hit_display = event_text

    def update_score(self, parsed_packet):

        with self.lock:

            if parsed_packet is None:
                self.invalid_packets += 1
                print(Fore.RED + "Invalid packet - score not updated")
                return

            self.valid_packets += 1
            self.last_packet_received_time = time.time()

            player_id = parsed_packet["player_id"]
            hit_type = parsed_packet["hit_type"]
            time_stamp = parsed_packet["time"]

            self.last_hit_display = f"{player_id} {hit_type} ({time_stamp})"

            if self.timer_seconds <= 0:
                event_text = f"[{time_stamp}] {player_id} {hit_type} ignored because timer expired"
                self.add_event(event_text)
                print(Fore.MAGENTA + "Timer expired, score not updated")
                return

            if self.match_over:
                event_text = f"[{time_stamp}] {player_id} {hit_type} ignored because match already ended"
                self.add_event(event_text)
                print(Fore.MAGENTA + "Match already ended, score not updated")
                return

            event_text = f"[{time_stamp}] {player_id} {hit_type}"
            self.add_event(event_text)

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

        if self.match_over:
            return

        if self.player_1_score >= self.winning_score:
            self.match_over = True
            self.winner = "Player 1"
            self.timer_running = False

        elif self.player_2_score >= self.winning_score:
            self.match_over = True
            self.winner = "Player 2"
            self.timer_running = False

    def print_scoreboard(self):

        with self.lock:
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

        with self.lock:
            print("\n===== MATCH HISTORY =====")

            for i, event in enumerate(self.event_history, start=1):
                print(f"{i}. {event}")

            print("========================")
            print(f"Final Score: {self.player_1_score} - {self.player_2_score}")

            if self.winner:
                print("Winner:", self.winner)

            print("========================")

    def start_timer(self):

        with self.lock:
            if self.match_over:
                return

            self.timer_running = True

            if not self.timer_thread_started:
                self.timer_thread_started = True
                threading.Thread(target=self.run_timer, daemon=True).start()

    def pause_timer(self):

        with self.lock:
            self.timer_running = False

    def reset_timer(self):

        with self.lock:
            self.timer_seconds = self.timer_start_seconds
            self.timer_running = False

    def run_timer(self):

        while True:
            time.sleep(1)

            with self.lock:

                if self.timer_running and self.timer_seconds > 0 and not self.match_over:
                    self.timer_seconds -= 1

                    if self.timer_seconds <= 0:
                        self.timer_seconds = 0
                        self.timer_running = False
                        self.add_event("Timer expired")
                        self.last_hit_display = "Timer expired"

    def get_timer_display(self):

        minutes = self.timer_seconds // 60
        seconds = self.timer_seconds % 60

        return f"{minutes}:{seconds:02d}"

    def get_state(self):

        with self.lock:
            elapsed_time = round(time.time() - self.match_start_time, 1)

            match_point = "None"

            if not self.match_over:
                if self.player_1_score == self.winning_score - 1:
                    match_point = "Player 1"

                elif self.player_2_score == self.winning_score - 1:
                    match_point = "Player 2"

            if self.last_packet_received_time is None:
                last_packet_age = "None"
            else:
                last_packet_age = round(time.time() - self.last_packet_received_time, 1)

            return {
                "bout_type": self.bout_type,
                "match_number": self.match_number,
                "winning_score": self.winning_score,
                "weapon_mode": self.weapon_mode,
                "lockout_window": self.lockout_window,
                "player_1_score": self.player_1_score,
                "player_2_score": self.player_2_score,
                "player_1_cards": list(self.player_1_cards),
                "player_2_cards": list(self.player_2_cards),
                "last_hit": self.last_hit_display,
                "last_packet_age": last_packet_age,
                "match_time": elapsed_time,
                "timer_display": self.get_timer_display(),
                "timer_seconds": self.timer_seconds,
                "timer_running": self.timer_running,
                "match_point": match_point,
                "match_over": self.match_over,
                "winner": self.winner,
                "valid_packets": self.valid_packets,
                "invalid_packets": self.invalid_packets,
                "duplicate_hits": self.duplicate_hits,
                "simultaneous_hits": self.simultaneous_hits,
                "event_history": list(self.event_history[-8:]),
                "device_status": dict(self.device_status)
            }

    def add_card(self, player_id, card_type):

        with self.lock:

            if self.match_over:
                print(Fore.MAGENTA + "Match already ended, card ignored")
                return

            card_type = card_type.lower()

            if card_type not in ["yellow", "red"]:
                return

            if player_id == "P1":
                self.player_1_cards.append(card_type)
                event_text = f"P1 received {card_type} card"

                if card_type == "red":
                    self.player_2_score += 1
                    event_text += " | Point awarded to P2"

            elif player_id == "P2":
                self.player_2_cards.append(card_type)
                event_text = f"P2 received {card_type} card"

                if card_type == "red":
                    self.player_1_score += 1
                    event_text += " | Point awarded to P1"

            else:
                return

            self.add_event(event_text)
            self.last_hit_display = event_text
            self.check_winner()

    def clear_cards(self):

        with self.lock:
            self.player_1_cards = []
            self.player_2_cards = []

            event_text = "Cards cleared"
            self.add_event(event_text)
            self.last_hit_display = event_text

    def manual_score(self, player_id, amount):

        with self.lock:

            if self.match_over:
                print(Fore.MAGENTA + "Match already ended, manual score ignored")
                return

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
            self.add_event(event_text)
            self.last_hit_display = event_text

            self.check_winner()

    def set_bout_preset(self, preset):

        with self.lock:

            preset = preset.lower()

            if preset == "pool":

                self.bout_type = "pool"
                self.winning_score = 5
                self.timer_start_seconds = 180

            elif preset == "de":

                self.bout_type = "de"
                self.winning_score = 15
                self.timer_start_seconds = 180

            elif preset == "practice":

                self.bout_type = "practice"
                self.winning_score = 99
                self.timer_start_seconds = 60

            else:
                return

        self.reset_match()


    def set_weapon(self, weapon_mode):

        with self.lock:
            self.weapon_mode = weapon_mode.lower()

            if self.weapon_mode == "epee":
                self.lockout_window = 0.045

            elif self.weapon_mode == "foil":
                self.lockout_window = 0.300

            elif self.weapon_mode == "saber":
                self.lockout_window = 0.170

            else:
                self.weapon_mode = "epee"
                self.lockout_window = 0.045

            event_text = f"Weapon mode changed to {self.weapon_mode.upper()}"
            self.add_event(event_text)
            self.last_hit_display = event_text

    def set_mode(self, bout_type):

        with self.lock:
            self.bout_type = bout_type.lower()

            if self.bout_type == "de":
                self.winning_score = 15
            else:
                self.bout_type = "pool"
                self.winning_score = 5

        self.reset_match()

    def reset_match(self):

        with self.lock:
            self.match_number += 1
            self.player_1_score = 0
            self.player_2_score = 0

            self.player_1_cards = []
            self.player_2_cards = []

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

            self.timer_seconds = self.timer_start_seconds
            self.timer_running = False

            print(Fore.CYAN + "Match reset complete")