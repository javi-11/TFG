
import datetime
from zoneinfo import ZoneInfo
from flask import Flask, request, jsonify, Response, make_response
from bson import  json_util
from bson.objectid import ObjectId
import pymongo
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from functools import wraps


app = Flask(__name__)
app.config["SECRET_KEY"] = "key"
client = MongoClient("mongodb+srv://javit:f6dFZDZsA4M0rTz8@cluster0.ejgdxfg.mongodb.net/?retryWrites=true&w=majority",server_api=ServerApi('1'))

mongo = client.test

def create_app(test):
    if test==True:
        global mongo 
        mongo = client.tfg 
        with app.app_context():
            mongo.db.users.create_index('uuid', unique = True)
            mongo.db.users.create_index("username", unique = True, sparse = True)
            mongo.db.users.create_index("email", unique = True, sparse = True) 
        return app
    else:
        mongo = client.test
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
    with app.app_context():
        mongo.db.users.create_index('uuid', unique = True)
        mongo.db.users.create_index("username", unique = True, sparse = True)
        mongo.db.users.create_index("email", unique = True, sparse = True) 
    app.run(debug = True)

def clear_app():
    mongo = client.tfg 
    mongo.drop_collection("db.stays")
    mongo.drop_collection("db.users")
       

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return jsonify({'message': 'Token is missing'}), 403
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
        except:
            return jsonify({'message' : 'Token is invalid'}), 403

        return f(*args, **kwargs)
    return decorated


#Módulo de Estancias
#Necesita el room_name y el user_id para funcionar
@app.route('/stays', methods =['POST'])
def create_stay():

    #Recibiendo como datos room_name y user_id
    if 'room_name' in request.json and 'uuid' in request.json:
        room_name = str(request.json['room_name'])
        uuid = str(request.json['uuid'])
        if(room_name == "HF"):
            alt_name = "Bar"
        else:
            alt_name = "HF"
   
        start_dateAux = datetime.datetime.today().replace(microsecond=0)
        start_date = start_dateAux.astimezone()
        
        if mongo.db.stays.find_one({'uuid' : uuid, 'room_name': room_name, "end_date":{"$exists":False}}):
            response = jsonify({'message' : "Ya existe una estancia sin cerrar para esa habitación"})
        elif mongo.db.stays.find_one({'room_name': alt_name,'uuid':uuid, "end_date":{"$exists":False}}):
            response = jsonify({'message' : "No hay problema, las regiones se superponen"})
        else:
            id = mongo.db.stays.insert_one({'room_name' : room_name, 'uuid' : uuid, 'start_date': start_date})
            response = jsonify({'message' : 'Estancia con id: ' + str(id) + ' creada satisfactoriamente'})

        return response

    else:
        return invalid()

@app.route('/stays', methods=['GET'])
def list_stays():
    stays = mongo.db.stays.find()
    response = json_util.dumps(stays)
    #Lo de abajo indica que la repuesta es un archivo json
    return Response(response, mimetype='application/json')

@app.route('/stays', methods =['PUT'] )
def update_stay():
    #Con tener un user_id el sistema se encargará de actualizar la estancia de por si solo
    end_dateAux = datetime.datetime.today().replace(microsecond=0)
    end_date = end_dateAux.astimezone()
    if 'room_name' in request.json and 'uuid' in request.json:
        room_name = str(request.json['room_name'])
        uuid = str(request.json['uuid'])
        if mongo.db.stays.find_one({'uuid' : uuid,'room_name': room_name, "end_date":{"$exists":False}}):
            id = mongo.db.stays.update_many({'uuid' : uuid, 'end_date' :{"$exists":False}},
                                            {'$set':{'end_date': end_date}})
            response = jsonify({'message' : 'Estancia con id: ' + str(id) + ' modificada satisfactoriamente'})
            return response
        else:
            response = jsonify({'message' : "Ya hay una estancia creada sin cerrar"})
            return response
    else:
        return invalid()

