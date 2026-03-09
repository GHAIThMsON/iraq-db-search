import click
import json
import os
import sys
from .database import Database

def get_db_path():
    if os.path.exists('database.db'):
        return os.path.abspath('database.db')
    pkg_dir = os.path.dirname(os.path.dirname(__file__))
    db_path = os.path.join(pkg_dir, 'database.db')
    if os.path.exists(db_path):
        return db_path
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
@click.option('--db', default=DEFAULT_DB, help='Path to database file')
def search(value, limit, db):
    """Search for any value (name, phone, or any text)"""
    db_obj = Database(db)
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
@click.option('--db', default=DEFAULT_DB, help='Path to database file')
def name(name, limit, db):
    """Search by name"""
    db_obj = Database(db)
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
@click.option('--db', default=DEFAULT_DB, help='Path to database file')
def phone(phone, limit, db):
    """Search by phone number"""
    db_obj = Database(db)
    results = db_obj.search(phone, None, limit)
    
    output = []
    for r in results:
        data = {k: v for k, v in r['data'].items() if k not in ('id', 'source_file') and v}
        if data:
            output.append(data)
    
    safe_echo(json.dumps(output, ensure_ascii=False, indent=2))

@cli.command()
@click.option('--db', default=DEFAULT_DB, help='Path to database file')
def stats(db):
    """Show database statistics"""
    db_obj = Database(db)
    stats_data = db_obj.get_all_stats()
    
    total = sum(stats_data.values())
    output = {
        "total_records": total,
        "total_tables": len(stats_data)
    }
    
    safe_echo(json.dumps(output, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    cli()
