# Random pun server using Python and AWS Lambda

[![License](https://img.shields.io/badge/license-MIT-lightgray.svg)](https://github.com/andrewmacheret/pun-server-lambda/blob/master/LICENSE.md)

Random pun server! Jokes come from [icanhazdadjoke](https://icanhazdadjoke.com/).

Returns `{"pun": "..."}` by default, or just the joke when called with `Accept: text/plain`.

## Development

Run tests with `cd src/lambda && python3 -m unittest` (needs Python 3.14). One test calls the real icanhazdadjoke API.

## Deploy

Pushes to `master` run the tests and deploy to the `Pun` AWS Lambda function through GitHub Actions (see `.github/workflows/deploy.yml`). To redeploy without a code change, use "Run workflow" on the Actions tab.

The workflow signs in to AWS with GitHub OIDC using the IAM role in the `AWS_ROLE_ARN` repo variable. The Lambda sits behind AWS API Gateway at `pun.andrewmacheret.com`.
