#!/usr/bin/env python3
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import mimetypes


ROOT = Path(__file__).resolve().parent
DASHBOARD_FILE = ROOT / "dashboard.html"
WORKBOOK_FILE = ROOT / "NAV_Data.xlsx"
HOST = "127.0.0.1"
PORT = 8000


class DashboardHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        route = self.path.split("?", 1)[0]
        if route in ("/", "/dashboard", "/dashboard.html"):
            self.serve_file(DASHBOARD_FILE, "text/html; charset=utf-8", no_cache=True)
            return
        if route in ("/NAV_Data.xlsx", "/dashboard/NAV_Data.xlsx"):
            self.serve_file(
                WORKBOOK_FILE,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                no_cache=True,
            )
            return
        self.send_error(HTTPStatus.NOT_FOUND, "File not found")

    def log_message(self, format, *args):
        return

    def serve_file(self, file_path: Path, content_type: str | None = None, no_cache: bool = False):
        if not file_path.exists():
            self.send_error(HTTPStatus.NOT_FOUND, f"Missing file: {file_path.name}")
            return

        ctype = content_type or mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
        data = file_path.read_bytes()

        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        if no_cache:
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")
        self.end_headers()
        self.wfile.write(data)


def main():
    server = ThreadingHTTPServer((HOST, PORT), DashboardHandler)
    print(f"Dashboard: http://{HOST}:{PORT}/dashboard.html")
    print(f"Workbook: {WORKBOOK_FILE}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
