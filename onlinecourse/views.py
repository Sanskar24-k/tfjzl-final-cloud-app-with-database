from django.shortcuts import render, get_object_or_404, redirect
from .models import Course, Question, Choice, Submission

def course_details(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    return render(request, 'onlinecourse/course_details_bootstrap.html', {'course': course})

def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if request.method == 'POST':
        selected_ids = []
        for key, value in request.POST.items():
            if key.startswith('choice_'):
                selected_ids.append(int(value))

        submission = Submission.objects.create(enrollment=request.user)
        selected_choices = Choice.objects.filter(id__in=selected_ids)
        submission.choices.set(selected_choices)

        return redirect('onlinecourse:show_exam_result', course_id=course.id, submission_id=submission.id)
    return redirect('onlinecourse:course_details', course_id=course.id)

def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)
    selected_ids = submission.choices.values_list('id', flat=True)

    total_score = 0
    max_score = 0
    question_results = []

    for lesson in course.lesson_set.all():
        for question in lesson.question_set.all():
            max_score += question.grade
            is_correct = question.is_get_score(selected_ids)
            if is_correct:
                total_score += question.grade
            question_results.append({
                'question': question,
                'is_correct': is_correct,
            })

    grade_percentage = round((total_score / max_score * 100) if max_score > 0 else 0, 1)

    context = {
        'course': course,
        'submission': submission,
        'total_score': total_score,
        'max_score': max_score,
        'grade_percentage': grade_percentage,
        'passed': grade_percentage >= 70,
        'question_results': question_results,
    }
    return render(request, 'onlinecourse/exam_result.html', context)