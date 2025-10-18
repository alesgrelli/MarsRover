"""rover.py - simple Flask API simulating a rover on a grid

This module provides a small API to simulate a rover moving on a grid.

Requirements summary:
 - Given an initial starting point (x, y) and a facing direction (N, S, E, W).
 - The rover receives a sequence of commands (characters).
 - Commands: move forward/backward (f, b), turn left/right (l, r).
 - Grid wrapping: moving off one edge appears on the opposite edge.
 - Obstacle detection: if a move would land on an obstacle, stop processing
     further commands and report the obstacle position.
"""

from flask import Flask, request, jsonify

app = Flask(__name__)

#the rover will be able to move in four directions: North, East, South, West.
#Each step in one of those directions will correspond to a change in position that can be represented as (dx, dy) pairs.
# North and East will be a +1, South and West will be a -1

directions = ["N", "E", "S", "W"]
move_delta = {
    "N": (0, 1),
    "E": (1, 0),
    "S": (0, -1),
    "W": (-1, 0)
}

##let's start by checking possibile errors in the input data
def validate_input(data):

    # Returns (True, None) if valid, or (False, error_message) if invalid.

    # Check that the 'commands' field exists
    if "commands" not in data:
        return False, "Missing 'commands' field."

    commands = data["commands"]
    if not isinstance(commands, str):
        return False, "'commands' must be a string."
    
    # Check the validity of commands
    valid_cmds = set("fblr")
    invalid = [c for c in commands if c.lower() not in valid_cmds]
    if invalid:
        return False, f"Invalid command(s): {invalid}. Allowed: f, b, l, r."

    # Check start direction
    start = data.get("start", {})
    direction = start.get("dir", "N")
    if direction not in ["N", "E", "S", "W"]:
        return False, f"Invalid start direction '{direction}'. Must be one of: N, E, S, W."

    # Check grid dimensions
    grid = data.get("grid", {})
    if "width" in grid and (not isinstance(grid["width"], int) or grid["width"] <= 0):
        return False, "'grid.width' must be a positive integer."
    if "height" in grid and (not isinstance(grid["height"], int) or grid["height"] <= 0):
        return False, "'grid.height' must be a positive integer."

    # Check obstacles
    obstacles = data.get("obstacles", [])
    if not isinstance(obstacles, list):
        return False, "'obstacles' must be a list."
    for o in obstacles:
        if not all(k in o for k in ("x", "y")):
            return False, f"Obstacle {o} missing x or y."
        if not isinstance(o["x"], int) or not isinstance(o["y"], int):
            return False, f"Obstacle coordinates must be integers. Got: {o}"

    return True, None



#now let's define the POST method of the API.
#in this post method we'll need to pass the grid dimentions, starting position and direction of the rover, list of obstacles and commands to execute.
@app.route("/api/v1/rover/command", methods=["POST"])
def move_rover():
    #let's retrieve here the body in json format
    data = request.get_json()

    #Let's first check the validity of the input data
    
    valid, error = validate_input(data)
    if not valid:
        return jsonify({"error": error}), 400

    #let's assign the values from the json to variables
    #if a field is missing we set a default value
    grid = data.get("grid", {"width": 10, "height": 10})
    start = data.get("start", {"x": 0, "y": 0, "dir": "N"})
    obstacles = data.get("obstacles", [])
    commands = data.get("commands", "")

    #let's upack further the variables, we need the dimensions of the grid and the starting position and direction of the rover
    width = grid.get("width", 10)
    height = grid.get("height", 10)

    x = start.get("x", 0)
    y = start.get("y", 0)
    direction = start.get("dir", "N")

    #let's transform the list of obstacles into a set of tuples (x, y), so we can quickly check if there's an obstacle in a position
    obstacle_set = {(o["x"], o["y"]) for o in obstacles}

    # Variables to keep track of any obstacles and the number of commands executed (I want to know how many commands were processed before hitting an obstacle)
    hit_obstacle = False
    obstacle_at = None
    processed = 0

    #now let's loop through the commands received
    for c in commands:
        if c == "l":  #left command
            idx = directions.index(direction)  #let's find the index of the current direction, the list is ["N", "E", "S", "W"]
            direction = directions[(idx - 1) % 4]  #go to the previous direction (we move counter_clockwise)
        elif c == "r":  #right command
            idx = directions.index(direction)
            direction = directions[(idx + 1) % 4]  #go to the next direction (we move clockwise)
        elif c in ["f", "b"]:  #if the command is "f" (forward) or "b" (backward)
            dx, dy = move_delta[direction]  #get the movement vector from the current direction
            if c == "b":  #if it's backward, reverse the movement (if it was North (0,1) it becomes South (0,-1))
                dx, dy = -dx, -dy

            # Calculate the new position (with wrapping since we are on a sphere)
            new_x = (x + dx) % width
            new_y = (y + dy) % height

            # Check if there's an obstacle in the new position
            if (new_x, new_y) in obstacle_set:
                hit_obstacle = True             # Report that we hit an obstacle
                obstacle_at = {"x": new_x, "y": new_y}  # Save where it is
                break                           # Stop processing commands
            else:
                # no obstacle, move the rover
                x, y = new_x, new_y

        processed += 1  # Increment the number of processed commands

    # now we have all the data to build the result to return
    result = {
        "position": {"x": x, "y": y, "dir": direction},      # Final position and direction of the rover
        "hit_obstacle": hit_obstacle,                        # True if we hit an obstacle
        "obstacle_at": obstacle_at,                          # Coordinates of the obstacle (if it exists)
        "processed_commands": processed,                     # Number of commands executed
        "remaining_commands": commands[processed:]           # Commands that were not executed (if any)
    }

    # Returns the response in JSON format
    return jsonify(result)


# Simple endpoint to check if the server is alive
@app.route("/health", methods=["GET"])
def health():
    return {"status": "ok"}


# Start the Flask server if we are running this file directly
if __name__ == "__main__":
    app.run(debug=True)  # debug=True allows us to see errors and automatically reload the server

