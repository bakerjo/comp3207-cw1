import logging
import os
import json
import re

import azure.functions as func
import azure.cosmos as cosmos
import azure.cosmos.errors as errors


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Get Text Prompt')

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
    word = req_body.get('word')
    exact = req_body.get('exact')

    # check body contains all required fields
    if word == None:
        logging.info("No word")
        return func.HttpResponse(status_code=400, body="Word is required")
    if exact == None:
        logging.info("No exact")
        return func.HttpResponse(status_code=400, body="Exact is required")
    if not isinstance(exact, bool):
        logging.info("Exact is not a boolean")
        return func.HttpResponse(status_code=400, body="Exact is not a boolean")
    
    client = cosmos.CosmosClient.from_connection_string(
        os.environ['CDB_CONNECTION_STRING'])

    database = client.get_database_client("cw1")
    
    prompts_container = database.get_container_client("prompts")
    
    #get prompts that text contains word
    prompts = list(prompts_container.query_items(
        "SELECT c.id, c.text, c.username FROM c WHERE CONTAINS(LOWER(c.text), @word)",
        parameters=[
            { "name": "@word", "value": str.lower(word) }
        ],
        enable_cross_partition_query=True
    ))
    
    #if exact is true, only return prompts that text is equal to word
    # if exact:
    #     prompts = [prompt for prompt in prompts if word in prompt['text']]
    
    returned_prompts = []
    
    for prompt in prompts:
        if not exact:
            prompt['text'] = str.lower(prompt['text'])
            word = str.lower(word)
            
        logging.info(1)
        words = re.split('[,.!? +\'"\[\]\{\}\(\)]',  prompt['text'])
        logging.info(words)
        
        if word in words:
            returned_prompts.append(prompt)
    
    #return the prompts
    return func.HttpResponse(json.dumps(returned_prompts))
    
