"""
This module provides a MQTT client for communication with remote devices.

Classes:
    - MqttClient: Client class for MQTT communication.

Dependencies:
    - os: Operating system functionality.
    - paho.mqtt.client: MQTT client library.
    - ssl: SSL/TLS support for secure communication.
    - json: JSON encoding and decoding.
    - time: Time-related functions.
    - secrets: Secure random number generator.
    - typing.Any: Type representing any type.
    - typing.Dict: Type representing a dictionary.
    - django.http.HttpResponse: Django HTTP response object.
    - MQTT_BROKER_ENDPOINT: MQTT broker endpoint.
    - .s3.BUCKET_FROM_RASPBERRY: Name of the S3 bucket.

Global Variables:
    - current_working_directory: Current working directory.

"""


import os
import paho.mqtt.client as mqtt
import ssl
import json
import time
import secrets
from typing import Any, Dict
from django.http import HttpResponse
from .s3 import BUCKET_FROM_RASPBERRY
from dotenv import load_dotenv


load_dotenv()

MQTT_BROKER_ENDPOINT = os.getenv('MQTT_BROKER_ENDPOINT')

current_working_directory = os.getcwd()


class MqttClient:
    """
    MQTT client for communicating with remote devices.

    Attributes:
        respondingTimeout (int): Timeout for waiting for device response.
        resultTimeout (int): Timeout for waiting for command result.
        client (mqtt.Client): MQTT client instance.
        results (Dict[str, Any]): Dictionary to store request results.

    Methods:
        - __init__: Initializes the MQTT client.
        - process_message: Processes incoming MQTT messages.
        - publish: Publishes MQTT messages.
        - wait_for_result: Waits for the result of a MQTT request.
        - wait_for_confirmation: Waits for confirmation of a MQTT request.
        - request_handler: Handles MQTT requests.
        - get_result: Retrieves the result of a MQTT request.
    """

    def __init__(self) -> None:
        """
        Initializes the MQTT client.
        """
        self.respondingTimeout: int = 5
        self.resultTimeout: int = 60

        self.client: mqtt.Client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
        self.client.tls_set(
            ca_certs=os.path.join(current_working_directory, 'remotecontrol/mqtt_certificates/AmazonRootCA1.pem'),
            certfile=os.path.join(current_working_directory, 'remotecontrol/mqtt_certificates/certificate.pem.crt'),
            keyfile=os.path.join(current_working_directory, 'remotecontrol/mqtt_certificates/private.pem.key'),
            tls_version=ssl.PROTOCOL_SSLv23)
        self.client.tls_insecure_set(True)
        self.client.connect(MQTT_BROKER_ENDPOINT, 8883, 60)
        self.client.on_message = self.process_message
        self.client.subscribe("raspberry/response", qos=1)

        self.results = {}

    def process_message(self, clt: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage) -> None:
        """
        Processes incoming MQTT messages.

        Parameters:
            clt (mqtt.Client): MQTT client instance.
            userdata (Any): User data.
            msg (mqtt.MQTTMessage): MQTT message.
        """
        message: Dict[str, Any] = json.loads(msg.payload.decode("utf-8"))
        request_id: str = message.get("RequestID")
        self.results[request_id] = message

    def publish(self, request: Dict[str, Any]) -> None:
        """
        Publishes MQTT messages.

        Parameters:
            request (Dict[str, Any]): MQTT request.
        """
        self.client.publish("raspberry/request", json.dumps(request))
        self.client.loop_start()

    def wait_for_result(self, one_time_token: str, timeout: int) -> Dict:
        """
        Waits for the result of a MQTT request.

        Parameters:
            one_time_token (str): Token for identifying the request.
            timeout (int): Timeout duration.

        Returns:
            Dict: MQTT request result.
        """
        start_time: float = time.time()
        while time.time() - start_time < timeout:
            if one_time_token in self.results:
                return self.results.pop(one_time_token)
        return {"error": "Timeout Error"}

    def wait_for_confirmation(self, one_time_token: str, timeout: int) -> bool:
        """
        Waits for confirmation of a MQTT request.

        Parameters:
            one_time_token (str): Token for identifying the request.
            timeout (int): Timeout duration.

        Returns:
            bool: True if confirmation received, False otherwise.
        """
        start_time: float = time.time()
        while time.time() - start_time < timeout:
            if one_time_token in self.results:
                if self.results.pop(one_time_token)["status"] == "OK":
                    return True
        return False

    def request_handler(self, request_type: str, device_id: str, respondingTimeout: str, resultTimeout: str, **kwargs: Any) -> HttpResponse:
        """
        Handles MQTT requests.

        Parameters:
            request_type (str): Type of request.
            device_id (str): ID of the target device.
            respondingTimeout (str): Timeout for waiting for device response.
            resultTimeout (str): Timeout for waiting for command result.
            **kwargs (Any): Additional request parameters.

        Returns:
            HttpResponse: Response indicating success or failure.
        """
        mqtt_request: Dict[str, Any] = {
            'DeviceID': device_id,
            'type': request_type,
            **kwargs
        }

        self.respondingTimeout = int(respondingTimeout)
        self.resultTimeout = int(resultTimeout)

        one_time_token: str = secrets.token_hex(32)
        mqtt_request['RequestID'] = one_time_token

        self.publish(mqtt_request)

        return self.get_result(one_time_token)

    def get_result(self, one_time_token: str) -> HttpResponse:
        """
        Retrieves the result of a MQTT request.

        Parameters:
            one_time_token (str): Token for identifying the request.

        Returns:
            HttpResponse: Response containing the result.
        """
        status: bool = self.wait_for_confirmation(one_time_token, self.respondingTimeout)

        if not status:
            self.client.loop_stop()
            return HttpResponse("Device Not Responding")

        result: Dict = self.wait_for_result(one_time_token, self.resultTimeout)

        self.client.loop_stop()

        if "result" in result:
            return HttpResponse(result["result"])
        elif "file_key_s3" in result:
            link: str = f'https://s3.console.aws.amazon.com/s3/object/{BUCKET_FROM_RASPBERRY}?region=us-east-1' \
                        f'&bucketType=general&prefix={result["file_key_s3"]}'
            res: str = f'<a href="{link}" target="_blank">File Link</a>'
            return HttpResponse(res)
        elif "error" in result:
            return HttpResponse(result["error"])
