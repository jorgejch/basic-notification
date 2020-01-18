import base64
import json
import logging
import os
from datetime import datetime

import pytz
from google.cloud import error_reporting
from twilio.base.exceptions import TwilioException
from twilio.rest import Client as TwilioClient
from google.cloud import storage
# from google.cloud.logging import Client as LoggingClient
from google.cloud import exceptions as google_cloud_exceptions


def get_logger(log_level: str):
    # client = LoggingClient()
    # handler = client.get_default_handler()
    formatter = logging.Formatter('[{levelname:<s}]-[{name:>s}]: {message}', None, '{')
    logger = logging.getLogger()
    for handler in logger.handlers:
        handler.setFormatter(formatter)
        handler.setLevel(logging._nameToLevel[log_level])
    # handler = logging.Handler
    # logger = logging.getLogger('cloudLogger')
    # logger.addHandler(handler)
    logger.setLevel(logging._nameToLevel[log_level])
    return logger


def get_twilio_client(acct_sid: str, auth_token: str) -> TwilioClient:
    twilio_account_sid = acct_sid
    twilio_auth_token = auth_token
    return TwilioClient(twilio_account_sid, twilio_auth_token)


def get_vars_dict(bucket_name: str, blob_name: str) -> dict:
    storage_client = storage.Client()
    blob = storage_client.get_bucket(bucket_name).get_blob(blob_name)
    return json.loads(blob.download_as_string())


def notify_sms(event, context):
    """
    >>> import mock
    >>> import main
    >>> import os
    >>> mock_context = mock.Mock()
    >>> mock_context.event_id = '617187464135194'
    >>> mock_context.timestamp = '2019-07-15T22:09:03.761Z'
    >>> data = {}
    >>> def get_vars_dict(bucket_name, blob_name):
    ...     return {
    ...                 "TWILIO_ACCOUNT_SID": os.getenv('TWILIO_ACCOUNT_SID'),
    ...                 "TWILIO_AUTH_TOKEN": os.getenv('TWILIO_AUTH_TOKEN'),
    ...                 "TWILIO_NOTIFY_SID": os.getenv('TWILIO_NOTIFY_SID'),
    ...            }
    >>> main.get_vars_dict = get_vars_dict
    >>> main.notify_sms(data, mock_context)
    0

    :param event:
    :param context:
    :return:
    """
    error_reporting_client = error_reporting.Client()
    logger = get_logger(os.getenv('LOG_LEVEL'))

    try:
        vars_dict = get_vars_dict(os.getenv('VARS_BUCKET'), os.getenv('VARS_BLOB'))
    except google_cloud_exceptions.NotFound as e:
        logger.error("Failed to obtain vars dictionary due to: {}.".format(e))
        error_reporting_client.report_exception()
        return 1

    try:
        from_number = vars_dict['FROM_SMS_NUMBER']
    except KeyError as e:
        logger.error("Failed to get from sms number variable(s) due to: {}.".format(e))
        error_reporting_client.report_exception()
        return 1

    try:
        sms_data = json.loads(base64.b64decode(event['data']).decode('utf-8'))['sms']
        message_text = sms_data['message']
        to_numbers = sms_data['to_numbers']
    except KeyError as e:
        logger.error("Message not found in event['data'] due to: {}.".format(e))
        error_reporting_client.report_exception()
        return 1

    try:
        for to_num in to_numbers:
            message = get_twilio_client(
                vars_dict['TWILIO_ACCOUNT_SID'],
                vars_dict['TWILIO_AUTH_TOKEN']
            ).messages.create(
                from_=from_number,
                to=to_num,
                body=message_text
            )

            logger.info(
                "Message sent at {} with notification sid {} to number {} and with body '{}'.".format(
                    datetime.now(tz=pytz.timezone('US/Pacific')).timestamp(), message.sid, to_num, message_text
                )
            )
    except TwilioException as e:
        logging.error("Failed to send sms messages with body {} to numbers {} due to: {}.".format(
            message_text, to_numbers, e
        ))
        return 1

    return 0


def notify_email(event, context):
    pass
