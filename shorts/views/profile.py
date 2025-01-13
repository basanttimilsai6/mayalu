from concurrent.futures import ThreadPoolExecutor
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from shorts.serializers import YouTubeShortSerializer
from userprofile.models import User, UserProfile
from youtubesearchpython import VideosSearch
import random
import logging

class YouTubeShortsByHobbyView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = YouTubeShortSerializer

    def fetch_videos(self, query,limit):
        video_search = VideosSearch(query, limit=limit)  # Reduced limit to speed up
        results = video_search.result()['result']
        return [
            {
                'input': query,
                'title': vid['title'],
                'duration': vid['duration'],
                'thumbnail': vid['thumbnails'][0]['url'],
                'channel': vid['channel']['name'],
                'link': vid['link'],
                'views': vid['viewCount']['short'],
                'published': vid['publishedTime'],
                'description': ''.join([snip['text'] for snip in vid['descriptionSnippet']]) if vid.get('descriptionSnippet') else ''
            }
            for vid in results
        ]

    def get(self, request, format=None):
        try:
            print(request.user)
            user = User.objects.get(email=request.user)
            try:
                profile = UserProfile.objects.get(user=user)
                hobbies = profile.hobbies.all()
                print(hobbies)
            except UserProfile.DoesNotExist:
                return Response({"error": "User profile not found."}, status=status.HTTP_404_NOT_FOUND)

            if not hobbies:
                return Response({"error": "No hobbies found for the user."}, status=status.HTTP_404_NOT_FOUND)

            hobby_names = [hobby.name for hobby in hobbies]
            hobby_count = len(hobbies)
            if hobby_count == 1:
                limit = 30
            elif hobby_count == 2:
                limit = 15
            elif hobby_count == 3:
                limit = 10
            elif hobby_count == 4:
                limit = 7
            elif hobby_count == 5:
                limit = 6
            elif hobby_count == 6:
                limit = 5
            else:
                limit=1
            
            result_lst = []
            with ThreadPoolExecutor() as executor:
                future_to_query = {executor.submit(self.fetch_videos, f"{hobby} shorts",limit): hobby for hobby in hobby_names}
                for future in future_to_query:
                    try:
                        result_lst.extend(future.result())
                    except Exception as e:
                        logging.error(f"Error fetching videos for hobby {future_to_query[future]}: {e}")

            random.shuffle(result_lst)

            return Response({'data': result_lst}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error':'Something went wrong..'
            })
