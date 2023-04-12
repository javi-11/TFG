
import datetime
from flask import Flask, request, jsonify, Response, make_response
from flask_pymongo import PyMongo 
from bson import json_util
from bson.objectid import ObjectId
import pymongo
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from functools import wraps

app = Flask(__name__)

app.config["SECRET_KEY"] = "a"
app.config["MONGO_URI"] = "mongodb+srv://javit:<f6dFZDZsA4M0rTz8>@cluster0.ejgdxfg.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient("mongodb+srv://javit:f6dFZDZsA4M0rTz8@cluster0.ejgdxfg.mongodb.net/?retryWrites=true&w=majority",server_api=ServerApi('1'))

mongo = client.test


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

#Esto será para la creación de habitaciones
'''
@app.route('/rooms', methods =['POST'] )
def create_room():

    #Recibiendo datos

    if 'name' in request.json:
        name = request.json['name']
        id = mongo.db.rooms.insert_one({'name' : name})
        response = {
            'id' : str(id),
            'name' : name
        } 

        return response

    else:
        return not_found()

@app.route('/rooms', methods=['GET'])
def list_rooms():
    users = mongo.db.rooms.find()
    response = json_util.dumps(users)
    #Lo de abajo indica que la repuesta es un archivo json
    return Response(response, mimetype='application/json')

@app.route('/rooms/<id>', methods = ['GET'])
def get_room(id):
    room = mongo.db.rooms.find_one({'_id' : ObjectId(id)})
    #Se convierte en un json
    response = json_util.dumps(room)
    return Response(response,mimetype = "application/json")

@app.route('/rooms/<id>', methods = ['DELETE'])
def delete_room(id):
    mongo.db.rooms.delete_one({'_id' : ObjectId(id)})
    response = jsonify({'message' : 'La habitación con el id ' + id + ' fue eliminada satisfactoriamente'})
    return response

@app.route('/rooms/<id>', methods = ['PUT'])
def update_rooms(id):
    if 'name' in request.json:
        name = request.json['name']
        mongo.db.rooms.update_one({'_id' : ObjectId(id)}, {'$set':{'name': name}})

        response = jsonify({'message' : 'Habitación' + id + 'modificada satisfactoriamente'})


        return response

    else:
        return not_found() 
'''


#Módulo de Estancias
#Necesita el room_name y el user_id para funcionar
@app.route('/stays', methods =['POST'] )
def create_stay():

    #Recibiendo como datos room_name y user_id

    if 'room_name' in request.json and 'uuid' in request.json:
        room_name = str(request.json['room_name'])
        user_id = str(request.json['uuid'])
        if(room_name == "HF"):
            alt_name = "Bar"
        else:
            alt_name = "HF"
        
        start_date = datetime.datetime.today().replace(microsecond=0)
        if mongo.db.stays.find_one({'user_id' : user_id, 'room_name': room_name, "end_date":{"$exists":False}}):
            response = jsonify({'message' : "Ya existe una estancia sin cerrar para esa habitación"})
        elif mongo.db.stays.find_one({'room_name': alt_name, "end_date":{"$exists":False}}):
            response = jsonify({'message' : "No hay problema, las regiones se superponen"})
        else:
            id = mongo.db.stays.insert_one({'room_name' : room_name, 'user_id' : user_id, 'start_date': start_date})
            response = jsonify({'message' : 'Estancia con id: ' + str(id) + ' creada satisfactoriamente'})

        return response

    else:
        return not_found()

@app.route('/stays', methods=['GET'])
def list_stays():
    stays = mongo.db.stays.find()
    response = json_util.dumps(stays)
    #Lo de abajo indica que la repuesta es un archivo json
    return Response(response, mimetype='application/json')

@app.route('/stays', methods =['PUT'] )
def update_stay():
    #Con tener un user_id el sistema se encargará de actualizar la estancia de por si solo
    end_date = datetime.datetime.today().replace(microsecond=0)
    if 'room_name' in request.json and 'uuid' in request.json:
        room_name = str(request.json['room_name'])
        user_id = str(request.json['uuid'])
        if mongo.db.stays.find_one({'user_id' : user_id,'room_name': room_name, "end_date":{"$exists":False}}):
            id = mongo.db.stays.update_many({'user_id' : user_id, 'end_date' :{"$exists":False}},
                                            {'$set':{'end_date': end_date}})
            response = jsonify({'message' : 'Estancia con id: ' + str(id) + ' modificada satisfactoriamente'})
            return response
        else:
            response = jsonify({'message' : "Ya hay una estancia creada sin cerrar"})
            return response
    else:
        return not_found()

@app.route('/stays/<id>', methods=['DELETE'])
def delete_stay(id):
    mongo.db.stays.delete_one({'_id':ObjectId(id)})
    response = jsonify({'message' : 'La estancia con el id ' + id + ' fue eliminada satisfactoriamente'})
    return response

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
                response = jsonify({'message' : 'Usuario con id ' + str(id) + ' creado satisfactoriamente'})
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
        return not_found()
    
##Login para usuarios con cuenta   
@app.route('/login', methods = ["POST"])
def login():
    if ('username' in request.json and 'password' in request.json):
        username = request.json['username']
        password = request.json['password']
        user = mongo.db.users.find_one({'username':username})     
        user_psw = user['password']
        if check_password_hash(user_psw,password):
            token = jwt.encode({'user': username, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes = 30)}, app.config['SECRET_KEY'])
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
            return jsonify({'token' : token})
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



if __name__ == "__main__":
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
    with app.app_context():
        mongo.db.users.create_index('uuid', unique = True)
        mongo.db.users.create_index(("username"), unique = True, sparse = True)
        mongo.db.users.create_index(("email"), unique = True, sparse = True) 
    app.run(debug = True)

  