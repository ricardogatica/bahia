#!/usr/bin/env python3
#
# Copyright 2026 Ricardo Gatica
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
Bahia - macOS port monitor TUI
Monitor open ports and kill processes
"""

import subprocess
import os
import sys
import json
import time
import urllib.request
import urllib.error
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional, Tuple
from textual import work
from textual.app import ComposeResult, App
from textual.widgets import DataTable, Static, Header, Footer
from textual.binding import Binding
from textual.containers import Container, Vertical


# ----- versioning / updates -----
REPO = os.environ.get("BAHIA_REPO", "ricardogatica/bahia")
REF = os.environ.get("BAHIA_REF", "main")
INSTALL_DIR = Path(__file__).resolve().parent
RAW_VERSION_URL = f"https://raw.githubusercontent.com/{REPO}/{REF}/VERSION"
UPDATE_CACHE = Path.home() / ".cache" / "bahia" / "update_check.json"
UPDATE_CACHE_TTL = 24 * 60 * 60  # seconds


def get_version() -> str:
    """Read the local version from the VERSION file (single source of truth)."""
    try:
        return (INSTALL_DIR / "VERSION").read_text().strip() or "0.0.0"
    except Exception:
        return "0.0.0"


__version__ = get_version()


def _parse_version(v: str) -> Tuple[int, ...]:
    """Turn '1.2.3' into (1, 2, 3) for comparison; ignores non-numeric parts."""
    parts = []
    for chunk in v.strip().split("."):
        num = "".join(c for c in chunk if c.isdigit())
        parts.append(int(num) if num else 0)
    return tuple(parts) if parts else (0,)


def fetch_latest_version(timeout: float = 4.0) -> Optional[str]:
    """Fetch the published version from GitHub. Returns None on any failure."""
    try:
        req = urllib.request.Request(
            RAW_VERSION_URL,
            headers={"User-Agent": f"bahia/{__version__}"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8").strip()
    except Exception:
        return None


def check_for_update(use_cache: bool = True) -> Optional[str]:
    """Return the latest version if it's newer than the local one, else None.

    Caches the result for UPDATE_CACHE_TTL so we don't hit the network on
    every launch.
    """
    if use_cache:
        try:
            cached = json.loads(UPDATE_CACHE.read_text())
            if time.time() - cached.get("ts", 0) < UPDATE_CACHE_TTL:
                latest = cached.get("latest")
                if latest and _parse_version(latest) > _parse_version(__version__):
                    return latest
                if latest:
                    return None  # cache fresh and we're up to date
        except Exception:
            pass

    latest = fetch_latest_version()
    if latest:
        try:
            UPDATE_CACHE.parent.mkdir(parents=True, exist_ok=True)
            UPDATE_CACHE.write_text(json.dumps({"ts": time.time(), "latest": latest}))
        except Exception:
            pass
        if _parse_version(latest) > _parse_version(__version__):
            return latest
    return None


@dataclass
class Port:
    port: str
    protocol: str
    process: str
    pid: str
    user: str

    def to_tuple(self):
        return (self.port, self.protocol, self.process, self.pid, self.user)


class BahiaApp(App):
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

    #update_banner {
        width: 100%;
        height: 1;
        display: none;
        background: $warning;
        color: $text;
        content-align: left middle;
        padding: 0 1;
    }

    #update_banner.visible {
        display: block;
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
        yield Static("", id="update_banner")
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

        # Check for a new version in the background (non-blocking).
        self.check_update_worker()

    @work(thread=True, exclusive=True)
    def check_update_worker(self) -> None:
        """Look for a newer published version without blocking the UI."""
        latest = check_for_update()
        if latest:
            self.call_from_thread(self._show_update_banner, latest)

    def _show_update_banner(self, latest: str) -> None:
        """Display the 'update available' banner."""
        try:
            banner = self.query_one("#update_banner", Static)
            banner.update(
                f"⬆ Actualización disponible: v{__version__} → v{latest}"
                "   ·   ejecuta:  bahia --update"
            )
            banner.add_class("visible")
        except Exception:
            pass

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

    def get_pids_for_port(self, port: str) -> List[str]:
        """Get every PID listening on a port (equivalent to lsof -ti :port)"""
        try:
            result = subprocess.run(
                ["lsof", "-ti", f":{port}", "-s", "TCP:LISTEN"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False
            )
            pids = [p.strip() for p in result.stdout.split("\n") if p.strip().isdigit()]
            # Deduplicate while preserving order
            return list(dict.fromkeys(pids))
        except Exception:
            return []

    def action_kill_selected(self) -> None:
        """Kill every process listening on the selected port"""
        table = self.query_one("#ports_table", DataTable)

        if table.row_count == 0:
            self.notify("No hay procesos para matar", timeout=2)
            return

        try:
            row = table.get_row_at(table.cursor_row)
        except Exception:
            self.notify("Selecciona un proceso primero", timeout=2)
            return

        if len(row) < 4:
            self.notify("Selecciona un proceso válido", timeout=2)
            return

        port = str(row[0]).strip()
        process = row[2]

        if not port.isdigit():
            self.notify("Selecciona un proceso válido", timeout=2)
            return

        # A single port can have several PIDs (e.g. forked workers).
        # Kill them all, just like `lsof -ti :PORT | xargs kill`.
        pids = self.get_pids_for_port(port)
        if not pids:
            self.notify(f"No hay procesos en el puerto {port}", timeout=2)
            return

        killed = []
        failed = []
        for pid in pids:
            try:
                result = subprocess.run(
                    ["kill", "-9", pid],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    check=False
                )
                if result.returncode == 0:
                    killed.append(pid)
                else:
                    failed.append(pid)
            except Exception:
                failed.append(pid)

        if killed and not failed:
            count = f"{len(killed)} proceso" + ("s" if len(killed) > 1 else "")
            self.notify(
                f"✓ {process} — puerto {port} liberado ({count})",
                timeout=2
            )
        elif killed and failed:
            self.notify(
                f"⚠ Puerto {port}: {len(killed)} terminados, "
                f"{len(failed)} fallaron (¿permisos?)",
                timeout=4
            )
        else:
            self.notify(
                f"✗ No se pudo liberar el puerto {port} (¿permisos?)",
                timeout=4
            )

        # Refresh after killing
        self.call_later(self.action_refresh)

    def action_refresh(self) -> None:
        """Refresh the ports list"""
        self.load_ports()

    def action_quit(self) -> None:
        """Quit the application"""
        self.exit()


def do_update() -> int:
    """Update Bahia in place. Returns a process exit code."""
    print(f"\n🔄 Bahia v{__version__} — buscando actualizaciones...\n")

    latest = fetch_latest_version()
    if latest:
        if _parse_version(latest) <= _parse_version(__version__):
            print(f"  ✓ Ya tienes la última versión (v{__version__}).\n")
            return 0
        print(f"  Nueva versión disponible: v{__version__} → v{latest}\n")

    # Preferred path: the install is a git checkout (~/.bahia), update via git.
    if (INSTALL_DIR / ".git").exists():
        print(f"  📥 Actualizando {INSTALL_DIR} ...")
        try:
            subprocess.run(
                ["git", "-C", str(INSTALL_DIR), "fetch", "--depth=1", "origin", REF],
                check=True, capture_output=True, text=True,
            )
            subprocess.run(
                ["git", "-C", str(INSTALL_DIR), "reset", "--hard", f"origin/{REF}"],
                check=True, capture_output=True, text=True,
            )
            print("  ✓ Código actualizado")
        except subprocess.CalledProcessError as e:
            print(f"  ✗ Error al actualizar el código: {(e.stderr or '').strip()}")
            return 1

        print("  📦 Actualizando dependencias ...")
        req = INSTALL_DIR / "requirements.txt"
        pip_target = ["-r", str(req)] if req.exists() else ["textual"]
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "--quiet", "--upgrade", *pip_target],
                check=True, capture_output=True, text=True,
            )
            print("  ✓ Dependencias actualizadas")
        except subprocess.CalledProcessError as e:
            print(f"  ⚠ No se pudieron actualizar las dependencias: {(e.stderr or '').strip()}")

        new_version = get_version()
        print(f"\n✓ Bahia actualizado a v{new_version}. Vuelve a ejecutar:  bahia\n")
        return 0

    # Fallback: not a git checkout — re-run the remote installer.
    print("  ℹ Instalación no-git: ejecutando el instalador remoto...\n")
    installer = f"https://raw.githubusercontent.com/{REPO}/{REF}/install.sh"
    cmd = f'sh -c "$(curl -fsSL {installer})"'
    try:
        subprocess.run(cmd, shell=True, check=True)
        return 0
    except subprocess.CalledProcessError:
        print(
            "\n  ✗ No se pudo actualizar automáticamente. Reinstala con:\n"
            f"      {cmd}\n"
        )
        return 1


HELP_TEXT = f"""Bahia v{__version__} — Monitor de Puertos macOS

Uso:
  bahia              Abrir el monitor de puertos (TUI)
  bahia --update     Actualizar Bahia a la última versión
  bahia --version    Mostrar la versión instalada
  bahia --help       Mostrar esta ayuda

Controles dentro de la app:
  ↑↓  navegar  ·  k  liberar puerto  ·  r  refrescar  ·  q  salir
"""


def main():
    """Main entry point"""
    args = sys.argv[1:]

    if args:
        arg = args[0]
        if arg in ("--update", "update", "-u"):
            sys.exit(do_update())
        if arg in ("--version", "-v"):
            print(f"bahia {__version__}")
            sys.exit(0)
        if arg in ("--help", "-h", "help"):
            print(HELP_TEXT)
            sys.exit(0)
        print(f"Opción desconocida: {arg}\n")
        print(HELP_TEXT)
        sys.exit(2)

    app = BahiaApp()
    app.run()


if __name__ == "__main__":
    main()
