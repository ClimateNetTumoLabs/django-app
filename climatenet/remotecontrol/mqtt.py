import os
import paho.mqtt.client as mqtt
import ssl
import json

from django.http import HttpResponse

from .config import MQTT_BROKER_ENDPOINT
import time
import secrets

from .s3 import BUCKET_FROM_RASPBERRY

current_working_directory = os.getcwd()


class MqttClient:
    def __init__(self):
        self.respondingTimeout = 5
        self.resultTimeout = 60
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
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

    def process_message(self, clt, userdata, msg):
        message = json.loads(msg.payload.decode("utf-8"))
        request_id = message.get("RequestID")
        self.results[request_id] = message

    def publish(self, request):
        self.client.publish("raspberry/request", json.dumps(request))
        self.client.loop_start()

    def wait_for_result(self, one_time_token, timeout):
        start_time = time.time()
        while time.time() - start_time < timeout:
            if one_time_token in self.results:
                return self.results.pop(one_time_token)
        return "Timeout Error"

    def wait_for_confirmation(self, one_time_token, timeout):
        start_time = time.time()

        while time.time() - start_time < timeout:
            if one_time_token in self.results:
                if self.results.pop(one_time_token)["status"] == "OK":
                    return True
        return False

    def request_handler(self, request_type: str, device_id: str, respondingTimeout: str, resultTimeout: str, **kwargs):
        mqtt_request = {
            'DeviceID': device_id,
            'type': request_type,
            **kwargs
        }

        self.respondingTimeout = int(respondingTimeout)
        self.resultTimeout = int(resultTimeout)

        one_time_token = secrets.token_hex(32)
        mqtt_request['RequestID'] = one_time_token

        self.publish(mqtt_request)

        return self.get_result(one_time_token)

    def get_result(self, one_time_token):
        status = self.wait_for_confirmation(one_time_token, self.respondingTimeout)

        if not status:
            self.client.loop_stop()
            return HttpResponse("Device Not Responding")

        result = self.wait_for_result(one_time_token, self.resultTimeout)

        self.client.loop_stop()

        if "result" in result:
            return HttpResponse(result["result"])
        elif "file_key_s3" in result:
            link = f'https://s3.console.aws.amazon.com/s3/object/{BUCKET_FROM_RASPBERRY}?region=us-east-1' \
                   f'&bucketType=general&prefix={result["file_key_s3"]}'

            res = f'<a href="{link}" target="_blank">File Link</a>'
            return HttpResponse(res)
        elif "error" in result:
            return HttpResponse(result["error"])
        else:
            return HttpResponse(result)
