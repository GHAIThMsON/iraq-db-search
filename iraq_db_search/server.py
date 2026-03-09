from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'database.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_table_names():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        return tables
    except:
        return []

def search_tables(query, table=None, limit=100):
    tables = [table] if table else get_table_names()
    results = []
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
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
                results.append({'table': tbl, 'data': dict(row)})
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
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        h1 { text-align: center; color: #1a237e; margin-bottom: 20px; }
        
        .search-box { background: white; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .search-row { display: flex; gap: 10px; }
        select, input, button { padding: 15px; font-size: 16px; border: 2px solid #ddd; border-radius: 8px; font-family: Tahoma, Arial; }
        input { flex: 1; }
        button { background: #1a237e; color: white; border: none; cursor: pointer; }
        button:hover { background: #303f9f; }
        
        .results { max-height: 70vh; overflow-y: auto; }
        .result-item { padding: 15px; background: white; border-radius: 8px; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-right: 4px solid #1a237e; }
        .table-name { color: #666; font-size: 12px; background: #f0f2f5; padding: 4px 8px; border-radius: 4px; display: inline-block; margin-bottom: 8px; }
        .data span { background: #f8f9fa; padding: 6px 12px; border-radius: 4px; font-size: 13px; margin: 4px; display: inline-block; }
        .label { color: #1a237e; font-weight: bold; margin-left: 5px; }
        .loading, .no-results { text-align: center; padding: 40px; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <h1>البحث في قواعد البيانات</h1>
        
        <div class="search-box">
            <div class="search-row">
                <select id="tableSelect"><option value="">جميع الجداول</option></select>
                <input type="text" id="searchInput" placeholder="ابحث عن اسم او رقم هاتف...">
                <button onclick="doSearch()">بحث</button>
            </div>
        </div>
        
        <div id="resultsInfo"></div>
        <div class="results" id="results"></div>
    </div>

    <script>
        async function loadTables() {
            const res = await fetch('/api/tables');
            const tables = await res.json();
            tables.forEach(t => {
                const opt = document.createElement('option');
                opt.value = t;
                opt.textContent = t;
                document.getElementById('tableSelect').appendChild(opt);
            });
        }
        
        async function doSearch() {
            const query = document.getElementById('searchInput').value.trim();
            const table = document.getElementById('tableSelect').value;
            if (!query) return;
            
            document.getElementById('results').innerHTML = '<div class="loading">جاري البحث...</div>';
            
            let url = `/api/search?q=${encodeURIComponent(query)}&limit=100`;
            if (table) url += `&table=${encodeURIComponent(table)}`;
            
            const res = await fetch(url);
            const data = await res.json();
            
            if (data.length > 0) {
                document.getElementById('resultsInfo').innerHTML = `<div style="padding:10px;background:#e8eaf6;border-radius:8px;margin-bottom:15px;color:#1a237e;font-weight:bold">تم العثور على ${data.length} نتيجة</div>`;
                document.getElementById('results').innerHTML = data.map(item => `
                    <div class="result-item">
                        <div class="table-name">${item.table}</div>
                        <div class="data">
                            ${Object.entries(item.data).filter(([k]) => k !== 'id').map(([k, v]) => v ? `<span><span class="label">${k}:</span> ${v}</span>` : '').join('')}
                        </div>
                    </div>
                `).join('');
            } else {
                document.getElementById('results').innerHTML = '<div class="no-results">لا توجد نتائج</div>';
            }
        }
        
        document.getElementById('searchInput').addEventListener('keypress', e => { if (e.key === 'Enter') doSearch(); });
        loadTables();
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/api/tables')
def list_tables():
    return jsonify(get_table_names())

@app.route('/api/search')
def search():
    query = request.args.get('q', '')
    table = request.args.get('table', '')
    limit = int(request.args.get('limit', 100))
    if not query:
        return jsonify([])
    return jsonify(search_tables(query, table, limit))

if __name__ == '__main__':
    print("Starting at http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
