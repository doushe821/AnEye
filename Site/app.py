from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import sys

def run_server(port=80):
    # Меняем рабочую директорию на папку с HTML файлами
    web_dir = os.path.join(os.path.dirname(__file__), 'html')
    if os.path.exists(web_dir):
        os.chdir(web_dir)
    else:
        # Если папки html нет, используем текущую директорию
        print("Папка 'html' не найдена, используем текущую директорию")

    # Создаем HTTP сервер
    server_address = ('', port)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)

    print(f"Сервер запущен на http://localhost:{port}")
    print("Для остановки сервера нажмите Ctrl+C")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nСервер остановлен")
        httpd.shutdown()

if __name__ == '__main__':
    # Проверяем права для запуска на порту 80
    if os.name != 'nt' and os.geteuid() != 0 and len(sys.argv) > 1 and sys.argv[1] == '80':
        print("Для запуска на порту 80 на Linux/macOS可能需要 права администратора")
        print("Запустите: sudo python app.py")
        sys.exit(1)

    # Определяем порт
    port = 80
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("Используется порт по умолчанию: 80")
            port = 80

    run_server(port)
