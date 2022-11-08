import logging
import os
import json

import azure.functions as func
import azure.cosmos as cosmos
import azure.cosmos.errors as errors


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Getting leaderboard')

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
    top = req_body.get('top')

    if not top:
        return func.HttpResponse(status_code=400, body="Top is required")
    
    if not isinstance(top, int):
        return func.HttpResponse(status_code=400, body="Top must be an integer")
    
    if top <= 0:
        logging.info("Top must be positive")
        resp = {
            "result": False,
            "msg": "Value to add is <=0"
        }
        return func.HttpResponse(status_code=400, body=json.dumps(resp))
    
    client = cosmos.CosmosClient.from_connection_string(
        os.environ['CDB_CONNECTION_STRING'])

    database = client.get_database_client("cw1")

    players_container = database.get_container_client("players")
    
    #get top players by score
    top_players = players_container.query_items(
        query="SELECT TOP @top c.id, c.total_score, c.games_played FROM c ORDER BY c.total_score DESC",
        parameters=[
            { "name":"@top", "value": top }
        ],
        enable_cross_partition_query=True
    )
    
    logging.info("Returning top players")
    
    return func.HttpResponse(status_code=200, body=json.dumps(list(top_players)))
    
    
