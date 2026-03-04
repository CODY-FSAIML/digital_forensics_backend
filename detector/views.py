import os
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage
from rest_framework import status
from .models import ForensicScan
from .utils.video_ai import analyze_video_realness

# Import your utility functions
from .utils.video_processor import extract_best_frames
from .utils.image_forensics import perform_ela, analyze_screenshot_content
from .utils.forensic_logic import get_forensic_reasons
from .utils.audio_analyzer import analyze_audio_signature

@method_decorator(csrf_exempt, name='dispatch')
class VideoForensicView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        file_obj = request.FILES.get('file')
        
        # 1. Validation: Ensure file exists
        if not file_obj:
            return Response({"error": "No video file provided. Use key: 'file'"}, status=status.HTTP_400_BAD_REQUEST)

        # 2. Save file safely
        file_name = default_storage.save('temp_video.mp4', file_obj)
        file_path = default_storage.path(file_name)

        try:
            # 1. Run the REAL Computer Vision analysis
            fake_score, calculated_reasons = analyze_video_realness(file_path)
            
            # 2. Convert to percentages
            is_fake_result = bool(fake_score > 0.60) # 60% threshold
            
            # If it's real, confidence is how sure we are it's real. If fake, how sure it's fake.
            confidence = float(fake_score * 100) if is_fake_result else float((1.0 - fake_score) * 100)

            # --- SAVE TO DATABASE ---
            ForensicScan.objects.create(
                media_type='VIDEO', file_name=file_obj.name,
                is_fake=is_fake_result, confidence=confidence, reasons=calculated_reasons
            )

            return Response({
                "is_fake": is_fake_result,
                "confidence": round(confidence, 1),
                "reasons": calculated_reasons,
                "metadata": {"frames_analyzed": True, "cv2_engine": "active"}
            })
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            # 3. Cleanup
            if os.path.exists(file_path): 
                os.remove(file_path)

@method_decorator(csrf_exempt, name='dispatch')
class ImageForensicView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        file_obj = request.FILES.get('file')
        
        if not file_obj:
            return Response({"error": "No image file provided. Use key: 'file'"}, status=status.HTTP_400_BAD_REQUEST)

        file_name = default_storage.save('temp_img.jpg', file_obj)
        file_path = default_storage.path(file_name)

        try:
            tamper_score, _ = perform_ela(file_path)
            text, scams = analyze_screenshot_content(file_path)
            
            is_fake = tamper_score > 25 or len(scams) > 0
            reasons = get_forensic_reasons('IMAGE', {
                'ela_score': tamper_score, 
                'is_scam_text': len(scams) > 0
            })

            # Calculate real confidence based on the ELA tamper score (assuming score > 25 is fake)
            if is_fake:
                confidence = min(99.9, 50.0 + (tamper_score * 1.5))
            else:
                confidence = max(50.1, 100.0 - (tamper_score * 2.0))
                
            confidence = round(float(confidence), 1)

            # --- THE FIX: We need to declare these variables before saving! ---
            is_fake_result = bool(is_fake)
            metadata = {"detected_text": text[:200]} if text else {}
            # ------------------------------------------------------------------

            # --- SAVE TO DATABASE ---
            ForensicScan.objects.create(
                media_type='IMAGE',
                file_name=file_obj.name,
                is_fake=is_fake_result,
                confidence=confidence,
                reasons=reasons
            )
            # ------------------------

            return Response({
                "is_fake": is_fake_result,
                "confidence": confidence,
                "reasons": reasons,
                "metadata": metadata
            })
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            if os.path.exists(file_path): 
                os.remove(file_path)

@method_decorator(csrf_exempt, name='dispatch')
class AudioForensicView(APIView):
    # Added parsers so request.FILES isn't empty
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        file_obj = request.FILES.get('file')
        
        if not file_obj:
            return Response({"error": "No audio file provided. Use key: 'file'"}, status=status.HTTP_400_BAD_REQUEST)

        file_name = default_storage.save('temp_audio.wav', file_obj)
        file_path = default_storage.path(file_name)
        
        try:
            results = analyze_audio_signature(file_path)

            # normalize
            reasons = results.get('reasons', [])
            if not isinstance(reasons, list):
                reasons = [str(reasons)]
            if not reasons:
                reasons = ["No significant digital artifacts detected."]

            confidence = float(results.get('confidence', 0.0))
            metadata = results.get('stats') if isinstance(results.get('stats'), dict) else {}
            is_fake_result = bool(results.get('is_fake', False))

            # --- SAVE TO DATABASE ---
            ForensicScan.objects.create(
                media_type='AUDIO',
                file_name=file_obj.name,
                is_fake=is_fake_result,
                confidence=confidence,
                reasons=reasons
            )
            # ------------------------

            return Response({
                "is_fake": is_fake_result,
                "confidence": confidence,
                "reasons": reasons,
                "metadata": metadata
            })
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)