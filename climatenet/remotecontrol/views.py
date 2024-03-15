from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.cache import never_cache
from django.contrib import messages
import paho.mqtt.client as mqtt
import os
import ssl
import json
import time
import secrets

results = {

}

current_working_directory = os.getcwd()


class MqttClient:
    def __init__(self):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
        self.client.tls_set(
            ca_certs=os.path.join(current_working_directory, 'remotecontrol/mqtt_certificates/AmazonRootCA1.pem'),
            certfile=os.path.join(current_working_directory, 'remotecontrol/mqtt_certificates/certificate.pem.crt'),
            keyfile=os.path.join(current_working_directory, 'remotecontrol/mqtt_certificates/private.pem.key'),
            tls_version=ssl.PROTOCOL_SSLv23)
        self.client.tls_insecure_set(True)
        self.client.connect("a3b2v7yks3ewbi-ats.iot.us-east-1.amazonaws.com", 8883, 60)
        self.client.on_message = self.process_message
        self.client.subscribe("raspberry/response", qos=1)

    def process_message(self, clt, userdata, msg):
        message = json.loads(msg.payload.decode("utf-8"))
        request_id = message.get("RequestID")
        results[request_id] = message
        self.client.loop_stop()

    def publish(self, request):
        self.client.publish("raspberry/request", json.dumps(request))
        self.client.loop_start()


def logout_user(request):
    logout(request)
    return redirect('remote-control-login')


@never_cache
def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('remote-control')
        else:
            messages.success(request, "Something Wrong")
            return redirect('remote-control-login')
    else:
        return render(request, 'authenticate/login.html', {})


@never_cache
def home(request):
    return render(request, 'remote_control/home.html')


def get_result(mqtt_request):
    one_time_token = secrets.token_hex(32)
    mqtt_request['RequestID'] = one_time_token

    client = MqttClient()
    client.publish(mqtt_request)

    result = "Timeout Error"

    start_time = time.time()
    while time.time() - start_time < 15:
        if one_time_token in results:
            result = results[one_time_token]
            del results[one_time_token]
            break

    if "result" in result:
        return HttpResponse(result["result"])
    elif "file_key_s3" in result:
        link = f'https://s3.console.aws.amazon.com/s3/object/raspberry-file-transfer?region=us-east-1' \
               f'&bucketType=general&prefix={result["file_key_s3"]}'

        res = f'<a href="{link}" target="_blank">File Link</a>'
        print(res)
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


def submit_command_file_request(request):
    device_id = request.POST.get('commandFileDeviceId')
    command = request.POST.get('commandFileCommand')

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
