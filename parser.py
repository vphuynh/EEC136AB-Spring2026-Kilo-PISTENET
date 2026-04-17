# parser.py

# this function takes in a raw string like "P1,hit,123456"
# and breaks it into parts so we can actually use the data
def parse_data(data):

    # remove any extra spaces or newline characters
    data = data.strip()

    # if nothing was entered, just ignore it
    if data == "":
        return None

    # split the string by commas
    parts = data.split(",")

    # make sure we actually got 3 pieces
    if len(parts) != 3:
        return None

    # unpack the values into variables
    player_id, hit_type, time = parts

    # return the parsed data in a clean structure
    return {
        "player_id": player_id,
        "hit_type": hit_type,
        "time": time
    }


# this function prints parsed packet data in a clean way
def print_parsed(data):

    # if parsing failed, show invalid packet
    if data is None:
        print("Invalid packet")
        print("----------------------")
        return

    # print the packet contents
    print("Received Packet:")
    print("Player:", data["player_id"])
    print("Hit Type:", data["hit_type"])
    print("Time:", data["time"])
    print("----------------------")