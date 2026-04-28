from models import USER_AGENT_FALLBACK

import random
from fake_useragent import UserAgent
import logging

logging.getLogger('fake_useragent').setLevel(logging.CRITICAL)

class StealthMode:
    def __init__(self):
        self.ua_active = False
        try:
            self.ua = UserAgent()
            self.ua_active = True
        except:
            self.ua = None
        self.base_headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "DNT": "1"
        }

    def get_jumbled_header(self) -> dict[str, str]:
        header = self.base_headers.copy()

        if self.ua_active:
            try:
                header["User-Agent"] = self.ua.random if self.ua else self._get_manual_ua()
            except:
                header["User-Agent"] = self._get_manual_ua()
        else:
            header["User-Agent"] = self._get_manual_ua()

        header_items = list(header.items())
        random.shuffle(header_items)
        header_dict = dict(header_items)

        return dict(header_dict)

    def _get_manual_ua(self) -> str:
        fallbacks = USER_AGENT_FALLBACK
        return random.choice(fallbacks)

