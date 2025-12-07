from http.server import HTTPServer, SimpleHTTPRequestHandler
import os


class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()


def run_local_server():
    os.chdir(os.path.dirname(__file__))

    # Создаем простой HTML файл для теста
    html_content = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Тест игры</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            padding: 20px;
            text-align: center;
        }
        .game-container {
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
            border-radius: 10px;
        }
        button {
            padding: 15px 30px;
            margin: 10px;
            font-size: 16px;
            cursor: pointer;
            background: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div class="game-container">
        <h1>🎮 Тестовая игра</h1>
        <p>Простая игра для тестирования WebApp</p>

        <div id="game-content">
            <p>Вы набрали: <span id="score">0</span> очков</p>
            <button onclick="incrementScore()">➕ Добавить 100 очков</button>
            <button onclick="completeGame()">✅ Завершить игру</button>
        </div>
    </div>

    <script>
        const tg = window.Telegram.WebApp;
        tg.expand();

        let score = 0;

        function incrementScore() {
            score += 100;
            document.getElementById('score').textContent = score;
        }

        function completeGame() {
            // Отправляем данные в бота
            tg.sendData(JSON.stringify({
                action: 'game_complete',
                score: score,
                level: 1,
                timestamp: new Date().toISOString()
            }));

            tg.close();
        }
    </script>
</body>
</html>
    """

    with open('test_game.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

    print("🌐 Запускаю локальный сервер на https://github.com/IrinaSereda123/skills-introduction-to-github/pull/3/files#diff-50a94518fd531cec4b0dfffe54f6d5e2b35b40b9a9f07567564945087f61ea93")
    print("📁 Файл для теста: test_game.html")

    server = HTTPServer(('localhost', 8000), CORSRequestHandler)
    print("✅ Сервер запущен. Для остановки нажмите Ctrl+C")
    server.serve_forever()


if __name__ == '__main__':
    run_local_server()