import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app.config.connect_db import test_connection

@pytest.mark.asyncio
async def test_db_connection():
    assert await test_connection() is True