import paho.mqtt.client as mqtt
import os
import ssl
import json
import time
import secrets
from .config import IAM_SECRET_KEY, IAM_ACCESS_KEY, MQTT_BROKER_ENDPOINT
from .s3 import S3Manager, BUCKET_TO_RASPBERRY, BUCKET_FROM_RASPBERRY
from django.views.decorators.cache import never_cache
from django.shortcuts import render, redirect
from backend.models import DeviceDetail
from django.contrib.auth import logout
from django.http import HttpResponse


results = {

}

current_working_directory = os.getcwd()

s3_manager = S3Manager(IAM_ACCESS_KEY, IAM_SECRET_KEY)


class MqttClient:
    def __init__(self):
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

    def process_message(self, clt, userdata, msg):
        message = json.loads(msg.payload.decode("utf-8"))
        request_id = message.get("RequestID")
        results[request_id] = message

    def publish(self, request):
        self.client.publish("raspberry/request", json.dumps(request))
        self.client.loop_start()


def logout_user(request):
    logout(request)
    return redirect('/admin/login/?next=/remote-control/')


@never_cache
def home(request):
    s3_files = s3_manager.list_files(bucket=BUCKET_TO_RASPBERRY)
    device_list = DeviceDetail.objects.all().order_by('parent_name', 'name')
    context = {
        'device_list': device_list,
        's3_files': s3_files
    }
    return render(request, 'remote_control/home.html', context)


def get_result(mqtt_request):
    one_time_token = secrets.token_hex(32)
    mqtt_request['RequestID'] = one_time_token

    client = MqttClient()
    client.publish(mqtt_request)

    start_time = time.time()
    status = False
    while time.time() - start_time < 5:
        if one_time_token in results:
            result = results[one_time_token]
            if result.get("status") == "OK":
                status = True
            del results[one_time_token]
            break
    if not status:
        client.client.loop_stop()
        return HttpResponse("Device Not Responding")

    result = "Timeout Error"

    start_time = time.time()
    while time.time() - start_time < 60:
        if one_time_token in results:
            result = results[one_time_token]
            del results[one_time_token]
            break

    client.client.loop_stop()

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


def submit_command_request(request):
    device_id = request.POST.get('deviceId')
    command = request.POST.get('command')

    if not all([device_id, command]):
        return HttpResponse("ERROR: Missing required parameters")

    mqtt_request = {
        'DeviceID': device_id,
        'type': "command_request",
        'command': command
    }

    return get_result(mqtt_request)


def submit_result_as_file_request(request):
    device_id = request.POST.get('resultAsFileDeviceId')
    command = request.POST.get('resultAsFileCommand')

    if not all([device_id, command]):
        return HttpResponse("ERROR: Missing required parameters")

    mqtt_request = {
        'DeviceID': device_id,
        'type': "command_file_request",
        'command': command
    }

    return get_result(mqtt_request)


def submit_file_request(request):
    device_id = request.POST.get('fileDeviceId')
    file_path = request.POST.get('filePath')

    if not all([device_id, file_path]):
        return HttpResponse("ERROR: Missing required parameters")

    mqtt_request = {
        'DeviceID': device_id,
        'type': "file_request",
        'file_path': file_path
    }

    return get_result(mqtt_request)


def submit_file_transfer(request):
    device_id = request.POST.get('fileTransferDeviceId')
    file_key = request.POST.get('fileTransferS3Key')
    destination_path = request.POST.get('fileTransferDestination')

    if not all([device_id, file_key, destination_path]):
        return HttpResponse("ERROR: Missing required parameters")

    mqtt_request = {
        'DeviceID': device_id,
        'type': "file_transfer",
        's3_file_key': file_key,
        'destination_path': destination_path
    }

    return get_result(mqtt_request)
