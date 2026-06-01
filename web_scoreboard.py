# web_scoreboard.py

from flask import Flask, jsonify, render_template_string
import threading
import logging
import time

class WebScoreboard:

    def __init__(self, scoreboard):
        self.scoreboard = scoreboard
        self.app = Flask(__name__)

        @self.app.route("/")
        def home():
            return render_template_string(PAGE_HTML)
        
        @self.app.route("/repeater")
        def repeater():
            return render_template_string(REPEATER_HTML)
        
        @self.app.route("/data")
        def data():
            return jsonify(self.scoreboard.get_state())
        
        @self.app.route("/repeater-data")
        def repeater_data():
            state = self.scoreboard.get_state()

            return jsonify({
                "p1": state["player_1_score"],
                "p2": state["player_2_score"],
                "timer": state["timer_display"],
                "weapon": state["weapon_mode"],
                "bout": state["bout_type"],
                "last": state["last_hit"],
                "match_over": state["match_over"],
                "winner": state["winner"]
            })

        @self.app.route("/reset", methods=["POST"])
        def reset():
            self.scoreboard.reset_match()
            return jsonify({"status": "reset complete"})

        @self.app.route("/mode/pool", methods=["POST"])
        def set_pool():
            self.scoreboard.set_mode("pool")
            return jsonify({"status": "pool mode selected"})

        @self.app.route("/mode/de", methods=["POST"])
        def set_de():
            self.scoreboard.set_mode("de")
            return jsonify({"status": "de mode selected"})

        @self.app.route("/score/p1/add", methods=["POST"])
        def score_p1_add():
            self.scoreboard.manual_score("P1", 1)
            return jsonify({"status": "P1 score added"})

        @self.app.route("/score/p2/add", methods=["POST"])
        def score_p2_add():
            self.scoreboard.manual_score("P2", 1)
            return jsonify({"status": "P2 score added"})

        @self.app.route("/score/p1/sub", methods=["POST"])
        def score_p1_sub():
            self.scoreboard.manual_score("P1", -1)
            return jsonify({"status": "P1 score removed"})

        @self.app.route("/score/p2/sub", methods=["POST"])
        def score_p2_sub():
            self.scoreboard.manual_score("P2", -1)
            return jsonify({"status": "P2 score removed"})
        
        @self.app.route("/manual_offtarget/P1", methods=["POST"])
        def manual_offtarget_p1():

            packet = {
                "player_id": "P1",
                "hit_type": "offtarget",
                "time": str(int(time.time() * 1000))
            }

            self.scoreboard.update_score(packet)

            return jsonify({"status": "P1 off-target"})


        @self.app.route("/manual_offtarget/P2", methods=["POST"])
        def manual_offtarget_p2():

            packet = {
                "player_id": "P2",
                "hit_type": "offtarget",
                "time": str(int(time.time() * 1000))
            }

            self.scoreboard.update_score(packet)

            return jsonify({"status": "P2 off-target"})

        @self.app.route("/timer/start", methods=["POST"])
        def timer_start():
            self.scoreboard.start_timer()
            return jsonify({"status": "timer started"})

        @self.app.route("/timer/pause", methods=["POST"])
        def timer_pause():
            self.scoreboard.pause_timer()
            return jsonify({"status": "timer paused"})

        @self.app.route("/timer/reset", methods=["POST"])
        def timer_reset():
            self.scoreboard.reset_timer()
            return jsonify({"status": "timer reset"})

        @self.app.route("/weapon/epee", methods=["POST"])
        def weapon_epee():
            self.scoreboard.set_weapon("epee")
            return jsonify({"status": "epee selected"})

        @self.app.route("/weapon/foil", methods=["POST"])
        def weapon_foil():
            self.scoreboard.set_weapon("foil")
            return jsonify({"status": "foil selected"})

        @self.app.route("/weapon/saber", methods=["POST"])
        def weapon_saber():
            self.scoreboard.set_weapon("saber")
            return jsonify({"status": "saber selected"})
        
        @self.app.route("/preset/pool", methods=["POST"])
        def preset_pool():
            self.scoreboard.set_bout_preset("pool")
            return jsonify({"status": "pool preset selected"})


        @self.app.route("/preset/de", methods=["POST"])
        def preset_de():
            self.scoreboard.set_bout_preset("de")
            return jsonify({"status": "de preset selected"})


        @self.app.route("/preset/practice", methods=["POST"])
        def preset_practice():
            self.scoreboard.set_bout_preset("practice")
            return jsonify({"status": "practice preset selected"})
        
        @self.app.route("/card/p1/yellow", methods=["POST"])
        def card_p1_yellow():
            self.scoreboard.add_card("P1", "yellow")
            return jsonify({"status": "P1 yellow card"})

        @self.app.route("/card/p1/red", methods=["POST"])
        def card_p1_red():
            self.scoreboard.add_card("P1", "red")
            return jsonify({"status": "P1 red card"})

        @self.app.route("/card/p2/yellow", methods=["POST"])
        def card_p2_yellow():
            self.scoreboard.add_card("P2", "yellow")
            return jsonify({"status": "P2 yellow card"})

        @self.app.route("/card/p2/red", methods=["POST"])
        def card_p2_red():
            self.scoreboard.add_card("P2", "red")
            return jsonify({"status": "P2 red card"})

        @self.app.route("/card/clear", methods=["POST"])
        def card_clear():
            self.scoreboard.clear_cards()
            return jsonify({"status": "cards cleared"})


    def start(self):
        thread = threading.Thread(target=self.run_server, daemon=True)
        thread.start()

    def run_server(self):
        log = logging.getLogger("werkzeug")
        log.setLevel(logging.ERROR)

        self.app.run(
            host="127.0.0.1",
            port=5000,
            debug=False,
            use_reloader=False
        )


