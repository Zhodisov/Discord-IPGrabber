import os
from multiprocessing import Process
from server.Server import app
import datetime

def run_flask_app():
    is_local = "DYNO" not in os.environ

    if is_local:
        app.run(
            host="localhost",
            port=7812,
            debug=True
        )
    else:
        port = int(os.environ.get("PORT", 80))
        app.run(
            host="0.0.0.0",
            port=port,
            debug=False
        )

if __name__ == "__main__":
    p1 = Process(target=run_flask_app)
    p1.start()
    p1.join()
