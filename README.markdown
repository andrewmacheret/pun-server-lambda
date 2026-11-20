# Random pun server using Python and AWS Lambda

[![License](https://img.shields.io/badge/license-MIT-lightgray.svg)](https://github.com/andrewmacheret/pun-server-lambda/blob/master/LICENSE.md)

Random pun server! Each request returns a random line from [`src/lambda/puns.txt`](src/lambda/puns.txt).

Returns `{"pun": "..."}` by default, or just the joke when called with `Accept: text/plain`.

## Credits

The puns come from:

- [official_joke_api](https://github.com/15Dkatz/official_joke_api) by [David Katz](https://github.com/15Dkatz), MIT License
- [dadjokes](https://github.com/yesinteractive/dadjokes) by [Yes Interactive](https://github.com/yesinteractive), MIT License
- [devpun](https://github.com/elijahmanor/devpun) by [Elijah Manor](https://github.com/elijahmanor), MIT License
- [icanhazdadjoke](https://icanhazdadjoke.com/)

The MIT license texts are in [`PUNS_LICENSE.md`](PUNS_LICENSE.md). Each joke's setup and punchline were joined into one line, and duplicates and near-duplicates were removed.

## Development

Run tests with `cd src/lambda && python3 -m unittest` (needs Python 3.14). To add a pun, add a line to `puns.txt`.

## Deploy

Pushes to `master` run the tests and deploy to the `Pun` AWS Lambda function through GitHub Actions (see `.github/workflows/deploy.yml`). To redeploy without a code change, use "Run workflow" on the Actions tab.

The workflow signs in to AWS with GitHub OIDC using the IAM role in the `AWS_ROLE_ARN` repo variable. The Lambda sits behind AWS API Gateway at `pun.andrewmacheret.com`.
