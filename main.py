# Shabak Challenge
# Prequesites - Solve the nonogram puzzles and write down the solution

# Process - for each api request you will get jwt token that will contain the cursor current location
# You need to move the cursor by sending new jwt token with an instruction code (Up, Down, Left etc...)
# in response you will get the new cursor position and so on.

# Target - Make the cursor go over all the points that are part of the solution. if you will step on a non-solution point you will start over...

import random
import requests
import jwt

# Puzzles are NxN size.
# Solution puzzle is #3 so we will use it
puzzle_size = {
    0: 0,
    1: 3,
    2: 11,
    3: 25,
    4: 13,
    5: 21
}

# Direction codes for next step cursor
direction_map = {
    'u': '2337',
    'd': '147',
    'r': '1337',
    'l': '1937',
    'lu': '21817',
    'ru': '1437',
    'rd': '147'
}

# Solution for #3 Nonogram
pzl3_solution_lst = "9,10,11,12,13,14,15,34,33,32,40,41,42,43,35,36,37,38,39,66,67,68,69,94,95,120,121,146,147,172,197,173,198,223,224,423,398,373,348,323,298,273,248,249,274,299,324,349,374,399,424,448,447,473,472,497,496,521,520,546,545,544,569,568,567,593,592,591,616,608,609,610,611,612,613,614,615,583,584,585,586,587,588,589,590,582,581,558,557,556,555,532,533,530,529,504,503,478,477,452,451,426,401,400,225,250,275,300,325,350,375,226,251,276,301,326,351,376,201,176,151,152,127,128,103,57,56,55,80,79,59,84,109,134,159,184,209,234,259,284,309,334,359,384,409,385,360,335,310,285,260,235,210,185,160,135,110,85,60,63,88,113,138,163,188,213,238,263,288,313,338,363,388,413,437,438,463,64,89,114,139,164,189,214,239,264,289,314,339,364,389,414,82,107,132,157,182,207,232,257,282,307,81,106,131,156,181,206,231,256,281,306,331,356,104,129,154,179,204,229,254,153,178,203,228,253,278,177,277,377,378,379,402,427,302,330,355,354,353,453,454,455,456,457,462,408,433,432,431,479,480,487,486,485,511,510,509,535,534".split(
    ",")

# Save places that the cursur already stepped at
chosen_lst = []

# Puzzle to solve
puzzle_number = 3

# Challenge API url
url = 'http://puzzle.shieldchallenges.com'

current_token = ''

# Request opening token

response = requests.get(url + '/api/token', json={
    "username": "Test_User",
    "password": "SecretPassw0rd",
    "puzzle_id": puzzle_number
})
json_response = response.json()

if 'token' in json_response:
    current_token = json_response['token']
    jwt_decode = jwt.decode(json_response['token'], options={
                            "verify_signature": False})
    print(jwt_decode)

# Available moves for each step
available_moves = []

# Must send this instruction to start
current_instruction = '1337'

# Helping with not checking already checked position
last_cursor = -1

while True:
    if current_instruction in direction_map:
        ins = direction_map[current_instruction]
    else:
        ins = '1337'
    while len(ins) < 6:
        ins = '0' + ins

    headers = {"Authorization": "Bearer " + current_token}
    response = requests.patch(
        url + f'/api/puzzle/{puzzle_number}', json={"instructions": ins}, headers=headers)
    json_response = response.json()

    if 'token' in json_response:
        jwt_decode = jwt.decode(json_response['token'], options={
                                "verify_signature": False})
        state = jwt_decode['state']
        final_str = ''
        for idx, s in enumerate(state):
            final_str += s
            if (idx + 1) % puzzle_size[puzzle_number] == 0:
                final_str += '\n'
        cursor = jwt_decode['cursor']
        if str(cursor) not in pzl3_solution_lst:
            print('The position we started at is not valid, run again...')
            break
        chosen_lst.append(cursor)
        print(str(final_str))
        print(f'cursor: {cursor}')

        # Find what options available for next step
        available_moves = []
        available_priority = []

        if cursor % puzzle_size[puzzle_number] != 0 and str(cursor - 1) in pzl3_solution_lst:
            available_moves.append('l')
            if cursor - 1 not in chosen_lst and cursor - 1 != last_cursor:
                available_priority.append('l')
        if ((cursor + 1) % puzzle_size[puzzle_number] != 0) and (str(cursor + 1) in pzl3_solution_lst):
            available_moves.append('r')
            if cursor + 1 not in chosen_lst and cursor + 1 != last_cursor:
                available_priority.append('r')
        if str(cursor + puzzle_size[puzzle_number]) in pzl3_solution_lst:
            available_moves.append('d')
            if cursor + puzzle_size[puzzle_number] not in chosen_lst and cursor + puzzle_size[
                    puzzle_number] != last_cursor:
                available_priority.append('d')
        if str(cursor - puzzle_size[puzzle_number]) in pzl3_solution_lst:
            available_moves.append('u')
            if cursor - puzzle_size[puzzle_number] not in chosen_lst and cursor - puzzle_size[
                    puzzle_number] != last_cursor:
                available_priority.append('u')
        current_instruction = random.choice(
            available_priority if available_priority else available_moves)
        print(f'Available moves: {available_moves}')
        current_token = json_response['token']
        last_cursor = cursor
    elif 'flag' in json_response:
        print(json_response)
        input('Well Done...')
        break
