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
import error_handling

app = Flask(__name__)
error_handling.register_error_handlers(app)

# Direzioni e vettori di movimento
directions = ["N", "E", "S", "W"]
move_delta = {
    "N": (0, 1),
    "E": (1, 0),
    "S": (0, -1),
    "W": (-1, 0)
}


def validate_input_or_raise(data):
    """
    Validate incoming JSON; raises ValidationError on any problem.
    """
    if data is None:
        raise error_handling.ValidationError("Missing JSON body")

    # commands
    if "commands" not in data:
        raise error_handling.ValidationError("Missing 'commands' field.")
    commands = data["commands"]
    if not isinstance(commands, str):
        raise error_handling.ValidationError("'commands' must be a string.")
    valid_cmds = set("fblr")
    invalid = [c for c in commands if c.lower() not in valid_cmds]
    if invalid:
        # mostra i caratteri non validi trovati
        raise error_handling.ValidationError(f"Invalid command(s): {invalid}. Allowed: f, b, l, r.", details={"invalid_commands": invalid})

    # start.dir
    start = data.get("start", {})
    direction = start.get("dir", "N")
    if direction not in directions:
        raise error_handling.ValidationError(f"Invalid start direction '{direction}'. Must be one of: {directions}.")

    # grid dimensions
    grid = data.get("grid", {})
    if "width" in grid and (not isinstance(grid["width"], int) or grid["width"] <= 0):
        raise error_handling.ValidationError("'grid.width' must be a positive integer.")
    if "height" in grid and (not isinstance(grid["height"], int) or grid["height"] <= 0):
        raise error_handling.ValidationError("'grid.height' must be a positive integer.")

    # obstacles
    obstacles = data.get("obstacles", [])
    if not isinstance(obstacles, list):
        raise error_handling.ValidationError("'obstacles' must be a list.")
    for o in obstacles:
        if not isinstance(o, dict) or not all(k in o for k in ("x", "y")):
            raise error_handling.ValidationError(f"Obstacle {o} missing x or y.", details={"obstacle": o})
        if not isinstance(o["x"], int) or not isinstance(o["y"], int):
            raise error_handling.ValidationError(f"Obstacle coordinates must be integers. Got: {o}", details={"obstacle": o})

    # tutto ok
    return True


@app.route("/api/v1/rover/command", methods=["POST"])
def rover_command():
    # parse JSON (Flask lancerà BadRequest se JSON malformato)
    data = request.get_json()

    # validazione (lancia ValidationError in caso di problemi)
    validate_input_or_raise(data)

    # --- unpack dati (sicuro ora che sono validi) ---
    grid = data.get("grid", {"width": 10, "height": 10})
    start = data.get("start", {"x": 0, "y": 0, "dir": "N"})
    obstacles = data.get("obstacles", [])
    commands = data.get("commands", "")

    width = grid.get("width", 10)
    height = grid.get("height", 10)

    x = start.get("x", 0)
    y = start.get("y", 0)
    direction = start.get("dir", "N")

    obstacle_set = {(o["x"], o["y"]) for o in obstacles}

    hit_obstacle = False
    obstacle_at = None
    processed = 0

    for c in commands:
        if c == "l":
            idx = directions.index(direction)
            direction = directions[(idx - 1) % 4]
        elif c == "r":
            idx = directions.index(direction)
            direction = directions[(idx + 1) % 4]
        elif c in ["f", "b"]:
            dx, dy = move_delta[direction]
            if c == "b":
                dx, dy = -dx, -dy

            new_x = (x + dx) % width
            new_y = (y + dy) % height

            if (new_x, new_y) in obstacle_set:
                # Opzione A (consigliata se vuoi mantenere la risposta che riporta la posizione
                # e i comandi rimanenti): fermati e ritorna il risultato (come facevi prima).
                hit_obstacle = True
                obstacle_at = {"x": new_x, "y": new_y}
                break

                # Opzione B (alternativa): sollevare un'eccezione che verrà gestita dagli error handlers.
                # Se preferisci usare questa opzione, commenta il blocco sopra e decommenta la riga sotto.
                # raise error_handling.ObstacleError("Obstacle encountered", obstacle={"x": new_x, "y": new_y})

            else:
                x, y = new_x, new_y

        processed += 1

    result = {
        "position": {"x": x, "y": y, "dir": direction},
        "hit_obstacle": hit_obstacle,
        "obstacle_at": obstacle_at,
        "processed_commands": processed,
        "remaining_commands": commands[processed:]
    }

    return jsonify(result)


@app.route("/health", methods=["GET"])
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(debug=True)
