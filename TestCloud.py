import unittest, wrapper ,random, string, logging, dotenv

APP_KEY=dotenv.get_key('.env','APP_KEY')

LOCAL_SERVER=dotenv.get_key('.env','LOCAL_SERVER')
#Replace below as appropriate
CLOUD_SERVER=dotenv.get_key('.env','CLOUD_SERVER')

is_local = False
#TEST SETS
registered_players = []
added_prompts = []


def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    return (''.join(random.choice(letters) for i in range(length)))

class TestCloud(unittest.TestCase):
    def testa1_player_register(self):
        logging.info("Test 1: Registering a player with a valid username and password")

        #valid inputs
        valid_lower = {"username": get_random_string(4), "password": get_random_string(8)}
        valid_upper = {"username": get_random_string(16), "password": get_random_string(24)}
        
        valid_inputs = [valid_lower, valid_upper]
        #invalid inputs
        invalid_lower = {"username": get_random_string(4), "password": get_random_string(7)}
        invalid_upper = {"username": get_random_string(16), "password": get_random_string(25)}
        invalid_lower2 = {"username": get_random_string(3), "password": get_random_string(8)}
        invalid_upper2 = {"username": get_random_string(17), "password": get_random_string(24)}
       
        invalid_u_inputs = [invalid_lower2, invalid_upper2]
        invalid_p_inputs = [invalid_lower, invalid_upper]
        
        for input in valid_inputs:
            logging.info("Testing with valid input: " + str(input))
            response = wrapper.player_register((input), local=is_local)
            logging.info("Response: " + str(response))
            correct_response = {"result": True, "msg": "OK"}
            self.assertEqual(response, correct_response)
            registered_players.append(input)
            
        for input in invalid_u_inputs:
            logging.info("Testing with invalid input: " + str(input))
            response = wrapper.player_register(input, local=is_local)
            logging.info("Response: " + str(response))
            correct_response = {"result": False, "msg": "Username less than 4 characters or more than 16 characters"}
            self.assertEqual(response, correct_response)
            
        for input in invalid_p_inputs:
            logging.info("Testing with invalid input: " + str(input))
            response = wrapper.player_register(input, local=is_local)
            logging.info("Response: " + str(response))
            correct_response = {"result": False, "msg": "Password less than 8 characters or more than 24 characters"}
            self.assertEqual(response, correct_response)
            
        logging.info("Testing already registered user...")
        response = wrapper.player_register(valid_lower, local=is_local)
        logging.info("Response: " + str(response))
        correct_response = {"result": False, "msg": "Username already exists"}
        self.assertEquals(response, correct_response)
            
        
        
    def testb2_player_login(self):
        logging.info("Test 2: Logging in a player with a valid username and password")
        
        invalid_lower = {"username": get_random_string(4), "password": get_random_string(7)}
        invalid_upper = {"username": get_random_string(16), "password": get_random_string(25)}
        invalid_lower2 = {"username": get_random_string(3), "password": get_random_string(8)}
        invalid_upper2 = {"username": get_random_string(17), "password": get_random_string(24)}
       
        invalid_inputs = [invalid_lower2, invalid_upper2, invalid_lower, invalid_upper]
        
        for player in registered_players:
            logging.info("Testing with valid input: " + str(player))
            response = wrapper.player_login(player, local=is_local)
            logging.info("Response: " + str(response))
            correct_response = {"result": True, "msg": "OK"}
            self.assertEqual(response, correct_response)
            
        for input in invalid_inputs:
            logging.info("Testing with invalid input: " + str(input))
            response = wrapper.player_login(input, local=is_local)
            logging.info("Response: " + str(response))
            correct_response = {"result": False, "msg": "Username or password incorrect"}
            self.assertEqual(response, correct_response)
    
    def testc3_player_update(self):
        logging.info("Test 3: Updating a player's password")
        
        invalid_user = {"username": get_random_string(4), "password": get_random_string(7), "add_to_score": 1}
        
        invalid_password = {"username": registered_players[0]["username"], "password": get_random_string(7), "add_to_score": 1}
        
        #Test with valid inputs
        for player in registered_players:
            player = {"username": player["username"], "password": player["password"], "add_to_score": 1}
            logging.info("Testing with valid input: " + str(player))
            response = wrapper.player_update(player, local=is_local)
            logging.info("Response: " + str(response))
            correct_response = {"result": True, "msg": "OK"}
            self.assertEqual(response, correct_response)
            
        #Test with invalid username
        logging.info("Testing with invalid username: " + str(invalid_user))
        response = wrapper.player_update(invalid_user, local=is_local)
        logging.info("Response: " + str(response))
        correct_response = {"result": False, "msg": "user does not exist"}
        self.assertEqual(response, correct_response)
        
        #Test with invalid password
        logging.info("Testing with invalid password: " + str(invalid_password))
        response = wrapper.player_update(invalid_password, local=is_local)
        logging.info("Response: " + str(response))
        correct_response = {"result": False, "msg": "wrong password"}
        self.assertEqual(response, correct_response)
        
        #Test with invalid score
        player = registered_players[0].copy()
        player["add_to_score"] = 0
        logging.info("Testing with invalid score: " + str(player))
        logging.info("original player: " + str(registered_players[0]))
        response = wrapper.player_update(player, local=is_local)
        logging.info("Response: " + str(response))
        correct_response = {"result": False, "msg": "Value to add is <=0"}
        self.assertEqual(response, correct_response)
        
        #Test with invalid games played
        player = registered_players[0].copy()
        player["add_to_games_played"] = 0
        logging.info("Testing with invalid games played: " + str(player))
        response = wrapper.player_update(player, local=is_local)
        logging.info("Response: " + str(response))
        correct_response = {"result": False, "msg": "Value to add is <=0"}
        self.assertEqual(response, correct_response)
        
    def testd4_player_leaderboard(self):
        logging.info("Test 4: Getting the leaderboard")
        high_player = registered_players[0].copy()
        high_player["add_to_score"] = 1000
        response = wrapper.player_update(high_player, local=is_local)
        logging.info("Response: " + str(response))
        correct_response = {"result": True, "msg": "OK"}
        self.assertEqual(response, correct_response)
        
        req = {"top" : 2}
        logging.info("Testing with valid input: " + str(req))
        response = wrapper.player_leaderboard(req, local=is_local)
        logging.info("Response: " + str(response))
        #check response is a list
        self.assertEqual(isinstance(response, list), True)
        #check response is of length 2
        self.assertEqual(len(response), 2)
        #check response is sorted
        self.assertEqual(response[0]["score"] >= response[1]["score"], True)
        
        req = {"top" : 1}
        response = wrapper.player_leaderboard(req, local=is_local)
        logging.info("Response: " + str(response))
        #check response is a list
        self.assertEqual(isinstance(response, list), True)
        #check response is of length 2
        self.assertEqual(len(response), 1)
            
    def teste5_prompt_create(self):
        player = registered_players[0].copy()
        player2 = registered_players[1].copy()
        prompt_lower = {"username": player["username"], "password": player["password"],"text": get_random_string(20)}
        prompt_upper = {"username": player["username"], "password": player["password"], "text": get_random_string(100)}
        prompt_lower2 = {"username": player2["username"], "password": player2["password"], "text": get_random_string(20)}
        promt_upper2 = {"username": player2["username"], "password": player2["password"], "text": get_random_string(100)}
        
        valid_prompts = [prompt_lower, prompt_upper, prompt_lower2, promt_upper2]
        
        invalid_prompt_lower = {"username": player["username"], "password": player["password"], "text": get_random_string(19)}
        invalid_prompt_higher = {"username": player["username"], "password": player["password"], "text": get_random_string(101)}
        
        invalid_prompts = [invalid_prompt_lower, invalid_prompt_higher]
        
        bad_username = {"username": get_random_string(4), "password": player["password"], "text": get_random_string(20)}
        bad_password = {"username": player["username"], "password": get_random_string(7), "text": get_random_string(20)}
        
        bad_credentials = [bad_username, bad_password]
        
        for prompt in valid_prompts:
            logging.info("Testing with valid input: " + str(prompt))
            response = wrapper.prompt_create(prompt, local=is_local)
            logging.info("Response: " + str(response))
            correct_response = {"result": True, "msg": "OK"}
            self.assertEqual(response, correct_response)
            # added_prompts.append(prompt)
        
        for prompt in invalid_prompts:
            logging.info("Testing with invalid input: " + str(prompt))
            response = wrapper.prompt_create(prompt, local=is_local)
            logging.info("Response: " + str(response))
            correct_response = {"result": False, "msg": "prompt length is <20 or > 100 characters"}
            self.assertEqual(response, correct_response)
        
        for prompt in bad_credentials:
            logging.info("Testing with invalid credentials: " + str(prompt))
            response = wrapper.prompt_create(prompt, local=is_local)
            logging.info("Response: " + str(response))
            correct_response = {"result": False, "msg": "bad username or password"}
            self.assertEqual(response, correct_response)
        
        for prompt in valid_prompts:
            logging.info("Testing with duplicate prompt: " + str(prompt))
            response = wrapper.prompt_create(prompt, local=is_local)
            logging.info("Response: " + str(response))
            correct_response = {"result": False, "msg": "This user already has a prompt with the same text"}
            self.assertEqual(response, correct_response)
        
    def testf6_prompt_get(self):
        logging.info("Test 6: Getting a prompt")
        req = {"prompts": 2}
        responses = []
        for i in range(5):
            response = wrapper.prompts_get(req, local=is_local)
            logging.info("Response: " + str(response))
            responses.append(response)
            #correct_response = {"result": True, "msg": "OK"}
            # self.assertEqual(response, correct_response)
            #check response is a list
            self.assertEqual(isinstance(response, list), True)
        
        logging.info("Testing out is random")
        is_random = False
        for response in responses:
            if response[0]["text"] != responses[1][0]["text"]:
                is_random = True
                break
        self.assertEqual(is_random, True)
        
        #add prompts to added_prompts
        req = {"prompts": 1000}
        response = wrapper.prompts_get(req, local=is_local)
        logging.info("Response: " + str(response))
        responses.append(response)
        # correct_response = {"result": True, "msg": "OK"}
        # self.assertEqual(response, correct_response)
        for prompt in response:
            added_prompts.append(prompt)
        
        #test username get
        player = added_prompts[0]["username"]
        req = {"players": [player]}
        response = wrapper.prompts_get(req, local=is_local)
        #check response is a list
        self.assertEqual(isinstance(response, list), True)
        for prompt in response:
            self.assertEqual(prompt["username"], player)
            
    def testg7_prompts_edit(self):
        player = registered_players[0].copy()
        prompt = None
        
        for p in added_prompts:
            logging.info("player: " + str(player) + " prompt: " + str(p))
            if p["username"] == player["username"]:
                prompt = p
                break
        if prompt is None:
            self.fail("Prompt not found")
        text = get_random_string(20)
        
        #valid request
        logging.info("Testing with valid input")
        req = {"id": prompt["id"], "username": player["username"], "password": player["password"], "text": str(text)}
        response = wrapper.prompt_edit(req, local=is_local)
        correct_response = {"result": True, "msg": "OK"}
        self.assertEqual(response, correct_response)
        
        #invalid id
        logging.info("Testing with invalid id")
        req = {"id": int(prompt["id"]) + 1, "username": player["username"], "password": player["password"], "text": get_random_string(20)}
        response = wrapper.prompt_edit(req, local=is_local)
        correct_response = {"result": False, "msg": "prompt id does not exist"}
        self.assertEqual(response, correct_response)
        
        #invalid username
        logging.info("Testing with invalid username")
        req = {"id": prompt["id"], "username": get_random_string(4), "password": player["password"], "text": get_random_string(20)}
        response = wrapper.prompt_edit(req, local=is_local)
        correct_response = {"result": False, "msg": "bad username or password"}
        self.assertEqual(response, correct_response)
        
        #invalid password
        logging.info("Testing with invalid password")
        req = {"id": prompt["id"], "username": player["username"], "password": get_random_string(8), "text": get_random_string(20)}
        response = wrapper.prompt_edit(req, local=is_local)
        correct_response = {"result": False, "msg": "bad username or password"}
        self.assertEqual(response, correct_response)
        
        #invalid text
        logging.info("Testing with invalid text")
        req = {"id": prompt["id"], "username": player["username"], "password": player["password"], "text": get_random_string(19)}
        response = wrapper.prompt_edit(req, local=is_local)
        correct_response = {"result": False, "msg": "prompt length is <20 or >100 characters"}
        self.assertEqual(response, correct_response)
        
        #invalid text
        logging.info("Testing with invalid text")
        req = {"id": prompt["id"], "username": player["username"], "password": player["password"], "text": get_random_string(101)}
        response = wrapper.prompt_edit(req, local=is_local)
        correct_response = {"result": False, "msg": "prompt length is <20 or >100 characters"}
        self.assertEqual(response, correct_response)
        
        ################################################
        ################### FIX THIS ###################
        ################################################
        
        # duplicate prompt
        logging.info("Testing with duplicate prompt")
        logging.info("prompt: " + str(prompt["text"]) + " text: " + str(text))
        req = {"id": prompt["id"], "username": player["username"], "password": player["password"], "text": str(text)}
        response = wrapper.prompt_edit(req, local=is_local)
        req = {"id": prompt["id"], "username": player["username"], "password": player["password"], "text": str(text)}
        response = wrapper.prompt_edit(req, local=is_local)
        correct_response = {"result": False, "msg": "This user already has a prompt with the same text"}
        self.assertEqual(response, correct_response)
        
        #test if prompt text changed
        req = {"players": [player["username"]]}
        response = wrapper.prompts_get(req, local=is_local)
        not_changed = True
        for prompt in response:
            if prompt["text"] == text:
                not_changed = False
                break
        self.assertEqual(not_changed, False)

        
    def testh8_prompt_delete(self):
        player = registered_players[0].copy()
        prompt = None
        
        for p in added_prompts:
            logging.info("player: " + str(player) + " prompt: " + str(p))
            if p["username"] == player["username"]:
                prompt = p
                break
        if prompt is None:
            self.fail("Prompt not found")
        
        #access denied
        player = registered_players[1].copy()
        req = {"id": prompt["id"], "username": player["username"], "password": player["password"]}
        response = wrapper.prompt_delete(req, local=is_local)
        correct_response = {"result": False, "msg": "access denied"}
        self.assertEqual(response, correct_response)
        
        player = registered_players[0].copy()
        #valid request
        logging.info("Testing with valid input")
        req = {"id": prompt["id"], "username": player["username"], "password": player["password"]}
        response = wrapper.prompt_delete(req, local=is_local)
        correct_response = {"result": True, "msg": "OK"}
        self.assertEqual(response, correct_response)
        
        #repeat to check its deleted
        logging.info("Testing with invalid repeated input")
        req = {"id": prompt["id"], "username": player["username"], "password": player["password"]}
        response = wrapper.prompt_delete(req, local=is_local)
        correct_response = {"result": False, "msg": "prompt id does not exist"}
        self.assertEqual(response, correct_response)
        
        #invalid id
        logging.info("Testing with invalid id")
        req = {"id": int(prompt["id"]) + 1, "username": player["username"], "password": player["password"]}
        response = wrapper.prompt_delete(req, local=is_local)
        correct_response = {"result": False, "msg": "prompt id does not exist"}
        self.assertEqual(response, correct_response)
        
        #invalid username
        logging.info("Testing with invalid username")
        req = {"id": prompt["id"], "username": get_random_string(6), "password": player["password"]}
        response = wrapper.prompt_delete(req, local=is_local)
        correct_response = {"result": False, "msg": "bad username or password"}
        self.assertEqual(response, correct_response)
        
        #invalid password
        logging.info("Testing with invalid password")
        req = {"id": prompt["id"], "username": player["username"], "password": get_random_string(8)}
        response = wrapper.prompt_delete(req, local=is_local)
        correct_response = {"result": False, "msg": "bad username or password"}
        self.assertEqual(response, correct_response)
        
    def testi9_prompt_getText(self):
        word = get_random_string(10)
        capitalised_word = word.capitalize()
        texts = [capitalised_word + " is a test prompt text", 
                 word + " is a test prompt text", 
                 word + ", is a test prompt text", 
                 "?" + capitalised_word + ", is a test prompt text"]
        
        player = registered_players[0].copy()
        
        #Add test prompts
        for text in texts:
            req = {"username": player["username"], "password": player["password"], "text": text}
            response = wrapper.prompt_create(req, local=is_local)
            correct_response = {"result": True, "msg": "OK"}
            self.assertEqual(response, correct_response)
            
        #Test if all prompts are returned
        req = {"word": word, "exact": False}
        response = wrapper.prompts_getText(req, local=is_local)
        #check is list
        self.assertEqual(isinstance(response, list), True)
        #check if all prompts are returned
        self.assertEqual(len(response), len(texts))
        #check user is correct
        for prompt in response:
            self.assertEqual(prompt["username"], player["username"])
            
        #Test if all prompts are returned
        req = {"word": capitalised_word, "exact": False}
        response = wrapper.prompts_getText(req, local=is_local)
        #check is list
        self.assertEqual(isinstance(response, list), True)
        #check if all prompts are returned
        self.assertEqual(len(response), len(texts))
        
        #Test case sensitivity
        req = {"word": word, "exact": True}
        response = wrapper.prompts_getText(req, local=is_local)
        #check is list
        self.assertEqual(isinstance(response, list), True)
        #check if all prompts are returned
        self.assertEqual(len(response), 2)
        
        req = {"word": capitalised_word, "exact": True}
        response = wrapper.prompts_getText(req, local=is_local)
        #check is list
        self.assertEqual(isinstance(response, list), True)
        #check if all prompts are returned
        self.assertEqual(len(response), 2)
        
        
        
        
        
def run_tests():
    logging.basicConfig(level=logging.DEBUG)
    unittest.TestLoader.sortTestMethodsUsing = None
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCloud)
    unittest.TextTestRunner(verbosity=2).run(suite)
    

        