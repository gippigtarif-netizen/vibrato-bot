import os
import http.server
import socketserver
import threading
import requests

TOKEN = os.getenv("BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL")
PORT = int(os.getenv("PORT", 10000))

# Веб-сервер, который отдает страницу index.html для мини-приложения
class WebAppHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path.startswith("/?"):
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            with open("index.html", "rb") as f:
                self.wfile.write(f.read())
        else:
            super().do_GET()

def run_server():
    with socketserver.TCPServer(("", PORT), WebAppHandler) as httpd:
        print(f"Server started on port {PORT}")
        httpd.serve_forever()

server_thread = threading.Thread(target=run_server, daemon=True)
server_thread.start()

def send_welcome(chat_id):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": "📳 Нажми кнопку ниже, чтобы открыть мини-приложение с вибрацией:",
        "reply_markup": {
            "inline_keyboard": [
                [
                    {
                        "text": "📲 Открыть Вибрато Бот",
                        "web_app": {"url": WEBAPP_URL}
                    }
                ]
            ]
        }
    }
    requests.post(url, json=payload)

def run_bot():
    offset = 0
    print("Bot polling started...")
    while True:
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={offset}&timeout=30"
            response = requests.get(url, timeout=35).json()
            
            if "result" in response:
                for update in response["result"]:
                    offset = update["update_id"] + 1
                    if "message" in update and "text" in update["message"]:
                        chat_id = update["message"]["chat"]["id"]
                        text = update["message"]["text"]
                        
                        if text == "/start":
                            send_welcome(chat_id)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    run_bot()