PAGE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>PisteNet Scoreboard</title>

    <style>
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            min-height: 100vh;
            font-family: Arial, sans-serif;
            color: white;
            background:
                linear-gradient(90deg, rgba(0, 255, 150, 0.12), transparent 30%, transparent 70%, rgba(255, 70, 90, 0.14)),
                radial-gradient(circle at top, #1f2937 0%, #0b0f17 45%, #020305 100%);
            overflow-x: hidden;
        }

        .arena-line {
            position: fixed;
            top: 0;
            left: 50%;
            width: 2px;
            height: 100%;
            background: linear-gradient(to bottom, transparent, rgba(255,255,255,0.35), transparent);
            opacity: 0.4;
            z-index: 0;
        }

        .page {
            position: relative;
            z-index: 1;
            padding: 28px;
        }

        .title {
            text-align: center;
            margin-bottom: 28px;
        }

        .title h1 {
            margin: 0;
            font-size: 52px;
            letter-spacing: 8px;
            font-weight: 900;
        }

        .title .brand {
            color: #facc15;
            letter-spacing: 4px;
            font-size: 15px;
            margin-top: 8px;
        }

        .bout-info {
            color: #cbd5e1;
            margin-top: 10px;
            font-size: 17px;
        }

        .main-scoreboard {
            max-width: 1200px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: 1fr 300px 1fr;
            gap: 24px;
            align-items: stretch;
        }

        .fighter-card {
            min-height: 390px;
            border-radius: 34px;
            padding: 28px;
            position: relative;
            overflow: hidden;
            box-shadow: 0 35px 100px rgba(0,0,0,0.55);
            transition: 0.2s;
        }

        .fighter-card::before {
            content: "";
            position: absolute;
            inset: 0;
            background: linear-gradient(135deg, rgba(255,255,255,0.20), transparent 42%);
            pointer-events: none;
        }

        .fighter-card::after {
            content: "";
            position: absolute;
            bottom: 24px;
            left: 28px;
            right: 28px;
            height: 3px;
            border-radius: 99px;
            opacity: 0.7;
        }

        .left-card {
            background: linear-gradient(145deg, #064e3b, #07111d 65%);
            border: 1px solid rgba(52, 255, 170, 0.35);
        }

        .left-card::after {
            background: #34ffaa;
            box-shadow: 0 0 22px #34ffaa;
        }

        .right-card {
            background: linear-gradient(145deg, #5f111b, #07111d 65%);
            border: 1px solid rgba(255, 80, 105, 0.4);
        }

        .right-card::after {
            background: #ff5069;
            box-shadow: 0 0 22px #ff5069;
        }

        .fighter-label {
            position: relative;
            z-index: 1;
            font-size: 18px;
            color: #cbd5e1;
            letter-spacing: 4px;
            margin-bottom: 12px;
        }

        .fighter-name {
            position: relative;
            z-index: 1;
            font-size: 34px;
            font-weight: 900;
            letter-spacing: 2px;
        }

        .left-color {
            color: #34ffaa;
            text-shadow: 0 0 20px rgba(52,255,170,0.45);
        }

        .right-color {
            color: #ff5069;
            text-shadow: 0 0 20px rgba(255,80,105,0.45);
        }

        .score {
            position: relative;
            z-index: 1;
            font-size: 170px;
            font-weight: 900;
            line-height: 1;
            margin-top: 44px;
            transition:
                transform 0.15s,
                text-shadow 0.2s;
        }

        .center-console {
            background: rgba(255,255,255,0.07);
            border: 1px solid rgba(255,255,255,0.12);
            border-radius: 34px;
            padding: 24px;
            box-shadow: 0 35px 100px rgba(0,0,0,0.45);
            display: flex;
            flex-direction: column;
            justify-content: center;
            backdrop-filter: blur(10px);
        }

        .center-ready {
            border-color: rgba(56,189,248,0.75);
            box-shadow: 0 0 45px rgba(56,189,248,0.28);
        }

        .center-active {
            border-color: rgba(52,255,170,0.85);
            box-shadow: 0 0 55px rgba(52,255,170,0.35);
        }

        .center-halt {
            border-color: rgba(255,80,105,0.85);
            box-shadow: 0 0 55px rgba(255,80,105,0.35);
        }

        .center-victory {
            border-color: rgba(250,204,21,0.9);
            box-shadow: 0 0 65px rgba(250,204,21,0.45);
        }

        .timer-label {
            color: #94a3b8;
            font-size: 13px;
            letter-spacing: 3px;
            margin-bottom: 8px;
        }

        .timer-time {
            font-size: 72px;
            font-weight: 900;
            color: #facc15;
            text-shadow: 0 0 28px rgba(250, 204, 21, 0.5);
        }

        .timer-state {
            margin-top: 6px;
            font-size: 18px;
            color: #e5e7eb;
        }

        .phrase {
            margin-top: 22px;
            font-size: 28px;
            font-weight: 900;
            letter-spacing: 5px;
            color: #ffffff;
        }

        .last-hit {
            margin-top: 18px;
            color: #facc15;
            font-size: 15px;
            line-height: 1.4;
        }

        .status-row {
            max-width: 1200px;
            margin: 20px auto 0 auto;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 24px;
        }

        .status-pill {
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 18px;
            padding: 14px 18px;
            color: #cbd5e1;
        }

        .connected {
            color: #34ffaa;
            font-weight: bold;
            text-shadow: 0 0 14px rgba(52,255,170,0.7);
        }

        .disconnected {
            color: #ff5069;
            font-weight: bold;
            text-shadow: 0 0 14px rgba(255,80,105,0.7);
        }

        .lower-grid {
            max-width: 1200px;
            margin: 24px auto 0 auto;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 24px;
        }

        .panel {
            background: rgba(255,255,255,0.065);
            border: 1px solid rgba(255,255,255,0.12);
            border-radius: 26px;
            padding: 20px;
            box-shadow: 0 25px 70px rgba(0,0,0,0.35);
            backdrop-filter: blur(10px);
        }

        .panel-title {
            color: #38bdf8;
            font-size: 16px;
            font-weight: bold;
            letter-spacing: 3px;
            margin-bottom: 12px;
        }

        .control-section {
            margin-bottom: 18px;
        }

        .section-label {
            font-size: 12px;
            color: #94a3b8;
            letter-spacing: 2px;
            margin-bottom: 8px;
        }

        .button-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 8px;
        }

        .screen-flash {
            position: fixed;
            inset: 0;
            pointer-events: none;
            opacity: 0;
            z-index: 999;
            transition: opacity 0.25s;
        }

        .screen-flash-p1 {
            background: linear-gradient(90deg, rgba(52,255,170,0.42), transparent 65%);
        }

        .screen-flash-p2 {
            background: linear-gradient(270deg, rgba(255,80,105,0.42), transparent 65%);
        }        

        .screen-flash-offtarget-p1 {
            background: linear-gradient(90deg, rgba(255,255,255,0.55), transparent 65%);
        }

        .screen-flash-offtarget-p2 {
            background: linear-gradient(270deg, rgba(255,255,255,0.55), transparent 65%);
        }

        .flash-offtarget {
            box-shadow: 0 0 90px rgba(255,255,255,0.95);
            transform: scale(1.04);
        }        

        .screen-flash-show {
            opacity: 1;
        }

        .timer-warning {
            color: #ff5069 !important;
            text-shadow: 0 0 30px rgba(255, 80, 105, 0.9);
            animation: pulseTimer 0.8s infinite;
        }

        .match-point {
            margin-top: 10px;
            color: #facc15;
            font-size: 16px;
            font-weight: bold;
            letter-spacing: 2px;
            min-height: 22px;
        }        

        @keyframes pulseTimer {
            0% {
                transform: scale(1);
            }
            50% {
                transform: scale(1.06);
            }
            100% {
                transform: scale(1);
            }
        }

        button {
            background: rgba(255,255,255,0.075);
            color: white;
            border: 1px solid rgba(255,255,255,0.16);
            border-radius: 14px;
            padding: 12px 8px;
            font-size: 14px;
            cursor: pointer;
            transition: 0.15s;
        }

        button:hover {
            background: rgba(56,189,248,0.22);
            border-color: rgba(56,189,248,0.7);
            transform: translateY(-1px);
        }

        .good:hover {
            background: rgba(52,255,170,0.18);
            border-color: rgba(52,255,170,0.7);
        }

        .danger:hover {
            background: rgba(255,80,105,0.22);
            border-color: rgba(255,80,105,0.75);
        }

        .stats {
            color: #d1d5db;
            line-height: 1.7;
            font-size: 15px;
        }

        .event-list, .saved-list {
            max-height: 210px;
            overflow-y: auto;
            text-align: left;
        }

        .event-item {
            padding: 8px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            color: #e5e7eb;
            font-size: 14px;
        }

        .event-item:last-child {
            border-bottom: none;
        }

        .flash-p1 {
            box-shadow: 0 0 80px rgba(52,255,170,0.9);
            transform: scale(1.04);
        }

        .flash-p2 {
            box-shadow: 0 0 80px rgba(255,80,105,0.9);
            transform: scale(1.04);
        }

        .overlay {
            display: none;
            max-width: 1200px;
            margin: 24px auto 0 auto;
            padding: 22px;
            border-radius: 26px;
            font-size: 40px;
            color: #facc15;
            font-weight: 900;
            background: rgba(250,204,21,0.12);
            border: 1px solid rgba(250,204,21,0.45);
            box-shadow: 0 0 45px rgba(250,204,21,0.25);
            text-align: center;
            animation: winnerPulse 1.2s infinite;
            backdrop-filter: blur(8px);
        }

        @keyframes winnerPulse {
            0% {
                transform: scale(1);
                box-shadow: 0 0 40px rgba(250,204,21,0.25);
            }

            50% {
                transform: scale(1.03);
                box-shadow: 0 0 70px rgba(250,204,21,0.55);
            }

            100% {
                transform: scale(1);
                box-shadow: 0 0 40px rgba(250,204,21,0.25);
            }
        }        

        .card-display {
            margin-top: 10px;
            font-size: 36px;
            min-height: 44px;
        }

        body.showcase-mode .lower-grid {
                    display: none;
                }

                body.showcase-mode .status-row {
                    display: none;
                }

                body.showcase-mode .last-hit {
                    display: none;
                }

                body.showcase-mode .main-scoreboard {
                    max-width: 1350px;
                    grid-template-columns: 1fr 340px 1fr;
                }

                body.showcase-mode .fighter-card {
                    min-height: 500px;
                }

                body.showcase-mode .score {
                    font-size: 220px;
                }

                body.showcase-mode .timer-time {
                    font-size: 92px;
                }

                body.showcase-mode .match-point {
                    font-size: 22px;
                }               

        .showcase-btn {
            position: fixed;
            top: 122px;
            right: 18px;
            z-index: 1000;
            width: 44px;
            height: 44px;
            border-radius: 50%;
            font-size: 18px;
            padding: 0;
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.18);
        }   

        @media (max-width: 950px) {
            .main-scoreboard,
            .lower-grid,
            .status-row {
                grid-template-columns: 1fr;
            }

            .score {
                font-size: 120px;
            }

            .timer-time {
                font-size: 60px;
            }

            .button-grid {
                grid-template-columns: repeat(2, 1fr);
            }

            .scoring-status {
                margin-top: 8px;
                font-size: 14px;
                letter-spacing: 2px;
                color: #cbd5e1;
            }

            .scoring-active {
                color: #34ffaa;
            }

            .scoring-disabled {
                color: #ff5069;
            }            

        .fullscreen-btn {
            position: fixed;
            top: 18px;
            right: 18px;
            z-index: 1000;
            width: 44px;
            height: 44px;
            border-radius: 50%;
            font-size: 22px;
            padding: 0;
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.18);
        }

        .fullscreen-btn:hover {
            background: rgba(56,189,248,0.22);
        }

        .sound-btn {
            position: fixed;
            top: 70px;
            right: 18px;
            z-index: 1000;
            width: 44px;
            height: 44px;
            border-radius: 50%;
            font-size: 20px;
            padding: 0;
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.18);
        }

        .sound-btn:hover {
            background: rgba(56,189,248,0.22);
        }

        .small-clear-btn {
            margin-bottom: 10px;
            padding: 7px 12px;
            font-size: 12px;
            border-radius: 10px;
            color: #cbd5e1;
        }      

        }
    </style>
