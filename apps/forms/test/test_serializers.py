from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.exceptions import ValidationError

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

from apps.forms.api.serializers.core_serializer import (
    CategorySerializer,
    ProcessSerializer,
    ProcessPasswordSerializer,
)

from apps.forms.api.serializers.form_serializer import (
    FormSerializer,
    FormPasswordSerializer,
    QuestionSerializer,
    QuestionOptionSerializer,
)

from apps.forms.api.serializers.submission_serializer import (
    SubmissionSerializer,
    AnswerSerializer,
    AnswerOptionSerializer,
    SubmitAnswerSerializer,
)

User = get_user_model()


class SerializerTestMixin:

    def create_user(self):
        return User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

    def create_category(self):
        return Category.objects.create(name="Technology")

    def create_process(self, user=None, category=None):
        user = user or self.user
        category = category or self.category

        return Process.objects.create(
            user=user,
            visibility="public",
            type="liner",
            category=category,
        )

    def create_form(self, process=None, category=None):
        process = process or self.process
        category = category or self.category

        return Form.objects.create(
            visibility="public",
            process=process,
            category=category,
        )

    def create_question(
        self,
        form=None,
        question_type="text",
        is_required=False,
    ):
        form = form or self.form

        return Question.objects.create(
            text="Test question",
            form=form,
            type=question_type,
            is_required=is_required,
        )


