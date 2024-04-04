"""
This module contains views for handling requests related to remote device control.

Functions:
    - home: Renders the home page with a list of devices and S3 files.
    - submit_command_request: Submits a command request to a device via MQTT.
    - submit_result_as_file_request: Submits a request for command result as a file via MQTT.
    - submit_file_request: Submits a file request to a device via MQTT.
    - submit_file_transfer: Initiates a file transfer request to a device via MQTT.
    - get_devices: Retrieves a list of devices filtered by province.

Dependencies:
    - django.http.HttpRequest: Django HTTP request object.
    - django.http.HttpResponse: Django HTTP response object.
    - django.http.JsonResponse: Django JSON response object.
    - django.shortcuts.render: Django shortcut for rendering HTML templates.
    - django.views.decorators.cache.never_cache: Decorator to ensure a view is never cached.
    - IAM_SECRET_KEY: Secret key for AWS IAM authentication.
    - IAM_ACCESS_KEY: Access key for AWS IAM authentication.
    - .s3.S3Manager: Manager class for interacting with Amazon S3.
    - .s3.BUCKET_TO_RASPBERRY: Name of the S3 bucket.
    - backend.models.DeviceDetail: Django model representing device details.
    - .mqtt.MqttClient: MQTT client for communicating with devices.

Global Variables:
    - s3_manager: Instance of S3Manager for managing S3 operations.
    - mqtt_manager: Instance of MqttClient for handling MQTT communication.

"""

import os
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from .s3 import S3Manager, BUCKET_TO_RASPBERRY
from backend.models import DeviceDetail
from .mqtt import MqttClient
from dotenv import load_dotenv

load_dotenv()

IAM_SECRET_KEY = os.getenv('IAM_SECRET_KEY')
IAM_ACCESS_KEY = os.getenv('IAM_ACCESS_KEY')

s3_manager = S3Manager(IAM_ACCESS_KEY, IAM_SECRET_KEY)
mqtt_manager = MqttClient()


@never_cache
def home(request: HttpRequest) -> HttpResponse:
    """
    Renders the home page with a list of devices and S3 files.

    Parameters:
        request (HttpRequest): Django HTTP request object.

    Returns:
        HttpResponse: Rendered HTML response.
    """
    s3_files = s3_manager.files_list(bucket=BUCKET_TO_RASPBERRY)
    parent_list = set(DeviceDetail.objects.values_list('parent_name', flat=True).order_by('parent_name'))
    context = {
        'province_list': list(parent_list),
        's3_files': s3_files
    }
    return render(request, 'remote_control/home.html', context)


def submit_command_request(request: HttpRequest) -> HttpResponse:
    """
    Submits a command request to a device via MQTT.

    Parameters:
        request (HttpRequest): Django HTTP request object.

    Returns:
        HttpResponse: Response indicating success or failure.
    """
    device_id = request.POST.get('deviceId', '')
    command = request.POST.get('command', '')
    respondingTimeout = request.POST.get('respondingTimeout', '')
    resultTimeout = request.POST.get('resultTimeout', '')

    if not all([device_id, command, respondingTimeout, resultTimeout]):
        return HttpResponse("ERROR: Missing required parameters")

    return mqtt_manager.request_handler(request_type="command_request",
                                        device_id=device_id,
                                        respondingTimeout=respondingTimeout,
                                        resultTimeout=resultTimeout,
                                        command=command)


def submit_result_as_file_request(request: HttpRequest) -> HttpResponse:
    """
    Submits a request for command result as a file via MQTT.

    Parameters:
        request (HttpRequest): Django HTTP request object.

    Returns:
        HttpResponse: Response indicating success or failure.
    """
    device_id = request.POST.get('deviceId', '')
    command = request.POST.get('resultAsFileCommand', '')
    respondingTimeout = request.POST.get('respondingTimeout', '')
    resultTimeout = request.POST.get('resultTimeout', '')

    if not all([device_id, respondingTimeout, resultTimeout, command]):
        return HttpResponse("ERROR: Missing required parameters")

    return mqtt_manager.request_handler(request_type="command_file_request",
                                        device_id=device_id,
                                        respondingTimeout=respondingTimeout,
                                        resultTimeout=resultTimeout,
                                        command=command)


def submit_file_request(request: HttpRequest) -> HttpResponse:
    """
    Submits a file request to a device via MQTT.

    Parameters:
        request (HttpRequest): Django HTTP request object.

    Returns:
        HttpResponse: Response indicating success or failure.
    """
    device_id = request.POST.get('deviceId', '')
    file_path = request.POST.get('filePath', '')
    respondingTimeout = request.POST.get('respondingTimeout', '')
    resultTimeout = request.POST.get('resultTimeout', '')

    if not all([device_id, respondingTimeout, resultTimeout, file_path]):
        return HttpResponse("ERROR: Missing required parameters")

    return mqtt_manager.request_handler(request_type="file_request",
                                        device_id=device_id,
                                        respondingTimeout=respondingTimeout,
                                        resultTimeout=resultTimeout,
                                        file_path=file_path)


def submit_file_transfer(request: HttpRequest) -> HttpResponse:
    """
    Initiates a file transfer request to a device via MQTT.

    Parameters:
        request (HttpRequest): Django HTTP request object.

    Returns:
        HttpResponse: Response indicating success or failure.
    """
    device_id = request.POST.get('deviceId', '')
    file_key = request.POST.get('fileTransferS3Key', '')
    destination_path = request.POST.get('fileTransferDestination', '')
    respondingTimeout = request.POST.get('respondingTimeout', '')
    resultTimeout = request.POST.get('resultTimeout', '')

    if not all([device_id, respondingTimeout, resultTimeout, file_key, destination_path]):
        return HttpResponse("ERROR: Missing required parameters")

    return mqtt_manager.request_handler(request_type="file_transfer",
                                        device_id=device_id,
                                        respondingTimeout=respondingTimeout,
                                        resultTimeout=resultTimeout,
                                        s3_file_key=file_key,
                                        destination_path=destination_path)


def get_devices(request: HttpRequest) -> JsonResponse:
    """
    Retrieves a list of devices filtered by province.

    Parameters:
        request (HttpRequest): Django HTTP request object.

    Returns:
        JsonResponse: JSON response containing a list of devices.
    """
    if request.method == 'GET':
        province = request.GET.get('province', '')

        if province:
            devices = DeviceDetail.objects.filter(parent_name=province).order_by('name')
            device_list = [{'generated_id': device.generated_id,
                            'name': device.name} for device in devices]
            return JsonResponse(device_list, safe=False)
        else:
            return JsonResponse([], safe=False)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)
