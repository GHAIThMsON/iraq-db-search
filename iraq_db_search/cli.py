import click
import json
import os
import sys
from .database import Database

def get_db_path():
    # Check current directory first, then package directory
    if os.path.exists('database.db'):
        return os.path.abspath('database.db')
    pkg_dir = os.path.dirname(os.path.dirname(__file__))
    db_path = os.path.join(pkg_dir, 'database.db')
    if os.path.exists(db_path):
        return db_path
    # Fallback to current directory
    return os.path.abspath('database.db')

DEFAULT_DB = get_db_path()

def safe_echo(msg):
    msg = str(msg)
    if sys.platform == 'win32':
        sys.stdout.buffer.write(msg.encode('utf-8') + b'\n')
    else:
        click.echo(msg)

@click.group()
@click.option('--db', default=DEFAULT_DB, help='Path to database file')
@click.pass_context
def cli(ctx, db):
    ctx.ensure_object(dict)
    ctx.obj['db'] = Database(db)

@cli.command()
@click.option('--db', default=DEFAULT_DB, help='Path to database file')
def tables(db):
    """List all tables in database"""
    db_obj = Database(db)
    tables = db_obj.get_tables()
    for t in tables:
        info = db_obj.get_table_info(t)
        safe_echo(f"{t}: {info['count']:,} rows")

@cli.command()
@click.argument('query')
@click.option('--table', '-t', help='Search in specific table')
@click.option('--limit', '-l', default=50, help='Max results')
@click.option('--json', '-j', 'output_json', is_flag=True, help='Output as JSON')
@click.option('--db', default=DEFAULT_DB, help='Path to database file')
def search(query, table, limit, output_json, db):
    """Search for a name, phone, or any value"""
    db_obj = Database(db)
    results = db_obj.search(query, table, limit)
    
    if output_json:
        safe_echo(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        if not results:
            safe_echo("No results found.")
            return
        
        safe_echo(f"Found {len(results)} results:\n")
        
        # Group by table
        by_table = {}
        for r in results:
            tbl = r['table']
            if tbl not in by_table:
                by_table[tbl] = []
            by_table[tbl].append(r['data'])
        
        for tbl, rows in by_table.items():
            safe_echo(f"=== {tbl} ({len(rows)} results) ===")
            for row in rows:
                for key, val in row.items():
                    if key not in ('id', 'source_file') and val:
                        safe_echo(f"  {key}: {val}")
                safe_echo("")
            safe_echo("")

@cli.command()
@click.argument('table')
@click.option('--limit', '-l', default=10, help='Number of rows')
@click.option('--db', default=DEFAULT_DB, help='Path to database file')
def show(table, limit, db):
    """Show sample data from a table"""
    db_obj = Database(db)
    info = db_obj.get_table_info(table)
    
    safe_echo(f"Table: {table}")
    safe_echo(f"Rows: {info['count']:,}")
    safe_echo(f"Columns: {', '.join([c['name'] for c in info['columns']])}")
    safe_echo("")
    
    results = db_obj.search('', table, limit)
    for r in results:
        safe_echo("---")
        for key, val in r['data'].items():
            if key not in ('id',) and val:
                safe_echo(f"  {key}: {val}")

@cli.command()
@click.option('--db', default=DEFAULT_DB, help='Path to database file')
def stats(db):
    """Show database statistics"""
    db_obj = Database(db)
    stats = db_obj.get_all_stats()
    
    total = sum(stats.values())
    safe_echo(f"Total tables: {len(stats)}")
    safe_echo(f"Total records: {total:,}\n")
    
    for tbl, count in sorted(stats.items(), key=lambda x: -x[1]):
        safe_echo(f"  {tbl}: {count:,}")

if __name__ == '__main__':
    cli()
