import ssl
from pathlib import Path
from flask import Flask, request, Response
import requests

UPSTREAM = "https://127.0.0.1:8443"

app = Flask(__name__)


def log(s: str):
    print(f"[MITM] {s}")


@app.route("/api/echo", methods=["POST"]) 
def mitm_echo():
    body = request.get_data(as_text=True)
    log(f"Received POST /api/echo with body: {body}")

    # Forward to upstream server; ignore TLS verification for demo simplicity
    upstream_resp = requests.post(
        f"{UPSTREAM}/api/echo",
        data=body,
        headers={k: v for k, v in request.headers if k.lower() != "host"},
        verify=False,
    )

    return Response(upstream_resp.content, status=upstream_resp.status_code, headers=dict(upstream_resp.headers))


@app.route("/")
def mitm_index():
    log("Received GET /")
    upstream_resp = requests.get(f"{UPSTREAM}/", verify=False)
    return Response(upstream_resp.content, status=upstream_resp.status_code, headers=dict(upstream_resp.headers))


if __name__ == "__main__":
    cert_dir = Path(__file__).parent / "certs"
    cert_path = cert_dir / "proxy.crt"
    key_path = cert_dir / "proxy.key"

    if not cert_path.exists() or not key_path.exists():
        raise SystemExit("Missing certs. Run: python certs/generate_certs.py")

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=str(cert_path), keyfile=str(key_path))

    print("MITM proxy listening on https://localhost:9443 forwarding to https://localhost:8443 ...")
    app.run(host="127.0.0.1", port=9443, ssl_context=context)
