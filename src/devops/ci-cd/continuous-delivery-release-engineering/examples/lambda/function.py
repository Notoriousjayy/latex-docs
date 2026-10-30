"""Demonstration Lambda handler with no network, AWS writes, or side effects."""
import json
import os


def handler(event, context):
    path = event.get("rawPath", "/") if isinstance(event, dict) else "/"
    if path == "/health" or path == "/":
        return {"statusCode": 200, "headers": {"content-type": "application/json"},
                "body": json.dumps({"status": "ok", "revision": os.getenv("APP_REVISION", "demo")},
                                   sort_keys=True)}
    return {"statusCode": 404, "headers": {"content-type": "application/json"},
            "body": json.dumps({"error": "not found"})}
