# web_scoreboard.py

from flask import Flask, jsonify, render_template_string
import threading
import logging


class WebScoreboard:

    def __init__(self, scoreboard):
        self.scoreboard = scoreboard
        self.app = Flask(__name__)

        @self.app.route("/")
        def home():
            return render_template_string(PAGE_HTML)

        @self.app.route("/data")
        def data():
            return jsonify(self.scoreboard.get_state())

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
    <title>Fencing Scoreboard</title>

    <style>
        body {
            font-family: Arial, sans-serif;
            background: #111;
            color: white;
            text-align: center;
            padding-top: 30px;
        }

        h1 {
            font-size: 44px;
            margin-bottom: 8px;
        }

        .mode {
            color: #00d9ff;
            font-size: 22px;
            margin-bottom: 20px;
        }

        .status-row {
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-bottom: 25px;
        }

        .status-box {
            background: #222;
            border-radius: 12px;
            padding: 12px 24px;
            font-size: 18px;
        }

        .connected {
            color: #00ff88;
        }

        .disconnected {
            color: #ff5555;
        }

        .scoreboard {
            display: flex;
            justify-content: center;
            gap: 60px;
            margin-bottom: 25px;
        }

        .player {
            background: #222;
            border-radius: 20px;
            padding: 30px;
            width: 240px;
            box-shadow: 0 0 20px #000;
            transition: 0.2s;
        }

        .player h2 {
            font-size: 30px;
        }

        .score {
            font-size: 95px;
            font-weight: bold;
        }

        .p1 {
            color: #00ff88;
        }

        .p2 {
            color: #ff5555;
        }

        .flash-p1 {
            box-shadow: 0 0 35px #00ff88;
            transform: scale(1.04);
        }

        .flash-p2 {
            box-shadow: 0 0 35px #ff5555;
            transform: scale(1.04);
        }

        .last-hit {
            font-size: 24px;
            color: yellow;
            margin-top: 10px;
            margin-bottom: 18px;
        }

        .stats {
            margin-top: 20px;
            color: #ccc;
            font-size: 18px;
            line-height: 1.6;
        }

        .event-feed {
            background: #1b1b1b;
            border-radius: 16px;
            width: 520px;
            margin: 25px auto;
            padding: 18px;
            text-align: left;
            box-shadow: 0 0 20px #000;
        }

        .event-feed h2 {
            text-align: center;
            margin-top: 0;
            color: #00d9ff;
        }

        .event-item {
            border-bottom: 1px solid #333;
            padding: 8px 0;
            color: #ddd;
            font-size: 16px;
        }

        .event-item:last-child {
            border-bottom: none;
        }

        .overlay {
            display: none;
            margin-top: 30px;
            font-size: 38px;
            color: yellow;
            font-weight: bold;
        }
    </style>
</head>

<body>
    <h1>FENCING SCOREBOARD</h1>

    <div class="mode" id="mode">Loading...</div>

    <div class="status-row">
        <div class="status-box">
            P1 Device: <span id="p1_status" class="disconnected">not connected</span>
        </div>
        <div class="status-box">
            P2 Device: <span id="p2_status" class="disconnected">not connected</span>
        </div>
    </div>

    <div class="scoreboard">
        <div class="player" id="p1_card">
            <h2 class="p1">Player 1</h2>
            <div class="score p1" id="p1_score">0</div>
        </div>

        <div class="player" id="p2_card">
            <h2 class="p2">Player 2</h2>
            <div class="score p2" id="p2_score">0</div>
        </div>
    </div>

    <div class="last-hit" id="last_hit">Last Hit: None</div>

    <div class="stats">
        <div id="timer">Match Time: 0s</div>
        <div id="packets">Valid Packets: 0 | Invalid Packets: 0</div>
        <div id="extra">Duplicates: 0 | Simultaneous Hits: 0</div>
    </div>

    <div class="event-feed">
        <h2>Live Event Feed</h2>
        <div id="event_list">No events yet</div>
    </div>

    <div class="overlay" id="winner"></div>

    <script>
        let lastP1Score = 0;
        let lastP2Score = 0;

        function flashCard(cardId, className) {
            const card = document.getElementById(cardId);
            card.classList.add(className);

            setTimeout(() => {
                card.classList.remove(className);
            }, 300);
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

        async function updateScoreboard() {
            const response = await fetch("/data");
            const data = await response.json();

            document.getElementById("mode").innerText =
                "Mode: " + data.bout_type.toUpperCase() + " | First to " + data.winning_score;

            updateStatus("p1_status", data.device_status["Fencing_P1"]);
            updateStatus("p2_status", data.device_status["Fencing_P2"]);

            document.getElementById("p1_score").innerText = data.player_1_score;
            document.getElementById("p2_score").innerText = data.player_2_score;

            if (data.player_1_score > lastP1Score) {
                flashCard("p1_card", "flash-p1");
            }

            if (data.player_2_score > lastP2Score) {
                flashCard("p2_card", "flash-p2");
            }

            lastP1Score = data.player_1_score;
            lastP2Score = data.player_2_score;

            document.getElementById("last_hit").innerText =
                "Last Hit: " + data.last_hit;

            document.getElementById("timer").innerText =
                "Match Time: " + data.match_time + "s";

            document.getElementById("packets").innerText =
                "Valid Packets: " + data.valid_packets + " | Invalid Packets: " + data.invalid_packets;

            document.getElementById("extra").innerText =
                "Duplicates: " + data.duplicate_hits + " | Simultaneous Hits: " + data.simultaneous_hits;

            updateEventFeed(data.event_history);

            if (data.match_over) {
                document.getElementById("winner").style.display = "block";
                document.getElementById("winner").innerText =
                    "MATCH OVER - " + data.winner + " Wins";
            } else {
                document.getElementById("winner").style.display = "none";
                document.getElementById("winner").innerText = "";
            }
        }

        setInterval(updateScoreboard, 500);
        updateScoreboard();
    </script>
</body>
</html>
"""