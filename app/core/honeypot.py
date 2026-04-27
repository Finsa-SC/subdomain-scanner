from models import HONEYPOT_TITLE, HONEYPOT_NAME, HONEYPOT_HASHES, HONEYPOT_SERVERS, OBSOLETE_VERSIONS, \
    SUSPICIOUS_HEADER_ORDERS
from utils import is_cloudflare

class HoneypotAnalyzer:
    def __init__(self, data, config):
        self.data = data
        self.http = data["http"]
        self.https = data["https"]
        self.config = config
        self.chance = 0
        self.findings = []

    def check_static(self):
        sub = self.data["subdomain"].lower()
        h_title = self.http["title"].lower()
        s_title = self.https["title"].lower()
        h_server = self.http["server"].lower()
        s_server = self.https["server"].lower()

        for pattern, weight in HONEYPOT_NAME.items():
            if pattern in sub:
                self.chance += weight
                self.findings.append("Unusual subdomain")

        for pattern, weight in HONEYPOT_TITLE:
            if pattern in [h_title, s_title]:
                self.chance += weight
                self.findings.append("Clickbait title")

        for pattern, weight in HONEYPOT_SERVERS.items():
            if h_server in pattern or s_server in pattern:
                self.chance += weight
                self.findings.append("Suspicious server signature")

        if any(v in h_server for v in OBSOLETE_VERSIONS) or any(v in s_server for v in OBSOLETE_VERSIONS):
            self.chance += 25
            self.findings.append(f"Server is leaking an obsolete/vulnerable version: '{h_server or s_server}'")

        if s_server != h_server and "Unknown" not in [h_server, s_server]:
            self.chance += 15
            self.findings.append("Different server")

        if is_cloudflare(self.data["ip_address"]) and "cloudflare" not in [h_server, s_server]:
            self.chance += 30
            self.findings.append("Cloudflare detected but server header is leaking backend info (High Anomaly)")



    def check_structural(self):
        h_hash = self.http.get("body_hash")
        s_hash = self.https.get("body_hash")
        h_keys = [k.lower() for k in self.http.get("header_keys", [])]
        s_keys = [k.lower() for k in self.https.get("header_keys", [])]

        for b_hash in [h_hash, s_hash]:
            if b_hash in HONEYPOT_HASHES:
                self.chance += 50
                self.findings.append(f"Content hash matches known honeypot: {HONEYPOT_HASHES[b_hash]}")
                break

        for keys in [h_keys, s_keys]:
            if not keys: return
            for trap_order in SUSPICIOUS_HEADER_ORDERS:
                if all(item in keys for item in trap_order):
                    indices = [keys.index(item) for item in trap_order]
                    if indices == sorted(indices):
                        self.chance += 20
                        self.findings.append("Suspicious HTTP header ordering detected")
                        break

        h_size = self.http.get("size", 0)
        s_size = self.https.get("size", 0)
        if h_size == s_size and h_size > 0:
            self.chance += 10
            self.findings.append("Identical response size on both protocols")


    def check_behavioral(self):
        ...

    def run_all(self):
        self.check_static()
        self.check_structural()

        return min(self.chance, 100), self.findings