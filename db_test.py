import pytest
from unittest.mock import Mock, patch
from db import (add_user_to_db, add_user_status,
                add_channel_to_db, add_keyword_to_db,
                add_payment_to_db, read_sub_info,
                read_channels_info, read_keywords_info,
                read_status_info, find_chat_id_by_payment_id)

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
    chat_id = ''

    with patch('db.add_user_to_db', mock_connection):
        await add_user_to_db(chat_id)

    with pytest.raises(Exception) as ex:
        await add_user_to_db(chat_id)
        assert err in str(ex.value)

    mock_cursor.execute.assert_not_called()
    mock_connection.commit.assert_not_called()

@pytest.mark.asyncio
async def test_add_user_status():
    mock_connection = Mock()
    mock_cursor = Mock()
    sql = "UPDATE userid SET status = %s WHERE id = %s "
    chat_id = 1122
    state = 1

    with patch('db.add_user_to_db', mock_connection):
        await add_user_status(state, chat_id)

    assert mock_cursor.execute(sql, (state, chat_id))
    assert mock_connection.commit()

@pytest.mark.asyncio
async def test_add_user_status_exception():
    mock_connection = Mock()
    mock_cursor = Mock()
    err = '''Error adding user to database: (1366, "Incorrect integer value: '' for column 'id' at row 1")'''
    chat_id = ''
    state = ''

    with patch('db.add_user_to_db', mock_connection):
        await add_user_status(state, chat_id)

    with pytest.raises(Exception) as ex:
        await add_user_status(state, chat_id)
        assert err in str(ex.value)

    mock_cursor.execute.assert_not_called()
    mock_connection.commit.assert_not_called()

@pytest.mark.asyncio
async def test_add_channel_to_db():
    mock_connection = Mock()
    mock_cursor = Mock()
    sql = "UPDATE userid SET channels = %s WHERE id = %s "
    chat_id = 1122
    channel = 1

    with patch('db.add_channel_to_db', mock_connection):
        await add_channel_to_db(channel, chat_id)

    assert mock_cursor.execute(sql, (channel, chat_id))
    assert mock_connection.commit()

@pytest.mark.asyncio
async def test_add_channel_to_db_excepption():
    mock_connection = Mock()
    mock_cursor = Mock()
    err = '''Error adding user to database: (1366, "Incorrect integer value: '' for column 'id' at row 1")'''
    chat_id = ''
    channel = ''

    with patch('db.add_channel_to_db', mock_connection):
        await add_channel_to_db(channel, chat_id)

    with pytest.raises(Exception) as ex:
        await add_channel_to_db(channel, chat_id)
        assert err in str(ex.value)

    mock_cursor.execute.assert_not_called()
    mock_connection.commit.assert_not_called()

@pytest.mark.asyncio
async def test_add_keyword_to_db():
    mock_connection = Mock()
    mock_cursor = Mock()
    sql = "UPDATE userid SET keywords = %s WHERE id = %s "
    chat_id = 1122
    channel = 1

    with patch('db.add_keyword_to_db', mock_connection):
        await add_keyword_to_db(channel, chat_id)

    assert mock_cursor.execute(sql, (channel, chat_id))
    assert mock_connection.commit()

@pytest.mark.asyncio
async def test_add_keyword_to_db_excepption():
    mock_connection = Mock()
    mock_cursor = Mock()
    err = '''Error adding user to database: (1366, "Incorrect integer value: '' for column 'id' at row 1")'''
    chat_id = ''
    channel = ''

    with patch('db.add_keyword_to_db', mock_connection):
        await add_keyword_to_db(channel, chat_id)

    with pytest.raises(Exception) as ex:
        await add_keyword_to_db(channel, chat_id)
        assert err in str(ex.value)

    mock_cursor.execute.assert_not_called()
    mock_connection.commit.assert_not_called()

@pytest.mark.asyncio
async def test_add_payment_to_db():
    mock_connection = Mock()
    mock_cursor = Mock()
    sql = "UPDATE userid SET keywords = %s WHERE id = %s "
    chat_id = 1122
    channel = 1

    with patch('db.add_payment_to_db', mock_connection):
        await add_payment_to_db(channel, chat_id)

    assert mock_cursor.execute(sql, (channel, chat_id))
    assert mock_connection.commit()

@pytest.mark.asyncio
async def test_add_payment_to_db_excepption():
    mock_connection = Mock()
    mock_cursor = Mock()
    err = '''Error adding user to database: (1366, "Incorrect integer value: '' for column 'id' at row 1")'''
    chat_id = ''
    channel = ''

    with patch('db.add_payment_to_db', mock_connection):
        await add_payment_to_db(channel, chat_id)

    with pytest.raises(Exception) as ex:
        await add_payment_to_db(channel, chat_id)
        assert err in str(ex.value)

    mock_cursor.execute.assert_not_called()
    mock_connection.commit.assert_not_called()

