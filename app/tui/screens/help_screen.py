from textual.screen import ModalScreen
from textual.widgets import Static
from textual.containers import ScrollableContainer
from textual.binding import Binding
from textual.app import ComposeResult
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.padding import Padding
from rich.console import Group as RichGroup


def _kbd(key: str) -> Text:
    """Render a key label with consistent styling."""
    return Text(key, style="bold #FFD700")


def _section(title: str, rows: list[tuple], key_color: str = "#00E0FF", key_width: int = 18) -> Panel:
    """Build a titled panel with a two-column key→description table."""
    table = Table.grid(padding=(0, 3))
    table.add_column(style=key_color, justify="right", min_width=key_width, no_wrap=True)
    table.add_column(style="#C0CAF5", ratio=1)

    for key, desc in rows:
        if key == "---":
            table.add_row("", "")
        elif isinstance(key, Text):
            table.add_row(key, desc if isinstance(desc, Text) else Text(desc, style="#C0CAF5"))
        else:
            table.add_row(_kbd(key), desc)

    return Panel(
        Padding(table, (0, 1)),
        title=f"[bold #00A3FF]{title}[/]",
        border_style="#1E2030",
        padding=(0, 1),
    )


class HelpScreen(ModalScreen):
    BINDINGS = [
        Binding("escape", "dismiss", "Close"),
        Binding("f1",     "dismiss", "Close"),
        Binding("q",      "dismiss", "Close"),
    ]

    CSS = """
    HelpScreen {
        align: center middle;
        background: rgba(0, 0, 0, 0.75);
    }

    #help-scroll {
        width: 80;
        max-height: 90vh;
        background: #0B0E14;
        border: double #00A3FF;
        padding: 0 1;
    }

    #help-content {
        padding: 1 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield ScrollableContainer(
            Static(self._build_help(), id="help-content"),
            id="help-scroll",
        )

    def _build_help(self):
        header = Text.assemble(
            ("  Keyboard Reference", "bold #FFD700"),
            ("  ·  ", "#565F89"),
            ("ESC / F1 / Q to close", "#565F89"),
        )

        nav_panel = _section("Navigation", [
            ("↑ / ↓",    "Move between rows in the table"),
            ("Enter / D", "Open side detail panel"),
            ("F",         "Open fullscreen detail view"),
            ("Escape",    "Close panel · unfocus filter bar"),
            ("Tab",       "Switch focus between panels"),
        ])

        fs_panel = _section("Fullscreen Actions", [
            ("S",            "Take screenshot  (Playwright / headless Chromium)"),
            ("X",            "Run deep scan on this subdomain"),
            ("P",            "Port scan  —  prompts for range, e.g. 80,443,8000-8100"),
            ("F / Esc / Q",  "Close fullscreen and return to table"),
        ])

        act_panel = _section("Main Table Actions", [
            ("A",        "External tool menu for selected subdomain"),
            ("Shift+A",  "Bulk tool menu for all filtered results"),
            ("B",        "Open subdomain in browser"),
            ("C",        "Copy subdomain to clipboard"),
            ("S",        "Screenshot selected subdomain"),
            ("E",        "Export selected result"),
            ("Shift+E",  "Export all filtered results"),
            ("R",        "Restart scan  (current filter is preserved)"),
            ("Q",        "Quit"),
        ])

        fil_panel = _section("Filter Query Syntax", [
            ("/ (slash)",         "Focus the filter bar"),
            ("---", ""),
            ("status:200",        "Exact HTTP status code"),
            ("status:live",       "HTTP 200 or any redirect"),
            ("status:available",  "Any valid HTTP response"),
            ("status:forbidden",  "401 / 402 / 403"),
            ("status:redirect",   "301 / 302 / 307 / 308"),
            ("status:misconfigured", "526 / 527 / 530  (Cloudflare errors)"),
            ("---", ""),
            ("server:nginx",      "Match server header value"),
            ("tech:php",          "Match detected technology"),
            ("title:admin",       "Match page title keyword"),
            ("subdomain:*.dev.*", "Glob match on subdomain name"),
            ("---", ""),
            ("ip:1.2.3.*",        "IP pattern match  (supports *)"),
            ("ip:proxy",          "Show only CDN / proxy IPs"),
            ("---", ""),
            ("honeypot:true",     "Suspected honeypots  (score ≥ 50%)"),
            ("honeypot:confirmed","Match by confidence label"),
            ("wildcard:true",     "Show / hide wildcard matches"),
            ("---", ""),
            ("size:500-5000",     "Response body size range  (bytes)"),
            ("latency:100-500",   "Response latency range  (ms)"),
            ("port:443",          "Filter by open port"),
            ("---", ""),
            ("has:login",         "Deep scan · login form detected"),
            ("has:register",      "Deep scan · registration page detected"),
            ("has:admin",         "Deep scan · admin panel detected"),
            ("has:credentials",   "Deep scan · hardcoded secrets in JS"),
            ("has:js",            "Deep scan · JS files were scanned"),
            ("---", ""),
            ("NOT status:404",    "Negate any filter"),
        ], key_color="#73DACA", key_width=22)

        tools_panel = _section("External Tools  ( A / Shift+A )", [
            ("Nmap",         "Fast port discovery · full service scan"),
            ("FFuf",         "Directory fuzzing · JSON payload fuzzing"),
            ("SQLMap",       "SQL injection testing"),
            ("Nuclei",       "Vulnerability template scanning"),
            ("Nikto",        "Web server vulnerability scanning"),
            ("WafW00f",      "WAF fingerprinting  (bulk mode supported)"),
            ("WhatWeb",      "Tech fingerprinting  (bulk mode supported)"),
            ("theHarvester", "OSINT — emails, subdomains, names"),
            ("Whois",        "Domain ownership lookup"),
            ("Dig",          "DNS record inspection"),
            ("Curl",         "HTTP header inspection"),
            ("Searchsploit", "Exploit DB search  (auto-matched to detected tech)"),
        ], key_color="#BB9AF7")

        ds_panel = _section("Deep Scan  ( X in fullscreen · --deep-scan )", [
            ("Favicon Hash", "MMH3 hash → known tech / honeypot DB + Shodan query"),
            ("Tech Version", "Header + body → precise version fingerprinting"),
            ("Page Recon",   "URL crawl · login/admin detection · JS secret scanning"),
            ("---", ""),
            (
                Text("⚠  Warning", style="bold #F7768E"),
                Text("Sends many extra HTTP requests per subdomain", style="#F7768E"),
            ),
        ], key_color="#F7768E")

        misc_panel = _section("Other", [
            ("F1",       "Show this help screen"),
            ("% button", "Toggle percentage mode in the stats bar"),
        ])

        return RichGroup(
            Padding(header, (1, 0, 1, 1)),
            nav_panel,
            Padding(Text(""), (0,)),
            fs_panel,
            Padding(Text(""), (0,)),
            act_panel,
            Padding(Text(""), (0,)),
            fil_panel,
            Padding(Text(""), (0,)),
            tools_panel,
            Padding(Text(""), (0,)),
            ds_panel,
            Padding(Text(""), (0,)),
            misc_panel,
            Padding(Text(""), (0,)),
        )

    def action_dismiss(self):
        self.app.pop_screen()