from .config import IAM_SECRET_KEY, IAM_ACCESS_KEY
from .s3 import S3Manager, BUCKET_TO_RASPBERRY
from django.views.decorators.cache import never_cache
from django.http import HttpResponse, JsonResponse
from backend.models import DeviceDetail
from django.shortcuts import render
from .mqtt import MqttClient


s3_manager = S3Manager(IAM_ACCESS_KEY, IAM_SECRET_KEY)
mqtt_manager = MqttClient()


@never_cache
def home(request):
    s3_files = s3_manager.files_list(bucket=BUCKET_TO_RASPBERRY)

    parent_list = set(DeviceDetail.objects.values_list('parent_name', flat=True).order_by('parent_name'))

    context = {
        'province_list': list(parent_list),
        's3_files': s3_files
    }
    return render(request, 'remote_control/home.html', context)


def submit_command_request(request):
    device_id = request.POST.get('deviceId')
    command = request.POST.get('command')
    respondingTimeout = request.POST.get('respondingTimeout')
    resultTimeout = request.POST.get('resultTimeout')
    print(device_id, respondingTimeout, resultTimeout, command)
    if not all([device_id, command, respondingTimeout, resultTimeout]):
        return HttpResponse("ERROR: Missing required parameters")

    return mqtt_manager.request_handler(request_type="command_request",
                                        device_id=device_id,
                                        respondingTimeout=respondingTimeout,
                                        resultTimeout=resultTimeout,
                                        command=command)


def submit_result_as_file_request(request):
    device_id = request.POST.get('deviceId')
    command = request.POST.get('resultAsFileCommand')
    respondingTimeout = request.POST.get('respondingTimeout')
    resultTimeout = request.POST.get('resultTimeout')

    if not all([device_id, respondingTimeout, resultTimeout, command]):
        return HttpResponse("ERROR: Missing required parameters")

    return mqtt_manager.request_handler(request_type="command_file_request",
                                        device_id=device_id,
                                        respondingTimeout=respondingTimeout,
                                        resultTimeout=resultTimeout,
                                        command=command)


def submit_file_request(request):
    device_id = request.POST.get('deviceId')
    file_path = request.POST.get('filePath')
    respondingTimeout = request.POST.get('respondingTimeout')
    resultTimeout = request.POST.get('resultTimeout')

    if not all([device_id, respondingTimeout, resultTimeout, file_path]):
        return HttpResponse("ERROR: Missing required parameters")

    return mqtt_manager.request_handler(request_type="file_request",
                                        device_id=device_id,
                                        respondingTimeout=respondingTimeout,
                                        resultTimeout=resultTimeout,
                                        file_path=file_path)


def submit_file_transfer(request):
    device_id = request.POST.get('deviceId')
    file_key = request.POST.get('fileTransferS3Key')
    destination_path = request.POST.get('fileTransferDestination')
    respondingTimeout = request.POST.get('respondingTimeout')
    resultTimeout = request.POST.get('resultTimeout')

    if not all([device_id, respondingTimeout, resultTimeout, file_key, destination_path]):
        return HttpResponse("ERROR: Missing required parameters")

    return mqtt_manager.request_handler(request_type="file_transfer",
                                        device_id=device_id,
                                        respondingTimeout=respondingTimeout,
                                        resultTimeout=resultTimeout,
                                        s3_file_key=file_key,
                                        destination_path=destination_path)


def get_devices(request):
    if request.method == 'GET':
        province = request.GET.get('province', None)
        if province is not None:
            devices = DeviceDetail.objects.filter(parent_name=province).order_by('name')
            device_list = [{'generated_id': device.generated_id,
                            'name': device.name} for device in devices]
            return JsonResponse(device_list, safe=False)
        else:
            return JsonResponse([], safe=False)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)
