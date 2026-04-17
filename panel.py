from flask import Flask, request, redirect
import sqlite3

app = Flask(__name__)

def db():
    return sqlite3.connect("shop.db")

@app.route("/")
def home():
    conn = db()
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS stock (product TEXT, data TEXT)")
    cur.execute("SELECT product, COUNT(*) FROM stock GROUP BY product")
    rows = cur.fetchall()

    html = "<h2>📦 STOCK PANEL</h2>"
    for r in rows:
        html += f"<p>{r[0]} → {r[1]}</p>"

    html += '''
    <h3>Add Stock</h3>
    <form method='post' action='/add'>
    Product: <input name='product'><br>
    Data: <input name='data'><br>
    <button type='submit'>Add</button>
    </form>
    '''
    return html

@app.route("/add", methods=["POST"])
def add():
    product = request.form["product"]
    data = request.form["data"]
    conn = db()
    cur = conn.cursor()
    cur.execute("INSERT INTO stock VALUES (?, ?)", (product, data))
    conn.commit()
    return redirect("/")

app.run(host="0.0.0.0", port=5000)
