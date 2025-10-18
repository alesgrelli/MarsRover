"""Small test runner for the rover Flask app using Flask's test_client.

This avoids network issues and posts directly to the app object.
"""
import json
from rover import app

TESTS = [
    {
        "name": "basic obstacle hit",
        "payload": {
            "grid": {"width": 5, "height": 5},
            "start": {"x": 0, "y": 0, "dir": "E"},
            "obstacles": [{"x": 2, "y": 0}],
            "commands": "fff",
        },
    },
    {
        "name": "unknown commands ignored",
        "payload": {
            "grid": {"width": 5, "height": 5},
            "start": {"x": 0, "y": 0, "dir": "E"},
            "obstacles": [{"x": 2, "y": 0}],
            "commands": "fabc",
        },
    },
    {
        "name": "wrap around",
        "payload": {
            "grid": {"width": 5, "height": 5},
            "start": {"x": 4, "y": 0, "dir": "E"},
            "obstacles": [],
            "commands": "f",
        },
    },
]

if __name__ == "__main__":
    with app.test_client() as client:
        for t in TESTS:
            print(f"--- {t['name']} ---")
            resp = client.post("/api/v1/rover/command", json=t["payload"]) 
            try:
                data = resp.get_json()
            except Exception:
                data = {"error": "invalid json", "status_code": resp.status_code}
            print(json.dumps(data, indent=2))
            print()