</head>

<body>
    <div class="arena-line"></div>
    <button class="fullscreen-btn" onclick="toggleFullscreen()">⛶</button>
    <button class="sound-btn" id="sound_btn" onclick="toggleSound()">🔊</button>
        <button class="showcase-btn" id="showcase_btn" onclick="toggleShowcaseMode()">🎬</button>
    <div id="screen_flash" class="screen-flash"></div>

    <div class="page">
        <div class="title">
            <h1>PISTENET</h1>
            <div class="brand">WIRELESS FENCING SCORE SYSTEM</div>
            <div class="bout-info" id="mode">Loading bout info...</div>
        </div>

        <div class="main-scoreboard">
            <div class="fighter-card left-card" id="p1_card">
                <div class="fighter-label">LEFT</div>
                <div class="fighter-name left-color">PLAYER 1</div>
                <div class="score left-color" id="p1_score">0</div>
                <div class="card-display" id="p1_cards"></div>
            </div>

            <div class="center-console center-ready" id="center_console">
                <div class="timer-label">BOUT CLOCK</div>
                <div class="timer-time" id="timer_time">3:00</div>
                <div class="timer-state" id="timer_state">Paused</div>
                <div class="phrase" id="bout_phrase">EN GARDE</div>
                <div class="match-point" id="match_point"></div>
                <div class="last-hit" id="last_hit">Last Hit: None</div>
            </div>

            <div class="fighter-card right-card" id="p2_card">
                <div class="fighter-label">RIGHT</div>
                <div class="fighter-name right-color">PLAYER 2</div>
                <div class="score right-color" id="p2_score">0</div>
                <div class="card-display" id="p2_cards"></div>
            </div>
        </div>

        <div class="status-row">
            <div class="status-pill">
                P1 Device: <span id="p1_status" class="disconnected">not connected</span>
            </div>

            <div class="status-pill">
                P2 Device: <span id="p2_status" class="disconnected">not connected</span>
            </div>
        </div>

        <div class="lower-grid">
            <div class="panel">
                <div class="panel-title">CONTROL CONSOLE</div>
                <div class="section-label">Shortcuts: Space start/pause | R reset | 1/P1 | 2/P2 | S save</div>

                <div class="control-section">
                    <div class="section-label">TIMER</div>
                    <div class="button-grid">
                        <button class="good" onclick="sendTimerCommand('/timer/start', 'ALLEZ')">Start</button>
                        <button onclick="sendTimerCommand('/timer/pause', 'HALT')">Pause</button>
                        <button onclick="sendTimerCommand('/timer/reset', 'EN GARDE')">Reset Timer</button>
                        <button class="danger" onclick="sendCommand('/reset')">Reset Match</button>
                    </div>
                </div>

                <div class="control-section">
                    <div class="section-label">MATCH</div>
                    <div class="button-grid">
                        <button onclick="sendCommand('/preset/pool')">Pool Bout</button>
                        <button onclick="sendCommand('/preset/de')">DE Bout</button>
                        <button onclick="sendCommand('/preset/practice')">Practice</button>
                    </div>
                </div>

                <div class="control-section">
                    <div class="section-label">WEAPON</div>
                    <div class="button-grid">
                        <button onclick="sendCommand('/weapon/epee')">Epee</button>
                        <button onclick="sendCommand('/weapon/foil')">Foil</button>
                        <button onclick="sendCommand('/weapon/saber')">Saber</button>
                    </div>
                </div>

                <div class="control-section">
                    <div class="section-label">MANUAL SCORE</div>
                    <div class="button-grid">
                        <button onclick="sendCommand('/score/p1/add')">P1 +1</button>
                        <button onclick="sendCommand('/score/p1/sub')">P1 -1</button>
                        <button onclick="sendCommand('/score/p2/add')">P2 +1</button>
                        <button onclick="sendCommand('/score/p2/sub')">P2 -1</button>
                        <button onclick="manualOffTarget('P1')">P1 Off-Target</button>
                        <button onclick="manualOffTarget('P2')">P2 Off-Target</button>                        
                    </div>
                </div>

                <div class="control-section">
                    <div class="section-label">CARDS</div>
                    <div class="button-grid">
                        <button onclick="sendCommand('/card/p1/yellow')">P1 Yellow</button>
                        <button class="danger" onclick="sendCommand('/card/p1/red')">P1 Red</button>
                        <button onclick="sendCommand('/card/p2/yellow')">P2 Yellow</button>
                        <button class="danger" onclick="sendCommand('/card/p2/red')">P2 Red</button>
                        <button onclick="sendCommand('/card/clear')">Clear Cards</button>
                    </div>
                </div>

            </div>


            <div class="panel">
                <div class="panel-title">SYSTEM TELEMETRY</div>
                <div class="stats">
                    <div id="runtime">Runtime: 0s</div>
                    <div id="packets">Valid Packets: 0 | Invalid Packets: 0</div>
                    <div id="extra">Duplicates: 0 | Simultaneous Hits: 0</div>
                    <div id="packet_age">Last Packet: None</div>
                    <div>BLE Receiver: Active</div>
                    <div>Packet Parser: Enabled</div>
                    <div>Lockout Logic: Enabled</div>
                </div>
            </div>
        </div>

        <div class="lower-grid">
            <div class="panel">
                <div class="panel-title">LIVE EVENT FEED</div>
                <div class="event-list" id="event_list">No events yet</div>
            </div>

            <div class="panel">
                <div class="panel-title">SAVED MATCHES</div>
                <button class="small-clear-btn" onclick="clearSavedMatches()">Clear Saved</button>
                <button class="small-clear-btn" onclick="exportSavedMatches()">Export Saved</button>
                <div class="saved-list" id="saved_matches">No saved matches yet</div>
            </div>
        </div>

        <div class="overlay" id="winner"></div>
    </div>

    <script>

        let audioContext = null;
        let soundEnabled = true;
        let winnerSoundPlayed = false;

        function playHitSound(frequency) {

            if (!soundEnabled) {
                return;
            }

            if (!audioContext) {
                audioContext = new (window.AudioContext || window.webkitAudioContext)();
            }

            const oscillator = audioContext.createOscillator();
            const gain = audioContext.createGain();

            oscillator.connect(gain);
            gain.connect(audioContext.destination);

            oscillator.frequency.value = frequency;
            oscillator.type = "square";

            gain.gain.setValueAtTime(0.08, audioContext.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.001, audioContext.currentTime + 0.18);

            oscillator.start();
            oscillator.stop(audioContext.currentTime + 0.18);
        }
    
        let lastP1Score = 0;
        let lastP2Score = 0;

        let previousLastHit = "";        

        function flashCard(cardId, className) {
            const card = document.getElementById(cardId);
            card.classList.add(className);

            setTimeout(() => {
                card.classList.remove(className);
            }, 300);
        }

        function flashScreen(className) {
            const flash = document.getElementById("screen_flash");

            flash.className = "screen-flash " + className + " screen-flash-show";

            setTimeout(() => {
                flash.className = "screen-flash";
            }, 500);
        }

        function renderCards(containerId, cards) {

            const container = document.getElementById(containerId);

            if (!cards || cards.length === 0) {
                container.innerHTML = "";
                return;
            }

            let output = "";

            cards.forEach((card) => {

                if (card === "yellow") {
                    output += "🟨 ";
                }

                else if (card === "red") {
                    output += "🟥 ";
                }
            });

            container.innerHTML = output;
        }

        function toggleFullscreen() {
            if (!document.fullscreenElement) {
                document.documentElement.requestFullscreen();
            } else {
                document.exitFullscreen();
            }
        }

        function toggleSound() {

            soundEnabled = !soundEnabled;

            const button = document.getElementById("sound_btn");

            if (soundEnabled) {
                button.innerText = "🔊";
            } else {
                button.innerText = "🔇";
            }
        }

         function toggleShowcaseMode() {
            document.body.classList.toggle("showcase-mode");

            const button = document.getElementById("showcase_btn");

            if (document.body.classList.contains("showcase-mode")) {
                button.innerText = "🧪";
            } else {
                button.innerText = "🎬";
            }
        }       

        function updateStatus(elementId, status) {
            const element = document.getElementById(elementId);
            element.innerText = status;

            if (status === "connected") {
                element.className = "connected";
            } else {
                element.className = "disconnected";
            }
        }

        function updateEventFeed(events) {
            const eventList = document.getElementById("event_list");

            if (!events || events.length === 0) {
                eventList.innerText = "No events yet";
                return;
            }

            eventList.innerHTML = "";

            events.slice().reverse().forEach((eventText) => {
                const item = document.createElement("div");
                item.className = "event-item";
                item.innerText = eventText;
                eventList.appendChild(item);
            });
        }

        async function saveMatchToBrowser() {
            const response = await fetch("/data");
            const data = await response.json();

            const savedMatches = JSON.parse(localStorage.getItem("savedMatches") || "[]");

            savedMatches.push({
                saved_at: new Date().toLocaleString(),
                match_number: data.match_number,
                mode: data.bout_type.toUpperCase(),
                weapon: data.weapon_mode.toUpperCase(),
                score: data.player_1_score + " - " + data.player_2_score,
                winner: data.winner || "None",
                timer: data.timer_display,
                valid_packets: data.valid_packets,
                invalid_packets: data.invalid_packets,
                duplicate_hits: data.duplicate_hits,
                simultaneous_hits: data.simultaneous_hits
            });

            localStorage.setItem("savedMatches", JSON.stringify(savedMatches));
            renderSavedMatches();
        }

        function renderSavedMatches() {
            const savedMatches = JSON.parse(localStorage.getItem("savedMatches") || "[]");
            const container = document.getElementById("saved_matches");

            if (savedMatches.length === 0) {
                container.innerText = "No saved matches yet";
                return;
            }

            container.innerHTML = "";

            savedMatches.slice().reverse().forEach((match) => {
                const item = document.createElement("div");
                item.className = "event-item";

                item.innerText =
                    "Match " + match.match_number +
                    " | " + match.saved_at +
                    " | " + match.mode +
                    " | " + match.weapon +
                    " | Score: " + match.score +
                    " | Winner: " + match.winner +
                    " | Timer: " + match.timer;

                container.appendChild(item);
            });
        }

        function clearSavedMatches() {
            localStorage.removeItem("savedMatches");
            renderSavedMatches();
        }

        function exportSavedMatches() {
            const savedMatches = localStorage.getItem("savedMatches") || "[]";
            const blob = new Blob([savedMatches], { type: "application/json" });

            const link = document.createElement("a");
            link.href = URL.createObjectURL(blob);
            link.download = "saved_matches.json";
            link.click();
        }
        
        async function sendCommand(route) {
            await fetch(route, { method: "POST" });
            updateScoreboard();
        }

        async function sendTimerCommand(route, phrase) {
            await fetch(route, { method: "POST" });

            document.getElementById("bout_phrase").innerText = phrase;

            updateScoreboard();
        }

        async function manualOffTarget(player) {

            const response = await fetch("/manual_offtarget/" + player, {
                method: "POST"
            });

            updateScoreboard();
        }

        function setupKeyboardShortcuts() {

            document.addEventListener("keydown", function(event) {

                const key = event.key.toLowerCase();

                if (key === " ") {
                    event.preventDefault();

                    const timerState = document.getElementById("timer_state").innerText;

                    if (timerState === "Running") {
                        sendTimerCommand("/timer/pause", "HALT");
                    } else {
                        sendTimerCommand("/timer/start", "ALLEZ");
                    }
                }

                else if (key === "r") {
                    sendCommand("/reset");
                }

                else if (key === "1") {
                    sendCommand("/score/p1/add");
                }

                else if (key === "2") {
                    sendCommand("/score/p2/add");
                }

                else if (key === "s") {
                    saveMatchToBrowser();
                }

                else if (key === "e") {
                    sendCommand("/weapon/epee");
                }

                else if (key === "f") {
                    sendCommand("/weapon/foil");
                }

                else if (key === "b") {
                    sendCommand("/weapon/saber");
                }
            });
        }

        async function updateScoreboard() {
            const response = await fetch("/data");
            const data = await response.json();

            const centerConsole = document.getElementById("center_console");

            centerConsole.classList.remove(
                "center-ready",
                "center-active",
                "center-halt",
                "center-victory"
            );

            if (data.match_over) {
                centerConsole.classList.add("center-victory");
            }
            else if (data.timer_running) {
                centerConsole.classList.add("center-active");
            }
            else if (
                data.player_1_score === 0 &&
                data.player_2_score === 0 &&
                data.timer_display === "3:00"
            ) {
                centerConsole.classList.add("center-ready");
            }
            else {
                centerConsole.classList.add("center-halt");
            }
            
            const lockoutMs = Math.round(data.lockout_window * 1000);

            document.getElementById("mode").innerText =
                data.bout_type.toUpperCase() +
                " BOUT | " +
                data.weapon_mode.toUpperCase() +
                " | FIRST TO " +
                data.winning_score +
                " | LOCKOUT " +
                lockoutMs +
                " ms";

            updateStatus("p1_status", data.device_status["Fencing_P1"]);
            updateStatus("p2_status", data.device_status["Fencing_P2"]);

            document.getElementById("p1_score").innerText = data.player_1_score;
            document.getElementById("p2_score").innerText = data.player_2_score;

            renderCards("p1_cards", data.player_1_cards);
            renderCards("p2_cards", data.player_2_cards);

            if (data.player_1_score > lastP1Score) {
                flashCard("p1_card", "flash-p1");
                flashScreen("screen-flash-p1");
                playHitSound(660);
            }            

            if (data.player_2_score > lastP2Score) {
                flashCard("p2_card", "flash-p2");
                flashScreen("screen-flash-p2");
                playHitSound(440);
            }

            if (
                data.last_hit.toLowerCase().includes("off-target") &&
                data.last_hit !== previousLastHit
            ) {
                if (data.last_hit.startsWith("P1")) {
                    flashCard("p1_card", "flash-offtarget");
                    flashScreen("screen-flash-offtarget-p1");
                }

                else if (data.last_hit.startsWith("P2")) {
                    flashCard("p2_card", "flash-offtarget");
                    flashScreen("screen-flash-offtarget-p2");
                }

                playHitSound(520);
            }

            previousLastHit = data.last_hit;

            lastP1Score = data.player_1_score;
            lastP2Score = data.player_2_score;

            document.getElementById("last_hit").innerText =
                "Last Hit: " + data.last_hit;

            document.getElementById("runtime").innerText =
                "Runtime: " + data.match_time + "s";

            const timerElement = document.getElementById("timer_time");
            timerElement.innerText = data.timer_display;

            if (data.timer_seconds <= 30 && data.timer_seconds > 0) {
                timerElement.classList.add("timer-warning");
            } else {
                timerElement.classList.remove("timer-warning");
            }                

            document.getElementById("timer_state").innerText =
                data.timer_running ? "Running" : "Paused";

            if (data.timer_seconds <= 0) {

                document.getElementById("bout_phrase").innerText = "HALT";

            }
            else if (data.timer_running) {

                document.getElementById("bout_phrase").innerText = "ALLEZ";

            }
            else {

                if (
                    data.player_1_score === 0 &&
                    data.player_2_score === 0 &&
                    data.timer_display === "3:00"
                ) {

                    document.getElementById("bout_phrase").innerText = "EN GARDE";

                }
                else {

                    document.getElementById("bout_phrase").innerText = "HALT";

                }
            }               

            if (data.match_point !== "None") {
                document.getElementById("match_point").innerText =
                    "MATCH POINT: " + data.match_point.toUpperCase();
            } else {
                document.getElementById("match_point").innerText = "";
            }

            document.getElementById("packets").innerText =
                "Valid Packets: " + data.valid_packets + " | Invalid Packets: " + data.invalid_packets;

            document.getElementById("extra").innerText =
                "Duplicates: " + data.duplicate_hits + " | Simultaneous Hits: " + data.simultaneous_hits;

            if (data.last_packet_age === "None") {
                document.getElementById("packet_age").innerText = "Last Packet: None";
            } else {
                document.getElementById("packet_age").innerText =
                    "Last Packet: " + data.last_packet_age + "s ago";
            }

            updateEventFeed(data.event_history);

            if (data.match_over) {
                if (!winnerSoundPlayed) {
                        playHitSound(880);
                        winnerSoundPlayed = true;
                    }
                document.getElementById("winner").style.display = "block";
                document.getElementById("winner").innerText =
                    "VICTORY — " + data.winner.toUpperCase();
            } else {
                winnerSoundPlayed = false;
                document.getElementById("winner").style.display = "none";
                document.getElementById("winner").innerText = "";
            }
        }

        setInterval(updateScoreboard, 500);
        updateScoreboard();
        renderSavedMatches();
        setupKeyboardShortcuts();
    </script>
