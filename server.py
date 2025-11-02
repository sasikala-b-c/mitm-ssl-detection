import ssl
from pathlib import Path
from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/api/echo", methods=["POST"]) 
def echo():
    data = request.get_json(silent=True) or {}
    return jsonify({"echo": data, "from": "server"})


@app.route("/")
def index():
    return jsonify({"service": "secure-server", "status": "ok"})


if __name__ == "__main__":
    cert_dir = Path(__file__).parent / "certs"
    cert_path = cert_dir / "server.crt"
    key_path = cert_dir / "server.key"

    if not cert_path.exists() or not key_path.exists():
        raise SystemExit("Missing certs. Run: python certs/generate_certs.py")

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=str(cert_path), keyfile=str(key_path))

    print("HTTPS server listening on https://localhost:8443 ...")
    app.run(host="127.0.0.1", port=8443, ssl_context=context)
