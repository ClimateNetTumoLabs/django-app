from rest_framework import generics, viewsets, status
from rest_framework.response import Response
from .serializers import DeviceDetailSerializer
from .models import DeviceDetail
import pandas as pd
from datetime import datetime, timedelta
from .fetch_data import fetch_data_with_time_range, fetch_last_records, preprocess_device_data, \
    preprocess_device_data_new
from .count_means import compute_group_means, compute_mean_for_time_range

from django.db import connections



class DeviceDetailView(generics.ListAPIView):
    """
    Provides a detailed view of device data including
    querying by device ID and time range.

    """
    def get_queryset(self):
        device_id = self.kwargs.get('device_id')

        if device_id is None or not str(device_id).isdigit():
            return Response({'error': 'Invalid device_id'},
                            status=status.HTTP_400_BAD_REQUEST)

        start_time_str = self.request.GET.get('start_time_str')
        end_time_str = self.request.GET.get('end_time_str')
        if start_time_str == end_time_str:
            # Case where start_time_str equals end_time_str
            cursor = connections['aws'].cursor()
            # Example: Execute a query
            if not cursor:
                return Response({'error': 'Failed to establish a connection'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            table_name = f'device{str(device_id)}'
            rows = fetch_last_records(cursor, table_name)
            print(rows)
            if int(device_id) == 8:
                device_data = preprocess_device_data(rows)
            else:
                device_data = preprocess_device_data_new(rows)
            df = pd.DataFrame(device_data)
            df['time'] = pd.to_datetime(df['time'])

            num_records = len(df)

            if num_records < 24:
                return Response(device_data, status=status.HTTP_200_OK)
            else:
                group_means = compute_group_means(df, 4)
                return Response(group_means, status=status.HTTP_200_OK)

        try:
            cursor = establish_postgresql_connection().cursor()
            if not cursor:
                return Response({'error': 'Failed to establish a connection'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            table_name = f'device{str(device_id)}'

            # Case when filter is present
            if 'start_time_str' in self.request.query_params \
                    and 'end_time_str' in self.request.query_params:

                try:
                    start_date = datetime.strptime(start_time_str, '%Y-%m-%d')
                    end_date = datetime.strptime(end_time_str, '%Y-%m-%d')
                    + timedelta(days=1)

                    if start_date > end_date:
                        return Response({'error': 'start_time_str should be '
                                                  'earlier than end_time_str'},
                                        status=status.HTTP_400_BAD_REQUEST)

                    rows = fetch_data_with_time_range(cursor, table_name,
                                                      start_date, end_date)
                    device_data = preprocess_device_data(rows)

                    df = pd.DataFrame(device_data)
                    df['time'] = pd.to_datetime(df['time'])

                    num_records = len(df)

                    if num_records < 24:
                        return device_data
                    else:
                        interval = (end_date - start_date).days
                        if interval <= 1:
                            group_means = compute_group_means(df, 4)
                        else:
                            mean_interval = 4 * interval
                            group_means = compute_mean_for_time_range(df, start_date,
                                                                      end_date, mean_interval)

                        return Response(group_means, status=status.HTTP_200_OK)

                except ValueError:
                    return Response({'error': 'Invalid date format in '
                                              'start_time_str or end_time_str'},
                                    status=status.HTTP_400_BAD_REQUEST)

            # Case when query is not present
            elif not self.request.query_params:
                rows = fetch_last_records(cursor, table_name)
                device_data = preprocess_device_data(rows)

                df = pd.DataFrame(device_data)
                df['time'] = pd.to_datetime(df['time'])

                num_records = len(df)

                if num_records < 24:
                    return device_data
                else:
                    group_means = compute_group_means(df, 4)

                    return Response(group_means, status=status.HTTP_200_OK)
            else:
                return Response([], status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'An error occurred while fetching the data.'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            return queryset
        except Exception as e:
            return Response({'error': 'An error occurred while fetching the data.'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeviceDetailViewSet(viewsets.ModelViewSet):
    queryset = DeviceDetail.objects.all()
    serializer_class = DeviceDetailSerializer