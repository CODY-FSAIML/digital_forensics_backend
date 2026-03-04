def get_forensic_reasons(media_type, analysis_data):
    reasons = []
    if media_type == 'IMAGE':
        if analysis_data.get('ela_score', 0) > 30:
            reasons.append("Digital Tampering: High pixel inconsistency detected (ELA). This suggests the image was edited.")
        if analysis_data.get('is_scam_text'):
            reasons.append("Linguistic Red Flag: The text content matches known scam/phishing templates.")
    elif media_type == 'VIDEO':
        if analysis_data.get('face_consistency', 1) < 0.6:
            reasons.append("Visual Artifacts: Inconsistent skin textures and 'ghosting' around facial boundaries.")
        if analysis_data.get('unnatural_blinking'):
            reasons.append("Biological Error: The subject's blink rate is statistically improbable.")
    return reasons