@app.route('/stays/<id>', methods=['DELETE'])
def delete_stay(id):
    print(mongo)
    mongo.db.stays.delete_one({'_id':ObjectId(id)})
    response = jsonify({'message' : 'La estancia con el id ' + id + ' fue eliminada satisfactoriamente'})
    return response

#Historial
@app.route('/stays/history', methods = ['POST'])
def history():
    
    if 'uuid' in request.json:
        uuid = str(request.json['uuid'])
        stays = mongo.db.stays.find({'uuid' : uuid})
        response = json_util.dumps(stays)
        ##response = jsonify({'message' : 'Estancias del usuario ' + uuid + ' recuperadas satisfactoriamente: '+ stays})
        return Response(response,mimetype = "application/json")
    
    else:
        response = jsonify({'message' : "No enviaste un identificador válido" })
        return response
    
#Historial indicando días
@app.route('/stays/history/day', methods = ['POST'])
def history_d():

    if 'uuid' in request.json and 'day' in request.json:
        uuid = str(request.json['uuid'])
        ##Conversiones temporales necesarias para poder hacer la comprobacion
        day_aux =  str(request.json['day'])
        day = datetime.datetime.strptime(day_aux, '%Y-%m-%d').date()
        day2_aux = day + datetime.timedelta(days = 1)
        day = datetime.datetime.combine(day, datetime.datetime.min.time()).replace(tzinfo=datetime.timezone.utc).isoformat()
        day2 = datetime.datetime.combine(day2_aux, datetime.datetime.min.time()).replace(tzinfo=datetime.timezone.utc).isoformat()

        stays = mongo.db.stays.find({'uuid': uuid, "start_date":{'$gte' : datetime.datetime.fromisoformat(day), '$lt' : datetime.datetime.fromisoformat(day2) }})
        response = json_util.dumps(stays)
        
        return Response(response,mimetype = "application/json")
    else:
        response = jsonify({'message' : "No enviaste un identificador o fecha válidos" })
        return response
#Historial indicando horas
@app.route('/stays/history/hour', methods = ['POST'])
def history_h():
    
    ##Toma de entrada dos horas en nuestra zona horaria y al buscar busca por las mismas pero en UTC que es como se guardan en la base de datos
    if 'uuid' in request.json and 'hour1' in request.json and 'hour2' in request.json:
        uuid = str(request.json['uuid'])

        ##Conversiones temporales necesarias para poder hacer la comprobacion
        hour1_aux =  str(request.json['hour1'])
        hour1 = datetime.datetime.strptime(hour1_aux, '%Y-%m-%d %H:%M:%S')
        hour2_aux = str(request.json['hour2'])
        hour2 = datetime.datetime.strptime(hour2_aux, '%Y-%m-%d %H:%M:%S')

        ##Se añade la información de la timezone en la que estamos paar luego poder hacer la conversión
        hour1 = hour1.replace(tzinfo=ZoneInfo("Europe/Madrid"))
        hour2 = hour2.replace(tzinfo=ZoneInfo("Europe/Madrid"))
        
        ##Horas locales en utc para que se pueda comprobar bien en la base de datos
        h1 = hour1.astimezone(datetime.timezone.utc).isoformat()
        h2 = hour2.astimezone(datetime.timezone.utc).isoformat()
    
        
        stays = mongo.db.stays.find({'uuid': uuid, "start_date":{'$gte' : datetime.datetime.fromisoformat(h1), '$lt' : datetime.datetime.fromisoformat(h2) }})
        response = json_util.dumps(stays)
 
        return Response(response,mimetype = "application/json")
    else:
        response = jsonify({'message' : "No enviaste un identificador o fecha válidos" })
        return response
