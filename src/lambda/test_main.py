import json
import unittest
from unittest import mock

import main

JSON_HEADERS = {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"}
TEXT_HEADERS = {"Content-Type": "text/plain", "Access-Control-Allow-Origin": "*"}


class TestGetPun(unittest.TestCase):
  def test_puns_file(self):
    self.assertGreater(len(main.PUNS), 0)
    for pun in main.PUNS:
      self.assertEqual(pun, pun.strip())
      self.assertGreater(len(pun), 0)

  def test_get_pun(self):
    self.assertIn(main.get_pun(), main.PUNS)


@mock.patch("main.get_pun", return_value="I'm reading a book about anti-gravity. It's impossible to put down!")
class TestHandler(unittest.TestCase):
  def test_text_plain(self, _):
    response = main.lambda_handler({"headers": {"Accept": "text/plain"}}, {})
    self.assertEqual(response["statusCode"], 200)
    self.assertEqual(response["headers"], TEXT_HEADERS)
    self.assertEqual(response["body"], "I'm reading a book about anti-gravity. It's impossible to put down!")

  def test_lower_case_header(self, _):
    response = main.lambda_handler({"headers": {"accept": "text/plain"}}, {})
    self.assertEqual(response["headers"], TEXT_HEADERS)

  def test_json(self, _):
    response = main.lambda_handler({"headers": {"Accept": "application/json"}}, {})
    self.assertEqual(response["statusCode"], 200)
    self.assertEqual(response["headers"], JSON_HEADERS)
    self.assertEqual(json.loads(response["body"]), {"pun": "I'm reading a book about anti-gravity. It's impossible to put down!"})

  def test_no_headers(self, _):
    response = main.lambda_handler({"headers": None}, {})
    self.assertEqual(response["headers"], JSON_HEADERS)

  def test_no_headers_key(self, _):
    response = main.lambda_handler({}, {})
    self.assertEqual(response["headers"], JSON_HEADERS)

  def test_browser_accept(self, _):
    response = main.lambda_handler({"headers": {"Accept": "application/json, text/javascript, */*; q=0.01"}}, {})
    self.assertEqual(response["headers"], JSON_HEADERS)

  def test_unknown_accept(self, _):
    response = main.lambda_handler({"headers": {"Accept": "text/html"}}, {})
    self.assertEqual(response["headers"], JSON_HEADERS)


class TestHandlerError(unittest.TestCase):
  @mock.patch("main.get_pun", side_effect=Exception("boom"))
  def test_error(self, _):
    response = main.lambda_handler({"headers": {"Accept": "text/plain"}}, {})
    self.assertEqual(response["statusCode"], 500)
    self.assertEqual(response["headers"], JSON_HEADERS)
    self.assertEqual(json.loads(response["body"]), {"errors": ["boom"]})


if __name__ == "__main__":
  unittest.main()
