from .models import Form , Submission

def can_access_form(form,user=None,session_id=None):

    if form.process.type == "free":
        return True

    previous_form = Form.objects.filter(
        process=form.process,
        order=form.order - 1
    ).first()

    if previous_form is None:
        return True

    if user and user.is_authenticated:
        return Submission.objects.filter(
            form=previous_form,
            user=user
        ).exists()

    if session_id is None:
        return False 
    
    return Submission.objects.filter(
        form=previous_form,
        user__isnull=True,
        session_id=session_id
    ).exists()
