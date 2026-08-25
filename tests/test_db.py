from play_along.db import get_db
import mssql_python

def test_conn():
    assert get_db() == mssql_python