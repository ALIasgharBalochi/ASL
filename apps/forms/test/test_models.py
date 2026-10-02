from uuid import UUID

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.forms.models import (
    Answer,
    AnswerOption,
    Category,
    Form,
    Process,
    Question,
    QuestionOption,
    Submission,
)

User = get_user_model()


class CategoryModelTest(TestCase):

    def test_create_category(self):
        category = Category.objects.create(
            name="Technology",
        )

        self.assertEqual(category.name, "Technology")
        self.assertIsNotNone(category.created_at)


class ProcessModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

        self.category = Category.objects.create(
            name="Technology",
        )

    def test_create_process(self):
        process = Process.objects.create(
            user=self.user,
            visibility="public",
            type="liner",
            category=self.category,
        )

        self.assertEqual(process.user, self.user)
        self.assertEqual(process.visibility, "public")
        self.assertEqual(process.type, "liner")
        self.assertEqual(process.category, self.category)

    def test_set_password_hashes_password(self):
        process = Process.objects.create(
            user=self.user,
            visibility="private",
            type="liner",
        )

        raw_password = "secret123"

        process.set_password(raw_password)
        process.save()

        self.assertIsNotNone(process.password)
        self.assertNotEqual(process.password, raw_password)
        self.assertTrue(process.check_password(raw_password))

    def test_check_password_with_wrong_password(self):
        process = Process.objects.create(
            user=self.user,
            visibility="private",
            type="liner",
        )

        process.set_password("secret123")

        self.assertFalse(
            process.check_password("wrong-password")
        )

    def test_check_password_without_password(self):
        process = Process.objects.create(
            user=self.user,
            visibility="private",
            type="liner",
        )

        self.assertFalse(
            process.check_password("secret123")
        )

    def test_set_empty_password_removes_password(self):
        process = Process.objects.create(
            user=self.user,
            visibility="private",
            type="liner",
        )

        process.set_password("secret123")

        self.assertIsNotNone(process.password)

        process.set_password("")

        self.assertIsNone(process.password)


class FormModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

        self.category = Category.objects.create(
            name="Technology",
        )

        self.process = Process.objects.create(
            user=self.user,
            visibility="public",
            type="liner",
            category=self.category,
        )

    def test_create_form(self):
        form = Form.objects.create(
            visibility="public",
            process=self.process,
            category=self.category,
        )

        self.assertEqual(form.process, self.process)
        self.assertEqual(form.category, self.category)
        self.assertEqual(form.visibility, "public")

    def test_form_has_uuid_primary_key(self):
        form = Form.objects.create(
            visibility="public",
            process=self.process,
            category=self.category,
        )

        self.assertIsInstance(form.id, UUID)

    def test_default_views_is_zero(self):
        form = Form.objects.create(
            visibility="public",
            process=self.process,
            category=self.category,
        )

        self.assertEqual(form.views, 0)

    def test_default_order_is_one(self):
        form = Form.objects.create(
            visibility="public",
            process=self.process,
            category=self.category,
        )

        self.assertEqual(form.order, 1)

    def test_set_password_hashes_password(self):
        form = Form.objects.create(
            visibility="private",
            process=self.process,
            category=self.category,
        )

        raw_password = "secret123"

        form.set_password(raw_password)
        form.save()

        self.assertIsNotNone(form.password)
        self.assertNotEqual(form.password, raw_password)
        self.assertTrue(form.check_password(raw_password))

    def test_check_password_with_wrong_password(self):
        form = Form.objects.create(
            visibility="private",
            process=self.process,
            category=self.category,
        )

        form.set_password("secret123")

        self.assertFalse(
            form.check_password("wrong-password")
        )

    def test_check_password_without_password(self):
        form = Form.objects.create(
            visibility="public",
            process=self.process,
            category=self.category,
        )

        self.assertFalse(
            form.check_password("secret123")
        )

    def test_set_empty_password_removes_password(self):
        form = Form.objects.create(
            visibility="private",
            process=self.process,
            category=self.category,
        )

        form.set_password("secret123")

        self.assertIsNotNone(form.password)

        form.set_password("")

        self.assertIsNone(form.password)


class QuestionModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

        self.category = Category.objects.create(
            name="Technology",
        )

        self.process = Process.objects.create(
            user=self.user,
            visibility="public",
            type="liner",
            category=self.category,
        )

        self.form = Form.objects.create(
            visibility="public",
            process=self.process,
            category=self.category,
        )

    def test_create_question(self):
        question = Question.objects.create(
            text="What is your name?",
            form=self.form,
        )

        self.assertEqual(question.text, "What is your name?")
        self.assertEqual(question.form, self.form)

    def test_question_is_not_required_by_default(self):
        question = Question.objects.create(
            text="What is your name?",
            form=self.form,
        )

        self.assertFalse(question.is_required)

    def test_question_type_is_text_by_default(self):
        question = Question.objects.create(
            text="What is your name?",
            form=self.form,
        )

        self.assertEqual(question.type, "text")


class QuestionOptionModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

        self.category = Category.objects.create(
            name="Technology",
        )

        self.process = Process.objects.create(
            user=self.user,
            visibility="public",
            type="liner",
            category=self.category,
        )

        self.form = Form.objects.create(
            visibility="public",
            process=self.process,
            category=self.category,
        )

        self.question = Question.objects.create(
            text="Choose your favorite language",
            form=self.form,
            type="select",
        )

    def test_create_question_option(self):
        option = QuestionOption.objects.create(
            question=self.question,
            value="Python",
        )

        self.assertEqual(option.question, self.question)
        self.assertEqual(option.value, "Python")

    def test_deleting_question_deletes_options(self):
        option = QuestionOption.objects.create(
            question=self.question,
            value="Python",
        )

        self.question.delete()

        self.assertFalse(
            QuestionOption.objects.filter(
                id=option.id
            ).exists()
        )


class SubmissionModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

        self.category = Category.objects.create(
            name="Technology",
        )

        self.process = Process.objects.create(
            user=self.user,
            visibility="public",
            type="liner",
            category=self.category,
        )

        self.form = Form.objects.create(
            visibility="public",
            process=self.process,
            category=self.category,
        )

    def test_create_submission(self):
        submission = Submission.objects.create(
            form=self.form,
            user=self.user,
        )

        self.assertEqual(submission.form, self.form)
        self.assertEqual(submission.user, self.user)

    def test_submission_user_can_be_null(self):
        submission = Submission.objects.create(
            form=self.form,
            user=None,
        )

        self.assertIsNone(submission.user)

    def test_submission_can_be_created_without_session_id(self):
        submission = Submission.objects.create(
            form=self.form,
            user=self.user,
        )

        self.assertIsNone(submission.session_id)


class AnswerModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

        self.category = Category.objects.create(
            name="Technology",
        )

        self.process = Process.objects.create(
            user=self.user,
            visibility="public",
            type="liner",
            category=self.category,
        )

        self.form = Form.objects.create(
            visibility="public",
            process=self.process,
            category=self.category,
        )

        self.question = Question.objects.create(
            text="What is your name?",
            form=self.form,
        )

        self.submission = Submission.objects.create(
            form=self.form,
            user=self.user,
        )

    def test_create_answer(self):
        answer = Answer.objects.create(
            submission=self.submission,
            question=self.question,
            value="Ali",
        )

        self.assertEqual(answer.submission, self.submission)
        self.assertEqual(answer.question, self.question)
        self.assertEqual(answer.value, "Ali")

    def test_answer_value_can_be_null(self):
        answer = Answer.objects.create(
            submission=self.submission,
            question=self.question,
            value=None,
        )

        self.assertIsNone(answer.value)


class AnswerOptionModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

        self.category = Category.objects.create(
            name="Technology",
        )

        self.process = Process.objects.create(
            user=self.user,
            visibility="public",
            type="liner",
            category=self.category,
        )

        self.form = Form.objects.create(
            visibility="public",
            process=self.process,
            category=self.category,
        )

        self.question = Question.objects.create(
            text="Choose a language",
            form=self.form,
            type="select",
        )

        self.option = QuestionOption.objects.create(
            question=self.question,
            value="Python",
        )

        self.submission = Submission.objects.create(
            form=self.form,
            user=self.user,
        )

        self.answer = Answer.objects.create(
            submission=self.submission,
            question=self.question,
            value="Python",
        )

    def test_create_answer_option(self):
        answer_option = AnswerOption.objects.create(
            answer=self.answer,
            option=self.option,
        )

        self.assertEqual(answer_option.answer, self.answer)
        self.assertEqual(answer_option.option, self.option)