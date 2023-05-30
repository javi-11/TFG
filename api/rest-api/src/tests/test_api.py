import json
import datetime

def post_json(client, url, json_dict):
    """Send dictionary json_dict as a json to the specified url """
    return client.post(url, data=json.dumps(json_dict), content_type='application/json')

def put_json(client, url, json_dict):
    """Send dictionary json_dict as a json to the specified url """
    return client.put(url, data=json.dumps(json_dict), content_type='application/json')

def json_of_response(response):
    """Decode json from response"""
    return json.loads(response.data.decode('utf8'))

def test_create_stay(client):
    response = post_json(client,"/stays",{'room_name':'HF','uuid':'1'})
    message = json_of_response(response).get("message")
    
    assert response.status_code == 200
    assert "Estancia con id: " in message

    response = post_json(client,"/stays",{'room_name':'HF','uuid':'2'})
    message = json_of_response(response).get("message")

    response2 = post_json(client,"/stays",{'room_name':'HF','uuid':'1'})
    message = json_of_response(response2).get("message")
    assert response2.status_code == 200
    assert "Ya existe una estancia sin cerrar para esa habitación" == message

    response3 = post_json(client,"/stays",{'room_name':'Bar','uuid':'1'})
    message = json_of_response(response3).get("message")
    assert response3.status_code == 200
    assert "No hay problema, las regiones se superponen" == message
    
def test_get_stays(client):
    rsp = client.get("/stays")
    assert len(json_of_response(rsp)) == 2
    
def test_update_stays(client):
    rsp = put_json(client, "/stays", {'room_name' : 'HF', 'uuid' : '1'})
    message = json_of_response(rsp).get("message")
    assert "modificada satisfactoriamente" in message
    assert rsp.status_code == 200
    rsp2 = put_json(client, "/stays", {'room_name' : 'Bar', 'uuid' : '1'})
    message = json_of_response(rsp2).get("message")
    assert rsp2.status_code == 200
    assert "Ya hay una estancia creada sin cerrar" == message
    rsp3 = put_json(client, "/stays", {'room_name' : 'Bar'})
    message = json_of_response(rsp2).get("message")
    assert rsp3.status_code == 400    

def test_history(client):
    rsp = post_json(client, "/stays/history", {'uuid':'1'})
    assert len(json_of_response(rsp)) == 1

    rsp2 = post_json(client, "/stays/history", {})
    assert json_of_response(rsp2).get("message") == "No enviaste un identificador válido"

def test_history_d(client):
    start_dateAux = datetime.date.today()
    rsp = post_json(client, "/stays/history/day", {'uuid':'1','day':str(start_dateAux)})

    assert len(json_of_response(rsp)) == 1

    rsp = post_json(client, "/stays/history/day", {'uuid':'3','day':str(start_dateAux)})
    assert len(json_of_response(rsp)) == 0

    rsp2 = post_json(client, "/stays/history/day", {})
    assert json_of_response(rsp2).get("message") == "No enviaste un identificador o fecha válidos"

def test_history_h(client):
    start_dateAux = datetime.datetime.now().replace(microsecond=0)
    start_date = start_dateAux - datetime.timedelta(hours=1)
    start_date = start_date.isoformat().replace("T", " ")
    end_date = start_dateAux + datetime.timedelta(hours=1)
    end_date = end_date.isoformat().replace("T", " ") 
    rsp = post_json(client, "/stays/history/hour", {'uuid':'1','hour1':str(start_date), 'hour2':str(end_date)})
    assert len(json_of_response(rsp)) == 1

    rsp = post_json(client, "/stays/history/hour", {'uuid':'3', 'hour1':str(start_date), 'hour2' : str(end_date)})
    assert len(json_of_response(rsp)) == 0

    rsp2 = post_json(client, "/stays/history/hour", {})
    assert json_of_response(rsp2).get("message") == "No enviaste un identificador o fecha válidos"

def test_stays_room_hours(client):
    start_dateAux = datetime.datetime.now().replace(microsecond=0)
    start_date = start_dateAux - datetime.timedelta(hours=1)
    start_date = start_date.isoformat().replace("T", " ")
    end_date = start_dateAux + datetime.timedelta(hours=1)
    end_date = end_date.isoformat().replace("T", " ") 

    rsp = post_json(client, "/stays/room/hours", {'room_name':'HF','hour1':str(start_date), 'hour2':str(end_date)})
    assert json_of_response(rsp).get("message") == 2

    rsp = post_json(client, "/stays/room/hours", {'room_name':'comedor', 'hour1':str(start_date), 'hour2' : str(end_date)})
    assert json_of_response(rsp).get("message") == 0

    rsp2 = post_json(client, "/stays/room/hours", {})
    assert json_of_response(rsp2).get("message") == "No enviaste un identificador o fecha válidos"