class CategorySerializerTest(SerializerTestMixin, TestCase):

    def setUp(self):
        self.category = self.create_category()

    def test_category_serializer_contains_expected_fields(self):
        serializer = CategorySerializer(instance=self.category)

        self.assertEqual(
            set(serializer.data.keys()),
            {
                "id",
                "name",
                "created_at",
                "forms",
                "process",
            },
        )

    def test_category_read_only_fields(self):
        serializer = CategorySerializer()

        self.assertIn("id", serializer.Meta.read_only_fields)
        self.assertIn("created_at", serializer.Meta.read_only_fields)
        self.assertIn("forms", serializer.Meta.read_only_fields)
        self.assertIn("process", serializer.Meta.read_only_fields)

    def test_category_serializer_creates_category(self):
        serializer = CategorySerializer(
            data={
                "name": "Programming",
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

        category = serializer.save()

        self.assertEqual(category.name, "Programming")

    def test_forms_are_read_only(self):
        serializer = CategorySerializer()

        self.assertTrue(serializer.fields["forms"].read_only)

    def test_process_is_read_only(self):
        serializer = CategorySerializer()

        self.assertTrue(serializer.fields["process"].read_only)


class ProcessSerializerTest(SerializerTestMixin, TestCase):

    def setUp(self):
        self.user = self.create_user()
        self.category = self.create_category()

        self.process = self.create_process()

    def test_user_is_read_only(self):
        serializer = ProcessSerializer()

        self.assertTrue(serializer.fields["user"].read_only)

    def test_password_is_write_only(self):
        serializer = ProcessSerializer()

        self.assertTrue(serializer.fields["password"].write_only)

    def test_password_is_not_returned_in_response(self):
        serializer = ProcessSerializer(instance=self.process)

        self.assertNotIn("password", serializer.data)

    def test_create_password_is_hashed(self):
        serializer = ProcessSerializer(
            instance=None,
            data={
                "visibility": "private",
                "type": "liner",
                "category": self.category.id,
                "password": "secret123",
            },
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        process = serializer.create(
            {
                "user": self.user,
                "visibility": "private",
                "type": "liner",
                "category": self.category,
                "password": "secret123",
            }
        )

        self.assertNotEqual(
            process.password,
            "secret123",
        )

        self.assertTrue(process.check_password("secret123"))

    def test_update_password(self):
        self.process.set_password("old-password")
        self.process.save()

        serializer = ProcessSerializer(
            instance=self.process,
            data={
                "password": "new-password",
            },
            partial=True,
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        updated_process = serializer.save()

        self.assertTrue(updated_process.check_password("new-password"))

        self.assertFalse(updated_process.check_password("old-password"))

    def test_update_without_password_keeps_old_password(self):
        self.process.set_password("old-password")
        self.process.save()

        old_hashed_password = self.process.password

        serializer = ProcessSerializer(
            instance=self.process,
            data={
                "visibility": "private",
            },
            partial=True,
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        updated_process = serializer.save()

        self.assertEqual(
            updated_process.password,
            old_hashed_password,
        )

        self.assertEqual(
            updated_process.visibility,
            "private",
        )


class ProcessPasswordSerializerTest(TestCase):

    def test_password_is_required(self):
        serializer = ProcessPasswordSerializer(data={})

        self.assertFalse(serializer.is_valid())

        self.assertIn(
            "password",
            serializer.errors,
        )

    def test_password_is_valid(self):
        serializer = ProcessPasswordSerializer(data={"password": "secret123"})

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

    def test_password_is_write_only(self):
        serializer = ProcessPasswordSerializer()

        self.assertTrue(serializer.fields["password"].write_only)


class FormSerializerTest(SerializerTestMixin, TestCase):

    def setUp(self):
        self.user = self.create_user()
        self.category = self.create_category()
        self.process = self.create_process()

        self.form = self.create_form()

    def test_password_is_write_only(self):
        serializer = FormSerializer()

        self.assertTrue(serializer.fields["password"].write_only)

    def test_password_is_not_returned(self):
        serializer = FormSerializer(instance=self.form)

        self.assertNotIn(
            "password",
            serializer.data,
        )

    def test_questions_are_read_only(self):
        serializer = FormSerializer()

        self.assertTrue(serializer.fields["questions"].read_only)

    def test_create_form_with_password(self):
        serializer = FormSerializer(
            data={
                "visibility": "private",
                "process": self.process.id,
                "category": self.category.id,
                "password": "secret123",
            }
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        form = serializer.save()

        self.assertTrue(form.check_password("secret123"))

        self.assertNotEqual(
            form.password,
            "secret123",
        )

    def test_update_form_password(self):
        self.form.set_password("old-password")
        self.form.save()

        serializer = FormSerializer(
            instance=self.form,
            data={
                "password": "new-password",
            },
            partial=True,
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        form = serializer.save()

        self.assertTrue(form.check_password("new-password"))

        self.assertFalse(form.check_password("old-password"))

    def test_update_without_password_keeps_old_password(self):
        self.form.set_password("old-password")
        self.form.save()

        old_password = self.form.password

        serializer = FormSerializer(
            instance=self.form,
            data={
                "visibility": "private",
            },
            partial=True,
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        form = serializer.save()

        self.assertEqual(
            form.password,
            old_password,
        )


class FormPasswordSerializerTest(TestCase):

    def test_password_is_required(self):
        serializer = FormPasswordSerializer(data={})

        self.assertFalse(serializer.is_valid())

        self.assertIn(
            "password",
            serializer.errors,
        )

    def test_password_is_valid(self):
        serializer = FormPasswordSerializer(data={"password": "secret123"})

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )


class QuestionSerializerTest(SerializerTestMixin, TestCase):

    def setUp(self):
        self.user = self.create_user()
        self.category = self.create_category()
        self.process = self.create_process()
        self.form = self.create_form()

    def test_text_question_without_options_is_valid(self):
        serializer = QuestionSerializer(
            data={
                "text": "What is your name?",
                "form": self.form.id,
                "type": "text",
                "is_required": True,
            }
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

    def test_number_question_without_options_is_valid(self):
        serializer = QuestionSerializer(
            data={
                "text": "How old are you?",
                "form": self.form.id,
                "type": "number",
                "is_required": True,
            }
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

    def test_text_question_with_options_is_invalid(self):
        serializer = QuestionSerializer(
            data={
                "text": "What is your name?",
                "form": self.form.id,
                "type": "text",
                "options": [
                    {"value": "Ali"},
                ],
            }
        )

        self.assertFalse(serializer.is_valid())

        self.assertIn(
            "options",
            serializer.errors,
        )

    def test_number_question_with_options_is_invalid(self):
        serializer = QuestionSerializer(
            data={
                "text": "How old are you?",
                "form": self.form.id,
                "type": "number",
                "options": [
                    {"value": "20"},
                ],
            }
        )

        self.assertFalse(serializer.is_valid())

        self.assertIn(
            "options",
            serializer.errors,
        )

    def test_select_question_requires_options(self):
        serializer = QuestionSerializer(
            data={
                "text": "Choose your language",
                "form": self.form.id,
                "type": "select",
            }
        )

        self.assertFalse(serializer.is_valid())

        self.assertIn(
            "options",
            serializer.errors,
        )

    def test_checkbox_question_requires_options(self):
        serializer = QuestionSerializer(
            data={
                "text": "Choose your skills",
                "form": self.form.id,
                "type": "checkbox",
            }
        )

        self.assertFalse(serializer.is_valid())

        self.assertIn(
            "options",
            serializer.errors,
        )

    def test_select_question_with_options_is_valid(self):
        serializer = QuestionSerializer(
            data={
                "text": "Choose your language",
                "form": self.form.id,
                "type": "select",
                "options": [
                    {"value": "Python"},
                    {"value": "JavaScript"},
                ],
            }
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

    def test_checkbox_question_with_options_is_valid(self):
        serializer = QuestionSerializer(
            data={
                "text": "Choose your skills",
                "form": self.form.id,
                "type": "checkbox",
                "options": [
                    {"value": "Python"},
                    {"value": "Django"},
                ],
            }
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

    def test_create_question_with_options(self):
        serializer = QuestionSerializer(
            data={
                "text": "Choose your language",
                "form": self.form.id,
                "type": "select",
                "options": [
                    {"value": "Python"},
                    {"value": "JavaScript"},
                ],
            }
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        question = serializer.save()

        self.assertEqual(
            question.options.count(),
            2,
        )

        self.assertEqual(
            set(
                question.options.values_list(
                    "value",
                    flat=True,
                )
            ),
            {"Python", "JavaScript"},
        )


class QuestionOptionSerializerTest(TestCase):

    def test_question_is_read_only(self):
        serializer = QuestionOptionSerializer()

        self.assertTrue(serializer.fields["question"].read_only)

    def test_id_is_read_only(self):
        serializer = QuestionOptionSerializer()

        self.assertTrue(serializer.fields["id"].read_only)


class SubmissionSerializerTest(TestCase):

    def test_user_is_read_only(self):
        serializer = SubmissionSerializer()

        self.assertTrue(serializer.fields["user"].read_only)

    def test_answers_are_read_only(self):
        serializer = SubmissionSerializer()

        self.assertTrue(serializer.fields["answers"].read_only)


class AnswerSerializerTest(TestCase):

    def test_selected_options_are_read_only(self):
        serializer = AnswerSerializer()

        self.assertTrue(serializer.fields["selected_options"].read_only)


class AnswerOptionSerializerTest(TestCase):

    def test_answer_option_fields(self):
        serializer = AnswerOptionSerializer()

        self.assertIn(
            "answer",
            serializer.fields,
        )

        self.assertIn(
            "option",
            serializer.fields,
        )

    def test_id_is_read_only(self):
        serializer = AnswerOptionSerializer()

        self.assertTrue(serializer.fields["id"].read_only)


class SubmitAnswerSerializerTest(
    SerializerTestMixin,
    TestCase,
):

    def setUp(self):
        self.user = self.create_user()
        self.category = self.create_category()
        self.process = self.create_process()
        self.form = self.create_form()

    def create_question_and_options(
        self,
        question_type,
        number_of_options=2,
    ):
        question = self.create_question(question_type=question_type)

        options = []

        for index in range(number_of_options):
            options.append(
                QuestionOption.objects.create(
                    question=question,
                    value=f"Option {index + 1}",
                )
            )

        return question, options

    def test_text_question_with_value_is_valid(self):
        question = self.create_question(question_type="text")

        serializer = SubmitAnswerSerializer(
            data={
                "question": question.id,
                "value": "Hello",
            }
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

    def test_text_question_without_value_is_invalid(self):
        question = self.create_question(question_type="text")

        serializer = SubmitAnswerSerializer(
            data={
                "question": question.id,
            }
        )

        self.assertFalse(serializer.is_valid())

        self.assertIn(
            "value",
            serializer.errors,
        )

    def test_text_question_cannot_have_options(self):
        question, options = self.create_question_and_options(
            question_type="text",
            number_of_options=1,
        )

        serializer = SubmitAnswerSerializer(
            data={
                "question": question.id,
                "value": "Hello",
                "options": [options[0].id],
            }
        )

        self.assertFalse(serializer.is_valid())

        self.assertIn(
            "options",
            serializer.errors,
        )

    def test_number_question_with_valid_number_is_valid(self):
        question = self.create_question(question_type="number")

        serializer = SubmitAnswerSerializer(
            data={
                "question": question.id,
                "value": "25",
            }
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

    def test_number_question_with_float_is_valid(self):
        question = self.create_question(question_type="number")

        serializer = SubmitAnswerSerializer(
            data={
                "question": question.id,
                "value": "25.5",
            }
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

    def test_number_question_with_invalid_number_is_invalid(self):
        question = self.create_question(question_type="number")

        serializer = SubmitAnswerSerializer(
            data={
                "question": question.id,
                "value": "abc",
            }
        )

        self.assertFalse(serializer.is_valid())

        self.assertIn(
            "value",
            serializer.errors,
        )

    def test_number_question_without_value_is_invalid(self):
        question = self.create_question(question_type="number")

        serializer = SubmitAnswerSerializer(
            data={
                "question": question.id,
            }
        )

        self.assertFalse(serializer.is_valid())

        self.assertIn(
            "value",
            serializer.errors,
        )

    def test_number_question_cannot_have_options(self):
        question, options = self.create_question_and_options(
            question_type="number",
            number_of_options=1,
        )

        serializer = SubmitAnswerSerializer(
            data={
                "question": question.id,
                "value": "25",
                "options": [options[0].id],
            }
        )

        self.assertFalse(serializer.is_valid())

        self.assertIn(
            "options",
            serializer.errors,
        )

    def test_select_question_with_one_option_is_valid(self):
        question, options = self.create_question_and_options(
            question_type="select",
            number_of_options=2,
        )

        serializer = SubmitAnswerSerializer(
            data={
                "question": question.id,
                "options": [options[0].id],
            }
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

    def test_select_question_requires_option(self):
        question = self.create_question(question_type="select")

        serializer = SubmitAnswerSerializer(
            data={
                "question": question.id,
            }
        )

        self.assertFalse(serializer.is_valid())

        self.assertIn(
            "options",
            serializer.errors,
        )

    def test_select_question_accepts_only_one_option(self):
        question, options = self.create_question_and_options(
            question_type="select",
            number_of_options=2,
        )

        serializer = SubmitAnswerSerializer(
            data={
                "question": question.id,
                "options": [
                    options[0].id,
                    options[1].id,
                ],
            }
        )

        self.assertFalse(serializer.is_valid())

        self.assertIn(
            "options",
            serializer.errors,
        )

    def test_select_question_cannot_have_value(self):
        question, options = self.create_question_and_options(
            question_type="select",
            number_of_options=1,
        )

        serializer = SubmitAnswerSerializer(
            data={
                "question": question.id,
                "options": [options[0].id],
                "value": "Python",
            }
        )

        self.assertFalse(serializer.is_valid())

        self.assertIn(
            "value",
            serializer.errors,
        )

    def test_checkbox_question_with_options_is_valid(self):
        question, options = self.create_question_and_options(
            question_type="checkbox",
            number_of_options=2,
        )

        serializer = SubmitAnswerSerializer(
            data={
                "question": question.id,
                "options": [
                    options[0].id,
                    options[1].id,
                ],
            }
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

    def test_checkbox_question_requires_options(self):
        question = self.create_question(question_type="checkbox")

        serializer = SubmitAnswerSerializer(
            data={
                "question": question.id,
            }
        )

        self.assertFalse(serializer.is_valid())

        self.assertIn(
            "options",
            serializer.errors,
        )

    def test_checkbox_question_cannot_have_value(self):
        question, options = self.create_question_and_options(
            question_type="checkbox",
            number_of_options=1,
        )

        serializer = SubmitAnswerSerializer(
            data={
                "question": question.id,
                "options": [options[0].id],
                "value": "Python",
            }
        )

        self.assertFalse(serializer.is_valid())

        self.assertIn(
            "value",
            serializer.errors,
        )

    def test_option_must_belong_to_same_question(self):
        question1, options1 = self.create_question_and_options(
            question_type="select",
            number_of_options=1,
        )

        question2, options2 = self.create_question_and_options(
            question_type="select",
            number_of_options=1,
        )

        serializer = SubmitAnswerSerializer(
            data={
                "question": question1.id,
                "options": [options2[0].id],
            }
        )

        self.assertFalse(serializer.is_valid())

        self.assertIn(
            "options",
            serializer.errors,
        )
