from utils import get_logger
import re

log = get_logger("tech_version")

HEADER_PATTERNS = [
    # Server header
    {"tech": "Nginx", "header": "server", "pattern": r"nginx[/\s]([\d.]+)"},
    {"tech": "Apache", "header": "server", "pattern": r"apache[/\s]([\d.]+)"},
    {"tech": "IIS", "header": "server", "pattern": r"microsoft-iis[/\s]([\d.]+)"},
    {"tech": "LiteSpeed", "header": "server", "pattern": r"litespeed[/\s]([\d.]+)"},
    {"tech": "Caddy", "header": "server", "pattern": r"caddy[/\s]([\d.]+)"},
    {"tech": "OpenResty", "header": "server", "pattern": r"openresty[/\s]([\d.]+)"},
    {"tech": "Tengine", "header": "server", "pattern": r"tengine[/\s]([\d.]+)"},
    {"tech": "Cloudflare", "header": "server", "pattern": r"cloudflare"},
    # X-Powered-By
    {"tech": "PHP", "header": "x-powered-by", "pattern": r"php[/\s]([\d.]+)"},
    {"tech": "ASP.NET", "header": "x-powered-by", "pattern": r"asp\.net"},
    {"tech": "Express", "header": "x-powered-by", "pattern": r"express[/\s]?([\d.]*)"},
    {"tech": "Next.js", "header": "x-powered-by", "pattern": r"next\.js[/\s]?([\d.]*)"},
    # Versi spesifik dari header lain
    {"tech": "ASP.NET", "header": "x-aspnet-version", "pattern": r"([\d.]+)"},
    {"tech": "Varnish", "header": "x-varnish", "pattern": r".+"},
    {"tech": "Varnish", "header": "via", "pattern": r"varnish[/\s]?([\d.]*)"},
    # CDN / proxy
    {"tech": "Cloudflare", "header": "cf-ray", "pattern": r".+"},
    {"tech": "Fastly", "header": "x-served-by", "pattern": r"cache-"},
    {"tech": "Akamai", "header": "x-check-cacheable", "pattern": r".+"},
]

