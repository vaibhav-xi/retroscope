"""
RetroScope Networking
Flask Control Server
"""

from threading import Thread
from flask import Flask, request, jsonify

import config

app = Flask(__name__)


# --------------------------------------------------------
# Helpers
# --------------------------------------------------------

def current_state():

    return {
        "waveform": config.runtime["waveform"],
        "frequency": config.runtime["frequency"],
        "amplitude": config.runtime["amplitude"],
        "speed": config.runtime["speed"],
        "freeze": config.runtime["freeze"],
        "grid": config.runtime["grid"],
        "glow": config.runtime["glow"],
        "scanlines": config.runtime["scanlines"],
        "persistence": config.runtime["persistence"],
        "noise": config.runtime["noise"],
        "vignette": config.runtime["vignette"],
    }


# --------------------------------------------------------
# REST API
# --------------------------------------------------------

@app.get("/api/state")
def api_state():

    return jsonify(current_state())


@app.post("/api/update")
def api_update():

    data = request.json

    if not data:
        return jsonify({"success": False})

    for key in data:

        if key in config.runtime:

            config.runtime[key] = data[key]

    return jsonify({
        "success": True,
        "state": current_state()
    })


@app.post("/api/reset")
def api_reset():

    config.runtime["waveform"] = config.DEFAULT_WAVEFORM
    config.runtime["frequency"] = config.FREQUENCY
    config.runtime["amplitude"] = config.AMPLITUDE
    config.runtime["speed"] = config.SPEED

    config.runtime["freeze"] = False
    config.runtime["grid"] = True
    config.runtime["glow"] = True
    config.runtime["scanlines"] = True
    config.runtime["persistence"] = True
    config.runtime["noise"] = True
    config.runtime["vignette"] = True

    return jsonify({
        "success": True,
        "state": current_state()
    })


# --------------------------------------------------------
# Future pages
# --------------------------------------------------------

@app.get("/")
def home():

    return """
<html>

<head>

<title>RetroScope</title>

<style>

body{

background:#101010;

color:#00ff66;

font-family:monospace;

padding:40px;

}

button{

font-size:20px;

margin:8px;

padding:12px;

}

</style>

</head>

<body>

<h1>RetroScope</h1>

<p>Renderer connected.</p>

<p>Web interface coming soon.</p>

</body>

</html>
"""


# --------------------------------------------------------
# Thread
# --------------------------------------------------------

def run_server():

    app.run(
        host="0.0.0.0",
        port=config.WEB_PORT,
        threaded=True,
        debug=False,
        use_reloader=False,
    )


def start():

    thread = Thread(
        target=run_server,
        daemon=True,
    )

    thread.start()
