from .lambda_function import handler


def test_handler_uv_above_threshold(mocker):
    mock_get = mocker.patch("src.lambda_function.requests.get")
    mock_send_message = mocker.patch("src.lambda_function.send_message_to_telegram")

    mock_response = mocker.MagicMock()
    mock_response.status_code = 200
    mock_response.content = """
    <root>
        <location id="Melbourne">
            <index>4.0</index>
        </location>
    </root>
    """
    mock_get.return_value = mock_response

    handler({}, {})

    mock_send_message.assert_called_once_with("UV is 4.0 > 3.0 - be sunsmart!")


def test_handler_uv_below_threshold(mocker):
    mock_get = mocker.patch("src.lambda_function.requests.get")
    mock_send_message = mocker.patch("src.lambda_function.send_message_to_telegram")

    mock_response = mocker.MagicMock()
    mock_response.status_code = 200
    mock_response.content = """
    <root>
        <location id="Melbourne">
            <index>2.0</index>
        </location>
    </root>
    """
    mock_get.return_value = mock_response

    handler({}, {})

    mock_send_message.assert_called_once_with("UV is safe in Melbourne right now.")


def test_handler_invalid_uv_value(mocker):
    mock_get = mocker.patch("src.lambda_function.requests.get")
    mock_send_message = mocker.patch("src.lambda_function.send_message_to_telegram")
    mock_logger = mocker.patch("src.lambda_function.logger")

    mock_response = mocker.MagicMock()
    mock_response.status_code = 200
    mock_response.content = """
    <root>
        <location id="Melbourne">
            <index>invalid</index>
        </location>
    </root>
    """
    mock_get.return_value = mock_response

    handler({}, {})

    mock_send_message.assert_not_called()
    mock_logger.error.assert_called_once()
