import yaml, threading, webbrowser, subprocess
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

class ModelEditorServer:
    def __init__(self, yaml_path="./datos/modelo.yml"):
        self.yaml_path = yaml_path

    def _load(self):
        with open(self.yaml_path, "r") as f:
            return yaml.safe_load(f)

    def _save(self, data):
        with open(self.yaml_path, "w") as f:
            yaml.safe_dump(data, f, sort_keys=False)

    def run(self, host="127.0.0.1", port=5000, open_browser=True):
        if open_browser:
            threading.Timer(1, lambda: webbrowser.open(f"http://{host}:{port}")).start()
        app.config['MODEL_SERVER'] = self
        app.run(host=host, port=port, debug=False)
        return "OK"


# --------------------- UI HTML ---------------------
PAGE = """
<!doctype html>
<html>
<head>
<title>Inventario de Red</title>
<style>
body { font-family: Arial; background:#eef5ff; margin:0; padding:20px;}
.container { width:70%; margin:auto; background:white; padding:25px; 
    border-radius:10px; box-shadow:0 0 10px rgba(0,0,0,.1);}
h2 { color:#005a9c; margin-bottom:10px; }
table { width:100%; border-collapse: collapse; margin-top:15px; }
td, th { border:1px solid #ddd; padding:8px; text-align:center; }
th { background:#005a9c; color:white; }
input { width:95%; padding:5px; }
.status { font-weight:bold; }
.ok { color:green; }
.fail { color:red; }
button { background:#0078ff; color:white; border:none; padding:10px 18px; 
  border-radius:5px; cursor:pointer; font-size:15px; }
button:disabled { background:gray; cursor:not-allowed; }
</style>

<script>
async function pingALL() {
    const rows = document.querySelectorAll("tr.dev");
    let allGood = true;
    for (let tr of rows) {
        let ip = tr.querySelector(".ip").value;
        let statusCell = tr.querySelector(".status");
        statusCell.textContent = "⏳";
        try {
            let res = await fetch("/ping?ip=" + ip);
            let j = await res.json();
            if (j.reachable) {
                statusCell.textContent = "✅";
                statusCell.className = "status ok";
            } else {
                statusCell.textContent = "❌";
                statusCell.className = "status fail";
                allGood = false;
            }
        } catch {
            statusCell.textContent = "❌";
            statusCell.className = "status fail";
            allGood = false;
        }
    }
    document.getElementById("saveBtn").disabled = !allGood;
}

async function saveConfig() {
    let data = [];
    document.querySelectorAll("tr.dev").forEach(tr=>{
        data.push({
            hostname: tr.dataset.h,
            host: tr.querySelector(".ip").value,
            username: tr.querySelector(".usr").value,
            password: tr.querySelector(".pass").value
        });
    });
    await fetch("/save", {
        method:"POST",
        headers:{ "Content-Type":"application/json" },
        body:JSON.stringify(data)
    });
    alert("Inventario actualizado correctamente. Cerrando servidor...");
    window.close();
}
</script>
</head>

<body>
<div class="container">
<h2>Inventario de Red</h2>
<p>Editá las credenciales. Probá la conectividad antes de guardar.</p>

<table>
<tr><th>Hostname</th><th>IP</th><th>Usuario</th><th>Password</th><th>Ping</th></tr>

{% for d in devices %}
<tr class="dev" data-h="{{d.hostname}}">
<td>{{d.hostname}}</td>
<td><input class="ip" value="{{d.host}}"></td>
<td><input class="usr" value="{{d.username}}"></td>
<td><input class="pass" value="{{d.password}}"></td>
<td class="status">-</td>
</tr>
{% endfor %}

</table>

<br>
<button onclick="pingALL()">Test Ping</button>
<button id="saveBtn" disabled onclick="saveConfig()">Guardar & Cerrar</button>
</div>
</body>
</html>
"""


# ----------------------- Flask Endpoints -----------------------
@app.route("/")
def index():
    server = app.config['MODEL_SERVER']
    m = server._load()
    devices = m['modelo']['estructura']['infra']
    data = [
        {
            "hostname": d['hostname'],
            "host": d['connection']['host'],
            "username": d['connection']['username'],
            "password": d['connection']['password']
        }
        for d in devices
    ]
    return render_template_string(PAGE, devices=data)


@app.route("/ping")
def ping():
    ip = request.args.get("ip")
    try:
        r = subprocess.run(["ping", "-n", "1", "-w", "500", ip],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ok = (r.returncode == 0)
    except:
        ok = False
    return jsonify({"reachable": ok})


@app.route("/save", methods=["POST"])
def save():
    server = app.config['MODEL_SERVER']
    posted = request.json
    m = server._load()

    for dev in m['modelo']['estructura']['infra']:
        for row in posted:
            if row['hostname'] == dev['hostname']:
                dev['connection']['host'] = row['host']
                dev['connection']['username'] = row['username']
                dev['connection']['password'] = row['password']

    server._save(m)
    threading.Timer(1, lambda: request.environ.get('werkzeug.server.shutdown')()).start()
    return "OK"
