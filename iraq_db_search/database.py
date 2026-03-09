import sqlite3
import os

class Database:
    def __init__(self, db_path='database.db'):
        self.db_path = db_path
        
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def get_tables(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        return tables
    
    def search(self, query, table=None, limit=100):
        tables = [table] if table else self.get_tables()
        results = []
        
        conn = self.get_connection()
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
                    results.append({
                        'table': tbl,
                        'data': dict(row)
                    })
            except Exception:
                continue
        
        conn.close()
        return results
    
    def get_table_info(self, table):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(f'PRAGMA table_info("{table}")')
        columns = [{'name': row[1], 'type': row[2]} for row in cursor.fetchall()]
        cursor.execute(f'SELECT COUNT(*) FROM "{table}"')
        count = cursor.fetchone()[0]
        conn.close()
        return {'columns': columns, 'count': count}
    
    def get_all_stats(self):
        stats = {}
        for table in self.get_tables():
            info = self.get_table_info(table)
            stats[table] = info['count']
        return stats
