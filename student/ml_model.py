import numpy as np

def predict_result(attendance, math, english, science, bangla):
    """
    Simple rule-based prediction
    TensorFlow এর মতো কাজ করে
    """
    # Average marks
    avg_marks = (math + english + science + bangla) / 4

    # Weighted score (attendance 30%, marks 70%)
    score = (attendance * 0.30) + (avg_marks * 0.70)

    # Pass/Fail logic
    failed_subjects = sum([
        1 for mark in [math, english, science, bangla] if mark < 33
    ])

    if score >= 50 and failed_subjects == 0 and attendance >= 75:
        prediction = "Pass"
        confidence = min(99, round(score + 10, 1))
    elif score >= 40 and failed_subjects <= 1 and attendance >= 60:
        prediction = "Borderline"
        confidence = round(score, 1)
    else:
        prediction = "Fail"
        confidence = round(100 - score, 1)

    return {
        'prediction': prediction,
        'confidence': confidence,
        'avg_marks': round(avg_marks, 1),
        'weighted_score': round(score, 1),
        'failed_subjects': failed_subjects,
        'details': {
            'math': math,
            'english': english,
            'science': science,
            'bangla': bangla,
            'attendance': attendance,
        }
    }