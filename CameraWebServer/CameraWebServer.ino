#include "esp_camera.h"
#include <WiFi.h>
#include <WebServer.h>
#include <HTTPClient.h>
#include <Preferences.h> // For storing settings in flash

// ===========================
// Select camera model in board_config.h
// ===========================
#include "board_config.h"

// Preferences object for storing settings
Preferences preferences;

// WiFi credentials (initially default, can be changed via web interface)
String ssid = "kikimora";
String password = "pivo1488";
String serverIP = "192.168.1.100"; // Default server IP (your laptop)
int serverPort = 80; // Default server port

// Button handling
const int BUTTON_PIN = 0; // GPIO 0 - the physical button on ESP32-CAM
int lastButtonState = HIGH;
int currentButtonState = HIGH;
bool captureTriggered = false;
unsigned long lastDebounceTime = 0;
const unsigned long debounceDelay = 50; // Reduced debounce delay for potentially faster response

// Web server on port 80
WebServer server(80);

void setupCamera();
void handleRoot();
void handleCapture();
void handleSettings();
void handleSaveSettings();
void handleNotFound();
bool captureAndUpload();
bool uploadPhotoToServer(uint8_t *pData, size_t len);

void setup() {
  Serial.begin(115200);
  Serial.setDebugOutput(true);
  Serial.println();

  // Load saved settings
  preferences.begin("cam_settings", false);
  String savedSSID = preferences.getString("ssid", "kikimora");
  String savedPassword = preferences.getString("password", "pivo1488");
  String savedServerIP = preferences.getString("serverIP", "192.168.1.117");


  pinMode(BUTTON_PIN, INPUT_PULLUP);

  
  if (savedSSID.length() > 0) ssid = savedSSID;
  if (savedPassword.length() > 0) password = savedPassword;
  if (savedServerIP.length() > 0) serverIP = savedServerIP;
  
  preferences.end();

  // Initialize camera
  delay(1000); // wait so there is no error
  setupCamera();

  // Connect to WiFi
  WiFi.begin(ssid.c_str(), password.c_str());
  WiFi.setSleep(false);

  Serial.print("WiFi connecting");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  // Define web server routes
  server.on("/", HTTP_GET, handleRoot);
  server.on("/capture", HTTP_GET, handleCapture);
  server.on("/settings", HTTP_GET, handleSettings);
  server.on("/save_settings", HTTP_POST, handleSaveSettings);
  server.onNotFound(handleNotFound);

  // Start the server
  server.begin();
  Serial.println("HTTP server started");
}

void loop() {
  server.handleClient(); // Handle incoming client requests
  
  // Read the current button state
  int reading = digitalRead(BUTTON_PIN);

  // Check if the button state changed (from HIGH to LOW or LOW to HIGH)
  if (reading != lastButtonState) {
    // Reset the debouncing timer
    lastDebounceTime = millis();
  }

  // If the button state has been stable for longer than the debounce delay
  if ((millis() - lastDebounceTime) > debounceDelay) {
    // If the button state has actually changed since last check
    if (reading != currentButtonState) {
      currentButtonState = reading;
      // Button state has changed
      if (currentButtonState == LOW) { // Button pressed (active low due to pull-up)
        Serial.println("Button pressed - capturing image");
        captureAndUpload();
      }
    }
  }
  
  // Update the last button state for the next loop iteration
  lastButtonState = reading;
  
  delay(10); // Small delay to prevent excessive CPU usage
}

void setupCamera() {
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.frame_size = FRAMESIZE_VGA;
  config.pixel_format = PIXFORMAT_JPEG;
  config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
  config.fb_location = CAMERA_FB_IN_PSRAM;
  config.jpeg_quality = 6;
  config.fb_count = 1;

  // camera init
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }

  sensor_t *s = esp_camera_sensor_get();
  // initial sensors are flipped vertically and colors are a bit saturated
  if (s->id.PID == OV3660_PID) {
    s->set_vflip(s, 1);
    s->set_brightness(s, 1);
    s->set_saturation(s, -2);
  }
  if (config.pixel_format == PIXFORMAT_JPEG) {
    s->set_framesize(s, FRAMESIZE_VGA); // Use smaller size for faster capture
  }
}

void handleRoot() {
  String html = "<!DOCTYPE html><html>";
  html += "<head><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">";
  html += "<link rel=\"icon\" href=\"data:,\">";
  html += "<style>html { font-family: Arial; display: inline-block; margin: 0px auto; text-align:center;}";
  html += ".button { background-color: #4CAF50; border: none; color: white; padding: 16px 40px;";
  html += "text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;}";
  html += ".button2 { background-color: #555555;}</style></head>";
  html += "<body><h1>ESP32-CAM Control Panel</h1>";
  html += "<p><a href=\"/capture\"><button class=\"button\">CAPTURE & UPLOAD</button></a></p>";
  html += "<p><a href=\"/settings\"><button class=\"button button2\">Settings</button></a></p>";
  html += "</body></html>";
  
  server.send(200, "text/html", html);
}

