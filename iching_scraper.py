import requests
from bs4 import BeautifulSoup
import time
import psycopg2
from psycopg2 import sql
import logging
import traceback

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# 定義64卦的資訊
hexagrams = {
    "乾": { "number": 1, "symbol": "䷀", "name": "乾", "nature": "天天", "spell": "qian" },
    "坤": { "number": 2, "symbol": "䷁", "name": "坤", "nature": "地地", "spell": "kun" },
    "屯": { "number": 3, "symbol": "䷂", "name": "屯", "nature": "水雷", "spell": "zhun" },
    "蒙": { "number": 4, "symbol": "䷃", "name": "蒙", "nature": "山水", "spell": "meng" },
    "需": { "number": 5, "symbol": "䷄", "name": "需", "nature": "水天", "spell": "xu" },
    "訟": { "number": 6, "symbol": "䷅", "name": "訟", "nature": "天水", "spell": "song" },
    "師": { "number": 7, "symbol": "䷆", "name": "師", "nature": "地水", "spell": "shi" },
    "比": { "number": 8, "symbol": "䷇", "name": "比", "nature": "水地", "spell": "bi" },
    "小畜": { "number": 9, "symbol": "䷈", "name": "小畜", "nature": "風天", "spell": "xiachu" },
    "履": { "number": 10, "symbol": "䷉", "name": "履", "nature": "天澤", "spell": "lu" },
    "泰": { "number": 11, "symbol": "䷊", "name": "泰", "nature": "地天", "spell": "tai" },
    "否": { "number": 12, "symbol": "䷋", "name": "否", "nature": "天地", "spell": "pi" },
    "同人": { "number": 13, "symbol": "䷌", "name": "同人", "nature": "天火", "spell": "tongren" },
    "大有": { "number": 14, "symbol": "䷍", "name": "大有", "nature": "火天", "spell": "dayou" },
    "謙": { "number": 15, "symbol": "䷎", "name": "謙", "nature": "地山", "spell": "qian" },
    "豫": { "number": 16, "symbol": "䷏", "name": "豫", "nature": "雷地", "spell": "yu" },
    "隨": { "number": 17, "symbol": "䷐", "name": "隨", "nature": "澤雷", "spell": "sui" },
    "蠱": { "number": 18, "symbol": "䷑", "name": "蠱", "nature": "山風", "spell": "gu" },
    "臨": { "number": 19, "symbol": "䷒", "name": "臨", "nature": "地澤", "spell": "lin" },
    "觀": { "number": 20, "symbol": "䷓", "name": "觀", "nature": "風地", "spell": "guan" },
    "噬嗑": { "number": 21, "symbol": "䷔", "name": "噬嗑", "nature": "火雷", "spell": "shike" },
    "賁": { "number": 22, "symbol": "䷕", "name": "賁", "nature": "山火", "spell": "bi" },
    "剝": { "number": 23, "symbol": "䷖", "name": "剝", "nature": "山地", "spell": "bo" },
    "復": { "number": 24, "symbol": "䷗", "name": "復", "nature": "地雷", "spell": "fu" },
    "无妄": { "number": 25, "symbol": "䷘", "name": "无妄", "nature": "天雷", "spell": "wuwang" },
    "大畜": { "number": 26, "symbol": "䷙", "name": "大畜", "nature": "山天", "spell": "dachu" },
    "頤": { "number": 27, "symbol": "䷚", "name": "頤", "nature": "山雷", "spell": "i" },
    "大過": { "number": 28, "symbol": "䷛", "name": "大過", "nature": "澤風", "spell": "daguo" },
    "坎": { "number": 29, "symbol": "䷜", "name": "坎", "nature": "水水", "spell": "kan" },
    "離": { "number": 30, "symbol": "䷝", "name": "離", "nature": "火火", "spell": "li" },
    "咸": { "number": 31, "symbol": "䷞", "name": "咸", "nature": "澤山", "spell": "xian" },
    "恒": { "number": 32, "symbol": "䷟", "name": "恒", "nature": "雷風", "spell": "heng" },
    "遯": { "number": 33, "symbol": "䷠", "name": "遯", "nature": "天山", "spell": "dun" },
    "大壯": { "number": 34, "symbol": "䷡", "name": "大壯", "nature": "雷天", "spell": "dazhuang" },
    "晉": { "number": 35, "symbol": "䷢", "name": "晉", "nature": "火地", "spell": "jin" },
    "明夷": { "number": 36, "symbol": "䷣", "name": "明夷", "nature": "地火", "spell": "mingyi" },
    "家人": { "number": 37, "symbol": "䷤", "name": "家人", "nature": "風火", "spell": "jiaren" },
    "睽": { "number": 38, "symbol": "䷥", "name": "睽", "nature": "火澤", "spell": "kui" },
    "蹇": { "number": 39, "symbol": "䷦", "name": "蹇", "nature": "水山", "spell": "jian" },
    "解": { "number": 40, "symbol": "䷧", "name": "解", "nature": "雷水", "spell": "jie" },
    "損": { "number": 41, "symbol": "䷨", "name": "損", "nature": "山澤", "spell": "sun" },
    "益": { "number": 42, "symbol": "䷩", "name": "益", "nature": "風雷", "spell": "yi" },
    "夬": { "number": 43, "symbol": "䷪", "name": "夬", "nature": "澤天", "spell": "guai" },
    "姤": { "number": 44, "symbol": "䷫", "name": "姤", "nature": "天風", "spell": "gou" },
    "萃": { "number": 45, "symbol": "䷬", "name": "萃", "nature": "澤地", "spell": "cui" },
    "升": { "number": 46, "symbol": "䷭", "name": "升", "nature": "地風", "spell": "shen" },
    "困": { "number": 47, "symbol": "䷮", "name": "困", "nature": "澤水", "spell": "kun" },
    "井": { "number": 48, "symbol": "䷯", "name": "井", "nature": "水風", "spell": "jing" },
    "革": { "number": 49, "symbol": "䷰", "name": "革", "nature": "澤火", "spell": "ge" },
    "鼎": { "number": 50, "symbol": "䷱", "name": "鼎", "nature": "火風", "spell": "ding" },
    "震": { "number": 51, "symbol": "䷲", "name": "震", "nature": "雷雷", "spell": "zhen" },
    "艮": { "number": 52, "symbol": "䷳", "name": "艮", "nature": "山山", "spell": "gen" },
    "漸": { "number": 53, "symbol": "䷴", "name": "漸", "nature": "風山", "spell": "jian" },
    "歸妹": { "number": 54, "symbol": "䷵", "name": "歸妹", "nature": "雷澤", "spell": "guimei" },
    "豐": { "number": 55, "symbol": "䷶", "name": "豐", "nature": "雷火", "spell": "feng" },
    "旅": { "number": 56, "symbol": "䷷", "name": "旅", "nature": "火山", "spell": "lu" },
    "巽": { "number": 57, "symbol": "䷸", "name": "巽", "nature": "風風", "spell": "xun" },
    "兌": { "number": 58, "symbol": "䷹", "name": "兌", "nature": "澤澤", "spell": "dui" },
    "渙": { "number": 59, "symbol": "䷺", "name": "渙", "nature": "風水", "spell": "huan" },
    "節": { "number": 60, "symbol": "䷻", "name": "節", "nature": "水澤", "spell": "jie" },
    "中孚": { "number": 61, "symbol": "䷼", "name": "中孚", "nature": "風澤", "spell": "zhongfu" },
    "小過": { "number": 62, "symbol": "䷽", "name": "小過", "nature": "雷山", "spell": "xiaoguo" },
    "既濟": { "number": 63, "symbol": "䷾", "name": "既濟", "nature": "水火", "spell": "jiji" },
    "未濟": { "number": 64, "symbol": "䷿", "name": "未濟", "nature": "火水", "spell": "weiji" }
}
headers = ["卦號", "卦名", "卦辭", "關鍵", "六十四卦的序列", "相關詞", "運勢", "願望", "愛情・關係", "婚姻", "個性", 
           "事業和策略", "住宅", "行情", "旅行", "生病・病狀", 
           "爻辭1", "爻辭2", "爻辭3", "爻辭4", "爻辭5", "爻辭6", "爻辭7", "爻辭8"]
