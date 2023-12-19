import json

def read_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def write_json(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)
        
def get_user(server_id, user_id):
    for server in json_data["servers"]:
        if server["serverId"] == server_id:
            for user in server["users"]:
                if user["userId"] == user_id:
                    return user

def ban_user(server_id, user_id):
    user = get_user(server_id, user_id)
    user["banned"] = "True"

def get_user_globally(user_id, json_data):
    data = []
    for server in json_data["servers"]:
        for user in server["users"]:
            if user["userId"] == user_id:
                data.append([server["serverId"], user])
    return data

def get_stats(server_id, user_id, file_path):
    user = get_user_globally(user_id, read_json(file_path))

    locally_played_songs = 0
    globally_played_songs = 0
    for server in user:
        globally_played_songs = globally_played_songs + server[1]["queued_songs"]
        if(server_id == server[0]):
            locally_played_songs = locally_played_songs + server[1]["queued_songs"]
    
    return locally_played_songs, globally_played_songs