void handleCapture() {
  server.send(200, "text/html", "<!DOCTYPE html><html><head><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">");
  server.sendContent("<link rel=\"icon\" href=\"data:,\"><style>html { font-family: Arial; display: inline-block; margin: 0px auto; text-align:center;}");
  server.sendContent("</style></head><body><h2>Capturing and Uploading...</h2>");
  
  // Capture and upload image
  if (captureAndUpload()) {
    server.sendContent("<p>Image captured and uploaded successfully!</p>");
  } else {
    server.sendContent("<p>Failed to capture or upload image.</p>");
  }
  
  server.sendContent("<p><a href=\"/\">Back to Control Panel</a></p></body></html>");
}

void handleSettings() {
  String html = "<!DOCTYPE html><html>";
  html += "<head><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">";
  html += "<link rel=\"icon\" href=\"data:,\">";
  html += "<style>html { font-family: Arial; display: inline-block; margin: 0px auto; text-align:center;}";
  html += "form { max-width: 400px; margin: 0 auto; padding: 20px; }";
  html += "input[type=text], input[type=password] { width: 100%; padding: 12px; margin: 8px 0; box-sizing: border-box; }";
  html += "input[type=submit] { background-color: #4CAF50; color: white; padding: 14px 20px; border: none; cursor: pointer; width: 100%; }";
  html += "input[type=submit]:hover { opacity: 0.8; }</style></head>";
  html += "<body><h2>ESP32-CAM Settings</h2>";
  html += "<form action=\"/save_settings\" method=\"post\">";
  html += "<label for=\"ssid\">WiFi SSID:</label>";
  html += "<input type=\"text\" id=\"ssid\" name=\"ssid\" value=\"" + ssid + "\">";
  html += "<label for=\"password\">WiFi Password:</label>";
  html += "<input type=\"password\" id=\"password\" name=\"password\" value=\"" + password + "\">";
  html += "<label for=\"serverIP\">Server IP:</label>";
  html += "<input type=\"text\" id=\"serverIP\" name=\"serverIP\" value=\"" + serverIP + "\">";
  html += "<input type=\"submit\" value=\"Save Settings\"></form>";
  html += "<p><a href=\"/\">Back to Control Panel</a></p>";
  html += "</body></html>";
  
  server.send(200, "text/html", html);
}

void handleSaveSettings() {
  if (server.hasArg("ssid") && server.hasArg("password") && server.hasArg("serverIP")) {
    String newSSID = server.arg("ssid");
    String newPassword = server.arg("password");
    String newServerIP = server.arg("serverIP");
    
    // Save to preferences
    preferences.begin("cam_settings", false);
    preferences.putString("ssid", newSSID);
    preferences.putString("password", newPassword);
    preferences.putString("serverIP", newServerIP);
    preferences.end();
    
    ssid = newSSID;
    password = newPassword;
    serverIP = newServerIP;
    
    server.send(200, "text/html", "<!DOCTYPE html><html><body><h2>Settings Saved!</h2>");
    server.sendContent("<p>Restart the device to connect to the new WiFi network.</p>");
    server.sendContent("<p><a href=\"/\">Back to Control Panel</a></p></body></html>");
  } else {
    server.send(400, "text/plain", "Bad Request");
  }
}

void handleNotFound() {
  server.send(404, "text/plain", "404 Not found");
}

bool captureAndUpload() {
  // Capture a frame
  camera_fb_t *fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("Camera capture failed");
    return false;
  }
  
  Serial.println("Image captured");
  Serial.print("Image size: ");
  Serial.println(fb->len);
  
  // Upload the image
  bool success = uploadPhotoToServer(fb->buf, fb->len);
  
  // Return the frame buffer back to the driver for reuse
  esp_camera_fb_return(fb);
  
  return success;
}

bool uploadPhotoToServer(uint8_t *pData, size_t len) {
  HTTPClient http;
  String url = "http://" + serverIP + ":" + String(serverPort) + "/upload";
  
  http.begin(url);
  http.addHeader("Content-Type", "image/jpeg");
  http.addHeader("Content-Length", String(len));
  
  int httpResponseCode = http.POST(pData, len);
  
  if (httpResponseCode > 0) {
    String response = http.getString();
    Serial.println("HTTP Response code: " + String(httpResponseCode));
    Serial.println("Response: " + response);
    http.end();
    return true;
  } else {
    Serial.print("Error on sending POST: ");
    Serial.println(httpResponseCode);
    http.end();
    return false;
  }
}
