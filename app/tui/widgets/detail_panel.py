from textual.widgets import Static
from rich.panel import Panel
from rich.table import Table
from rich.rule import Rule
from rich.text import Text
from .subdomain_table import _normalize_status

class DetailPanel(Static):
    def show_detail(self, result):
        if not result:
            self.update("")
            return

        detail_table = Table.grid(padding=(0, 1))
        detail_table.add_column(style="#565F89", justify="right")
        detail_table.add_column(style="#00E0FF")

        detail_table.add_row("IP: ", result.get("ip_address", "No IP"))

        http = result.get("http", {})
        https = result.get("https", {})
        h_lat = http.get("latency")
        s_lat = https.get("latency")
        h_st = _normalize_status(http.get("status"))
        s_st = _normalize_status(https.get("status"))

        detail_table.add_row("", "")
        detail_table.add_row("[bold]HTTP", "")
        detail_table.add_row("  Status:", str(h_st))
        detail_table.add_row("  Server:", http.get("server", "Unknown"))
        detail_table.add_row("  Latency:", f"{h_lat}ms" if h_lat is not None else "N/A")
        detail_table.add_row("  Title:", http.get("title", "-"))

        detail_table.add_row("", "")
        detail_table.add_row("[bold]HTTPS", "")
        detail_table.add_row("  Status:", str(s_st))
        detail_table.add_row("  Server:", https.get("server", "Unknown"))
        detail_table.add_row("  Latency:", f"{s_lat}ms" if s_lat is not None else "N/A")
        detail_table.add_row("  Title:", https.get("title", "-"))


        score = result.get("honeypot_score")
        if score is None:

            score = result.get("is_honeypot", 0)
            if isinstance(score, bool):
                score = 1.0 if score else 0.0

        label = result.get("honeypot_label", "")

        filled = int(score * 10)
        bar_char = ["░"] * 10

        for i in range(filled):
            if i < 2.5:
                bar_char[i] = "[#00E0FF]█[/]"
            elif i < 5:
                bar_char[i] = "[#00C8FF]█[/]"
            elif i < 7.5:
                bar_char[i] = "[#00A3FF]█[/]"
            else:
                bar_char[i] = "[#0077BB]█[/]"

        bar = "".join(bar_char)

        if score >= 0.75:
            text_color = "#F7768E"
        elif score >= 0.5:
            text_color = "#FFD700"
        else:
            text_color = "#565F89"

        detail_table.add_row("", "")
        detail_table.add_row("Honeypot:", f"{bar} [{text_color}] {score * 100:.0f}%[/]")

        detail_table.add_row("Label:", f"[{text_color} bold]{label}[/]")
        if result.get("wildcard"):
            detail_table.add_row("Wildcard:", "[#00E0FF]Detected[/]")
        else:
            detail_table.add_row("Wildcard:", "")


        panel = Panel(
            detail_table,
            title=f"[bold #00E0FF]{result.get('subdomain', '')}[/]",
            border_style="#FFD700")
        self.update(panel)

