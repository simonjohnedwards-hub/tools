import hmac
import hashlib
import base64
import sys
import os

os.environ["TK_SILENCE_DEPRECATION"] = "1"


def hmacSHA256hex(productID, password):
    digest = hmac.new(
        password.encode("utf-8"),
        productID.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    return digest.hex()


def hmacSHA256base64(productID, password):
    digest = hmac.new(
        password.encode("utf-8"),
        productID.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    return base64.b64encode(digest).decode("utf-8")


def run_cli():
    if len(sys.argv) >= 2:
        productID = sys.argv[1]
        password = sys.argv[2] if len(sys.argv) >= 3 else "nomis"
    else:
        productID = input("Product ID: ")
        password = input("Password [nomis]: ") or "nomis"

    print(f"Base64 : {hmacSHA256base64(productID, password)}")
    print(f"Hex    : {hmacSHA256hex(productID, password)}")


def run_gui():
    import http.server
    import json
    import webbrowser
    import threading
    import urllib.parse

    HTML = """<!DOCTYPE html>
<html>
<head>
<title>HMAC-SHA256</title>
<style>
  body { font-family: Helvetica, Arial, sans-serif; max-width: 700px; margin: 40px auto; padding: 20px; }
  label { display: block; font-size: 16px; margin-top: 14px; }
  input[type=text] { width: 100%; padding: 10px; font-size: 16px; margin-top: 4px; box-sizing: border-box; border: 1px solid #999; border-radius: 4px; }
  button { margin-top: 18px; padding: 10px 30px; font-size: 16px; cursor: pointer; }
  .result { margin-top: 20px; }
  .result label { font-weight: bold; }
  .result p { font-family: Courier, monospace; color: blue; word-break: break-all; margin: 4px 0 0 0; }
</style>
</head>
<body>
<h2>HMAC-SHA256</h2>
<label>Product ID</label>
<input type="text" id="input1" autofocus>
<label>Password</label>
<input type="text" id="input2" value="nomis">
<br>
<button onclick="createCode()">Create code</button>
<div class="result">
  <label>Base64</label>
  <p id="text5">&nbsp;</p>
  <label>Hex</label>
  <p id="text6">&nbsp;</p>
</div>
<script>
async function createCode() {
  const pid = document.getElementById('input1').value;
  const pw = document.getElementById('input2').value;
  const resp = await fetch('/generate?productID=' + encodeURIComponent(pid) + '&password=' + encodeURIComponent(pw));
  const data = await resp.json();
  document.getElementById('text5').textContent = data.base64;
  document.getElementById('text6').textContent = data.hex;
}
</script>
</body>
</html>"""

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path.startswith("/generate?"):
                qs = urllib.parse.urlparse(self.path).query
                params = urllib.parse.parse_qs(qs)
                pid = params.get("productID", [""])[0]
                pw = params.get("password", ["nomis"])[0]
                result = json.dumps({
                    "base64": hmacSHA256base64(pid, pw),
                    "hex": hmacSHA256hex(pid, pw),
                })
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(result.encode())
            else:
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(HTML.encode())

        def log_message(self, format, *args):
            pass  # silence request logs

    server = http.server.HTTPServer(("127.0.0.1", 0), Handler)
    port = server.server_address[1]
    url = f"http://127.0.0.1:{port}"
    print(f"Opening {url} — press Ctrl+C to quit")
    webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
        server.server_close()


if __name__ == "__main__":
    if "--gui" in sys.argv:
        run_gui()
    elif len(sys.argv) >= 2:
        run_cli()
    else:
        run_gui()
