from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserDataCookieSerializer
from .models import UserDataCookie

class CollectUserDataView(APIView):
    def post(self, request):
        serializer = UserDataCookieSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Save data to the database
            return Response({"message": "Data successfully saved!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        data = UserDataCookie.objects.all()
        serializer = UserDataCookieSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
