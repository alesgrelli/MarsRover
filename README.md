# Mars Rover Exercise

This small Flask app simulates a rover moving on a finite grid. The API accepts a JSON payload describing the grid, the rover's starting position and direction, obstacles, and a sequence of commands. The rover executes commands until the sequence finishes or it encounters an obstacle.

Features
- Move forward/backward: `f`, `b`
- Turn left/right: `l`, `r`
- Grid wrapping (edges wrap to the opposite side)
- Obstacle detection: when a move would land on an obstacle the rover stops and reports it
- Input validation with helpful error responses

Files
- `rover.py` - Flask app implementing the API
- `test_post.py` - test runner using Flask's test client to exercise happy path and error cases

Run the app
1. (Optional) create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1    # PowerShell; may be blocked by execution policy
# or use cmd.exe:
.venv\Scripts\activate.bat
```

2. Install dependencies (Flask):

```powershell
pip install Flask
```

3. Start the server:

```powershell
python rover.py
```

The server will listen on http://127.0.0.1:5000 by default.

API
- Health

  GET /health

  Response: {"status": "ok"}

- Rover command

  POST /api/v1/rover/command

  Request JSON shape (example):

  ```json
  {
    "grid": { "width": 5, "height": 5 },
    "start": { "x": 1, "y": 1, "dir": "N" },
    "obstacles": [],
    "commands": "ffrff"
  }
  ```

  Successful response example:

  ```json
  {
    "position": { "x": 0, "y": 0, "dir": "N" },
    "hit_obstacle": false,
    "obstacle_at": null,
    "processed_commands": 5,
    "remaining_commands": ""
  }
  ```

Examples
- curl (Linux/macOS or curl.exe on Windows):

```bash
curl -s -X POST http://127.0.0.1:5000/api/v1/rover/command \
  -H "Content-Type: application/json" \
  -d '{"grid":{"width":5,"height":5},"start":{"x":0,"y":0,"dir":"E"},"obstacles":[{"x":2,"y":0}],"commands":"fff"}'
```

- PowerShell (Invoke-RestMethod):

```powershell
$body = @{
  grid = @{ width = 5; height = 5 }
  start = @{ x = 0; y = 0; dir = 'E' }
  obstacles = @(@{ x = 2; y = 0 })
  commands = 'fff'
} | ConvertTo-Json -Depth 4

Invoke-RestMethod -Uri http://127.0.0.1:5000/api/v1/rover/command -Method Post -Body $body -ContentType 'application/json'
```

Testing
- Run the included test runner which posts several payloads directly to the Flask app (no network required):

```powershell
python test_post.py
```

This will print the responses for happy path and several error cases (malformed JSON, missing fields, invalid types, wrong HTTP method).

Notes
- PowerShell may block activating virtualenv scripts depending on your execution policy. If activation is blocked, either run the activation from an admin PowerShell and set a less restrictive policy (e.g., `Set-ExecutionPolicy RemoteSigned`) or use cmd.exe to activate the venv.
- The Flask server in this repo runs in debug mode by default. Do not use the development server in production.

If you want, I can:
- Add a `requirements.txt` with pinned versions
- Convert `test_post.py` to `pytest` tests and add a test runner
- Normalize error response shapes and update tests to assert exact messages

Enjoy! 

