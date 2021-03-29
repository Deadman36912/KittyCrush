from app import app
from app import sql_select, sql_insert, sql_delete, sql_update
from flask import request
from flask import jsonify


@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    #requête pour récupérer les joueurs
    request_sql = f'''SELECT players_id, players_pseudo 
    FROM players'''

    #on exécute la requete
    data = sql_select(request_sql)

    #on print le résultat de la requête
    print(data)

    #on parcourt le résultat
    for player in data:
        #on récupère l'id du joueur
        player_id = player["players_id"]

        #requête pour récupérer les chats d'un joueur
        request_sql = f'''SELECT * FROM cats 
        JOIN rooms ON rooms.rooms_id = cats.rooms_id 
        WHERE rooms.players_id = {player_id}'''


        cats = sql_select(request_sql)
        print(f'''CHATS DU JOUEUR {player_id} : \n''')
        print(len(cats))

        #on ajoute le nombre de chats (le nombre d'objets dans la liste renvoyée par le serveur) au player actuel
        player["cats_count"] = len(cats)

    #on renvoie le résultat jsonifié
    return jsonify(data), 200


@app.route('/login', methods=['POST'])
def login():
    # on récupère le json envoyé par le client
    formulaire_login = (request.get_json())

    # on récupère l'email
    email = formulaire_login["email"]

    # on check si l'email existe, si oui on check password
    sql_request = f'''SELECT * FROM players WHERE players_email = "{email}"'''

    players_avec_cette_email = sql_select(sql_request)

    if len(players_avec_cette_email) > 0:
        # on récupère le password
        password = formulaire_login["password"]

        # on check si le password est correcte
        sql_request = f'''SELECT players_id FROM players WHERE players_email = "{email}" AND players_password = "{password}"'''

        id_players_avec_email_et_password = sql_select(sql_request)

        if len(id_players_avec_email_et_password) > 0:
            print(id_players_avec_email_et_password[0]["players_id"])
            player_id = {"id" : int(id_players_avec_email_et_password[0]["players_id"])}
            return jsonify(player_id)
        else:
            return "Password Incorrect", 403
    else:
        return "Email non existant", 403


@app.route('/signup', methods=['POST'])
def sign_up():
    #on récupère le json envoyé par le client
    formulaire_inscription = (request.get_json())

    #on récupère l'email
    email = formulaire_inscription["email"]

    #on check si l'email existe, si oui on envoie une erreur
    sql_request = f'''SELECT * FROM players WHERE players_email = "{email}"'''

    players_avec_cette_email = sql_select(sql_request)

    if len(players_avec_cette_email) > 0:
        return "Email déjà existant", 503

    #on ajoute le joueur
    sql_request = f'''INSERT INTO players(players_pseudo, players_email, players_password)
    VALUES("{formulaire_inscription["pseudo"]}", 
    "{formulaire_inscription["email"]}", 
    "{formulaire_inscription["password"]}")'''

    players_id = sql_insert(sql_request)

    add_room(players_id, 0, 0, formulaire_inscription["seed"])

    return "OK", 200


@app.route('/users/<int:players_id>/rooms', methods=['GET', 'POST'])
def rooms_handling(players_id):
    if request.method == 'GET':
        return get_rooms_request(players_id)
    elif request.method == 'POST':
        return add_room_request(players_id, request.get_json())


def get_rooms_request(players_id):
    #on recup les infos des rooms appartenant au joueur
    sql_request = f'''SELECT * FROM rooms WHERE players_id = "{players_id}"'''
    player_rooms_info = sql_select(sql_request)


    for room in player_rooms_info:
        sql_request = f'''SELECT * FROM cats WHERE rooms_id = "{room["rooms_id"]}"'''
        room["cats"] = sql_select(sql_request)

    print(player_rooms_info)
    return jsonify(player_rooms_info)

def add_room_request(players_id, request_json):
    print(request_json)
    return add_room(players_id, request_json["position_x"], request_json["position_y"], request_json["seed"])


def add_room(players_id, pos_x, pos_y, seed):

    #controle si une room existe déjà à cette position
    sql_request = f'''SELECT * FROM rooms 
    WHERE players_id = "{players_id}" 
    AND rooms_position_x = "{pos_x}" 
    AND rooms_position_y = "{pos_y}"'''
    player_rooms_info = sql_select(sql_request)

    if len(player_rooms_info) > 0:
        return "Une Room existe déjà ici", 403
    else:
        sql_request = f'''INSERT INTO rooms(rooms_position_x, rooms_position_y, rooms_seed, players_id) 
        VALUES("{pos_x}", "{pos_y}", "{seed}", "{players_id}")'''
        execute = sql_insert(sql_request)
        return {"id": execute}, 200


@app.route('/users/<int:players_id>/rooms/<int:rooms_id>', methods=['DELETE'])
def delete_room(players_id, rooms_id):

    sql_request = f'''SELECT * FROM cats WHERE rooms_id = "{rooms_id}"'''
    get_chats = sql_select(sql_request)

    if len(get_chats) > 0:
        return "Il y à des chats dans cette room", 403
    else:
        sql_request = f'''DELETE FROM rooms WHERE players_id = "{players_id}" AND rooms_id = "{rooms_id}"'''
        sql_delete(sql_request)
        return "OK Room Deleted", 200


@app.route('/cats', methods=['GET'])
def get_free_cats():
    sql_request = f'''SELECT * FROM cats WHERE rooms_id IS NULL'''
    cats_info = sql_select(sql_request)
    print(cats_info)
    return jsonify(cats_info)


@app.route('/cats/<int:cats_id>', methods=['PATCH', 'DELETE'])
def update_cat(cats_id):
    if request.method == 'PATCH':
        formulaire = request.get_json()
        cat_rooms_id = formulaire["rooms_id"]

        sql_request = f'''SELECT * FROM cats WHERE cats_id = "{cats_id}"'''
        cats_info = sql_select(sql_request)

        sql_request = f'''UPDATE cats SET rooms_id = "{cat_rooms_id}" WHERE cats_id = "{cats_id}"'''
        
        if cats_info[0]["rooms_id"] == None:
            sql_update(sql_request)
            return "OK chat adopté", 200
        else:
            sql_update(sql_request)
            return "OK chat déplacé", 200



    elif request.method == 'DELETE':
        print()


