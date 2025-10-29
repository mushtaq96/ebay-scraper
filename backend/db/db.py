from contextlib import asynccontextmanager
import aiosqlite

@asynccontextmanager
async def get_db_conn():
    async with aiosqlite.connect('sql_app.db') as conn:
        yield conn

async def link_exists(conn, url):
    async with conn.execute('SELECT * FROM links WHERE url = ?', (url,)) as cursor:
        result = await cursor.fetchall()
        return len(result) > 0

async def create_links_table(conn):
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS links ( 
            id INTEGER PRIMARY KEY,
            url TEXT NOT NULL
        );
    ''')
    await conn.commit()

async def get_links(conn):
    async with conn.execute('SELECT * FROM links') as cursor:
        return await cursor.fetchall()

async def insert_links(conn, url):
    await conn.execute('INSERT INTO links (url) VALUES (?)', (url,))
    await conn.commit()