import main

# get a pun
pun = main.get_pun()

print(pun)

# make sure it's valid

if type(pun) != unicode:
  raise Exception("Incorrect type: %s" % type(pun))

if len(pun) <= 0:
  raise Exception("Pun of non-positive length: %d" % len(pun))



response = main.lambda_handler({"headers": {"Accept": "text/plain"}}, {})
print(response)
if response["headers"] != {"Content-Type": "text/plain", "Access-Control-Allow-Origin": "*"}:
  raise Exception("Incorrect content type in response", response)
if response["statusCode"] != 200:
  raise Exception("Incorrect status code in response", response)
if response["body"].startswith("{"):
  raise Exception("Detected application/json response to a text/plain request", response)

response = main.lambda_handler({"headers": {"Accept": "application/json"}}, {})
print(response)
if response["headers"] != {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"}:
  raise Exception("Incorrect content type in response", response)
if response["statusCode"] != 200:
  raise Exception("Incorrect status code in response", response)
if not response["body"].startswith("{"):
  raise Exception("Detected text/plain response to an application/json request", response)

response = main.lambda_handler({"headers": None}, {})
print(response)
if response["headers"] != {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"}:
  raise Exception("Incorrect content type in response", response)
if response["statusCode"] != 200:
  raise Exception("Incorrect status code in response", response)
if not response["body"].startswith("{"):
  raise Exception("Detected text/plain response to an application/json request", response)

response = main.lambda_handler({"headers": {"Accept": "Accept:application/json, text/javascript, */*; q=0.01"}}, {})
print(response)
if response["headers"] != {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"}:
  raise Exception("Incorrect content type in response", response)
if response["statusCode"] != 200:
  raise Exception("Incorrect status code in response", response)
if not response["body"].startswith("{"):
  raise Exception("Detected text/plain response to an application/json request", response)