def test_history_room_most_used(client):
    start_dateAux = datetime.date.today()
    day_aux = start_dateAux-datetime.timedelta(days=2)
    rsp = post_json(client, "/stays/room/most_used", {'day':str(start_dateAux)})

    assert json_of_response(rsp).get("message") == "La sala más usada fue HF con 2 estancias."

    rsp = post_json(client, "/stays/room/most_used", {'day':str(day_aux)})
    assert json_of_response(rsp).get("message") == "La sala más usada fue  con 0 estancias."

    rsp2 = post_json(client, "/stays/room/most_used", {})
    assert json_of_response(rsp2).get("message") == "No enviaste un identificador o fecha válidos"

##Se crea una en bar y ya había 2 en HF
def test_history_room_most_used_per_hour(client):

    ##Creación de una nueva estancia
    response = post_json(client,"/stays",{'room_name':'Bar','uuid':'1'})

    #Fechas para búsqueda y horas esperadas en el mensaje
    start_dateAux = datetime.date.today()
    day_aux = start_dateAux-datetime.timedelta(days=2)
    hour1 = datetime.datetime.now().hour
    hour2 = datetime.datetime.now()+datetime.timedelta(hours=1)
    hour2 = hour2.hour
    rsp = post_json(client, "/stays/room/most_used_per_hour", {'day':str(start_dateAux)})
   
    frase = "Esta fue la hora con mayor número de personas para cada sala: No ha habido nadie en Comedor. HF - 2 personas - " +  str(hour1) +"-" + str(hour2) + ". Bar - 1 personas - " +  str(hour1) + "-" + str(hour2) +". "

    assert json_of_response(rsp).get("message").lower().__eq__(frase.lower())

    rsp = post_json(client, "/stays/room/most_used_per_hour", {'day':str(day_aux)})
    assert json_of_response(rsp).get("message").__eq__("Esta fue la hora con mayor número de personas para cada sala: No ha habido nadie en Comedor.  No ha habido nadie en HF.  No ha habido nadie en Bar. ")

    rsp2 = post_json(client, "/stays/room/most_used_per_hour", {})
    assert json_of_response(rsp2).get("message") == "No enviaste un identificador o fecha válidos"

def test_stays_get_room_occupation(client):
    response = post_json(client,"/stays/room/occupation",{})
    assert json_of_response(response).get("message")=={'Bar': '1', 'Comedor': '0', 'HF': '2'}

def test_open_stays(client):
    response = client.get("/stays/open")
    assert len(json_of_response(response))==2

def test_history_room_occupation_perHour(client):
    start_dateAux = datetime.date.today()
    start_datetimeAux = datetime.datetime.now().replace(microsecond=0)
    #start_datetime = start_datetimeAux.isoformat().replace("T", " ")
    response = post_json(client,"/stays/room/occupation_by_hour", {'day': str(start_dateAux), 'room_name': 'HF'})
    hora = start_datetimeAux.hour
    if hora < 10:
        hora = "0" + str(hora) + ":00"
    else:
        hora = str(hora) + ":00"
    assert json_of_response(response).get("message").get(hora) == str(2)

    response2 = post_json(client,"/stays/room/occupation_by_hour",{})
    assert json_of_response(response2).get("message") == "No enviaste un día o habitación válidos"

def test_history_room_stays_perHour(client):
    start_dateAux = datetime.date.today()
    start_datetimeAux = datetime.datetime.now().replace(microsecond=0)
    #start_datetime = start_datetimeAux.isoformat().replace("T", " ")
    response = post_json(client,"/stays/room/getByRoomAndDay", {'day': str(start_dateAux), 'room_name': 'HF'})
    print(json_of_response(response))
    hora = start_datetimeAux.hour
    if hora < 10:
        hora = "0" + str(hora)
    else:
        hora = str(hora)
    print()
    assert json_of_response(response).get("message").get(hora) == '["1", "2"]'

