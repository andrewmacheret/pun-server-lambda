#!/usr/bin/env python2.7

# imports
from pprint import pprint
import urllib2
import socket
import json  
from bs4 import BeautifulSoup
#from pymongo import MongoClient

def lambda_handler(event, context):
  try:
    body = get_pun()
  except Exception as ex:
    return {
      "body": json.dumps({"errors" : ex.args}),
      "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
      "statusCode": 500
    }

  contentType = get_content_type(event)
  if contentType == "application/json":
    body = json.dumps({"pun" : body})

  return {
    "body": body,
    "headers": {"Content-Type": contentType, "Access-Control-Allow-Origin": "*"},
    "statusCode": 200
  }

def get_content_type(event):
  defaultContentType = "application/json"

  headers = event.get("headers")
  if headers is None:
    return defaultContentType

  acceptHeader = headers.get("Accept")
  if acceptHeader is None:
    return defaultContentType

  for acceptType in acceptHeader.split(","):
    simpleAcceptType = acceptType.split(";", 1)[0].strip()
    if simpleAcceptType == "application/json" or simpleAcceptType == "text/plain":
      return simpleAcceptType

  return defaultContentType

def get_pun():
  # read the html content of the random pun page into a string
  try:
    json_content = urllib2.urlopen("https://kylebob.com/get.php?category=puns", timeout = 1).read()
  except urllib2.URLError, e:
    raise Exception("URL error waiting for pun")
  except socket.timeout, e:
    raise Exception("Socket timeout waiting for pun")

  return json.loads(json_content)["thing"]

  #try:
  #  client = MongoClient()
  #  db = client["pundb"]
  #  collection = db["puns"]
  #  punDict = {"full": pun}
  #  collection.update(punDict, punDict, True)
  #except:
  #  # do nothing on insertion error
  #  pass


