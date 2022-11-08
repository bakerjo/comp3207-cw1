import logging
import os
import json
import random

import azure.functions as func
import azure.cosmos as cosmos
import azure.cosmos.errors as errors


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Get Prompt')

    # check if the request is a POST
    if not req.method == 'POST':
        return func.HttpResponse(status_code=405)

    # get the request body
    try:
        req_body = req.get_json()
    except ValueError:
        logging.info("No body")
        return func.HttpResponse(status_code=400, body="No body")

    # check if the request body has the required fields
    n_prompts = req_body.get('prompts')
    players = req_body.get('players')
    
    
    # check body contains all required fields
    if (n_prompts == None) == (players == None):
        logging.info("No prompts or players")
        return func.HttpResponse(status_code=400, body="Just prompts or players required")
    
    # check prompts is an int
    if n_prompts and not isinstance(n_prompts, int):
        logging.info("prompts is not an int")
        return func.HttpResponse(status_code=400, body="Prompts must be an int")
    
    # check players is a list
    if players and not isinstance(players, list):
        logging.info("players is not a list")
        return func.HttpResponse(status_code=400, body="Players must be a list")

    client = cosmos.CosmosClient.from_connection_string(
        os.environ['CDB_CONNECTION_STRING'])

    database = client.get_database_client("cw1")

    players_container = database.get_container_client("players")
    
    prompts_container = database.get_container_client("prompts")
    
    returned_prompts = []
    
    if n_prompts:
        # get all prompts
        all_prompts = list(prompts_container.query_items(
            "SELECT c.id, c.text, c.username FROM c",
            enable_cross_partition_query=True
        ))
        logging.info(10)
        random.shuffle(all_prompts)
        logging.info(11)
        for (i, prompt) in enumerate(all_prompts):
            logging.info(12)
            if i >= n_prompts:
                break
            returned_prompts.append(prompt)
        
    if players:
        for player in players:
            # get all prompts for player
            player_prompts = list(prompts_container.query_items(
                query="SELECT c.id, c.text, c.username FROM c WHERE c.username = @username",
                parameters=[
                    { "name":"@username", "value": player }
                ],
                enable_cross_partition_query=True
            ))
            for (i, prompt) in enumerate(player_prompts):
                returned_prompts.append(prompt)
    
    return func.HttpResponse(status_code=200, body=json.dumps(returned_prompts))