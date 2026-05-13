from urllib.parse import urlparse, urljoin
import mmh3, hashlib, base64, re
from curl_cffi import requests as req

from .logger import get_logger

log = get_logger("favicon")

KNOWN_FAVICON_HASHES: dict[int, str] = {
    # CMS
    -1255853263: "WordPress",
    116323821: "Joomla",
    -1506805757: "Drupal",
    1085041361: "Ghost CMS",
    -1251682462: "Magento",

    # Web servers / panels
    -335242539: "Nginx default page",
    1771008400: "Apache default page",
    -421993668: "cPanel",
    -1427222059: "Plesk",
    116836539: "Webmin",
    -1534575556: "phpMyAdmin",

    # Network devices
    -1160087947: "Cisco IOS",
    1028723239: "Fortinet FortiGate",
    -1411578193: "Palo Alto Networks",
    -1322284664: "MikroTik",
    -885210565: "pfSense",
    630641635: "Juniper",

    # Monitoring / DevOps
    -880068513: "Grafana",
    1765625046: "Kibana",
    -1135714337: "Prometheus",
    -1399555081: "Zabbix",
    -949425829: "Nagios",
    -1424337732: "Portainer",
    1455260951: "Rancher",

    # Cloud / Infrastructure
    -1983527995: "Jenkins",
    1484180222: "GitLab",
    -1885111544: "Gitea",
    116323821: "Gogs",
    1768835265: "Nexus Repository",
    -1113428726: "SonarQube",

    # Honeypots
    -1474703247: "Glastopf (Honeypot)",
    -728578634: "Cowrie (Honeypot)",
}

def _pick_base_url(subdomain: str, code: int) -> str:
    if code in (200, 301, 302, 307, 308):
        return f"http://{subdomain}"
    return f"http://{subdomain}"

def _fetch_bytes(url: str, timeout: float = 5.0) -> bytes | None:
    try:
        res = req.get(
            url,
            timeout=timeout,
            verify=False,
            allow_redirects=True
        )
    except:
        ...