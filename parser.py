# parser.py

# this function takes in a raw string like "P1,hit,1,123456"
# and breaks it into parts so we can actually use the data
def parse_data(data):

    if data is None:
        return None

    data = data.strip()

    if data == "":
        return None

    parts = data.split(",")

    if len(parts) != 4:
        return None

    player_id, hit_type, target_flag, time_stamp = parts

    player_id = player_id.strip().upper()
    hit_type = hit_type.strip().lower()
    target_flag = target_flag.strip()
    time_stamp = time_stamp.strip()

    # only accept player 1 or player 2
    if player_id not in ["P1", "P2"]:
        return None

    if hit_type != "hit":
        return None

    if target_flag not in ["0", "1"]:
        return None

    # make sure timestamp / hit id exists
    if time_stamp == "":
        return None

    return {
        "player_id": player_id,
        "hit_type": hit_type,
        "target_flag": int(target_flag),
        "time": time_stamp
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
    print("Target Flag:", data["target_flag"])
    print("Time/Hit ID:", data["time"])
    print("----------------------")