#Indicando una habitación y dos horas devuelve todas las estancias    
@app.route('/stays/room/hours', methods = ['POST'])
def stays_room_hours():

    ##Toma de entrada dos horas en nuestra zona horaria y al buscar busca por las mismas pero en UTC que es como se guardan en la base de datos
    if 'room_name' in request.json and 'hour1' in request.json and 'hour2' in request.json:
        room_name = str(request.json['room_name'])

        ##Conversiones temporales necesarias para poder hacer la comprobacion
        hour1_aux =  str(request.json['hour1'])
        hour1 = datetime.datetime.strptime(hour1_aux, '%Y-%m-%d %H:%M:%S')
        hour2_aux = str(request.json['hour2'])
        hour2 = datetime.datetime.strptime(hour2_aux, '%Y-%m-%d %H:%M:%S')

        ##Se añade la información de la timezone en la que estamos paar luego poder hacer la conversión
        hour1 = hour1.replace(tzinfo=ZoneInfo("Europe/Madrid"))
        hour2 = hour2.replace(tzinfo=ZoneInfo("Europe/Madrid"))
        
        ##Horas locales en utc para que se pueda comprobar bien en la base de datos
        h1 = hour1.astimezone(datetime.timezone.utc).isoformat()
        h2 = hour2.astimezone(datetime.timezone.utc).isoformat()
    
        
        stays = mongo.db.stays.distinct('uuid',{'room_name': room_name, "start_date":{'$gte' : datetime.datetime.fromisoformat(h1), '$lt' : datetime.datetime.fromisoformat(h2) }})
 
        return jsonify({'message' : len(stays)})
    
    else:
        response = jsonify({'message' : "No enviaste un identificador o fecha válidos" })
        return response
#Habitación más utilizada
@app.route('/stays/room/most_used', methods = ['POST'])
def history_room_most_used():

    if 'day' in request.json:
        ##Conversiones temporales necesarias para poder hacer la comprobacion
        day_aux =  str(request.json['day'])
        day = datetime.datetime.strptime(day_aux, '%Y-%m-%d').date()
        day2_aux = day + datetime.timedelta(days = 1)
        day = datetime.datetime.combine(day, datetime.datetime.min.time()).replace(tzinfo=datetime.timezone.utc).isoformat()
        day2 = datetime.datetime.combine(day2_aux, datetime.datetime.min.time()).replace(tzinfo=datetime.timezone.utc).isoformat()

        salas=['Comedor', 'HF', 'Bar']
        max_estancias = 0
        sala_def=""
        for sala in salas:
            estancias = mongo.db.stays.distinct('uuid', {"room_name" : sala , "start_date":{'$gte' : datetime.datetime.fromisoformat(day), '$lt' : datetime.datetime.fromisoformat(day2)}})
            if len(estancias) > max_estancias:
                max_estancias = len(estancias)
                sala_def=sala
        
        return jsonify({'message' : "La sala más usada fue "+ sala_def + " con " + str(max_estancias) + " estancias."})
    else:
        response = jsonify({'message' : "No enviaste un identificador o fecha válidos" })
        return response
