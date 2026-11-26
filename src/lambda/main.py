import json
import random
from pathlib import Path

PUNS_FILE = Path(__file__).with_name("puns.txt")
PUNS = PUNS_FILE.read_text(encoding="utf-8").splitlines()
# noindex keeps Google from listing this API in search results
HEADERS = {"Access-Control-Allow-Origin": "*", "X-Robots-Tag": "noindex"}


def lambda_handler(event, context):
  if event.get("resource") == "/healthcheck":
    return healthcheck()
  try:
    body = get_pun()
  except Exception as ex:
    return {
      "body": json.dumps({"errors": [str(ex)]}),
      "headers": {**HEADERS, "Content-Type": "application/json"},
      "statusCode": 500
    }

  contentType = get_content_type(event)
  if contentType == "application/json":
    body = json.dumps({"pun": body})

  return {
    "body": body,
    "headers": {**HEADERS, "Content-Type": contentType},
    "statusCode": 200
  }


def healthcheck():
  """GET /healthcheck, for the daily canary (github.com/andrewmacheret/canary)."""
  ok = len(PUNS) > 0
  checks = [{"name": "Jokes", "ok": ok, "detail": f"{len(PUNS)} jokes loaded"}]
  return {
    "body": json.dumps({"status": "ok" if ok else "fail", "checks": checks}),
    "headers": {**HEADERS, "Content-Type": "application/json", "Cache-Control": "no-store"},
    "statusCode": 200 if ok else 503
  }


def get_content_type(event):
  defaultContentType = "application/json"

  headers = event.get("headers") or {}
  acceptHeader = next((value for key, value in headers.items() if key.lower() == "accept"), None)
  if acceptHeader is None:
    return defaultContentType

  for acceptType in acceptHeader.split(","):
    simpleAcceptType = acceptType.split(";", 1)[0].strip()
    if simpleAcceptType == "application/json" or simpleAcceptType == "text/plain":
      return simpleAcceptType

  return defaultContentType


def get_pun():
  return random.choice(PUNS)
