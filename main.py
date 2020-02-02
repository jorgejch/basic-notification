# -*- coding: utf8 -*-
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
from google.cloud import exceptions as google_cloud_exceptions
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

_vars_dict = None
_error_reporting_client = None
_logger = None


def get_logger() -> logging.Logger:
    global _logger
    if _logger is not None:
        return _logger

    formatter = logging.Formatter('[{levelname:<s}]-[{name:>s}]: {message}', None, '{')
    stream_handler = logging.StreamHandler()
    _logger = logging.getLogger()
    _logger.addHandler(stream_handler)
    for handler in _logger.handlers:
        handler.setFormatter(formatter)
        handler.setLevel(logging._nameToLevel[os.getenv('LOG_LEVEL')])
    _logger.setLevel(logging._nameToLevel[os.getenv('LOG_LEVEL')])
    return _logger


def get_vars_dict() -> dict:
    global _vars_dict
    if _vars_dict is not None:
        return _vars_dict
    storage_client = storage.Client()
    blob = storage_client.get_bucket(os.getenv('VARS_BUCKET')).get_blob(os.getenv('VARS_BLOB'))
    _vars_dict = json.loads(blob.download_as_string())
    return _vars_dict


def get_error_reporting_client() -> error_reporting.Client:
    global _error_reporting_client
    if _error_reporting_client is not None:
        return _error_reporting_client
    _error_reporting_client = error_reporting.Client()
    return _error_reporting_client


def get_twilio_client(acct_sid: str, auth_token: str) -> TwilioClient:
    twilio_account_sid = acct_sid
    twilio_auth_token = auth_token
    return TwilioClient(twilio_account_sid, twilio_auth_token)


def notify_sms(event, context):
    """
    >>> import mock
    >>> import main
    >>> mock_context = mock.Mock()
    >>> mock_context.event_id = '617187464135194'
    >>> mock_context.timestamp = '2019-07-15T22:09:03.761Z'
    >>> mock_context.resource = 'scan_subreddits_new'
    >>> payload = {'sms': {'to_numbers': ['+18052845139'], 'message': '''Título: 6 ``boster packs...`` Enjoy :)
    ... Submitted: 2020-01-19 19:55:17-08:00
    ... Excerpts\\n	ZHT-5Vgm-WZ8
    ... Link: https://redd.it/er7m4a
    ... Is media link: True'''
    ... }}
    >>> event = {'data': base64.b64encode(bytes(json.dumps(payload), 'utf-8'))}
    >>> main.notify_sms(event, mock_context)
    0

    :param event: dict The `data` field contains the PubsubMessage message. The `attributes` field will contain custom
     attributes if there are any.
    :param context: google.cloud.functions.Context The `event_id` field contains the Pub/Sub message ID. The `timestamp`
     field contains the publish time. The `event_type` field is the type of the event,
     ex: "google.pubsub.topic.publish". The `resource` field is the resource that emitted the event.
    :return: 0 | 1
    """
    get_logger().info("Received request to notify via sms. Event id: {}. Emitting resource: {}.".format(
        context.event_id, context.resource
    ))

    try:
        msg_service_sid = get_vars_dict()['MESSAGING_SERVICE_SID']
    except KeyError as ke:
        get_logger().error("Failed to get messaging service sid # variable(s) due to: {}.".format(ke))
        get_error_reporting_client().report_exception()
        return 1
    except google_cloud_exceptions.NotFound as nfe:
        get_logger().error("Failed to get messaging service sid # variable(s) due to: {}.".format(nfe))
        get_error_reporting_client().report_exception()
        return 1

    try:
        sms_data = json.loads(base64.b64decode(event['data']).decode('utf-8'))['sms']
        message_text = sms_data['message']
        to_numbers = sms_data['to_numbers']
    except KeyError as e:
        get_logger().error("Message not found in event['data'] due to: {}.".format(e))
        get_error_reporting_client().report_exception()
        return 1

    try:
        for to_num in to_numbers:
            message = get_twilio_client(
                get_vars_dict()['TWILIO_ACCOUNT_SID'],
                get_vars_dict()['TWILIO_AUTH_TOKEN']
            ).messages.create(
                messaging_service_sid=msg_service_sid,
                to=to_num,
                body=message_text
            )

            get_logger().info(
                "Message sent at {} with notification sid {} to number {} and with body '{}'.".format(
                    datetime.now(tz=pytz.timezone('US/Pacific')).timestamp(), message.sid, to_num, message_text
                )
            )
    except TwilioException as e:
        logging.error("Failed to send sms messages with body {} to numbers {} due to: {}.".format(
            message_text, to_numbers, e
        ))
        get_error_reporting_client().report_exception()
        return 1
    return 0


def notify_email(event, context):
    """
    >>> import main
    >>> import mock
    >>> mock_context = mock.Mock()
    >>> mock_context.event_id = '617187464135194'
    >>> mock_context.timestamp = '2019-07-15T22:09:03.761Z'
    >>> payload = {'email':
    ...             {
    ...                 'message': 'Hello nurse!!!',
    ...                 'to_emails': ['jorgejch@gmail.com', 'jorgejchaddad@yahoo.com'],
    ...                 'subject': 'Test emails.'
    ...             }
    ...         }
    >>> event = {'data': base64.b64encode(bytes(json.dumps(payload), 'utf-8'))}
    >>> main.notify_email(event, mock_context)
    0

    :param event: dict The `data` field contains the PubsubMessage message. The `attributes` field will contain custom
     attributes if there are any.
    :param context: google.cloud.functions.Context The `event_id` field contains the Pub/Sub message ID. The `timestamp`
     field contains the publish time. The `event_type` field is the type of the event,
     ex: "google.pubsub.topic.publish". The `resource` field is the resource that emitted the event.
    :return: 0 | 1
    """
    get_logger().info("Received request to notify via email. Event id: {}. Emitting resource: {}.".format(
        context.event_id, context.resource
    ))

    try:
        email_data = json.loads(base64.b64decode(event['data']).decode('utf-8'))['email']
        message_content = email_data['message']
        to_emails = email_data['to_emails']
        subject = email_data['subject']
    except KeyError as e:
        get_logger().error("Message not found in event['data'] due to: {}.".format(e))
        get_error_reporting_client().report_exception()
        return 1

    try:
        from_email = get_vars_dict()['FROM_EMAIL']
    except Exception as e:
        get_logger().error('Unable to get from email due to: {}.'.format(e))
        get_error_reporting_client().report_exception()
        return 1

    message = Mail(
        from_email=from_email,
        to_emails=to_emails,
        subject=subject,
        html_content=message_content
    )

    try:
        sg = SendGridAPIClient(get_vars_dict()['SENDGRID_API_KEY'])
        response = sg.send(message)
    except google_cloud_exceptions.NotFound as nfe:
        get_logger().error("Failed to get sendgrid api key to send email message due to: {}.".format(nfe))
        get_error_reporting_client().report_exception()
        return 1
    except Exception as e:
        get_logger().error("Failed to send email message due to: {}.".format(e))
        get_error_reporting_client().report_exception()
        return 1

    get_logger().info("Sent email to '{}' from '{}' with subject '{}'.".format(to_emails, from_email, subject))
    get_logger().debug("Sent email content:\n{}".format(message_content))
    get_logger().debug('Response status code: {}.'.format(response.status_code))
    get_logger().debug('Response body: {}.'.format(response.body))
    get_logger().debug('Response headers:\n{}'.format(response.headers))
    return 0
