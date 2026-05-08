# parser.py

# this function takes in a raw string like "P1,hit,123456"
# and breaks it into parts so we can actually use the data
def parse_data(data):

    data = data.strip()

    if data == "":
        return None

    parts = data.split(",")

    if len(parts) != 3:
        return None

    player_id, hit_type, time = parts

    player_id = player_id.strip()
    hit_type = hit_type.strip().lower()
    time = time.strip()

    # only accept player 1 or player 2
    if player_id not in ["P1", "P2"]:
        return None

    # only accept hit events for now
    if hit_type != "hit":
        return None

    # make sure timestamp / hit id is not empty
    if time == "":
        return None

    return {
        "player_id": player_id,
        "hit_type": hit_type,
        "time": time
    }


# this function prints parsed packet data in a clean way
def print_parsed(data):

    if data is None:
        print("Invalid packet")
        print("----------------------")
        return

    print("Received Packet:")
    print("Player:", data["player_id"])
    print("Hit Type:", data["hit_type"])
    print("Time:", data["time"])
    print("----------------------")