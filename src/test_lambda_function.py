import pytest

from .lambda_function import handler


@pytest.fixture(autouse=True)
def mock_dynamodb(mocker):
    mock_boto3 = mocker.patch("src.lambda_function.boto3")

    mock_dynamodb_resource = mocker.MagicMock()
    mock_boto3.resource.return_value = mock_dynamodb_resource
    
    mock_table = mocker.MagicMock()
    mock_dynamodb_resource.Table.return_value = mock_table
    return mock_boto3


def test_handler_uv_above_threshold_and_previous_value_below_3(mocker):
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

    mock_previous_uv = mocker.patch("src.lambda_function.get_previous_uv")
    mock_previous_uv.return_value = 0.0

    handler({}, {})

    mock_send_message.assert_called_once_with(
        "UV is 4.0 > 3.0 - be sunsmart! UV observations courtesy of ARPANSA."
    )


def test_handler_uv_above_threshold_and_previous_value_above_3(mocker):
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

    mock_previous_uv = mocker.patch("src.lambda_function.get_previous_uv")
    mock_previous_uv.return_value = 10.0

    mock_send_message.assert_not_called()


def test_handler_uv_below_threshold_and_previous_above_threshold(mocker):
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

    mock_previous_uv = mocker.patch("src.lambda_function.get_previous_uv")
    mock_previous_uv.return_value = 10.0

    handler({}, {})

    mock_send_message.assert_called_once_with(
        "UV is safe in Melbourne right now. UV observations courtesy of ARPANSA."
    )


def test_handler_uv_below_threshold_and_previous_below_threshold(mocker):
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

    mock_previous_uv = mocker.patch("src.lambda_function.get_previous_uv")
    mock_previous_uv.return_value = 0.0

    handler({}, {})

    mock_send_message.assert_not_called()


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
