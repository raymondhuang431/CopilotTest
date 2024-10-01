import os
import logging
from flask import Flask, render_template, jsonify
import psycopg2
from psycopg2 import sql

# 設置日誌配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def get_db_connection():
    DATABASE_URL = os.environ.get('DATABASE_URL')  # 確保這個環境變量正確設置
    try:
        conn = psycopg2.connect(DATABASE_URL)
        logger.info("成功連接到數據庫")
        return conn
    except Exception as e:
        logger.error("無法連接到數據庫: %s", e)
        return None

def get_hexagram_info(hexagram_number):
    conn = get_db_connection()
    if conn is None:
        return None  # 如果連接失敗，返回 None

    cur = conn.cursor()
    query = sql.SQL("SELECT * FROM hexagrams WHERE {} = %s").format(sql.Identifier('卦號'))
    cur.execute(query, (hexagram_number,))
    result = cur.fetchone()
    
    # 確保在這裡獲取列名
    columns = [desc[0] for desc in cur.description] if cur.description else []
    
    cur.close()
    conn.close()
    
    if result:
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