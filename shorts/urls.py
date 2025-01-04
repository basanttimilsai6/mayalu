from django.urls import path
from shorts.views import YouTubeShortsByHobbyView

urlpatterns = [
    path('api/youtube-shorts-by-hobby/', YouTubeShortsByHobbyView.as_view(), name='youtube_shorts_by_hobby'),
]