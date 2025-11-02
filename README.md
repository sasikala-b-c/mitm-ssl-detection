# MITM over TLS: Simulation and Detection via Certificate Pinning

This mini-project demonstrates a simple TLS MITM (Man-In-The-Middle) scenario and how certificate pinning can detect it.

Components:
- HTTPS server ("victim" service) on https://localhost:8443
- HTTPS MITM proxy on https://localhost:9443 that logs and forwards traffic to the server
- Naive client that ignores verification and is vulnerable
- Secure client that performs certificate pinning and detects the MITM

## Prerequisites
- Python 3.9+
- Windows/macOS/Linux

## Setup
1) Create and activate a virtual environment
```
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux
```

2) Install dependencies
```
pip install -r requirements.txt
```

3) Generate self-signed certificates for the server and the proxy
```
python certs/generate_certs.py
```
This creates:
- certs/server.crt, certs/server.key
- certs/proxy.crt, certs/proxy.key

## Run
Open three terminals (with venv activated) and run:

1) Start the HTTPS server
```
python server.py
```

2) Start the MITM proxy
```
python proxy.py
```

3) In another terminal, run the clients.

- Naive client (VULNERABLE): connects to the proxy with TLS verification disabled, request succeeds and data is logged by the proxy.
```
python client_naive.py
```

- Secure client (PINNED): expects the server's certificate fingerprint when connecting to the proxy. It will FAIL and report a MITM detection because the proxy presents a different certificate.
```
python client_pinned.py
```

Optionally, confirm the pinned client trusts the real server when connecting directly:
```
python client_pinned.py --direct
```

## What happens
- The proxy terminates TLS using its own certificate, reads/prints the request body, then forwards the request to the real server and relays back the response.
- The naive client skips verification and is thus vulnerable.
- The pinned client computes the certificate fingerprint during the TLS handshake and compares it with the expected fingerprint of the real server certificate. A mismatch indicates a MITM.

## Notes
- This demo uses self-signed certificates generated locally to avoid CA complexities.
- Do not expose these keys or use them in production. They are for demo only.

## License
MIT
# mitm-ssl-detection