try:
    conn = psycopg2.connect(
        dbname="iching_db",
        user="postgres",
        password="12345",
        host="localhost",
        port="5432"
    )
    cursor = conn.cursor()
    logging.info("成功連接到數據庫")
    
    # 測試查詢
    cursor.execute("SELECT version();")
    db_version = cursor.fetchone()
    logging.info(f"PostgreSQL 數據庫版本：{db_version}")

except Exception as e:
    logging.error(f"數據庫連接失敗：{e}")
    exit(1)

# Create table
create_table_query = sql.SQL('''
    CREATE TABLE IF NOT EXISTS hexagrams (
        {} INTEGER PRIMARY KEY,
        {} TEXT,
        {} TEXT,
        {} TEXT,
        {} TEXT,
        {} TEXT,
        {} TEXT,
        {} TEXT,
        {} TEXT,
        {} TEXT,
        {} TEXT,
        {} TEXT,
        {} TEXT,
        {} TEXT,
        {} TEXT,
        {} TEXT,
        {} TEXT,
        {} TEXT,
        {} TEXT,
        {} TEXT,
        {} TEXT,
        {} TEXT,
        {} TEXT,
        {} TEXT
    )
''').format(*(sql.Identifier(header) for header in headers))

cursor.execute(create_table_query)



