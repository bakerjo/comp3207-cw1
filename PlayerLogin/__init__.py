import logging
import os
import json

import azure.functions as func
import azure.cosmos as cosmos
import azure.cosmos.errors as errors


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Logging in User')

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

    client = cosmos.CosmosClient.from_connection_string(
        os.environ['CDB_CONNECTION_STRING'])

    database = client.get_database_client("cw1")

    players_container = database.get_container_client("players")

    user = players_container.query_items(
        query="SELECT * FROM c WHERE c.id = @username",
        parameters=[
            dict(name="@username", value=username)
        ],
        enable_cross_partition_query=True
    )

    for u in user:
        if u['password'] == password:
            logging.info('User logged in')
            resp = {
                "result": True,
                "msg": "OK"
            }
            return func.HttpResponse(status_code=200, body=json.dumps(resp))
        else:
            logging.info('Password is incorrect')
            break

    resp = {
        "result": False,
        "msg": "Username or password incorrect"
    }
    return func.HttpResponse(status_code=400, body=json.dumps(resp))
