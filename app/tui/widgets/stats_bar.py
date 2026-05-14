from textual.widgets import Static
from rich.text import Text

class StatsBar(Static):
    def update_stats(self, total, filtered, live, honeypots, wildcard):
        text = Text()
        text.append("📊 ", style="bold")
        text.append(f"Total: {total}", style="#00A3FF")
        if filtered:
            text.append(" | ", style="dim")
            text.append(f"Shown: {filtered}", style="bold #00E0FF")
        if live:
            text.append(" | ", style="dim")
            text.append(f"Live: {live}", style="#73DACA")
        if honeypots:
            text.append(" | ", style="dim")
            text.append(f"Honeypots: {honeypots}", style="#ea5400")
        if wildcard:
            text.append(" | ", style="dim")
            text.append(f"Wildcard: {wildcard}", style="#b50ad8")

        self.update(text)
