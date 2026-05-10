from textual.widgets import Static
from rich.text import Text

class StatsBar(Static):
    def update_stats(self, total, filtered, live, honeypots):
        text = Text()
        text.append("📊 ", style="bold")
        text.append(f"Total: {total}", style="cyan")
        text.append(" | ", style="dim")
        text.append(f"Shown: {filtered}", style="bold")
        text.append(" | ", style="dim")
        text.append(f"Live: {live}", style="green")
        text.append(" | ", style="dim")
        text.append(f"Honeypots: {honeypots}", style="yellow")

        self.update(text)
