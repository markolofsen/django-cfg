"""Native CMDOP foreground workspace for the canonical customer Git root.

The machine identity lives in a private volume, not in a copied public checkout.
No Docker socket or host-wide filesystem is granted to this workspace.
"""
import json
import os
from pathlib import Path
import time

machine = Path.home() / ".config/cmdop/machine.json"
notified = False
while True:
    try:
        saved = json.loads(machine.read_text()) if machine.exists() else {}
        server = saved.get("server") or os.environ.get("CMDOP_SERVER")
    except (OSError, ValueError, TypeError):
        server = None
    if server:
        os.execvp("cmdop", ["cmdop", "run", "--server", server, "--name",
                            os.environ["CMDOP_MACHINE_NAME"], "--no-sessions"])
    if not notified:
        print("CMDOP awaiting_admission: this customer machine needs its own identity and owner grant.", flush=True)
        notified = True
    time.sleep(5)