### Pattern from BODY HTML
BODY_PATTERNS = [
    # Meta generator — paling reliable
    {"tech": "WordPress", "pattern": r'<meta[^>]+name=["\']generator["\'][^>]+content=["\']WordPress ([\d.]+)',
     "source": "meta generator"},
    {"tech": "Joomla", "pattern": r'<meta[^>]+name=["\']generator["\'][^>]+content=["\']Joomla[!\s]*([\d.]*)',
     "source": "meta generator"},
    {"tech": "Drupal", "pattern": r'<meta[^>]+name=["\']generator["\'][^>]+content=["\']Drupal ([\d.]+)',
     "source": "meta generator"},
    {"tech": "Ghost", "pattern": r'<meta[^>]+name=["\']generator["\'][^>]+content=["\']Ghost ([\d.]+)',
     "source": "meta generator"},
    {"tech": "Magento", "pattern": r'<meta[^>]+name=["\']generator["\'][^>]+content=["\']Magento[/\s]*([\d.]*)',
     "source": "meta generator"},
    {"tech": "TYPO3", "pattern": r'<meta[^>]+name=["\']generator["\'][^>]+content=["\']TYPO3 ([\d.]+)',
     "source": "meta generator"},
    {"tech": "Wix", "pattern": r'<meta[^>]+name=["\']generator["\'][^>]+content=["\']Wix\.com',
     "source": "meta generator"},
    {"tech": "Shopify", "pattern": r'Shopify\.theme\s*=\s*\{[^}]*"version"\s*:\s*"([\d.]+)"', "source": "js variable"},
    {"tech": "Laravel", "pattern": r'<meta[^>]+name=["\']csrf-token["\']', "source": "meta csrf"},

    # Script src dengan ?ver= (WordPress style)
    {"tech": "WordPress", "pattern": r'/wp-(?:content|includes)/[^"\']+\?ver=([\d.]+)', "source": "script ver param"},
    {"tech": "jQuery", "pattern": r'jquery[.-]([\d.]+)(?:\.min)?\.js', "source": "script src"},
    {"tech": "jQuery UI", "pattern": r'jquery-ui[.-]([\d.]+)(?:\.min)?\.js', "source": "script src"},
    {"tech": "Bootstrap", "pattern": r'bootstrap[.-]([\d.]+)(?:\.min)?\.(?:js|css)', "source": "script src"},
    {"tech": "React", "pattern": r'react(?:\.min)?\.js\?v=([\d.]+)|"react"\s*:\s*"([\d.]+)"', "source": "script src"},
    {"tech": "Vue.js", "pattern": r'vue(?:\.min)?\.js\?v=([\d.]+)|["\']vue["\']:\s*["\'](\^?[\d.]+)',
     "source": "script src"},
    {"tech": "Angular", "pattern": r'@angular/core@([\d.]+)', "source": "script src"},

    # HTML comment signatures
    {"tech": "WordPress", "pattern": r'<!--\s*This site is optimized with the Yoast SEO', "source": "html comment"},
    {"tech": "Drupal", "pattern": r'<!--\s*Drupal\s*([\d.]*)', "source": "html comment"},

    # Path signatures
    {"tech": "WordPress", "pattern": r'/wp-content/themes/([^/"\']+)', "source": "wp theme path"},
    {"tech": "Joomla", "pattern": r'/components/com_', "source": "joomla path"},
    {"tech": "Drupal", "pattern": r'/sites/(?:default|all)/(?:modules|themes)/', "source": "drupal path"},

    # Framework-specific markers
    {"tech": "Django", "pattern": r'csrfmiddlewaretoken', "source": "csrf token"},
    {"tech": "Ruby on Rails", "pattern": r'<meta[^>]+name=["\']csrf-param["\']', "source": "meta csrf-param"},
    {"tech": "ASP.NET", "pattern": r'__VIEWSTATE|__EVENTVALIDATION', "source": "asp.net viewstate"},
    {"tech": "ColdFusion", "pattern": r'cfid=|cftoken=', "source": "cf cookies"},

    # CMS admin paths
    {"tech": "WordPress", "pattern": r'wp-login\.php', "source": "wp login path"},
    {"tech": "phpMyAdmin", "pattern": r'<title>phpMyAdmin</title>', "source": "title"},
]

SOURCE_PRIORITY = {
    "meta generator": 1,
    "server header": 2,
    "x-powered-by header": 2,
    "x-aspnet-version header": 2,
    "js variable": 3,
    "script src": 4,
    "script ver param": 5,
    "html comment": 4,
    "wp theme path": 9,
    "joomla path": 9,
    "drupal path": 9,
}

def _match_version(pattern: str, text: str) -> str | None:
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    if not match:
        return None

    if match.lastindex:
        for i in range(1, match.lastindex + 1):
            g = match.group(1)
            if g and g.strip():
                return g.strip()
    return "detected"

def _scan_headers(headers: dict) -> list[dict]:
    results = []
    if not headers:
        return results

    h = {k.lower(): v for k, v in headers.items()}
    seen = set
    for pattern in HEADER_PATTERNS:
        val = h.get(pattern["header"].lower(), "")
        if not val:
            continue
        version = _match_version(pattern["pattern"], str(val))
        if not version:
            continue
        key = f"{pattern['tech']}:{version}"
        if key in seen:
            continue
        seen.add(key)
        results.append({
            "tech": pattern["tech"],
            "version": version,
            "source": f"{pattern['header']} header"
        })
    return results

def _fetch_body(result: dict, timeout: float = 8.0) -> str | None:
    import urllib3
    from curl_cffi import requests
    from core import StealthMode

    urllib3.disable_warnings()

    subdomain = result.get("subdomain", "")
    https_result = result.get("https", {}).get("status")
    url = f"https://{subdomain}" if https_result in (200, 301, 302, 307, 308) else f"http://{subdomain}"

    stealth = StealthMode()
    headers, engine = stealth.get_payload()

    try:
        res = requests.get(
            url=url,
            timeout=timeout,
            headers=headers,
            impersonate=engine,
            allow_redirects=True,
            verify=False,
        )
        if res.status_code == 200 and res.content:
            res.encoding = res.charset_encoding or "utf-8"
            return res.text
        return None
    except Exception as e:
        log.debug(f"_fetch_body failed {subdomain}: {e}")
        return None


