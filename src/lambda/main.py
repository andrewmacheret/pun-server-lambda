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
      "headers": {"Content-Type": "application/json"},
      "statusCode": 500
    }

  contentType = "text/plain"

  headers = event.get("headers")
  if headers is None:
    headers = {}
  acceptHeader = headers.get("Accept")
  if acceptHeader is None:
    acceptHeader = "application/json"

  if acceptHeader == "application/json":
    body = json.dumps({"pun" : body})
    contentType = "application/json"

  return {
    "body": body,
    "headers": {"Content-Type": contentType},
    "statusCode": 200
  }

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


