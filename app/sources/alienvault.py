# ===================================================
### API KEY is needed for This request
# ===================================================


import requests

def fetch_alienvault(domain: str):
    subdomains = set()
    url = f"https://otx.alienvault.com/api/v1/indicators/domain/{domain}/passive_dns"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code != 200:
            return subdomains
        data = res.json()
        print(data)
        for entry in data.get("passive_dns", []):
            hostname = entry.get("hostname")
            if hostname:
                sub = hostname.strip().lower()
                if sub and (sub.endswith(f".{domain}") or sub == domain):
                    yield sub
    except Exception as e:
        print(e)
    finally:
        return subdomains