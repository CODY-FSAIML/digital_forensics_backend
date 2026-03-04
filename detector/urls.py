from django.urls import path
from .views import VideoForensicView, ImageForensicView, AudioForensicView

urlpatterns = [
    path('analyze/video/', VideoForensicView.as_view(), name='video-forensic'),
    path('analyze/image/', ImageForensicView.as_view(), name='image-forensic'),
    path('analyze/audio/', AudioForensicView.as_view(), name='audio-forensic'),
]