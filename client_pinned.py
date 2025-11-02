import argparse
import binascii
import hashlib
import socket
import ssl
import json
import requests

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8443
PROXY_PORT = 9443


def get_peer_cert_sha256(host: str, port: int) -> str:
    ctx = ssl.create_default_context()
    with socket.create_connection((host, port)) as sock:
        with ctx.wrap_socket(sock, server_hostname="localhost") as ssock:
            der = ssock.getpeercert(binary_form=True)
    fp = hashlib.sha256(der).hexdigest().upper()
    return fp


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--direct", action="store_true", help="Connect directly to server to demonstrate valid pinning")
    args = parser.parse_args()

    # Learn/pin the legitimate server's fingerprint
    legit_fp = get_peer_cert_sha256(SERVER_HOST, SERVER_PORT)
    print("Pinned server SHA256 fingerprint:", legit_fp)

    target_port = SERVER_PORT if args.direct else PROXY_PORT

    # Check the certificate presented by the target (proxy or server)
    presented_fp = get_peer_cert_sha256(SERVER_HOST, target_port)
    print("Presented SHA256 fingerprint:", presented_fp)

    if presented_fp != legit_fp:
        print("MITM DETECTED: certificate fingerprint mismatch! Aborting request.")
    else:
        # Proceed with a real HTTPS request using the presented cert validated via system store.
        # For demo, we still skip CA verification by providing 'verify=False' because these are self-signed,
        # but in production you'd validate with the CA and also pin.
        url_base = f"https://{SERVER_HOST}:{target_port}"
        print("Making GET and POST with matching fingerprint...")
        r = requests.get(f"{url_base}/", verify=False)
        print("GET / =>", r.status_code, r.text)
        r = requests.post(f"{url_base}/api/echo", json={"hello": "world"}, verify=False)
        print("POST /api/echo =>", r.status_code, r.text)
