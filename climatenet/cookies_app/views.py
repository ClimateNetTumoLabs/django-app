from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserDataCookieSerializer
from .models import UserDataCookie

import logging

logger = logging.getLogger(__name__)
class CollectUserDataView(APIView):
    def post(self, request):
        try:
            data = request.data.copy()
            print(request.data)
            # Handle location field

            if 'location' in data:
                try:
                    # Split location into longitude and latitude
                    latitude, longitude = map(float, data['location'].split())

                    # Round to 6 decimal places
                    longitude = round(longitude, 6)
                    latitude = round(latitude, 6)
                    data['longitude'] = longitude
                    data['latitude'] = latitude
                    # Remove original location field
                    del data['location']
                except (ValueError, TypeError):
                    return Response({
                        "error": "Invalid location format"
                    }, status=status.HTTP_400_BAD_REQUEST)

            # Check if user with email already exists
            existing_user = UserDataCookie.objects.filter(email=data.get('email')).first()
            print(existing_user)
            if existing_user:
                # Update existing user
                serializer = UserDataCookieSerializer(existing_user, data=data, partial=True)
            else:
                # Create new user
                serializer = UserDataCookieSerializer(data=data)

            if serializer.is_valid():
                serializer.save()
                return Response({
                    "message": "Data successfully saved!",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "error": "An unexpected error occurred",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        data = UserDataCookie.objects.all()
        serializer = UserDataCookieSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)