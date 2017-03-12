import csv

def read_csv_file(file):
    #We want faster searching for the bot, so we return several structures
    #A map of player tags to the IDs they could represent
    #A map of player IDs to their actual score
    tag_id_map = {}
    id_score_map = {}
    with open(file) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            tag = row['tag'].lower()
            pid = row['id']
            score = float(row['score'])
            if (tag in tag_id_map):
                 tag_id_map[tag].add(pid)
            id_score_map[pid] = score
    return (tag_id_map, id_score_map)

data_cached = None
leaderboard = None
leaderboard_map = None

def obtain_score(player_name, players_cached = {}):
    player_name = player_name.lower()
    if player_name in players_cached:
        return players_cached[player_name]
    (tag_id_map, id_score_map) = data_cached
    if player_name in tag_id_map:
        ids = [pid for pid in tag_id_map[player_name]]
        #This resolves tag/id ambiguity
        if player_name in id_score_map:
            ids.append(player_name)
    else:
        ids = [player_name]
    scores = [leaderboard_map[pid] for pid in ids if pid in leaderboard_map]
    players_cached[player_name] = scores
    return scores

def calculate_leaderboard():
    global data_cached
    global leaderboard
    global leaderboard_map
    print("Calculating leaderboard...")
    data_cached = read_csv_file("most_recent_player_data.csv")
    (tag_id_map, id_score_map) = data_cached
    leaderboard = [(tag, pid, id_score_map[pid])
                   for tag in tag_id_map for pid in tag_id_map[tag]]
    leaderboard.sort(key = lambda k : k[2])
    leaderboard = list(enumerate(leaderboard))
    leaderboard_map = {}
    for rank, tag, pid, score in leaderboard:
        leaderboard_map[pid] = (tag, rank, score)
    print("Done")

