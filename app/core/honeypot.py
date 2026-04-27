from models import HONEYPOT_TITLE, HONEYPOT_NAME, HONEYPOT_HASHES, HONEYPOT_SERVERS, OBSOLETE_VERSIONS
from utils import is_cloudflare

class HoneypotAnalyzer:
    def __init__(self, sub_info, config):
        self.sub_info = sub_info
        self.config = config
        self.chance = 0
        self.findings = []

    def check_static(self):
        sub = self.sub_info["subdomain"].lower()
        http_title = self.sub_info["http_title"].lower()
        https_title = self.sub_info["https_title"].lower()
        server = self.sub_info["server"].lower()

        for pattern, weight in HONEYPOT_NAME.items():
            if pattern in sub:
                self.chance += weight
                self.findings.append("Unusual subdomain")

        for pattern, weight in HONEYPOT_TITLE:
            if http_title in pattern or https_title in pattern:
                self.chance += weight
                self.findings.append("Clickbait title")

        for pattern, weight in HONEYPOT_SERVERS.items():
            if server in pattern:
                self.chance += weight
                self.findings.append("Suspicious server signature")

        if any(v in server for v in OBSOLETE_VERSIONS):
            self.chance += 25
            self.findings.append(f"Server is leaking an obsolete/vulnerable version: '{server}'")

        if is_cloudflare(self.sub_info["ip_address"]) and "cloudflare" not in server:
            self.chance += 30
            self.findings.append("Cloudflare detected but server header is leaking backend info (High Anomaly)")



    def check_structural(self):


    def check_behavioral(self):
        ...

    def run_all(self):
        return self.chance, self.findings