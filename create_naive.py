import requests

PROXY_URL = "https://127.0.0.1:9443"

if __name__ == "__main__":
    print("Naive client: sending to proxy with verify=False (INSECURE)...")
    r = requests.get(f"{PROXY_URL}/", verify=False)
    print("GET / =>", r.status_code, r.text)

    r = requests.post(f"{PROXY_URL}/api/echo", json={"secret": "top"}, verify=False)
    print("POST /api/echo =>", r.status_code, r.text)
