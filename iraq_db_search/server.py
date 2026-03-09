from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

def get_db_path():
    if os.path.exists('database.db'):
        return os.path.abspath('database.db')
    pkg_dir = os.path.dirname(os.path.dirname(__file__))
    db_path = os.path.join(pkg_dir, 'database.db')
    if os.path.exists(db_path):
        return db_path
    return os.path.abspath('database.db')

DB_PATH = get_db_path()

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def search_db(query, limit=100):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence'")
    tables = [row[0] for row in cursor.fetchall()]
    
    results = []
    
    for tbl in tables:
        try:
            cursor.execute(f'PRAGMA table_info("{tbl}")')
            columns = [row[1] for row in cursor.fetchall()]
            data_cols = [c for c in columns if c not in ('id', 'source_file')]
            
            if not data_cols:
                continue
                
            where_clauses = [f'"{col}" LIKE ?' for col in data_cols]
            where_sql = " OR ".join(where_clauses)
            search_term = f"%{query}%"
            sql = f"SELECT * FROM {tbl} WHERE {where_sql} LIMIT ?"
            
            params = tuple([search_term] * len(data_cols) + [limit])
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            for row in rows:
                data = {k: v for k, v in dict(row).items() if k not in ('id', 'source_file') and v}
                if data:
                    results.append(data)
        except Exception:
            continue
    
    conn.close()
    return results

HTML = '''
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>البحث في قواعد البيانات</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: Tahoma, Arial, sans-serif; background: #f0f2f5; min-height: 100vh; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        h1 { text-align: center; color: #1a237e; margin-bottom: 30px; }
        
        .search-box { background: white; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .search-row { display: flex; gap: 10px; flex-wrap: wrap; }
        .search-type { display: flex; gap: 10px; margin-bottom: 10px; }
        .search-type button {
            padding: 10px 20px;
            background: #e8eaf6;
            border: 2px solid #ddd;
            border-radius: 8px;
            cursor: pointer;
            font-family: Tahoma, Arial;
            font-size: 14px;
        }
        .search-type button.active { background: #1a237e; color: white; border-color: #1a237e; }
        input, button { padding: 15px; font-size: 16px; border: 2px solid #ddd; border-radius: 8px; font-family: Tahoma, Arial; }
        input { flex: 1; }
        button.search-btn { background: #1a237e; color: white; border: none; cursor: pointer; }
        button.search-btn:hover { background: #303f9f; }
        
        .results { max-height: 70vh; overflow-y: auto; }
        .result-item { padding: 15px; background: white; border-radius: 8px; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .result-item .data span { background: #f8f9fa; padding: 6px 12px; border-radius: 4px; font-size: 13px; margin: 4px; display: inline-block; }
        .result-item .data .label { color: #1a237e; font-weight: bold; margin-left: 5px; }
        .loading, .no-results { text-align: center; padding: 40px; color: #666; }
        
        pre { background: #1e1e1e; color: #d4d4d4; padding: 20px; border-radius: 8px; overflow-x: auto; font-size: 13px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>البحث في قواعد البيانات</h1>
        
        <div class="search-box">
            <div class="search-type">
                <button class="active" onclick="setType('search', this)">بحث عام</button>
                <button onclick="setType('name', this)">بحث بالاسم</button>
                <button onclick="setType('phone', this)">بحث بالهاتف</button>
            </div>
            <div class="search-row">
                <input type="text" id="searchInput" placeholder="ابحث عن اسم او رقم او اي قيمة...">
                <button class="search-btn" onclick="doSearch()">بحث</button>
            </div>
        </div>
        
        <div id="count"></div>
        <div class="results" id="results"></div>
    </div>

    <script>
        let searchType = 'search';
        
        function setType(type, btn) {
            searchType = type;
            document.querySelectorAll('.search-type button').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        }
        
        async function doSearch() {
            const query = document.getElementById('searchInput').value.trim();
            if (!query) return;
            
            document.getElementById('results').innerHTML = '<div class="loading">جاري البحث...</div>';
            
            let url = `/api/${searchType}?q=${encodeURIComponent(query)}&limit=100`;
            const res = await fetch(url);
            const data = await res.json();
            
            if (data.results && data.results.length > 0) {
                document.getElementById('count').innerHTML = `<div style="padding:10px;background:#e8eaf6;border-radius:8px;margin-bottom:15px;color:#1a237e;font-weight:bold">تم العثور على ${data.results.length} نتيجة</div>`;
                document.getElementById('results').innerHTML = `<pre>${JSON.stringify(data.results, null, 2)}</pre>`;
            } else {
                document.getElementById('count').innerHTML = '';
                document.getElementById('results').innerHTML = '<div class="no-results">لا توجد نتائج</div>';
            }
        }
        
        document.getElementById('searchInput').addEventListener('keypress', e => { if (e.key === 'Enter') doSearch(); });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/api/search')
def api_search():
    query = request.args.get('q', '')
    limit = int(request.args.get('limit', 100))
    if not query:
        return jsonify({"results": []})
    results = search_db(query, limit)
    return jsonify({"results": results})

@app.route('/api/name')
def api_name():
    query = request.args.get('q', '')
    limit = int(request.args.get('limit', 100))
    if not query:
        return jsonify({"results": []})
    results = search_db(query, limit)
    return jsonify({"results": results})

@app.route('/api/phone')
def api_phone():
    query = request.args.get('q', '')
    limit = int(request.args.get('limit', 100))
    if not query:
        return jsonify({"results": []})
    results = search_db(query, limit)
    return jsonify({"results": results})

@app.route('/api/stats')
def api_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence'")
    tables = [row[0] for row in cursor.fetchall()]
    
    total = 0
    for tbl in tables:
        cursor.execute(f'SELECT COUNT(*) FROM "{tbl}"')
        total += cursor.fetchone()[0]
    
    conn.close()
    return jsonify({"total_records": total, "total_tables": len(tables)})

if __name__ == '__main__':
    print("Starting at http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
