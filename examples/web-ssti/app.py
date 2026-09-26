from flask import Flask, request, render_template_string

app = Flask(__name__)

PAGE = """<!doctype html>
<html><head><title>Greeting Card</title></head>
<body>
  <h1>Hello, %s!</h1>
  <p>Welcome to our greeting card service. Put your name in the ?name= parameter.</p>
</body></html>"""


@app.route("/")
def index():
    name = request.args.get("name", "guest")
    return render_template_string(PAGE % name)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
