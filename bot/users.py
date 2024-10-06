import json

def create_json(file_path):
    data = {
        "servers": [
            {
                'id': '',
                'users': [],
            },
        ]
    }
    write_json(data, file_path)


def server_exists(data, server_id):
    if not any(server['id'] == server_id for server in data['servers']):
        return False
    return True

def user_in_server(data, user_id, server_id):
    if(not server_exists(data, server_id)):
        return False

    servers = data['servers']
    for s in servers:
        if(s['id'] == server_id):
            return any(user['id'] == user_id for user in s['users'])

    return False

def add_server(data, server_id):
    if(not server_exists(data, server_id)):
        new_server = {
            "id" : server_id,
            "users" : []
        }

        data['servers'].append(new_server)

def add_user(data, server_id, user_id):
    print("New user detected!")
    if(not server_exists(data, server_id)):
        add_server(data, server_id)

    if(not user_in_server(data, user_id, server_id)):
        new_user = {
            "id" : user_id,
            "banned": False,
            "songs_played": 0,
            "admin": False
        }

        for s in data['servers']:
            if(s['id'] == server_id):
                s['users'].append(new_user)

def read_json(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
    except:
        create_json(file_path)
        with open(file_path, 'r') as file:
            data = json.load(file)

    return data


def write_json(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)

def get_server_played(data, server_id, user_id):
    if not any(server['id'] == server_id for server in data['servers']):
        add_server(data, server_id)

    if(not user_in_server(data, user_id, server_id)):
        add_user(data, server_id, user_id)

    for s in data['servers']:
        if(s['id'] == server_id):
            for c in s['users']:
                if(c['id'] == user_id):
                    return c['songs_played']
    return -1

def is_server_admin(data, server_id, user_id):
    if not any(server['id'] == server_id for server in data['servers']):
        add_server(data, server_id)

    if(not user_in_server(data, user_id, server_id)):
        add_user(data, server_id, user_id)

    for s in data['servers']:
        if(s['id'] == server_id):
            for c in s['users']:
                if(c['id'] == user_id):
                    return c['admin']
    return False

def is_user_banned(data, server_id, user_id):
    if not any(server['id'] == server_id for server in data['servers']):
        add_server(data, server_id)

    if(not user_in_server(data, user_id, server_id)):
        add_user(data, server_id, user_id)

    for s in data['servers']:
        if(s['id'] == server_id):
            for c in s['users']:
                if(c['id'] == user_id):
                    return c['banned']
    return False

def add_song_played(file_name, server_id, user_id, count):
    data = read_json(file_name)

    if not any(server['id'] == server_id for server in data['servers']):
        add_server(data, server_id)

    if(not user_in_server(data, user_id, server_id)):
        add_user(data, server_id, user_id)

    for s in data['servers']:
        if(s['id'] == server_id):
            for c in s['users']:
                if(c['id'] == user_id):
                    c['songs_played'] = c['songs_played'] + count
                    write_json(data, file_name)
                    return


def get_globally_played(data, user_id):
    count = 0
    for s in data['servers']:
        for c in s['users']:
            if c['id'] == user_id:
                count = count + c['songs_played']

    return count

def get_stats(server_id, user_id, file_path):
    data = read_json(file_path)
    l = get_server_played(data, server_id, user_id)
    g = get_globally_played(data, user_id)
    a = is_server_admin(data, server_id, user_id)
    b = is_user_banned(data, server_id, user_id)
    write_json(data, file_path)
    return l, g, a, b
