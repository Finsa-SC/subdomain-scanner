import sys
from textual.app import App
from textual.binding import Binding
from .screens.main_screen import MainScreen
from core import app_state

class SubdomainScannerTUI(App):
    CSS_PATH = "styles.css"

    BINDINGS = [
        Binding("q", "force_quit", "Quit", priority=True),
        Binding("ctrl+c", "force_quit", "Quit", show=False)
    ]

    def __init__(self, config, domain_or_file):
        super().__init__()
        self.scan_config = config
        self.domain_or_file = domain_or_file

    def on_mount(self) -> None:
        self.push_screen(MainScreen(self.scan_config, self.domain_or_file))

    def action_force_quit(self):
        app_state.stop()
        self.exit()
        sys.exit(0)

def run_tui(config, domain_or_file):
    app = SubdomainScannerTUI(config, domain_or_file)
    app.run()