import requests
import ijson

def fetch_crtsh(domain: str):
    url = f"https://crt.sh/?q={domain}&output=json"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            for entry in ijson.items(res.raw, "item"):
                name = entry['name_value'].lower()
                for n in name.split("\n"):
                    clean = n.replace("*.", "").strip()
                    if clean:
                        yield clean
    except:
        ...
    finally:
        return