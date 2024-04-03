from rest_framework import generics, viewsets, status
from rest_framework.response import Response
import pandas as pd
from datetime import datetime, timedelta
from collections import Counter
from django.http import HttpResponse
from rest_framework.decorators import api_view


def compute_group_means(df, mean_interval):
    """Compute means for groups of data within the given interval."""
    num_records = len(df)
    num_groups = num_records // mean_interval
    group_means = []

    for i in range(num_groups):
        group_start = i * mean_interval
        group_end = (i + 1) * mean_interval
        group = df.iloc[group_start:group_end]

        group_mean = {}

        for column in group.columns:
            if column == 'time':
                time_mean = group['time'].apply(lambda x: pd.to_datetime(x)).mean()
                mean_time_formatted = time_mean.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
                group_mean['time'] = mean_time_formatted
            elif pd.api.types.is_numeric_dtype(group[column].dtype):
                mean_value = round(group[column].mean(), 2)
                group_mean[column] = mean_value
            else:
                group_mean[column] = None
        if not group.empty:
            most_frequent_direction = Counter(group['direction']).most_common(1)[0][0]
            group_mean['direction'] = most_frequent_direction
        else:
            group_mean['direction'] = None

        group_means.append(group_mean)

    return group_means


def compute_mean_for_time_range(df, start_time, end_time, mean_interval):
    """Compute means for each day within the given time range."""
    num_records = len(df)
    num_days = (end_time - start_time).days
    mean_data = []

    for i in range(num_days):
        day_start = start_time + timedelta(days=i)
        day_end = day_start + timedelta(days=1)
        filtered_df = df[(df['time'] >= day_start) & (df['time'] < day_end)]

        if not filtered_df.empty:
            day_mean = {}
            day_mean['time'] = day_start.strftime('%Y-%m-%d')

            for column in df.columns:
                if column == 'time':
                    continue
                if pd.api.types.is_numeric_dtype(df[column].dtype):
                    mean_value = round(filtered_df[column].mean(), 2)
                    day_mean[column] = mean_value
                else:
                    day_mean[column] = None

            most_frequent_direction = Counter(filtered_df['direction']).most_common(1)
            if most_frequent_direction:
                day_mean['direction'] = most_frequent_direction[0][0]
            else:
                day_mean['direction'] = None

            mean_data.append(day_mean)
        else:
            mean_data.append(None)

    return mean_data