#Más usada en cada hora
@app.route('/stays/room/most_used_per_hour', methods = ['POST'])
def history_room_most_used_perHour():
    if 'day' in request.json:
        ##Conversiones temporales necesarias para poder hacer la comprobacion
        day_aux =  str(request.json['day'])
        day_a = datetime.datetime.strptime(day_aux, '%Y-%m-%d').date()
        
        day = datetime.datetime.combine(day_a, datetime.datetime.min.time()).replace(tzinfo=datetime.timezone.utc).isoformat()
        
        salas_str = ['Comedor', 'HF', 'Bar']
        salas = {'Comedor':0,'HF':0,'Bar':0}
        horas = {'Comedor':0, 'HF':0, 'Bar' : 0}
        horas2 = {'Comedor':0, 'HF':0, 'Bar' : 0}
        #Se comprueba la ocupación en cada sala para cada hora para saber cuál es la ocupación máxima y en qué hora se ha producido la misma.
        for sala in salas_str:
            i = 1
            while i <= 24:
                
                day_aux = datetime.datetime.combine(day_a, datetime.datetime.min.time())  + datetime.timedelta(hours = i-1)
                day_aux2 = day_aux.replace(tzinfo=datetime.timezone.utc)
                day = day_aux2.isoformat()
                day2_aux = datetime.datetime.combine(day_a, datetime.datetime.min.time())  + datetime.timedelta(hours = i)
                day2_aux2 = day2_aux.replace(tzinfo=datetime.timezone.utc)
                day2 = day2_aux2.isoformat()
                estancias = mongo.db.stays.distinct('uuid', {"room_name" : sala , "start_date":{'$gte' : datetime.datetime.fromisoformat(day), '$lt' : datetime.datetime.fromisoformat(day2)}})
                if len(estancias) > salas.get(sala):
                    salas[sala] = len(estancias)
                    horas[sala] = day_aux2.astimezone(ZoneInfo("Europe/Madrid")).hour
                    horas2[sala] = day2_aux2.astimezone(ZoneInfo("Europe/Madrid")).hour
                i = i + 1


        cadena = ""
        for sala in salas_str:
            if salas[sala] > 0:
                cadena = cadena + sala + " - " + str(salas[sala]) + " personas - " + str(horas[sala]) + "-" +str(horas2[sala])+". "
            else:
                cadena = cadena + " No ha habido nadie en " + sala +". "

        return jsonify({'message' : "Esta fue la hora con mayor número de personas para cada sala:"+ cadena})
    else:
        response = jsonify({'message' : "No enviaste un identificador o fecha válidos" })
        return response

#Ocupación actual de cada sala
@app.route('/stays/room/occupation', methods = ['POST'])
def get_occupation():
        
        start_dateAux = datetime.datetime.today().replace(microsecond=0)
        dt = start_dateAux.replace(tzinfo=ZoneInfo("Europe/Madrid"))
        dt2 = dt - datetime.timedelta(seconds = 10) + datetime.timedelta(hours = 2)
        dt2.replace(tzinfo=ZoneInfo("Europe/Madrid"))
        dt2 = dt2.astimezone(datetime.timezone.utc)
        dtDef2 = dt2.isoformat()

        salas_str = ['Comedor', 'HF', 'Bar']
        message = {}
        for sala in salas_str:
            #Estancias abiertas y cerradas en los últimos 10 segundos
            estancias = mongo.db.stays.distinct('uuid',{"$or":[{"room_name":sala, "end_date": {"$exists":False}}, {"room_name":sala, "end_date":{'$gte': datetime.datetime.fromisoformat(dtDef2)}}] })
            message[sala] = str(len(estancias))
        return jsonify({'message' : message})


@app.route('/stays/open', methods = ['GET'])
def get_open():
        #Estancias abiertas y cerradas en los últimos 10 segundos
        estancias = mongo.db.stays.find({"end_date": {"$exists":False}})
        message = json_util.dumps(estancias)

        return Response(message, mimetype='application/json')

