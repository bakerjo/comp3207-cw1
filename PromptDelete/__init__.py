import logging
import os
import json

import azure.functions as func
import azure.cosmos as cosmos
import azure.cosmos.errors as errors


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Delete Prompt')

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
    id = str(req_body.get('id'))
    username = req_body.get('username')
    password = req_body.get('password')

    # check body contains all required fields
    if username == None:
        logging.info("No username")
        return func.HttpResponse(status_code=400, body="Username is required")
    if password == None:
        logging.info("No password")
        return func.HttpResponse(status_code=400, body="Password is required")
    if id == None:
        logging.info("No id")
        return func.HttpResponse(status_code=400, body="Id is required")

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

    # check password
    if user['password'] != password:
        logging.info("Password incorrect")
        resp = {
            "result": False,
            "msg": "bad username or password"
        }
        return func.HttpResponse(status_code=400, body=json.dumps(resp))

    prompts_container = database.get_container_client("prompts")

    prompt = None
    # get prompt
    try:
        prompt = prompts_container.read_item(
            item=id, partition_key=id)
    except errors.CosmosResourceNotFoundError:
        logging.info(0)
        resp = {
            "result": False,
            "msg": "prompt id does not exist"
        }
        return func.HttpResponse(status_code=400, body=json.dumps(resp))

    if prompt['username'] != username:
        resp = {
            "result": False,
            "msg": "access denied"
        }
        return func.HttpResponse(status_code=400, body=json.dumps(resp))

    try:
        logging.info("Deleting prompt")
        prompts_container.delete_item(
            item=id,
            partition_key=id
        )
        resp = {
            "result": True,
            "msg": "OK"
        }
        return func.HttpResponse(status_code=200, body=json.dumps(resp))
    except errors.CosmosResourceNotFoundError:
        logging.info("Prompt not found")
        resp = {
            "result": False,
            "msg": "This prompt does not exist"
        }
        return func.HttpResponse(status_code=400, body=json.dumps(resp))
    except:
        logging.info("Error deleting prompt")
        return func.HttpResponse(status_code=500, body="Error deleting prompt")
