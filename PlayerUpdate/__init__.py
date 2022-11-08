import logging
import os
import json

import azure.functions as func
import azure.cosmos as cosmos
import azure.cosmos.errors as errors

# check attributes are ints


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Updating User')

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
    add_gp = req_body.get('add_to_games_played')
    add_score = req_body.get('add_to_score')

    if not username:
        return func.HttpResponse(status_code=400, body="Username is required")
    if not password:
        return func.HttpResponse(status_code=400, body="Password is required")
    if not add_gp and not add_score:
        return func.HttpResponse(status_code=400, body="No fields to update")
    if add_gp and not isinstance(add_gp, int):
        return func.HttpResponse(status_code=400, body="Games played must be an integer")
    if add_score and not isinstance(add_score, int):
        return func.HttpResponse(status_code=400, body="Score must be an integer")
    if add_gp and add_gp <= 0:
        logging.info("Games played must be positive")
        resp = {
            "result": False,
            "msg": "Value to add is <=0"
        }
        return func.HttpResponse(status_code=400, body=json.dumps(resp))
    if add_score and add_score <= 0:
        logging.info("Score must be positive")
        resp = {
            "result": False,
            "msg": "Value to add is <=0"
        }
        return func.HttpResponse(status_code=400, body=json.dumps(resp))

    client = cosmos.CosmosClient.from_connection_string(
        os.environ['CDB_CONNECTION_STRING'])

    database = client.get_database_client("cw1")

    players_container = database.get_container_client("players")

    try:
        user = players_container.read_item(
            item=username, partition_key=username)
    except errors.CosmosResourceNotFoundError:
        resp = {
            "result": False,
            "msg": "user does not exist"
        }
        return func.HttpResponse(status_code=400, body=json.dumps(resp))

    if user['password'] != password:
        resp = {
            "result": False,
            "msg": "wrong password"
        }
        return func.HttpResponse(status_code=400, body=json.dumps(resp))

    if add_gp:
        user['games_played'] += add_gp
    if add_score:
        user['total_score'] += add_score

    players_container.upsert_item(user)

    resp = {
        "result": True,
        "msg": "OK"
    }
    return func.HttpResponse(status_code=200, body=json.dumps(resp))
