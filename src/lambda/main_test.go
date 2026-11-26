package main

import (
	"encoding/json"
	"io"
	"maps"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

const joke = "I'm reading a book about anti-gravity. It's impossible to put down!"

var jsonHeaders = map[string]string{"Content-Type": "application/json", "Access-Control-Allow-Origin": "*", "X-Robots-Tag": "noindex"}
var textHeaders = map[string]string{"Content-Type": "text/plain", "Access-Control-Allow-Origin": "*", "X-Robots-Tag": "noindex"}

// usePuns swaps in a fixed joke list for one test
func usePuns(t *testing.T, list ...string) {
	saved := puns
	puns = list
	t.Cleanup(func() { puns = saved })
}

func TestPunsFile(t *testing.T) {
	if len(puns) == 0 {
		t.Fatal("no jokes loaded")
	}
	seen := map[string]bool{}
	for i, pun := range puns {
		if pun == "" || pun != strings.TrimSpace(pun) {
			t.Errorf("line %d is blank or has extra spaces: %q", i+1, pun)
		}
		if seen[pun] {
			t.Errorf("line %d is a duplicate: %q", i+1, pun)
		}
		seen[pun] = true
	}
}

func TestRandomPunComesFromFile(t *testing.T) {
	pun := handle(request{Headers: map[string]string{"Accept": "text/plain"}}).Body
	if !strings.Contains(punsFile, pun+"\n") {
		t.Errorf("%q isn't in puns.txt", pun)
	}
}

func TestAccept(t *testing.T) {
	tests := []struct {
		name    string
		headers map[string]string
		want    map[string]string
	}{
		{"text/plain", map[string]string{"Accept": "text/plain"}, textHeaders},
		{"lower case header", map[string]string{"accept": "text/plain"}, textHeaders},
		{"json", map[string]string{"Accept": "application/json"}, jsonHeaders},
		{"no headers", nil, jsonHeaders},
		{"browser", map[string]string{"Accept": "application/json, text/javascript, */*; q=0.01"}, jsonHeaders},
		{"unknown", map[string]string{"Accept": "text/html"}, jsonHeaders},
	}
	usePuns(t, joke)
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			got := handle(request{Headers: test.headers})
			if got.StatusCode != 200 {
				t.Errorf("status = %d, want 200", got.StatusCode)
			}
			if !maps.Equal(got.Headers, test.want) {
				t.Errorf("headers = %v, want %v", got.Headers, test.want)
			}
			want := joke
			if test.want["Content-Type"] == "application/json" {
				want = `{"pun":"I'm reading a book about anti-gravity. It's impossible to put down!"}`
			}
			if got.Body != want {
				t.Errorf("body = %s, want %s", got.Body, want)
			}
		})
	}
}

func TestNoJokes(t *testing.T) {
	usePuns(t)
	got := handle(request{Headers: map[string]string{"Accept": "text/plain"}})
	if got.StatusCode != 500 || got.Body != `{"errors":["no jokes loaded"]}` {
		t.Errorf("got %d %s", got.StatusCode, got.Body)
	}
	if !maps.Equal(got.Headers, jsonHeaders) {
		t.Errorf("headers = %v", got.Headers)
	}
}

func TestHealthcheck(t *testing.T) {
	got := handle(request{Resource: "/healthcheck"})
	var body health
	if err := json.Unmarshal([]byte(got.Body), &body); err != nil {
		t.Fatal(err)
	}
	if got.StatusCode != 200 || body.Status != "ok" || body.Checks[0].Name != "Jokes" || !body.Checks[0].OK {
		t.Errorf("got %d %s", got.StatusCode, got.Body)
	}
	if got.Headers["Cache-Control"] != "no-store" || got.Headers["X-Robots-Tag"] != "noindex" {
		t.Errorf("headers = %v", got.Headers)
	}
}

func TestHealthcheckNoJokes(t *testing.T) {
	usePuns(t)
	got := handle(request{Resource: "/healthcheck"})
	if got.StatusCode != 503 || !strings.Contains(got.Body, `"status":"fail"`) {
		t.Errorf("got %d %s", got.StatusCode, got.Body)
	}
}

func TestSplitLines(t *testing.T) {
	got := splitLines("a\r\nb\nc")
	if strings.Join(got, "|") != "a|b|c" {
		t.Errorf("got %q", got)
	}
	if len(splitLines("")) != 0 {
		t.Error("empty text should have no lines")
	}
}

// fakeRuntime stands in for the Lambda runtime API. It hands out one event and records the answer.
func fakeRuntime(t *testing.T, event string) (api string, answer func() (string, string)) {
	var path, body string
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Method == http.MethodGet && r.URL.Path == "/2018-06-01/runtime/invocation/next" {
			w.Header().Set("Lambda-Runtime-Aws-Request-Id", "abc")
			io.WriteString(w, event)
			return
		}
		data, _ := io.ReadAll(r.Body)
		path, body = r.URL.Path, string(data)
		w.WriteHeader(http.StatusAccepted)
	}))
	t.Cleanup(server.Close)
	return server.URL + "/2018-06-01/runtime/invocation/", func() (string, string) { return path, body }
}

func TestServeNext(t *testing.T) {
	usePuns(t, joke)
	api, answer := fakeRuntime(t, `{"resource":"/","headers":{"Accept":"text/plain"}}`)
	if err := serveNext(http.DefaultClient, api); err != nil {
		t.Fatal(err)
	}
	path, body := answer()
	if path != "/2018-06-01/runtime/invocation/abc/response" {
		t.Errorf("answered at %s", path)
	}
	var got response
	if err := json.Unmarshal([]byte(body), &got); err != nil {
		t.Fatal(err)
	}
	if got.StatusCode != 200 || got.Body != joke || !maps.Equal(got.Headers, textHeaders) {
		t.Errorf("got %s", body)
	}
}

func TestServeNextBadEvent(t *testing.T) {
	api, answer := fakeRuntime(t, `not json`)
	if err := serveNext(http.DefaultClient, api); err != nil {
		t.Fatal(err)
	}
	path, body := answer()
	if path != "/2018-06-01/runtime/invocation/abc/error" || !strings.Contains(body, `"errorType":"BadRequest"`) {
		t.Errorf("answered %s with %s", path, body)
	}
}
