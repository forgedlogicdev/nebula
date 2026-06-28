#!/usr/bin/env python3
"""Nebula Game Hub — web UI for managing the HP Mini game library.
Serves a dark-themed dashboard at http://10.0.0.108:8080"""

import json, os, subprocess, time, http.server, socketserver, urllib.parse, threading

APPS_FILE = os.path.expanduser("~/.config/sunshine/apps.json")
PORT = 8080

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>NEBULA GAME HUB</title>
<style>
  *{margin:0;padding:0;box-sizing:border-box}
  body{background:#060610;color:#ccc;font-family:'SF Mono','Fira Code',monospace;min-height:100vh}
  .bg{position:fixed;inset:0;background:radial-gradient(ellipse 60% 40% at 50% 0%,rgba(80,20,120,0.15),transparent),radial-gradient(ellipse 50% 30% at 80% 80%,rgba(20,60,140,0.1),transparent);pointer-events:none}
  .container{max-width:900px;margin:0 auto;padding:32px 20px;position:relative}
  h1{font-size:28px;font-weight:200;letter-spacing:12px;text-align:center;color:rgba(160,140,220,0.7);margin-bottom:8px}
  .subtitle{text-align:center;color:rgba(160,140,220,0.2);font-size:10px;letter-spacing:6px;margin-bottom:40px}
  
  .stats{display:flex;gap:12px;margin-bottom:32px;flex-wrap:wrap}
  .stat{flex:1;min-width:120px;background:rgba(10,8,24,0.6);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,0.04);border-radius:14px;padding:16px 18px}
  .stat-label{color:rgba(255,255,255,0.2);font-size:9px;letter-spacing:2px;text-transform:uppercase;margin-bottom:6px}
  .stat-value{color:rgba(200,180,240,0.8);font-size:22px;font-weight:200}
  .stat-unit{font-size:12px;opacity:0.4}

  .section-title{color:rgba(255,255,255,0.25);font-size:11px;letter-spacing:4px;text-transform:uppercase;margin-bottom:14px}
  
  .game-list{display:flex;flex-direction:column;gap:8px;margin-bottom:32px}
  .game-card{background:rgba(10,8,22,0.5);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,0.04);border-radius:14px;padding:16px 20px;display:flex;align-items:center;gap:14px;transition:all 0.2s}
  .game-card:hover{border-color:rgba(140,100,220,0.2);background:rgba(15,12,30,0.6)}
  .game-icon{width:44px;height:44px;border-radius:12px;background:linear-gradient(135deg,rgba(80,40,140,0.3),rgba(30,60,140,0.3));display:flex;align-items:center;justify-content:center;font-size:20px;flex-shrink:0}
  .game-name{color:rgba(220,210,240,0.8);font-size:14px;letter-spacing:1px;flex:1}
  .game-cmd{color:rgba(255,255,255,0.15);font-size:10px;margin-top:3px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:300px}
  .game-actions{display:flex;gap:6px}
  .btn{background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);color:rgba(255,255,255,0.5);padding:8px 16px;border-radius:10px;cursor:pointer;font-family:inherit;font-size:11px;letter-spacing:1px;transition:all 0.2s}
  .btn:hover{background:rgba(255,255,255,0.08)}
  .btn.launch{background:rgba(44,182,125,0.1);border-color:rgba(44,182,125,0.2);color:rgba(44,182,125,0.8)}
  .btn.launch:hover{background:rgba(44,182,125,0.2)}
  .btn.danger{color:rgba(255,80,100,0.6)}
  .btn.danger:hover{background:rgba(255,80,100,0.1);border-color:rgba(255,80,100,0.2)}

  .add-form{background:rgba(10,8,22,0.5);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,0.04);border-radius:14px;padding:20px;display:flex;gap:10px;align-items:flex-end;flex-wrap:wrap}
  .add-form input{background:rgba(0,0,0,0.3);border:1px solid rgba(255,255,255,0.08);color:rgba(255,255,255,0.7);padding:10px 14px;border-radius:10px;font-family:inherit;font-size:12px;flex:1;min-width:160px;outline:none}
  .add-form input:focus{border-color:rgba(140,100,220,0.3)}
  .btn.add{background:rgba(140,100,220,0.15);border-color:rgba(140,100,220,0.3);color:rgba(160,140,240,0.8);white-space:nowrap}
  .btn.add:hover{background:rgba(140,100,220,0.25)}

  .footer{text-align:center;color:rgba(255,255,255,0.08);font-size:9px;letter-spacing:3px;margin-top:40px}
  .status{display:inline-block;width:6px;height:6px;border-radius:50%;background:#2cb67d;margin-right:6px;box-shadow:0 0 8px rgba(44,182,125,0.6)}  
</style>
</head>
<body>
<div class="bg"></div>
<div class="container">
  <h1>NEBULA</h1>
  <div class="subtitle">GAME HUB // HP MINI</div>
  
  <div class="stats" id="stats">
    <div class="stat"><div class="stat-label">CPU</div><div class="stat-value" id="cpu">--<span class="stat-unit">%</span></div></div>
    <div class="stat"><div class="stat-label">RAM</div><div class="stat-value" id="ram">--<span class="stat-unit">G</span></div></div>
    <div class="stat"><div class="stat-label">DISK</div><div class="stat-value" id="disk">--<span class="stat-unit">G</span></div></div>
    <div class="stat"><div class="stat-label">SUNSHINE</div><div class="stat-value" id="sun"><span class="status"></span></div></div>
  </div>

  <div class="section-title">GAME LIBRARY</div>
  <div class="game-list" id="gamelist"></div>

  <div class="section-title">ADD GAME</div>
  <div class="add-form">
    <input type="text" id="gname" placeholder="Game Name">
    <input type="text" id="gcmd" placeholder="Command (e.g. supertux2)">
    <button class="btn add" onclick="addGame()">+ ADD</button>
  </div>
  
  <div class="footer">HP MINI &bull; 10.0.0.108 &bull; NEBULA GAME HUB</div>
</div>

<script>
async function load() {
  let r = await fetch("/api/games");
  let games = await r.json();
  let list = document.getElementById("gamelist");
  list.innerHTML = games.map((g,i) => 
    '<div class="game-card">' +
    '<div class="game-icon">' + (g.name||"?").charAt(0).toUpperCase() + '</div>' +
    '<div><div class="game-name">' + g.name + '</div>' +
    '<div class="game-cmd">' + (g.cmd || "—") + '</div></div>' +
    '<div class="game-actions">' +
    '<button class="btn launch" onclick="launch('+i+')">LAUNCH</button>' +
    '<button class="btn danger" onclick="remove('+i+')">DEL</button>' +
    '</div></div>'
  ).join("");

  let s = await fetch("/api/stats");
  let stats = await s.json();
  document.getElementById("cpu").innerHTML = stats.cpu + '<span class="stat-unit">%</span>';
  document.getElementById("ram").innerHTML = stats.ram + '<span class="stat-unit">G</span>';
  document.getElementById("disk").innerHTML = stats.disk + '<span class="stat-unit">G</span>';
  document.getElementById("sun").innerHTML = stats.sunshine ? '<span class="status"></span>ONLINE' : '<span style="color:#ff5f5f">OFFLINE</span>';
}

async function addGame() {
  let name = document.getElementById("gname").value.trim();
  let cmd = document.getElementById("gcmd").value.trim();
  if(!name||!cmd) return alert("Name and command required");
  await fetch("/api/games", {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({name,cmd})});
  document.getElementById("gname").value = "";
  document.getElementById("gcmd").value = "";
  load();
}

async function remove(i) {
  if(!confirm("Remove this game?")) return;
  await fetch("/api/games/"+i, {method:"DELETE"});
  load();
}

async function launch(i) {
  await fetch("/api/launch/"+i);
  alert("Game launched on HP Mini");
}

load();
setInterval(load, 5000);
</script>
</body>
</html>"""

class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def do_GET(self):
        p = urllib.parse.urlparse(self.path)
        if p.path == "/":
            self._html(HTML)
        elif p.path == "/api/games":
            self._json(load_apps()["apps"])
        elif p.path == "/api/stats":
            self._json(get_stats())
        elif p.path.startswith("/api/launch/"):
            idx = int(p.path.split("/")[-1])
            apps = load_apps()["apps"]
            if 0 <= idx < len(apps):
                cmd = apps[idx].get("cmd", "")
                if cmd:
                    threading.Thread(target=lambda: subprocess.run(cmd, shell=True, env={**os.environ, "DISPLAY":":99"})).start()
                self._json({"ok": True})
            else:
                self._json({"error": "not found"}, 404)
        else:
            self._json({"error": "not found"}, 404)

    def do_POST(self):
        p = urllib.parse.urlparse(self.path)
        if p.path == "/api/games":
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length))
            apps = load_apps()
            apps["apps"].append({"name": data["name"], "cmd": data.get("cmd", "")})
            save_apps(apps)
            self._json({"ok": True})

    def do_DELETE(self):
        p = urllib.parse.urlparse(self.path)
        if p.path.startswith("/api/games/"):
            idx = int(p.path.split("/")[-1])
            apps = load_apps()
            if 0 <= idx < len(apps["apps"]):
                del apps["apps"][idx]
                save_apps(apps)
                self._json({"ok": True})
            else:
                self._json({"error": "not found"}, 404)

    def _html(self, content):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(content.encode())

    def _json(self, data, code=200):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

def load_apps():
    try:
        with open(APPS_FILE) as f:
            return json.load(f)
    except:
        return {"env": {}, "apps": []}

def save_apps(apps):
    with open(APPS_FILE, "w") as f:
        json.dump(apps, f, indent=2)

def get_stats():
    try:
        cpu = os.popen("top -bn1 | grep 'Cpu(s)' | awk '{print $2}'").read().strip() or "0"
        ram = os.popen("free -m | awk '/Mem:/{printf \"%.1f\", $3/1024}'").read().strip() or "0"
        disk = os.popen("df -BG / | awk 'NR==2{print $4}' | tr -d 'G'").read().strip() or "0"
        sun = os.popen("pgrep -x sunshine >/dev/null && echo true || echo false").read().strip()
        return {"cpu": cpu, "ram": ram, "disk": disk, "sunshine": sun == "true"}
    except:
        return {"cpu": "0", "ram": "0", "disk": "0", "sunshine": False}

if __name__ == "__main__":
    print(f"NEBULA GAME HUB → http://10.0.0.108:{PORT}", flush=True)
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
        httpd.serve_forever()