@pytest.mark.asyncio
async def test_read_sub_info():
    mock_connection = Mock()
    mock_cursor = Mock()
    sql = "SELECT `sub` FROM usersinfo.userid WHERE `id` = %s"
    chat_id = 1121

    with patch('db.read_sub_info', mock_connection):
        await read_sub_info(chat_id)

    assert mock_cursor.execute(sql, (chat_id))
    assert mock_cursor.fetchone().get('sub')

@pytest.mark.asyncio
async def test_read_sub_info_exception():
    mock_connection = Mock()
    mock_cursor = Mock()
    err = '''Error adding user to database: (1366, "Incorrect integer value: '' for column 'id' at row 1")'''
    chat_id = ''

    with patch('db.read_sub_info', mock_connection):
        await read_sub_info(chat_id)

    with pytest.raises(Exception) as ex:
        await read_sub_info(chat_id)
        assert err in str(ex.value)

    mock_cursor.execute.assert_not_called()

''''''
@pytest.mark.asyncio
async def test_read_channels_info():
    mock_connection = Mock()
    mock_cursor = Mock()
    sql = "SELECT `channels` FROM usersinfo.userid WHERE `id` = %s"
    chat_id = 1121

    with patch('db.read_channels_info', mock_connection):
        await read_channels_info(chat_id)

    assert mock_cursor.execute(sql, (chat_id))
    assert mock_cursor.fetchone().get('channels')

@pytest.mark.asyncio
async def test_read_channels_info_exception():
    mock_connection = Mock()
    mock_cursor = Mock()
    err = '''Error adding user to database: (1366, "Incorrect integer value: '' for column 'id' at row 1")'''
    chat_id = ''

    with patch('db.read_channels_info', mock_connection):
        await read_channels_info(chat_id)

    with pytest.raises(Exception) as ex:
        await read_channels_info(chat_id)
        assert err in str(ex.value)

    mock_cursor.execute.assert_not_called()

@pytest.mark.asyncio
async def test_read_keywords_info():
    mock_connection = Mock()
    mock_cursor = Mock()
    sql = "SELECT `keywords` FROM usersinfo.userid WHERE `id` = %s"
    chat_id = 1121

    with patch('db.read_keywords_info', mock_connection):
        await read_keywords_info(chat_id)

    assert mock_cursor.execute(sql, (chat_id))
    assert mock_cursor.fetchone().get('keywords')

@pytest.mark.asyncio
async def test_read_keywords_info_exception():
    mock_connection = Mock()
    mock_cursor = Mock()
    err = '''Error adding user to database: (1366, "Incorrect integer value: '' for column 'id' at row 1")'''
    chat_id = ''

    with patch('db.read_channels_info', mock_connection):
        await read_keywords_info(chat_id)

    with pytest.raises(Exception) as ex:
        await read_keywords_info(chat_id)
        assert err in str(ex.value)

    mock_cursor.execute.assert_not_called()

@pytest.mark.asyncio
async def test_read_status_info():
    mock_connection = Mock()
    mock_cursor = Mock()
    sql = "SELECT `status` FROM usersinfo.userid WHERE `id` = %s"
    chat_id = 1121

    with patch('db.read_status_info', mock_connection):
        await read_status_info(chat_id)

    assert mock_cursor.execute(sql, (chat_id))
    assert mock_cursor.fetchone().get('status')

@pytest.mark.asyncio
async def test_read_status_info_exception():
    mock_connection = Mock()
    mock_cursor = Mock()
    err = '''Error adding user to database: (1366, "Incorrect integer value: '' for column 'id' at row 1")'''
    chat_id = ''

    with patch('db.read_status_info', mock_connection):
        await read_status_info(chat_id)

    with pytest.raises(Exception) as ex:
        await read_status_info(chat_id)
        assert err in str(ex.value)

    mock_cursor.execute.assert_not_called()

@pytest.mark.asyncio
async def test_find_chat_id_by_payment_id():
    mock_connection = Mock()
    mock_cursor = Mock()
    sql = "SELECT chat_id FROM payments WHERE payment_id = %s"
    payment_id = 2212

    with patch('db.find_chat_id_by_payment_id', mock_connection):
        await find_chat_id_by_payment_id(payment_id)

    assert mock_cursor.execute(sql, (payment_id))
    assert mock_cursor.fetcone(['chat_id'])

@pytest.mark.asyncio
async def test_find_chat_id_by_payment_id_exception():
    mock_connection = Mock()
    mock_cursor = Mock()
    err = '''Error adding user to database: (1366, "Incorrect integer value: '' for column 'id' at row 1")'''
    payment_id = ''

    with patch('db.find_chat_id_by_payment_id', mock_connection):
        await find_chat_id_by_payment_id(payment_id)

    with pytest.raises(Exception) as ex:
        await find_chat_id_by_payment_id(payment_id)
        assert err in str(ex.value)

    mock_cursor.execute.assert_not_called()
