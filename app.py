import os
from flask import Flask, render_template, jsonify
import psycopg2
from psycopg2 import sql

app = Flask(__name__)

def get_db_connection():
      DATABASE_URL = os.environ['DATABASE_URL']
      conn = psycopg2.connect(DATABASE_URL)
      return conn

def get_hexagram_info(hexagram_number):
    conn = get_db_connection()
    cur = conn.cursor()
    query = sql.SQL("SELECT * FROM hexagrams WHERE {} = %s").format(sql.Identifier('卦號'))
    cur.execute(query, (hexagram_number,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    if result:
        columns = [desc[0] for desc in cur.description]
        return dict(zip(columns, result))
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_hexagram/<int:hexagram_number>')
def get_hexagram(hexagram_number):
    hexagram_info = get_hexagram_info(hexagram_number)
    if hexagram_info:
        return jsonify(hexagram_info)
    return jsonify({"error": "Hexagram not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)