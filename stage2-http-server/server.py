# server.py - tiny HTTP server (educational)
import socket
import threading
import os
import mimetypes

HOST = "127.0.0.1"
PORT = 8080
DOCROOT = "static"   # folder to serve files from

CRLF = "\r\n"

# Simple safe join that prevents path traversal
def safe_path(docroot, url_path):
    # strip query params and fragment
    url_path = url_path.split("?", 1)[0].split("#", 1)[0]
    if url_path == "/":
        url_path = "/index.html"
    # normalize and join
    requested = os.path.normpath(os.path.join(docroot, url_path.lstrip("/")))
    # ensure requested is inside docroot
    docroot_abs = os.path.abspath(docroot)
    requested_abs = os.path.abspath(requested)
    if not requested_abs.startswith(docroot_abs + os.sep) and requested_abs != docroot_abs:
        return None
    return requested_abs

def http_response(status_code, reason, headers=None, body=b""):
    if headers is None:
        headers = {}
    status_line = f"HTTP/1.1 {status_code} {reason}"
    hdrs = "".join(f"{k}: {v}{CRLF}" for k, v in headers.items())
    return (status_line + CRLF + hdrs + CRLF).encode("utf-8") + body

def handle_client(conn, addr):
    try:
        data = conn.recv(65536)  # read request (simple)
        if not data:
            return
        # decode for parsing (keep raw bytes for file bodies)
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            text = data.decode("iso-8859-1")

        # parse request-line: e.g., "GET /path HTTP/1.1"
        request_line, *rest = text.split(CRLF, 1)
        parts = request_line.split()
        if len(parts) < 3:
            resp = http_response(400, "Bad Request", {"Content-Length": "0"})
            conn.sendall(resp)
            return
        method, path, http_ver = parts[0], parts[1], parts[2]

        # Only support GET for now
        if method != "GET":
            body = b"Method Not Allowed"
            resp = http_response(405, "Method Not Allowed", {"Content-Type":"text/plain; charset=utf-8", "Content-Length": str(len(body))}, body)
            conn.sendall(resp)
            return

        # map path to filesystem
        full_path = safe_path(DOCROOT, path)
        if full_path is None or not os.path.exists(full_path) or not os.path.isfile(full_path):
            body = b"<h1>404 Not Found</h1>"
            headers = {"Content-Type":"text/html; charset=utf-8", "Content-Length": str(len(body))}
            conn.sendall(http_response(404, "Not Found", headers, body))
            return

        # read file bytes
        with open(full_path, "rb") as f:
            body = f.read()

        mime_type, _ = mimetypes.guess_type(full_path)
        if mime_type is None:
            mime_type = "application/octet-stream"
        headers = {
            "Content-Type": mime_type,
            "Content-Length": str(len(body)),
            "Connection": "close",
        }
        conn.sendall(http_response(200, "OK", headers, body))

    except Exception as e:
        # minimal error response
        body = f"<h1>500 Server Error</h1><pre>{e}</pre>".encode("utf-8")
        conn.sendall(http_response(500, "Internal Server Error", {"Content-Type":"text/html; charset=utf-8", "Content-Length": str(len(body))}, body))
    finally:
        try:
            conn.close()
        except:
            pass

def run_server(host=HOST, port=PORT):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))
    sock.listen(50)
    print(f"Serving HTTP on http://{host}:{port} (docroot: {DOCROOT}) ...")
    try:
        while True:
            conn, addr = sock.accept()
            t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            t.start()
    except KeyboardInterrupt:
        print("Shutting down server.")
    finally:
        sock.close()

if __name__ == "__main__":
    run_server()
