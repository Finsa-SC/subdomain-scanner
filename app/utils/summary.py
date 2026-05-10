from dataclasses import dataclass
import threading

from rich import panel
from rich.table import Table
from rich.console import Console
from rich.panel import Panel

add_lock = threading.Lock()

@dataclass()
class ReconStats:
    ok: int = 0
    redirect: int = 0
    forbidden: int = 0
    rate_limit: int = 0
    ssl_error: int = 0
    conn_error: int = 0
    server_error: int = 0
    dead: int = 0
    other: int = 0
    not_found: int = 0

    def log(self, http_status, https_status):
        code = [http_status, https_status]
        forbidden = (301, 302, 307, 308)
        unauthor = (401, 402, 403)

        with add_lock:
            if any(c == 200 for c in code if isinstance(c, int)):
                self.ok += 1
            elif any(c in forbidden for c in code if isinstance(c, int)):
                self.redirect += 1
            elif any(c in unauthor for c in code if isinstance(c, int)):
                self.forbidden += 1
            elif any(c == 429 for c in code if isinstance(c, int)):
                self.rate_limit += 1
            elif "SSL_ERR" in code:
                self.ssl_error += 1
            elif any(500 <= c <= 504 for c in code if isinstance(c, int)):
                self.server_error += 1
            elif "CONN_ERR" in code:
                self.dead += 1
            elif any(c == 404 for c in code if isinstance(c, int)):
                self.not_found += 1
            else:
                self.other += 1

    def summary(self, time_scan):
        console = Console()
        host_up = (self.ok +
                   self.forbidden +
                   self.server_error +
                   self.redirect +
                   self.not_found +
                   self.other +
                   self.rate_limit
        )

        total_scan = host_up + self.ssl_error + self.dead

        summary_table = Table.grid(padding=(0, 2))
        summary_table.add_column(style="cyan", justify="right")
        summary_table.add_column(style="bold")

        summary_table.add_row("Total Scanned: ", f"{total_scan}")
        summary_table.add_row("Host Up: ", f"[green]{host_up}[/]")

        if self.ok > 0:
            summary_table.add_row("Live (200)", f"[green bold]{self.ok}[/]")
        if self.redirect > 0:
            summary_table.add_row("Redirects", f"[yellow]{self.redirect}[/]")
        if self.forbidden > 0:
            summary_table.add_row("Forbidden (403)", f"[red]{self.forbidden}[/]")
        if self.not_found > 0:
            summary_table.add_row("Not Found (404)", f"[dim]{self.not_found}[/]")
        if self.ssl_error > 0:
            summary_table.add_row("SSL Errors", f"[red]{self.ssl_error}[/]")
        if self.server_error > 0:
            summary_table.add_row("Server Errors", f"[red]{self.server_error}[/]")
        if self.dead > 0:
            summary_table.add_row("No Response", f"[dim]{self.dead}[/]")
        if self.rate_limit > 0:
            summary_table.add_row("Rate Limited", f"[yellow]{self.rate_limit}[/]")
        if self.other > 0:
            summary_table.add_row("Other", f"[dim]{self.other}[/]")

        summary_table.add_row("", "")
        summary_table.add_row("Duration", f"{time_scan:.2f}s")
        summary_table.add_row("Speed", f"{total_scan/time_scan:.1f} req/s")

        console.print("\n")
        console.print(Panel(
            summary_table,
            title="[bold cyan]Scan Summary[/]",
            border_style="cyan",
            padding=(0, 2)
        ))