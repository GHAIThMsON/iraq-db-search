import click
import json
import os
import sys
import io
from .database import Database

# Fix Windows console encoding for Arabic
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def get_db_path():
    # First check current working directory
    if os.path.exists('database.db'):
        return os.path.abspath('database.db')
    # Check the directory where the script is installed
    pkg_dir = os.path.dirname(os.path.dirname(__file__))
    db_path = os.path.join(pkg_dir, 'database.db')
    if os.path.exists(db_path):
        return db_path
    # Check common locations
    for path in ['database.db', '../database.db']:
        full_path = os.path.join(os.getcwd(), path)
        if os.path.exists(full_path):
            return os.path.abspath(full_path)
    # Fallback to cwd
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
@click.argument('value')
@click.option('--limit', '-l', default=50, help='Max results')
@click.option('--db', default=None, help='Path to database file')
def search(value, limit, db):
    """Search for any value (name, phone, or any text)"""
    db_path = db if db else DEFAULT_DB
    db_obj = Database(db_path)
    results = db_obj.search(value, None, limit)
    
    # Format output without table info
    output = []
    for r in results:
        data = {k: v for k, v in r['data'].items() if k not in ('id', 'source_file') and v}
        if data:
            output.append(data)
    
    safe_echo(json.dumps(output, ensure_ascii=False, indent=2))

@cli.command()
@click.argument('name')
@click.option('--limit', '-l', default=50, help='Max results')
@click.option('--db', default=None, help='Path to database file')
def name(name, limit, db):
    """Search by name"""
    db_path = db if db else DEFAULT_DB
    db_obj = Database(db_path)
    results = db_obj.search(name, None, limit)
    
    output = []
    for r in results:
        data = {k: v for k, v in r['data'].items() if k not in ('id', 'source_file') and v}
        if data:
            output.append(data)
    
    safe_echo(json.dumps(output, ensure_ascii=False, indent=2))

@cli.command()
@click.argument('phone')
@click.option('--limit', '-l', default=50, help='Max results')
@click.option('--db', default=None, help='Path to database file')
def phone(phone, limit, db):
    """Search by phone number"""
    db_path = db if db else DEFAULT_DB
    db_obj = Database(db_path)
    results = db_obj.search(phone, None, limit)
    
    output = []
    for r in results:
        data = {k: v for k, v in r['data'].items() if k not in ('id', 'source_file') and v}
        if data:
            output.append(data)
    
    safe_echo(json.dumps(output, ensure_ascii=False, indent=2))

@cli.command()
@click.option('--db', default=None, help='Path to database file')
def stats(db):
    """Show database statistics"""
    db_path = db if db else DEFAULT_DB
    db_obj = Database(db_path)
    stats_data = db_obj.get_all_stats()
    
    total = sum(stats_data.values())
    output = {
        "total_records": total,
        "total_tables": len(stats_data)
    }
    
    safe_echo(json.dumps(output, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    cli()
