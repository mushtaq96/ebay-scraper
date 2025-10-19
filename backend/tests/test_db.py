# backend/tests/test_db.py
import pytest
from backend.db.db import create_links_table, get_db_conn, get_links, insert_links, link_exists


@pytest.mark.asyncio
async def test_get_db_conn():
    async with get_db_conn() as conn:
        assert conn is not None


@pytest.mark.asyncio
async def test_create_links_table():
    async with get_db_conn() as conn:
        await create_links_table(conn)
        async with conn.execute('SELECT * FROM links') as cursor:
            result = await cursor.fetchall()
        assert result is not None


@pytest.mark.asyncio
async def test_insert_links():
    url = 'https://www.example.com'
    async with get_db_conn() as conn:
        await insert_links(conn, url)
        exists = await link_exists(conn, url)
        assert exists is True


@pytest.mark.asyncio
async def test_get_links():
    async with get_db_conn() as conn:
        links = await get_links(conn)
        assert links is not None


@pytest.mark.asyncio
async def test_link_exists_false():
    url = 'https://www.example-does-not-exist-12345.com'
    async with get_db_conn() as conn:
        exists = await link_exists(conn, url)
        assert exists is False
