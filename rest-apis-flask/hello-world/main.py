"""
Smallest possible Flask app - one route, one plain-text response.

Purpose here is just to confirm the setup works end-to-end (repo-root
venv + Flask import + dev server) and to see Werkzeug's routing in its
simplest form before adding anything JSON/REST-shaped in later stages.
"""

from flask import Flask

# Flask() builds the WSGI application object. __name__ tells Flask which
# module/package it's running from, so it can locate resources relative
# to this file (templates/, static/) if this app ever needs them - not
# used yet in this stage, but it's why __name__ is always passed here.
app = Flask(__name__)


@app.route("/")
def hello_world() -> str:
    """Handle GET / by returning a plain-text greeting.

    Flask wraps a returned str in a 200 OK HttpResponse automatically -
    no need to build a Response object by hand for a simple case like
    this.
    """
    return "Hello, World!"


if __name__ == "__main__":
    # debug=True turns on Werkzeug's interactive debugger and
    # auto-reload-on-save - convenient for local learning, but never
    # something to leave on for a real deployment (it can execute
    # arbitrary code from the browser if the debugger pin is exposed).
    app.run(debug=True)
