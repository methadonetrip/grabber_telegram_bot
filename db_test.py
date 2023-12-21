import pytest
from unittest.mock import Mock, patch
from db import add_user_to_db

@pytest.mark.asyncio
async def test_add_user_to_db():
    mock_connection = Mock()
    mock_cursor = Mock()
    sql = "INSERT INTO userid (id) VALUES (%s) ON DUPLICATE KEY UPDATE id = id"
    chat_id = 1122

    with patch('db.add_user_to_db', mock_connection):

        await add_user_to_db(chat_id)

    assert mock_cursor.execute(sql, (chat_id))

    assert mock_connection.commit()

@pytest.mark.asyncio
async def test_add_user_to_db_exception():
    mock_connection = Mock()
    mock_cursor = Mock()
    err = '''Error adding user to database: (1366, "Incorrect integer value: '' for column 'id' at row 1")'''
    chat_id=''

    with patch('db.add_user_to_db', mock_connection):
        await add_user_to_db(chat_id)

    with pytest.raises(Exception) as ex:
        await add_user_to_db(chat_id)
        assert err in str(ex.value)

    mock_cursor.execute.assert_not_called()
    mock_connection.commit.assert_not_called()
