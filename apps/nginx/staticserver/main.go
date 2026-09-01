package main

import (
	"encoding/json"
	"log"
	"net/http"
	"os"
)

func main() {
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}
	mux := http.NewServeMux()
	mux.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		_ = json.NewEncoder(w).Encode(map[string]string{
			"status":   "ok",
			"language": "nginx",
			"stack":    "static-distroless",
		})
	})
	mux.Handle("/", http.FileServer(http.Dir("/html")))
	log.Fatal(http.ListenAndServe(":"+port, mux))
}
