#!/usr/bin/env python3
#
# Copyright 2026 Ricardo Gatica M.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Ports App - macOS port monitor TUI
Monitor open ports and kill processes
"""

import subprocess
import os
from dataclasses import dataclass
from typing import List, Optional, Tuple
from textual.app import ComposeResult, App
from textual.widgets import DataTable, Static, Header, Footer
from textual.binding import Binding
from textual.containers import Container, Vertical


@dataclass
class Port:
    port: str
    protocol: str
    process: str
    pid: str
    user: str

    def to_tuple(self):
        return (self.port, self.protocol, self.process, self.pid, self.user)


class PortsApp(App):
    """TUI application for monitoring macOS ports"""

    TITLE = "PUERTOS - macOS"
    BINDINGS = [
        Binding("k", "kill_selected", "Matar"),
        Binding("r", "refresh", "Refrescar"),
        Binding("q", "quit", "Salir"),
    ]

    CSS = """
    Screen {
        background: $surface;
        color: $text;
    }

    Header {
        dock: top;
        height: 3;
        background: $boost;
        color: $text;
        border-bottom: solid $primary;
    }

    #instructions {
        width: 100%;
        height: 1;
        background: $panel;
        color: $text-muted;
        content-align: left middle;
        padding: 0 1;
    }

    DataTable {
        border: solid $primary;
        height: 1fr;
    }

    Footer {
        dock: bottom;
        background: $boost;
        color: $text;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose the UI"""
        yield Header()
        yield Static(
            "↑↓ Navega  •  k Matar  •  r Refrescar  •  q Salir",
            id="instructions"
        )
        yield DataTable(id="ports_table")
        yield Footer()

    def on_mount(self) -> None:
        """Initialize the app"""
        table = self.query_one("#ports_table", DataTable)

        # Setup columns
        table.add_columns(
            "Puerto",
            "Protocolo",
            "Proceso",
            "PID",
            "Usuario"
        )

        # Load ports
        self.load_ports()

    def load_ports(self) -> None:
        """Load open ports from system"""
        try:
            ports = self.get_open_ports()
            table = self.query_one("#ports_table", DataTable)
            table.clear()

            for port in ports:
                table.add_row(*port.to_tuple())

            if not ports:
                table.add_row("—", "—", "Sin puertos abiertos", "—", "—")

        except Exception as e:
            table = self.query_one("#ports_table", DataTable)
            table.clear()
            table.add_row("Error", "—", str(e), "—", "—")

    def get_open_ports(self) -> List[Port]:
        """Get list of open ports using lsof"""
        try:
            # Use lsof to get all internet connections
            result = subprocess.run(
                ["lsof", "-i", "-P", "-n", "-s", "TCP:LISTEN"],
                capture_output=True,
                text=True,
                timeout=5
            )

            ports = []
            lines = result.stdout.split("\n")[1:]  # Skip header

            seen = set()

            for line in lines:
                if not line.strip():
                    continue

                # Split carefully to handle spaces in names
                parts = line.split()
                if len(parts) < 9:
                    continue

                try:
                    # Parse lsof output
                    process = parts[0]
                    pid = parts[1]
                    user = parts[2]

                    # NAME field contains the address:port info
                    name = parts[8]

                    # Extract port and protocol
                    port_info = self.parse_port_info(name)
                    if not port_info:
                        continue

                    port, protocol = port_info

                    # Avoid duplicates
                    key = (port, process, pid)
                    if key in seen:
                        continue
                    seen.add(key)

                    ports.append(Port(
                        port=port,
                        protocol=protocol,
                        process=process[:20],  # Truncate long names
                        pid=pid,
                        user=user
                    ))
                except (IndexError, ValueError):
                    continue

            # Sort by port number
            ports.sort(key=lambda x: int(x.port) if x.port.isdigit() else 0)
            return ports

        except Exception as e:
            return []

    def parse_port_info(self, name: str) -> Optional[Tuple[str, str]]:
        """Parse port and protocol from lsof NAME field"""
        try:
            # Formats:
            # *:3000
            # 127.0.0.1:5000
            # [::1]:8080

            # Remove brackets for IPv6
            name = name.replace("[", "").replace("]", "")

            # Split by last colon
            if ":" in name:
                parts = name.rsplit(":", 1)
                if len(parts) == 2:
                    port = parts[1]
                    if port.isdigit() and 0 < int(port) <= 65535:
                        return (port, "TCP")

            return None
        except Exception:
            return None

    def action_kill_selected(self) -> None:
        """Kill the selected process"""
        table = self.query_one("#ports_table", DataTable)

        try:
            row_key, _ = table.get_cursor()
            row = table.get_row(row_key)

            if len(row) < 4:
                self.notify("Selecciona un proceso válido", timeout=2)
                return

            pid = row[3]
            process = row[2]

            # Try to kill the process
            try:
                subprocess.run(
                    ["kill", "-9", str(pid)],
                    capture_output=True,
                    timeout=5,
                    check=False
                )
                self.notify(f"✓ {process} (PID {pid}) terminado", timeout=2)
                # Refresh after a short delay
                self.call_later(self.action_refresh)
            except Exception as e:
                self.notify(f"✗ Error al matar: {str(e)[:30]}", timeout=2)

        except Exception as e:
            self.notify("Selecciona un proceso primero", timeout=2)

    def action_refresh(self) -> None:
        """Refresh the ports list"""
        self.load_ports()

    def action_quit(self) -> None:
        """Quit the application"""
        self.exit()


def main():
    """Main entry point"""
    app = PortsApp()
    app.run()


if __name__ == "__main__":
    main()
