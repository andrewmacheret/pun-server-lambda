// The Pun Lambda answers API Gateway requests with a random joke from puns.txt.
//
// It runs on Lambda's provided.al2023 runtime and talks to the Lambda runtime API itself,
// so it needs nothing outside the standard library.
package main

import (
	"bytes"
	_ "embed"
	"encoding/json"
	"fmt"
	"math/rand/v2"
	"net/http"
	"os"
	"strings"
)

//go:embed puns.txt
var punsFile string

var puns = splitLines(punsFile)

type request struct {
	Resource string            `json:"resource"`
	Headers  map[string]string `json:"headers"`
}

type response struct {
	StatusCode int               `json:"statusCode"`
	Headers    map[string]string `json:"headers"`
	Body       string            `json:"body"`
}

type check struct {
	Name   string `json:"name"`
	OK     bool   `json:"ok"`
	Detail string `json:"detail"`
}

type health struct {
	Status string  `json:"status"`
	Checks []check `json:"checks"`
}

func main() {
	api := "http://" + os.Getenv("AWS_LAMBDA_RUNTIME_API") + "/2018-06-01/runtime/invocation/"
	for {
		if err := serveNext(http.DefaultClient, api); err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}
	}
}

// serveNext waits for the next request from the Lambda runtime API and sends back the answer.
// See https://docs.aws.amazon.com/lambda/latest/dg/runtimes-api.html
func serveNext(client *http.Client, api string) error {
	next, err := client.Get(api + "next")
	if err != nil {
		return err
	}
	defer next.Body.Close()
	id := next.Header.Get("Lambda-Runtime-Aws-Request-Id")

	var req request
	var body []byte
	path := id + "/response"
	if err := json.NewDecoder(next.Body).Decode(&req); err != nil {
		path = id + "/error"
		body, _ = json.Marshal(map[string]string{"errorMessage": err.Error(), "errorType": "BadRequest"})
	} else {
		body, _ = json.Marshal(handle(req))
	}

	resp, err := client.Post(api+path, "application/json", bytes.NewReader(body))
	if err != nil {
		return err
	}
	resp.Body.Close()
	if resp.StatusCode >= 300 {
		return fmt.Errorf("runtime API answered %s to %s", resp.Status, path)
	}
	return nil
}

func handle(req request) response {
	if req.Resource == "/healthcheck" {
		return healthcheck()
	}
	if len(puns) == 0 {
		body, _ := json.Marshal(map[string][]string{"errors": {"no jokes loaded"}})
		return response{StatusCode: 500, Headers: headers("application/json"), Body: string(body)}
	}

	pun := puns[rand.IntN(len(puns))]
	contentType := contentTypeFor(req.Headers)
	body := pun
	if contentType == "application/json" {
		encoded, _ := json.Marshal(map[string]string{"pun": pun})
		body = string(encoded)
	}
	return response{StatusCode: 200, Headers: headers(contentType), Body: body}
}

// healthcheck answers GET /healthcheck, for the daily canary (github.com/andrewmacheret/canary)
func healthcheck() response {
	ok := len(puns) > 0
	result := health{Status: "ok", Checks: []check{{Name: "Jokes", OK: ok, Detail: fmt.Sprintf("%d jokes loaded", len(puns))}}}
	statusCode := 200
	if !ok {
		result.Status, statusCode = "fail", 503
	}
	body, _ := json.Marshal(result)
	h := headers("application/json")
	h["Cache-Control"] = "no-store"
	return response{StatusCode: statusCode, Headers: h, Body: string(body)}
}

// headers go on every answer. noindex keeps Google from listing this API in search results.
func headers(contentType string) map[string]string {
	return map[string]string{
		"Access-Control-Allow-Origin": "*",
		"Content-Type":                contentType,
		"X-Robots-Tag":                "noindex",
	}
}

// contentTypeFor picks text/plain or application/json from the Accept header, defaulting to JSON
func contentTypeFor(headers map[string]string) string {
	for key, value := range headers {
		if !strings.EqualFold(key, "Accept") {
			continue
		}
		for part := range strings.SplitSeq(value, ",") {
			mediaType, _, _ := strings.Cut(part, ";")
			mediaType = strings.TrimSpace(mediaType)
			if mediaType == "application/json" || mediaType == "text/plain" {
				return mediaType
			}
		}
	}
	return "application/json"
}

func splitLines(text string) []string {
	var lines []string
	for line := range strings.Lines(text) {
		lines = append(lines, strings.TrimRight(line, "\r\n"))
	}
	return lines
}
