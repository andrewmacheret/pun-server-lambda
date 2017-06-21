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
    html_content = urllib2.urlopen("http://www.punoftheday.com/cgi-bin/randompun.pl", timeout = 1).read()
  except urllib2.URLError, e:
    raise Exception("URL error waiting for pun")
  except socket.timeout, e:
    raise Exception("Socket timeout waiting for pun")

  # create a beautiful soup object out of the raw html (the prettify is probably not necessary)
  soup = BeautifulSoup(html_content, "html.parser")
  soup.prettify()

  # find and print the pun... it's the text in the element: div#main-content div.dropshadow1
  pun = soup.find("div", {"id": "main-content"}).find("div", {"class": "dropshadow1"}).text

  pun = pun.strip()

  return pun

  #try:
  #  client = MongoClient()
  #  db = client["pundb"]
  #  collection = db["puns"]
  #  punDict = {"full": pun}
  #  collection.update(punDict, punDict, True)
  #except:
  #  # do nothing on insertion error
  #  pass


