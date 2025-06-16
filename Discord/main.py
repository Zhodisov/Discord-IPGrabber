import os
from multiprocessing import Process
from server.Server import app
from utils.ServerConfig.Discord import run_discord_bot

def run_flask_app():
    if "DYNO" in os.environ:
        port = int(os.environ.get("PORT", 80))
        app.run(host="0.0.0.0", port=port, debug=True)
    else:
        port = 7812
        app.run(host="127.0.0.1", port=port, debug=True, use_reloader=False)

if __name__ == "__main__":
    p1 = Process(target=run_flask_app)
    p2 = Process(target=run_discord_bot)

    p1.start()
    p2.start()

    p1.join()
    p2.join()
