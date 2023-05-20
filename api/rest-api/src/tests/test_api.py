
import requests
import json


def post_json(client, url, json_dict):
    """Send dictionary json_dict as a json to the specified url """
    return client.post(url, data=json.dumps(json_dict), content_type='application/json')

def json_of_response(response):
    """Decode json from response"""
    return json.loads(response.data.decode('utf8'))


def test_create_stay(client):
    response = post_json(client,"/stays",{'room_name':'HF','uuid':'1'})
    message = json_of_response(response).get("message")
    assert response.status_code == 200
    assert "Estancia con id: " in message

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
    print(json_of_response(rsp))
    assert len(json_of_response(rsp)) == 1
    
#def test_update_stays(client):