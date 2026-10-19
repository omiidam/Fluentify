#!/usr/bin/env python3
"""Read a live Android WebView over the Chrome DevTools Protocol.

`adb install` will not install on this phone without a tap, so the app is
driven from here instead: attach to the WebView's devtools socket, run
expressions against the real page on the real device, and print what comes
back. Everything this prints is observed, not inferred.

    python3 tools/webview_cdp.py "document.title" "typeof Player"
"""
from __future__ import annotations

import asyncio
import json
import subprocess
import sys
import urllib.request

import websockets
from websockets.asyncio.client import connect


def sh(*cmd: str) -> str:
    return subprocess.run(cmd, capture_output=True, text=True).stdout.strip()


def pid() -> str:
    return sh("adb", "shell", "pidof", "app.fluentify")


def attach() -> dict:
    p = pid()
    if not p:
        raise SystemExit("app.fluentify is not running")
    sh("adb", "forward", "--remove-all")
    subprocess.run(["adb", "forward", "tcp:9222",
                    f"localabstract:webview_devtools_remote_{p}"], check=True)
    with urllib.request.urlopen("http://localhost:9222/json", timeout=10) as r:
        targets = json.load(r)
    pages = [t for t in targets if t.get("type") == "page"
             and "index.html" in (t.get("url") or "")]
    if not pages:
        raise SystemExit("no page target")
    return pages[0]


async def main() -> int:
    target = attach()
    url = target["webSocketDebuggerUrl"]
    url = url.replace("localhost", "127.0.0.1")
    exprs = sys.argv[1:] or ["document.title"]
    # A bounded handshake and a per-expression deadline. Without them a
    # renderer that is busy - or one that has gone away - leaves this hanging
    # until something else kills it, which is indistinguishable from the tool
    # being broken.
    try:
        ws = await asyncio.wait_for(
            websockets.connect(url, max_size=32 * 1024 * 1024,
                               open_timeout=15), timeout=20)
    except (asyncio.TimeoutError, OSError) as e:
        raise SystemExit(f"could not attach to the WebView: {e}")

    async with ws:
        n = 0
        for expr in exprs:
            n += 1
            await ws.send(json.dumps({
                "id": n, "method": "Runtime.evaluate",
                "params": {"expression": expr, "returnByValue": True,
                           "awaitPromise": True, "userGesture": True},
            }))
            while True:
                try:
                    msg = json.loads(await asyncio.wait_for(ws.recv(), timeout=25))
                except asyncio.TimeoutError:
                    print(f"  !! {expr}\n     -> no reply within 25s")
                    break
                if msg.get("id") != n:
                    continue
                res = msg.get("result", {})
                if "exceptionDetails" in res:
                    print(f"  !! {expr}\n     -> {res['exceptionDetails'].get('text')} "
                          f"{res['exceptionDetails'].get('exception', {}).get('description', '')}")
                else:
                    val = res.get("result", {}).get("value")
                    print(f"  {expr}\n    = {val!r}")
                break
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))