#Dadas la sala y el día obtener el aforo de cada hora
@app.route('/stays/room/occupation_by_hour', methods = ['POST'])
def history_room_occupation_perHour():
    if 'day' in request.json and 'room_name' in request.json:
        ##Conversiones temporales necesarias para poder hacer la comprobacion
        sala = str(request.json['room_name'])
        day_aux =  str(request.json['day'])
        day_a = datetime.datetime.strptime(day_aux, '%Y-%m-%d').date()
        
        ##Se comprueba la ocupación de la sala para cada hora para saber cuál es la ocupación en cada hora.
        i = 1
        message = {}
        while i <= 24:

            ##Primera hora de búsqueda en su corresponediente utc para poder realizar bien los filtro en la base de datos
            day_aux = datetime.datetime.combine(day_a, datetime.datetime.min.time())  + datetime.timedelta(hours = i-1)
            day_aux2 = day_aux.replace(tzinfo=ZoneInfo("Europe/Madrid"))
            day_aux2 = day_aux2.astimezone(datetime.timezone.utc)
            day = day_aux2.isoformat()

            ##Segunda hora de búsqueda en su correspondiente utc para filtrar los datos entre ambas fechas
            day2_aux = datetime.datetime.combine(day_a, datetime.datetime.min.time())  + datetime.timedelta(hours = i)
            day2_aux2 = day2_aux.replace(tzinfo=ZoneInfo("Europe/Madrid"))
            day2_aux2 = day2_aux2.astimezone(datetime.timezone.utc)
            day2 = day2_aux2.isoformat()

            dtDef2 = day_aux2.astimezone(ZoneInfo("Europe/Madrid"))

            estancias = mongo.db.stays.distinct('uuid', {"room_name" : sala , "start_date":{'$gte' : datetime.datetime.fromisoformat(day), '$lt' : datetime.datetime.fromisoformat(day2)}})
            if(dtDef2.hour < 10 ):
                    hora = "0" + str(dtDef2.hour) + ":" + "0" + str(dtDef2.minute)
                    message[hora] = str(len(estancias)) 
            else:
                    hora =  str(dtDef2.hour) + ":" + "0" + str(dtDef2.minute)
                    message[hora] = str(len(estancias)) 

            i = i + 1


        return jsonify({'message' : message})
    else:
        response = jsonify({'message' : "No enviaste un día o habitación válidos" })
        return response

#Dadas la sala y el día obtener que uuid han estado en cada hora
@app.route('/stays/room/getByRoomAndDay', methods = ['POST'])
def history_room_stays_perHour():
    if 'day' in request.json and 'room_name':
        ##Conversiones temporales necesarias para poder hacer la comprobacion
        sala = str(request.json['room_name'])
        day_aux =  str(request.json['day'])
        day_a = datetime.datetime.strptime(day_aux, '%Y-%m-%d').date()
        
        ##Se comprueba la ocupación de la sala para cada hora para saber cuál es la ocupación en cada hora.
        dct ={}
        i = 1
        while i <= 24:

            ##Primera hora de búsqueda en su corresponediente utc para poder realizar bien los filtro en la base de datos
            day_aux = datetime.datetime.combine(day_a, datetime.datetime.min.time())  + datetime.timedelta(hours = i-1)
            day_aux2 = day_aux.replace(tzinfo=ZoneInfo("Europe/Madrid"))
            day_aux2 = day_aux2.astimezone(datetime.timezone.utc)
            day = day_aux2.isoformat()

            ##Segunda hora de búsqueda en su correspondiente utc para filtrar los datos entre ambas fechas
            day2_aux = datetime.datetime.combine(day_a, datetime.datetime.min.time())  + datetime.timedelta(hours = i)
            day2_aux2 = day2_aux.replace(tzinfo=ZoneInfo("Europe/Madrid"))
            day2_aux2 = day2_aux2.astimezone(datetime.timezone.utc)
            day2 = day2_aux2.isoformat()

            dtDef2 = day_aux2.astimezone(ZoneInfo("Europe/Madrid"))

            estancias = mongo.db.stays.distinct('uuid', {"room_name" : sala , "start_date":{'$gte' : datetime.datetime.fromisoformat(day), '$lt' : datetime.datetime.fromisoformat(day2)}})
            "Poner bien la hora"
            if dtDef2.hour<10:
                hour = "0" + str(dtDef2.hour)
            else:
                hour = str(dtDef2.hour)

            i = i + 1
            dct[hour] = json_util.dumps(estancias)
         
        return jsonify({"message" : dct })
    else:
        response = jsonify({'message' : "No enviaste un día o habitación válidos" })
        return response

