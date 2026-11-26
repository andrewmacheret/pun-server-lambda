# Random pun server using Go and AWS Lambda

[![Test and deploy](https://github.com/andrewmacheret/pun-server-lambda/actions/workflows/deploy.yml/badge.svg)](https://github.com/andrewmacheret/pun-server-lambda/actions/workflows/deploy.yml) [![Canary](https://github.com/andrewmacheret/pun-server-lambda/actions/workflows/canary.yml/badge.svg)](https://github.com/andrewmacheret/pun-server-lambda/actions/workflows/canary.yml) [![License](https://img.shields.io/badge/license-MIT-lightgray.svg)](https://github.com/andrewmacheret/pun-server-lambda/blob/master/LICENSE.md)

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

Run tests with `cd src/lambda && go test ./...` (needs Go 1.27). To add a pun, add a line to `puns.txt`.

The Lambda runs on the `provided.al2023` runtime on arm64. `main.go` talks to the [Lambda runtime API](https://docs.aws.amazon.com/lambda/latest/dg/runtimes-api.html) itself, so it has no dependencies, and `puns.txt` is built into the binary. It starts cold in a few tens of milliseconds, even at 128 MB.

## Health check

Once a day, the Canary workflow (`.github/workflows/canary.yml`) checks that the API is up and its jokes loaded. It's started by [andrewmacheret/canary](https://github.com/andrewmacheret/canary).

## Deploy

Pushes to `master` run the tests and deploy to the `Pun` AWS Lambda function through GitHub Actions (see `.github/workflows/deploy.yml`). To redeploy without a code change, use "Run workflow" on the Actions tab.

The workflow signs in to AWS with GitHub OIDC using the IAM role in the `AWS_ROLE_ARN` repo variable. The Lambda sits behind AWS API Gateway at `pun.andrewmacheret.com`. The `live` stage's settings, which aren't in git, limit it to 20 requests a second with bursts of 40.
