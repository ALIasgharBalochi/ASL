from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser


# Create your models here.
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)


class Category(models.Model):
    name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)


class Process(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="process"
    )
    visibility_choise = [("public", "Public"), ("private", "Private")]
    process_type = [("liner", "Liner"), ("free", "Free")]

    visibility = models.CharField(choices=visibility_choise)
    type = models.CharField(choices=process_type)

    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="process"
    )
    created_at = models.DateTimeField(auto_now_add=True)


class Form(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    visibility_choise = [("public", "Public"), ("private", "Private")]

    visibility = models.CharField(choices=visibility_choise)
    proces = models.ForeignKey(Process, on_delete=models.CASCADE, related_name="forms")

    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="forms"
    )

    created_at = models.DateTimeField(auto_now_add=True)


class Question(models.Model):
    text = models.CharField(max_length=150)
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name="questions")
    is_requierd = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)


class QuestionOption(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="options",
    )
    value = models.CharField(max_length=50)


class Submission(models.Model):
    form = models.ForeignKey(
        Form,
        on_delete=models.CASCADE,
        related_name="submissions",
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="submissions",
    )
    created_at = models.DateTimeField(auto_now_add=True)


class Answer(models.Model):
    submission = models.ForeignKey(
        Submission,
        on_delete=models.CASCADE,
        related_name="answers",
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="answers",
    )
    value = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)


class AnswerOption(models.Model):
    answer = models.ForeignKey(
        Answer,
        on_delete=models.CASCADE,
        related_name="selected_options",
    )
    option = models.ForeignKey(
        QuestionOption,
        on_delete=models.CASCADE,
        related_name="answers",
    )