def test_mean(client):
    sala = "HF"
    start_dateAux = datetime.date.today()
    response = post_json(client,"/stays/mean", {'day': str(start_dateAux), 'room_name': sala})

    assert json_of_response(response).get("message") == "Esta es la media de ocupación de " + sala + " durante el día solicitado: " + "2.0" + ", se han tenido en cuenta 1 horas"
    response = post_json(client,"/stays/mean", {})
    assert json_of_response(response).get("message") == "No enviaste un día o habitación válidos"

def test_debug(client):
    response = post_json(client,"/stays/close", {})
    assert json_of_response(response).get("message") == "Se han cerrado satisfactoriamente todas las entradas"
    response = client.get("/stays/open")
    assert len(json_of_response(response))==0

def test_create_user(client):
    response = post_json(client,"/users", {"uuid" : 1})
    assert "creado satisfactoriamente" in json_of_response(response).get("message")
    response = client.get("/users")
    assert len(json_of_response(response))==1
    assert json_of_response(response)[0]["type"] == "Anonymous"

    #Actualización a usuario normal
    response = post_json(client,"/users", {"uuid" : 1, "username" : "raul123", "password" : "contraseña1", "email" : "raul123@gmail.com"})
    assert "modificado satisfactoriamente" in json_of_response(response).get("message")
    response = client.get("/users")
    assert json_of_response(response)[0]["type"] == "User"

    #Creación de usuario normal
    response = post_json(client,"/users", {"uuid" : 2, "username" : "Pedro", "password" : "contraseña1", "email" : "pedro@gmail.com"})
    assert "creado satisfactoriamente" in json_of_response(response).get("message")
    response = client.get("/users")
    assert json_of_response(response)[0]["type"] == "User"
    assert len(json_of_response(response)) == 2

    #Testing de errores
    response = post_json(client,"/users", {"uuid" : 3, "username" : "Pedro", "password" : "contraseña1", "email" : "raul@gmail.com"})
    assert json_of_response(response).get("message") == "Se ha producido un error. Ya existe un usuario con nombre de usuario Pedro"  
    assert response.status_code == 500

    response = post_json(client,"/users", {"uuid" : 2, "username" : "Rafa", "password" : "contraseña1", "email" : "raul1@gmail.com"})
    assert json_of_response(response).get("message") == "Se ha producido un error. Ya existe un usuario asociado a ese dispositivo"  
    assert response.status_code == 500

    response = post_json(client,"/users", {"uuid" : 4, "username" : "Pablo", "password" : "contraseña1", "email" : "raul123@gmail.com"})
    assert json_of_response(response).get("message") == "Se ha producido un error. Ya existe un usuario con email raul123@gmail.com"  
    assert response.status_code == 500

def test_login(client):
    response = post_json(client,"/login", {'username' : 'raul123', 'password': 'contraseña1'})
    print(json_of_response(response))
    assert json_of_response(response).get("token") != ""
  
def test_login_anonnymous(client):
    response = post_json(client,"/login/anonymous", {'uuid' : '1'})
    assert json_of_response(response).get("token") != ""
    response = post_json(client,"/login/anonymous", {'uuid' : '5'})
    assert json_of_response(response).get("token") != ""
    assert json_of_response(response).get("message") == "Además se ha creado un usuario anónimo para este dispositivo"
    response = post_json(client,"/login/anonymous", {})
    assert json_of_response(response).get("message") == "Debes enviar tu identificador"
  
def test_get_user_by_id(client):
    response = client.get("/users")
    assert len(json_of_response(response)) == 3
    print(json_of_response(response)[0])
    response = client.get("/users/"+str(json_of_response(response)[0]["_id"]['$oid']))
    assert json_of_response(response)["uuid"] == "1"

def test_get_user_by_uuid(client):
    response = client.get("/users/device/1")
    print(json_of_response(response))
    assert json_of_response(response)["uuid"] == "1"
    assert json_of_response(response)["username"] == "raul123"

def test_get_user_by_username_id(client):
    response = client.get("/users/username/raul123")
    assert json_of_response(response)["uuid"] == "1"
    assert json_of_response(response)["username"] == "raul123"

def test_delete_user(client):
    response = client.get("/users/username/raul123")
    oid =  json_of_response(response)["_id"]["$oid"]
    response = client.delete("/users/"+str(oid))
    response = client.get("/users/username/raul123")
    assert json_of_response(response) == None