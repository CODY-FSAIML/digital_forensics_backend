from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from unittest.mock import patch
from django.core.files.uploadedfile import SimpleUploadedFile


class ForensicViewsFormatTests(TestCase):
    def make_file(self, name=b"dummy", content=b"data"):
        return SimpleUploadedFile(name, content)

    @patch('detector.views.extract_best_frames')
    @patch('detector.views.get_forensic_reasons')
    def test_video_response_structure(self, mock_reasons, mock_frames):
        # stub utilities
        mock_frames.return_value = ([], {'resolution': '1920x1080'})
        mock_reasons.return_value = []

        response = self.client.post(
            reverse('video-forensic'),
            {'file': self.make_file()},
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        # check keys
        self.assertIn('is_fake', data)
        self.assertIn('confidence', data)
        self.assertIn('reasons', data)
        self.assertIn('metadata', data)
        self.assertIsInstance(data['reasons'], list)
        self.assertTrue(data['reasons'])  # default safe reason provided
        self.assertIsInstance(data['confidence'], float)
        self.assertIsInstance(data['metadata'], dict)

    @patch('detector.views.perform_ela')
    @patch('detector.views.analyze_screenshot_content')
    @patch('detector.views.get_forensic_reasons')
    def test_image_response_structure(self, mock_reasons, mock_content, mock_ela):
        mock_ela.return_value = (10, None)
        mock_content.return_value = ('', [])
        mock_reasons.return_value = []

        response = self.client.post(
            reverse('image-forensic'),
            {'file': self.make_file()},
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('is_fake', data)
        self.assertIn('confidence', data)
        self.assertIn('reasons', data)
        self.assertIn('metadata', data)
        self.assertIsInstance(data['reasons'], list)
        self.assertTrue(data['reasons'])
        self.assertIsInstance(data['confidence'], float)
        self.assertIsInstance(data['metadata'], dict)

    @patch('detector.views.analyze_audio_signature')
    def test_audio_response_structure(self, mock_audio):
        mock_audio.return_value = {'is_fake': False, 'confidence': 0, 'reasons': [], 'stats': {}}
        response = self.client.post(
            reverse('audio-forensic'),
            {'file': self.make_file()},
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('is_fake', data)
        self.assertIn('confidence', data)
        self.assertIn('reasons', data)
        self.assertIn('metadata', data)
        self.assertIsInstance(data['reasons'], list)
        self.assertTrue(data['reasons'])
        self.assertIsInstance(data['confidence'], float)
        self.assertIsInstance(data['metadata'], dict)
