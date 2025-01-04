import random
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from shorts.serializers import YouTubeShortSerializer
from userprofile.models import UserProfile
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from youtubesearchpython import VideosSearch
from userprofile.models import *

class YouTubeShortsByHobbyView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = YouTubeShortSerializer

    def get(self, request, format=None):
        print(User.objects.first().username)
        print(request.user)
        user = User.objects.get(username=request.user)
        try:
            profile = UserProfile.objects.get(user=user)
            hobbies = profile.hobbies.all()  # Fetch all hobbies for the user
        except UserProfile.DoesNotExist:
            return Response({"error": "User profile not found."}, status=status.HTTP_404_NOT_FOUND)

        if not hobbies:
            return Response({"error": "No hobbies found for the user."}, status=status.HTTP_404_NOT_FOUND)

        result_lst = []

        # Fetch YouTube Shorts based on the user's hobby
        for hobby in hobbies:
            query = f"{hobby.name} shorts"  # Use hobby name to form the query
            video = VideosSearch(query, limit=10)
            for i in video.result()['result']:
                result_dict = {
                    'input': query,
                    'title': i['title'],
                    'duration': i['duration'],
                    'thumbnail': i['thumbnails'][0]['url'],
                    'channel': i['channel']['name'],
                    'link': i['link'],
                    'views': i['viewCount']['short'],
                    'published': i['publishedTime'],
                }
                desc = ''
                if i['descriptionSnippet']:
                    for j in i['descriptionSnippet']:
                        desc += j['text']
                result_dict['description'] = desc
                result_lst.append(result_dict)

        return Response({'data': random.shuffle(result_lst)}, status=status.HTTP_200_OK)


























# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from shorts.serializers import YouTubeShortSerializer
# from userprofile.models import UserProfile
# from rest_framework.permissions import IsAuthenticated
# from rest_framework import status
# from userprofile.models import User, UserProfile
# from rest_framework_simplejwt.authentication import JWTAuthentication

# from youtubesearchpython import VideosSearch

# class YouTubeShortsByHobbyView(APIView):
#     authentication_classes = [JWTAuthentication]
#     serializer_class = YouTubeShortSerializer
#     permission_classes = [IsAuthenticated]


#     def get(self, request, format=None):
#         try:
#             profile = UserProfile.objects.get(user=request.user)
#             hobbey = profile.hobby
#         except:
#             return Response({"error": "User's hobby not found."}, status=status.HTTP_404_NOT_FOUND)

#         # Fetch YouTube Shorts based on the user's hobby
#         query = hobbey + ' shorts'
#         print(query)
#         result_lst = []
#         video = VideosSearch(query, limit=10)
#         for i in video.result()['result']:
#                 result_dict={
#                     'input':query,
#                     'title':i['title'],
#                     'duration':i['duration'],
#                     'thumbnail':i['thumbnails'][0]['url'],
#                     'channel':i['channel']['name'],
#                     'link':i['link'],
#                     'views':i['viewCount']['short'],
#                     'published':i['publishedTime'],
#                 }
#                 desc = ''
#                 if i['descriptionSnippet']:
#                     for j in i['descriptionSnippet']:
#                         desc += j['text']
#                 result_dict['description']=desc
#                 result_lst.append(result_dict)

#         # Serialize the data
#         # serializer = YouTubeShortSerializer(result_lst, many=True)
#         return Response({'data':result_lst}, status=status.HTTP_200_OK)