##Media de personas por día
@app.route('/stays/mean', methods = ['POST'])
def mean():
    if 'day' in request.json and 'room_name' in request.json:
        sala = str(request.json['room_name'])
        day_aux =  str(request.json['day'])
        day_a = datetime.datetime.strptime(day_aux, '%Y-%m-%d').date()
        contador = 0
        suma = 0
        i = 1
        while i <= 24:

            ##Primera hora de búsqueda en su corresponediente utc para poder realizar bien los filtro en la base de datos
            day_aux = datetime.datetime.combine(day_a, datetime.datetime.min.time())  + datetime.timedelta(hours = i-1)
            day_aux2 = day_aux.replace(tzinfo=ZoneInfo("Europe/Madrid"))
            day_aux2 = day_aux2.astimezone(datetime.timezone.utc)
            day = day_aux2.isoformat()

            ##Segunda hora de búsqueda en su correspondiente utc para filtrar los datos entre ambas fechas
            day2_aux = datetime.datetime.combine(day_a, datetime.datetime.min.time())  + datetime.timedelta(hours = i)
            day2_aux2 = day2_aux.replace(tzinfo=ZoneInfo("Europe/Madrid"))
            day2_aux2 = day2_aux2.astimezone(datetime.timezone.utc)
            day2 = day2_aux2.isoformat()

            estancias = mongo.db.stays.distinct('uuid', {"room_name" : sala , "start_date":{'$gte' : datetime.datetime.fromisoformat(day), '$lt' : datetime.datetime.fromisoformat(day2)}})
            if len(estancias) > 0:
                contador = contador +1
                suma = suma + len(estancias)
            i = i + 1
        if(contador == 0):
            return jsonify({'message' : "0" })
        else:
            return jsonify({'message' : str(suma/contador)})
   
    else:
        response = jsonify({'message' : "No enviaste un día o habitación válidos" })
        return response

#Cerrado de las estancias
@app.route('/stays/close', methods = ['POST'])
def debug():
    start_dateAux = datetime.datetime.today().replace(microsecond=0)
    dt = start_dateAux.replace(tzinfo=ZoneInfo("Europe/Madrid"))
    dtDef = dt.astimezone(datetime.timezone.utc).isoformat()
       
    mongo.db.stays.update_many({'end_date' :{"$exists":False}},
                                            {'$set':{'end_date': datetime.datetime.fromisoformat(dtDef) }})
    return jsonify({'message' : "Se han cerrado satisfactoriamente todas las entradas"})



#Módulo de usuarios

#Creación de usuarios, ya sean anónimos o no
#Necesita al menos la mac_address, y para usuarios con cuenta el username password y email
@app.route('/users', methods =['POST'] )
def create_users():
    #Recibiendo datos
    #Creación de usuarios completos
    if 'uuid' in request.json and 'username' in request.json and 'password' in request.json and 'email' in request.json:
        uuid = str(request.json['uuid'])
        username = str(request.json['username'])
        password = str(request.json['password'])
        email = str(request.json['email'])
        enc_password = generate_password_hash(password)
        #Comprobar que no se repita alguno de los campos que son únicos
        try:
            ##Si existe ya una cuenta anónima se modifica para que sea una cuenta normal
            user = mongo.db.users.find_one({'uuid' : uuid})
            if user and user['type'] == 'Anonymous':
                id = mongo.db.users.update_one({'uuid' : uuid},{'$set':{'type':'User', 'uuid':uuid, 'username':username, 'password': enc_password, 'email':email}})
                response = jsonify({'message' : 'Usuario con id ' + str(id) + ' modificado satisfactoriamente'})
                return response
            else:
                id = mongo.db.users.insert_one({'uuid' : uuid,'type':'User','username' : username, 'password' : enc_password, 'email' : email})
                response = jsonify({'message' : 'Usuario con id ' + str(id) + ' creado satisfactoriamente'})
                return response

        #Si alguno de los campos únicos está repetido identificar cual es y sacar el error correspondiente
        except pymongo.errors.DuplicateKeyError as error:

            field_aux = error.details['keyValue'].keys()
            field = list(field_aux)[0]
            if(field == "username"):
                response = jsonify({'message': 'Se ha producido un error. Ya existe un usuario con nombre de usuario ' + username,
        'status' : 500 })

            elif(field == "uuid"):

                response = jsonify({'message': 'Se ha producido un error. Ya existe un usuario asociado a ese dispositivo',
        'status' : 500 })
            else:
                response = jsonify({'message': 'Se ha producido un error. Ya existe un usuario con email ' + email,
        'status' : 500 })

            response.status_code=500
            return response

    #Creación de usuarios anónimos
    elif 'uuid' in request.json:
        uuid = str(request.json['uuid'])
        id = mongo.db.users.insert_one({'uuid' : str(uuid),'type':'Anonymous'})
        response = jsonify({'message' : 'Dispositivo con id: ' + str(id) + ' creado satisfactoriamente'})
        return response
    
    else:
        return invalid()
    
