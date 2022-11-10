import logging
import os
import json

import azure.functions as func
import azure.cosmos as cosmos
import azure.cosmos.errors as errors


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Registering User')

    # check if the request is a POST
    if not req.method == 'POST':
        return func.HttpResponse(status_code=405)

    # get the request body
    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse(status_code=400)

    # {"username" : "py_luis", "password": "pythonrulz" , "games_played" : 542 , "total_score" : 3744   }

    # check if the request body has the required fields
    username = req_body.get('username')
    password = req_body.get('password')

    if username == None:
        return func.HttpResponse(status_code=400, body="Username is required")
    if password == None:
        return func.HttpResponse(status_code=400, body="Password is required")

    # check username length
    if len(username) < 4 or len(username) > 16:
        resp = {
            "result": False,
            "msg": "Username less than 4 characters or more than 16 characters"
        }
        return func.HttpResponse(status_code=400, body=json.dumps(resp))

    # check password length
    if len(password) < 8 or len(password) > 24:
        resp = {
            "result": False,
            "msg": "Password less than 8 characters or more than 24 characters"
        }
        return func.HttpResponse(status_code=400, body=json.dumps(resp))

    client = cosmos.CosmosClient.from_connection_string(
        os.environ['CDB_CONNECTION_STRING'])

    database = client.get_database_client("cw1")

    players_container = database.get_container_client("players")

    user = {
        "id": username,
        "username" : username,
        "password": password,
        "games_played": 0,
        "total_score": 0
    }

    try:
        players_container.create_item(user)
        resp = {
            "result": True,
            "msg": "OK"
        }
        return func.HttpResponse(status_code=200, body=json.dumps(resp))
    except errors.CosmosResourceExistsError:
        resp = {
            "result": False,
            "msg": "Username already exists"
        }
        return func.HttpResponse(status_code=400, body=json.dumps(resp))
    except errors.CosmosHttpResponseError:
        return func.HttpResponse(status_code=500, body="Internal server error")
    except Exception as e:
        return func.HttpResponse(status_code=500, body="Internal server error")

    