</body>
</html>
"""
REPEATER_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>PisteNet Repeater</title>

    <style>
        body {
            margin: 0;
            min-height: 100vh;
            background: radial-gradient(circle at top, #1f2937 0%, #020617 65%);
            color: white;
            font-family: Arial, sans-serif;
            overflow: hidden;
        }

        .screen {
            height: 100vh;
            display: grid;
            grid-template-rows: auto 1fr auto;
            padding: 30px;
        }

        .top {
            text-align: center;
        }

        .title {
            font-size: 52px;
            font-weight: 900;
            letter-spacing: 8px;
        }

        .mode {
            margin-top: 10px;
            color: #cbd5e1;
            font-size: 22px;
            letter-spacing: 3px;
        }

        .score-row {
            display: grid;
            grid-template-columns: 1fr 220px 1fr;
            align-items: center;
            gap: 30px;
        }

        .player {
            text-align: center;
            border-radius: 34px;
            padding: 30px;
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.14);
        }

        .p1 {
            box-shadow: 0 0 60px rgba(52,255,170,0.22);
        }

        .p2 {
            box-shadow: 0 0 60px rgba(255,80,105,0.22);
        }

        .label {
            font-size: 30px;
            font-weight: 900;
            letter-spacing: 4px;
            color: #cbd5e1;
        }

        .score {
            font-size: 230px;
            font-weight: 900;
            line-height: 1;
        }

        .p1-score {
            color: #34ffaa;
            text-shadow: 0 0 28px rgba(52,255,170,0.65);
        }

        .p2-score {
            color: #ff5069;
            text-shadow: 0 0 28px rgba(255,80,105,0.65);
        }

        .center {
            text-align: center;
        }

        .timer {
            font-size: 70px;
            font-weight: 900;
            color: #facc15;
            text-shadow: 0 0 24px rgba(250,204,21,0.5);
        }

        .phrase {
            margin-top: 18px;
            font-size: 34px;
            font-weight: 900;
            letter-spacing: 5px;
        }

        .last {
            text-align: center;
            font-size: 30px;
            color: #e5e7eb;
            padding: 18px;
            border-radius: 22px;
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.12);
        }

        .winner {
            color: #facc15;
            font-weight: 900;
            text-shadow: 0 0 30px rgba(250,204,21,0.8);
        }
    </style>
</head>

<body>
    <div class="screen">
        <div class="top">
            <div class="title">PISTENET</div>
            <div class="mode" id="mode">Loading...</div>
        </div>

        <div class="score-row">
            <div class="player p1">
                <div class="label">PLAYER 1</div>
                <div class="score p1-score" id="p1_score">0</div>
            </div>

            <div class="center">
                <div class="timer" id="timer">3:00</div>
                <div class="phrase" id="phrase">EN GARDE</div>
            </div>

            <div class="player p2">
                <div class="label">PLAYER 2</div>
                <div class="score p2-score" id="p2_score">0</div>
            </div>
        </div>

        <div class="last" id="last_event">Last Event: None</div>
    </div>

    <script>
        async function updateRepeater() {
            const response = await fetch("/data");
            const data = await response.json();

            document.getElementById("mode").innerText =
                data.bout_type.toUpperCase() +
                " | " +
                data.weapon_mode.toUpperCase() +
                " | FIRST TO " +
                data.winning_score;

            document.getElementById("p1_score").innerText = data.player_1_score;
            document.getElementById("p2_score").innerText = data.player_2_score;
            document.getElementById("timer").innerText = data.timer_display;

            if (data.match_over) {
                document.getElementById("phrase").innerText = "VICTORY";
                document.getElementById("last_event").className = "last winner";
                document.getElementById("last_event").innerText =
                    "Winner: " + data.winner;
            } else {
                document.getElementById("last_event").className = "last";

                if (data.timer_running) {
                    document.getElementById("phrase").innerText = "ALLEZ";
                } else {
                    document.getElementById("phrase").innerText = "HALT";
                }

                document.getElementById("last_event").innerText =
                    "Last Event: " + data.last_hit;
            }
        }

        setInterval(updateRepeater, 500);
        updateRepeater();
    </script>
</body>
</html>
"""