##Login para usuarios con cuenta   
@app.route('/login', methods = ["POST"])
def login():
    if ('username' in request.json and 'password' in request.json):
        username = request.json['username']
        password = request.json['password']
        user = mongo.db.users.find_one({'username':username})     
        user_psw = user['password']
        print(user)
        if check_password_hash(user_psw,password):
            token = jwt.encode({'user': username, 'exp' : str(datetime.datetime.utcnow() + datetime.timedelta(minutes = 30))}, app.config['SECRET_KEY'])
            print(token)
            return jsonify({'token' : token})

        return make_response('could not verify!', 401,{'WWW-Authenticate' : 'Basic realm = "Login required"'})
    
##Login para usuarios anónimos
@app.route('/login/anonymous', methods = ["POST"])
def login_anonymous():
    if ('uuid' in request.json):
        uuid = request.json['uuid']
        user = mongo.db.users.find_one({'uuid':uuid})     
        if user:
            token = jwt.encode({'uuid': uuid, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes = 30)}, app.config['SECRET_KEY'])
            return jsonify({'token' : token})
        else:
            mongo.db.users.insert_one({'uuid' : uuid,'type':'Anonymous'})
            token = jwt.encode({'uuid': uuid, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes = 30)}, app.config['SECRET_KEY'])
            return jsonify({'token' : token, 'message' : "Además se ha creado un usuario anónimo para este dispositivo"})
    else:
        return jsonify({'message': "Debes enviar tu identificador"})
        
@app.route('/users', methods=['GET'])
def list_users():
    users = mongo.db.users.find()
    response = json_util.dumps(users)
    #Lo de abajo indica que la repuesta es un archivo json
    return Response(response, mimetype='application/json')

@app.route('/users/<id>', methods = ['GET'])
def get_users(id):
    user = mongo.db.users.find_one({'_id' : ObjectId(id)})
    #Se convierte en un json
    response = json_util.dumps(user)
    return Response(response,mimetype = "application/json")

@app.route('/users/device/<uuid>', methods = ['GET'])
def get_users_by_device_id(uuid):
    user = mongo.db.users.find_one({'uuid' : uuid})
    #Se convierte en un json
    response = json_util.dumps(user)
    return Response(response,mimetype = "application/json")

@app.route('/users/username/<id>', methods = ['GET'])
def get_users_by_username_id(id):
    user = mongo.db.users.find_one({'username' : id})
    #Se convierte en un json
    response = json_util.dumps(user)
    return Response(response,mimetype = "application/json")

@app.route('/users/<id>', methods = ['DELETE'])
def delete_devices(id):
    mongo.db.users.delete_one({'_id' : ObjectId(id)})
    response = jsonify({'message' : 'El usuario con el id ' + id + ' fue eliminado satisfactoriamente'})
    return response

@app.errorhandler(404)
def not_found(error = None):
    response = jsonify({
        'message' : 'Resource not found: ' + request.url,
        'status' : 404 
    })
    response.status_code=404
    return response

@app.errorhandler(400)
def invalid(error = None):
    response = jsonify({
        'message' : 'Resource not found: ' + request.url,
        'status' : 400
    })
    response.status_code=400
    return response

if __name__ == "__main__":
    create_app(False)
    

  