# 遍歷64卦
for hexagram in sorted(hexagrams.values(), key=lambda x: x["number"]):
    url = f"https://1percent-better.com/tw/oriental_wisdom/iching/hexagram/{hexagram['number']}_{hexagram['spell']}/"
    
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        main_content = soup.find('div', class_='entry-content')
        if not main_content:
            logging.warning(f"無法找到主要內容: {hexagram['number']} - {hexagram['name']}")
            continue

        data_dict = {header: "" for header in headers}
        data_dict["卦號"] = hexagram['number']
        data_dict["卦名"] = hexagram['name']

        for header in headers[2:16]:
            try:
                h3_tag = main_content.find('h3', string=lambda text: header in text if text else False)
                if h3_tag:
                    next_tag = h3_tag.find_next_sibling()
                    if next_tag and next_tag.name == 'p':
                        data_dict[header] = next_tag.text.strip()
                    else:
                        logging.warning(f"未找到 {header} 的內容: {hexagram['number']} - {hexagram['name']}")
            except Exception as e:
                logging.error(f"處理 {header} 時出錯: {hexagram['number']} - {hexagram['name']}")
                logging.error(traceback.format_exc())


        # ... (爻辭處理部分保持不變)
        insert_query = sql.SQL('''
            INSERT INTO hexagrams ({}) VALUES ({})
            ON CONFLICT (卦號) DO UPDATE SET
            {}
        ''').format(
            sql.SQL(', ').join(map(sql.Identifier, headers)),
            sql.SQL(', ').join(sql.Placeholder() * len(headers)),
            sql.SQL(', ').join(
                sql.SQL('{0} = EXCLUDED.{0}').format(sql.Identifier(header))
                for header in headers if header != '卦號'
        )
)
    
        cursor.execute(insert_query, [data_dict.get(header, "") for header in headers])
        conn.commit()
        logging.info(f"成功插入/更新第 {hexagram['number']} 卦: {hexagram['name']}")
    except Exception as e:
        conn.rollback()
        logging.error(f"插入/更新第 {hexagram['number']} 卦时出错: {e}")
        logging.error(f"插入的数据: {data_dict}")


# 關閉資料庫連接
cursor.close()
conn.close()

print("所有數據已成功寫入到 PostgreSQL 資料庫中。")