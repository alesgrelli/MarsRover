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
    {
        "name": "malformed json",
        "raw_body": "{not: valid json}",
        "content_type": "application/json",
        "expect_status": 400,
    },
    {
        "name": "missing commands field",
        "payload": {
            "grid": {"width": 5, "height": 5},
            "start": {"x": 0, "y": 0, "dir": "E"},
            "obstacles": [],
        },
        "expect_error_contains": "Missing 'commands'",
    },
    {
        "name": "commands wrong type",
        "payload": {
            "grid": {"width": 5, "height": 5},
            "start": {"x": 0, "y": 0, "dir": "E"},
            "obstacles": [],
            "commands": ["f", "f"],
        },
        "expect_error_contains": "'commands' must be a string",
    },
    {
        "name": "obstacles wrong type",
        "payload": {
            "grid": {"width": 5, "height": 5},
            "start": {"x": 0, "y": 0, "dir": "E"},
            "obstacles": {"x": 2, "y": 0},
            "commands": "f",
        },
        "expect_error_contains": "'obstacles' must be a list",
    },
    {
        "name": "wrong http method",
        "method": "GET",
        "expect_status": 405,
    },
    {
        "name": "large commands string",
        "payload": {
            "grid": {"width": 50, "height": 50},
            "start": {"x": 0, "y": 0, "dir": "N"},
            "obstacles": [],
            "commands": "f" * 1000,
        },
    },
]

if __name__ == "__main__":
    with app.test_client() as client:
        for t in TESTS:
            name = t["name"]
            print(f"--- {name} ---")

            method = t.get("method", "POST")

            # Raw body (malformed JSON) test
            if "raw_body" in t:
                resp = client.open("/api/v1/rover/command", method=method, data=t["raw_body"], content_type=t.get("content_type", "application/json"))
            else:
                if method == "POST":
                    resp = client.post("/api/v1/rover/command", json=t.get("payload"))
                else:
                    resp = client.open("/api/v1/rover/command", method=method)

            status = resp.status_code
            # Try to decode JSON body
            try:
                body = resp.get_json()
            except Exception:
                body = None

            expected_status = t.get("expect_status")
            if expected_status is not None:
                print(f"status: {status} (expected {expected_status})")
            else:
                print(f"status: {status}")

            if body is not None:
                print(json.dumps(body, indent=2))
            else:
                print("<no-json-response>")

            # Check expected error substrings when provided
            expect_err = t.get("expect_error_contains")
            if expect_err and body:
                ok = expect_err in (body.get("error") or str(body))
                print("expect_error_contains:", expect_err, "->", "OK" if ok else "MISSING")

            print()
