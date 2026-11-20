#!/usr/bin/env bash
set -e

source config/variables

echo
echo "Building lambda bundle ..."
./build-lambda-bundle.sh

# AWS blocks code updates on deprecated runtimes, so set the runtime first
echo
echo "Updating $LAMBDA_FUNCTION_NAME lambda function configuration ..."
aws lambda update-function-configuration \
  --function-name "$LAMBDA_FUNCTION_NAME" \
  --runtime "$LAMBDA_FUNCTION_RUNTIME" \
  --handler "$LAMBDA_FUNCTION_HANDLER" \
  --timeout "$LAMBDA_FUNCTION_TIMEOUT" \
  --memory-size "$LAMBDA_FUNCTION_MEMORY" \
  --output text --query 'LastUpdateStatus'
aws lambda wait function-updated --function-name "$LAMBDA_FUNCTION_NAME"

echo
echo "Updating $LAMBDA_FUNCTION_NAME lambda function code ..."
aws lambda update-function-code \
  --function-name "$LAMBDA_FUNCTION_NAME" \
  --zip-file "fileb://lambda-build.zip" \
  --output text --query 'LastUpdateStatus'
aws lambda wait function-updated --function-name "$LAMBDA_FUNCTION_NAME"

echo
echo 'Done!'
