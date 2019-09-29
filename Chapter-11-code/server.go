package main

import (
	"fmt"
	"net/http"
	"github.com/gin-gonic/gin"
)


func index(c *gin.Context){
	c.String(http.StatusOK, fmt.Sprintf("index"))
}

func login(c *gin.Context){
	c.String(http.StatusOK, fmt.Sprintf("login sucess"))
}

func logout(c *gin.Context){
	c.String(http.StatusOK, fmt.Sprintf("logout sucess"))

}

func profile(c *gin.Context) {
	c.String(http.StatusOK, fmt.Sprintf("profile"))

}

func main() {
	gin.SetMode(gin.ReleaseMode)
	router := gin.Default()

	router.POST("/login", login)
	router.POST("/logout", logout)
	router.GET("/", index)
	router.GET("/profile", profile)
	
	router.Run(":80")

}