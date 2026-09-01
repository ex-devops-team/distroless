package main

import (
	"net/http"
	"os"

	"github.com/gin-gonic/gin"
)

func healthHandler(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"status":   "ok",
		"language": "go",
		"stack":    "gin",
	})
}

func newRouter() *gin.Engine {
	r := gin.New()
	r.Use(gin.Recovery())
	r.GET("/health", healthHandler)
	return r
}

func main() {
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}
	gin.SetMode(gin.ReleaseMode)
	_ = newRouter().Run(":" + port)
}
