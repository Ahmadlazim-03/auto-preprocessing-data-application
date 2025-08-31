package main

import (
	"bytes"
	"io"
	"log"
	"mime/multipart"
	"net/http"
	"time"

	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/fiber/v2/middleware/cors"
)

const pythonServiceBaseURL = "http://localhost:5001"

func forwardToPython(c *fiber.Ctx, endpoint string) error {
	body := new(bytes.Buffer)
	writer := multipart.NewWriter(body)

	// Cara yang Benar: Parse multipart form satu kali
	form, err := c.MultipartForm()
	if err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Gagal mem-parsing form: " + err.Error()})
	}

	// 1. Teruskan semua file
	for name, fileHeaders := range form.File {
		for _, fileHeader := range fileHeaders {
			part, _ := writer.CreateFormFile(name, fileHeader.Filename)
			file, _ := fileHeader.Open()
			defer file.Close()
			io.Copy(part, file)
		}
	}

	// 2. Teruskan semua field teks
	for key, values := range form.Value {
		for _, value := range values {
			writer.WriteField(key, value)
		}
	}

	writer.Close()

	req, _ := http.NewRequest("POST", pythonServiceBaseURL+endpoint, body)
	req.Header.Set("Content-Type", writer.FormDataContentType())

	client := &http.Client{Timeout: time.Second * 60}
	resp, err := client.Do(req)
	if err != nil {
		return c.Status(fiber.StatusServiceUnavailable).JSON(fiber.Map{"error": "Layanan Python tidak dapat dihubungi"})
	}
	defer resp.Body.Close()

	for key, values := range resp.Header {
		for _, value := range values {
			c.Set(key, value)
		}
	}

	pythonResponse, _ := io.ReadAll(resp.Body)
	return c.Status(resp.StatusCode).Send(pythonResponse)
}


func main() {
	app := fiber.New()
	app.Use(cors.New())

	api := app.Group("/api")
	api.Post("/summarize", func(c *fiber.Ctx) error { return forwardToPython(c, "/summarize") })
	api.Post("/preprocess", func(c *fiber.Ctx) error { return forwardToPython(c, "/process") })
	api.Post("/export-code", func(c *fiber.Ctx) error { return forwardToPython(c, "/export-code") })
	api.Post("/visualize-transform", func(c *fiber.Ctx) error { return forwardToPython(c, "/visualize-transform") })

	log.Println("Server Go berjalan di http://localhost:3000")
	log.Fatal(app.Listen(":3000"))
}