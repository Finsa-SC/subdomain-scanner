class ReconStats:
    def __init__(self):
        super().__setattr__('allowed', ['ok', 'forbidden', 'ssl_error', 'server_error', 'dead'])
        for name in self.allowed:
            super().__setattr__(f"_{name}", 0)

    def log(self, http_status, https_status):
        code = [http_status, https_status]

        if any(isinstance(c, int) and c in (200, 301, 302) for c in code):
            self.ok += 1
        elif any(isinstance(c, int) and c in (402, 403) for c in code):
            self.forbidden += 1
        elif "SSL_ERR" in code:
            self.ssl_error += 1
        elif "CONN_ERR" in code:
            self.dead += 1
        elif any(isinstance(c, int) and 500 <= c <= 504 for c in code):
            self.server_error += 1

    def summary(self):
        print("\n\nSummary:")
        print(f"Host Up      : {self.ok}")
        print(f"Forbidden    : {self.forbidden}")
        print(f"SSL Error    : {self.ssl_error}")
        print(f"Server Error : {self.server_error}")
        print(f"No Response  : {self.dead}")

    def __setattr__(self, name, value):
        if name in getattr(self, 'allowed', []):
            current = getattr(self, f"{name}")

            if value < 0 or value > current + 1:
                print("[!] Alert: attempt to manipulate points")
                return
            super().__setattr__(f"_{name}", value)
        else:
            super().__setattr__(name, value)

    def __getattr__(self, name):
        if name in self.allowed:
            return getattr(self, f"_{name}")
        raise AttributeError