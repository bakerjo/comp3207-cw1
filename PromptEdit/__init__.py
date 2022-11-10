import logging
import os
import json

import azure.functions as func
import azure.cosmos as cosmos
import azure.cosmos.errors as errors
import uuid


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Edit Prompt')

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
    id = req_body.get('id')
    username = req_body.get('username')
    password = req_body.get('password')
    text = req_body.get('text')


    #check body contains all required fields
    if username == None:
        logging.info("No username")
        return func.HttpResponse(status_code=400, body="Username is required")
    if password == None:
        logging.info("No password")
        return func.HttpResponse(status_code=400, body="Password is required")
    if text == None:
        logging.info("No text")
        return func.HttpResponse(status_code=400, body="Text is required")
    if id == None:
        logging.info("No id")
        return func.HttpResponse(status_code=400, body="Id is required")
    
    # check text length
    if len(text) < 20 or len(text) > 100:
        resp = {
            "result": False,
            "msg": "prompt length is <20 or >100 characters"
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
        logging.info("User not found")
        resp = {
            "result": False,
            "msg": "bad username or password"
        }
        return func.HttpResponse(status_code=400, body=json.dumps(resp))


    #check password
    if user['password'] != password:
        logging.info("Password incorrect")
        resp = {
            "result": False,
            "msg": "bad username or password"
        }
        return func.HttpResponse(status_code=400, body=json.dumps(resp))
    
    prompts_container = database.get_container_client("prompts")
    
    try:
        prompt = prompts_container.read_item(item=str(id), partition_key=str(id))
        # prompt = list(prompts_container.query_items(
        #     "SELECT * FROM c WHERE c.id = @id",
        #     parameters=[dict(name="@id", value=id)],
        #     enable_cross_partition_query=True
        # ))[0]
    except Exception as e:
        logging.info("Prompt not found: " + str(e))
        resp = {
            "result": False,
            "msg" : "prompt id does not exist"
        }
        return func.HttpResponse(status_code=400, body=json.dumps(resp))
    
    
    logging.info("Prompt: " + str(prompt))
    # resp = {
    #     "result": True,
    #     "msg": "OK"
    # }
    # return func.HttpResponse(status_code=200, body=json.dumps(resp))
    
    
    #get users prompts
    user_prompts = prompts_container.query_items(
        query="SELECT c.text FROM c WHERE c.username = @username",
        parameters=[
            { "name":"@username", "value":username }
        ],
        enable_cross_partition_query=True
    )
    
    for user_prompt in user_prompts:
        if user_prompt['text'] == text:
            resp = {
                "result": False,
                "msg": "This user already has a prompt with the same text"
            }
            return func.HttpResponse(status_code=400, body=json.dumps(resp))
    
    new_prompt = {
        "id" : str(id),
        "username": str(username),
        "text": str(text)
    }
    
    try:
        prompts_container.upsert_item(body=new_prompt)
        resp = {
            "result": True,
            "msg": "OK"
        }
        return func.HttpResponse(status_code=200, body=json.dumps(resp))
    except Exception as e:
        logging.error("Error updating prompt: " + str(e))
        resp = {
            "result": False,
            "msg": "Error updating prompt"
        }
        return func.HttpResponse(status_code=500, body=json.dumps(resp))
        
        
    
    
    