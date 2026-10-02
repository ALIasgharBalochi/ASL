from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

from rest_framework.test import APIClient

from apps.forms.models import (
    Category,
    Process,
    Form,
    Question,
    QuestionOption,
    Submission,
    Answer,
    AnswerOption,
)


User = get_user_model()


@override_settings(
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "test-cache",
        }
    }
)
class FormsViewsTestCase(TestCase):

    def setUp(self):
        cache.clear()

        self.client = APIClient()

        # --------------------------------------------------
        # USERS
        # --------------------------------------------------

        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

        self.other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="testpass123",
        )

        self.client.force_authenticate(user=self.user)

        # --------------------------------------------------
        # CATEGORY
        # --------------------------------------------------

        self.category = Category.objects.create(
            name="Test Category",
            user=self.user,
        )

        self.other_category = Category.objects.create(
            name="Other Category",
            user=self.other_user,
        )

        # --------------------------------------------------
        # PROCESS
        # --------------------------------------------------

        self.process = Process.objects.create(
            user=self.user,
            visibility="public",
            type="liner",
            category=self.category,
        )

        self.password_process = Process.objects.create(
            user=self.user,
            visibility="private",
            type="liner",
            category=self.category,
        )
        self.password_process.set_password("process123")
        self.password_process.save()

        # --------------------------------------------------
        # FORM
        # --------------------------------------------------

        self.form = Form.objects.create(
            visibility="public",
            process=self.process,
            category=self.category,
        )

        self.password_form = Form.objects.create(
            visibility="private",
            process=self.process,
            category=self.category,
        )
        self.password_form.set_password("form123")
        self.password_form.save()

        # --------------------------------------------------
        # QUESTIONS
        # --------------------------------------------------

        self.text_question = Question.objects.create(
            text="What is your name?",
            form=self.form,
            is_required=True,
            type="text",
        )

        self.number_question = Question.objects.create(
            text="How old are you?",
            form=self.form,
            is_required=True,
            type="number",
        )

        self.select_question = Question.objects.create(
            text="Choose your country",
            form=self.form,
            is_required=True,
            type="select",
        )

        self.checkbox_question = Question.objects.create(
            text="Choose your hobbies",
            form=self.form,
            is_required=False,
            type="checkbox",
        )

        # --------------------------------------------------
        # OPTIONS
        # --------------------------------------------------

        self.option_iran = QuestionOption.objects.create(
            question=self.select_question,
            value="Iran",
        )

        self.option_germany = QuestionOption.objects.create(
            question=self.select_question,
            value="Germany",
        )

        self.hobby_programming = QuestionOption.objects.create(
            question=self.checkbox_question,
            value="Programming",
        )

        self.hobby_sport = QuestionOption.objects.create(
            question=self.checkbox_question,
            value="Sport",
        )

    # ======================================================
    # CATEGORY
    # ======================================================

    def test_category_list_returns_only_current_user_categories(self):
        response = self.client.get(
            reverse("category-list")
        )

        self.assertEqual(response.status_code, 200)

        returned_ids = [
            item["id"]
            for item in response.data
        ]

        self.assertIn(
            self.category.id,
            returned_ids,
        )

        self.assertNotIn(
            self.other_category.id,
            returned_ids,
        )

    def test_user_can_retrieve_own_category(self):
        response = self.client.get(
            reverse(
                "category-detail",
                kwargs={"pk": self.category.id},
            )
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.data["id"],
            self.category.id,
        )

    def test_user_cannot_retrieve_other_users_category(self):
        response = self.client.get(
            reverse(
                "category-detail",
                kwargs={"pk": self.other_category.id},
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_create_category(self):
        response = self.client.post(
            reverse("category-list"),
            {
                "name": "New Category",
            },
        )

        self.assertEqual(response.status_code, 201)

        category = Category.objects.get(
            name="New Category"
        )

        self.assertEqual(
            category.user,
            self.user,
        )

    def test_update_own_category(self):
        response = self.client.patch(
            reverse(
                "category-detail",
                kwargs={"pk": self.category.id},
            ),
            {
                "name": "Updated Category",
            },
        )

        self.assertEqual(response.status_code, 200)

        self.category.refresh_from_db()

        self.assertEqual(
            self.category.name,
            "Updated Category",
        )

    def test_cannot_update_other_users_category(self):
        response = self.client.patch(
            reverse(
                "category-detail",
                kwargs={"pk": self.other_category.id},
            ),
            {
                "name": "Hacked Category",
            },
        )

        self.assertEqual(response.status_code, 404)

    def test_delete_own_category(self):
        response = self.client.delete(
            reverse(
                "category-detail",
                kwargs={"pk": self.category.id},
            )
        )

        self.assertEqual(response.status_code, 204)

        self.assertFalse(
            Category.objects.filter(
                id=self.category.id
            ).exists()
        )

    def test_cannot_delete_other_users_category(self):
        response = self.client.delete(
            reverse(
                "category-detail",
                kwargs={"pk": self.other_category.id},
            )
        )

        self.assertEqual(response.status_code, 404)

        self.assertTrue(
            Category.objects.filter(
                id=self.other_category.id
            ).exists()
        )

    # ======================================================
    # PROCESS
    # ======================================================

    def test_process_list(self):
        response = self.client.get(
            reverse("process-list")
        )

        self.assertEqual(response.status_code, 200)

        returned_ids = [
            item["id"]
            for item in response.data
        ]

        self.assertIn(
            self.process.id,
            returned_ids,
        )

    def test_create_process(self):
        response = self.client.post(
            reverse("process-list"),
            {
                "visibility": "public",
                "type": "liner",
                "category": self.category.id,
            },
        )

        self.assertEqual(response.status_code, 201)

        process_id = response.data["id"]

        process = Process.objects.get(
            id=process_id
        )

        self.assertEqual(
            process.user,
            self.user,
        )

        self.assertEqual(
            process.category,
            self.category,
        )

    def test_process_retrieve_without_password(self):
        response = self.client.get(
            reverse(
                "process-detail",
                kwargs={"pk": self.process.id},
            )
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.data["id"],
            self.process.id,
        )

    def test_process_retrieve_password_protected(self):
        response = self.client.get(
            reverse(
                "process-detail",
                kwargs={"pk": self.password_process.id},
            )
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.data["detail"],
            "this process is password protected",
        )

    def test_process_password_is_hashed(self):
        self.assertNotEqual(
            self.password_process.password,
            "process123",
        )

        self.assertTrue(
            self.password_process.check_password(
                "process123"
            )
        )

    def test_process_unlock_with_correct_password(self):
        response = self.client.post(
            reverse(
                "process-unlock",
                kwargs={"pk": self.password_process.id},
            ),
            {
                "password": "process123",
            },
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.data["id"],
            self.password_process.id,
        )

    def test_process_unlock_with_wrong_password(self):
        response = self.client.post(
            reverse(
                "process-unlock",
                kwargs={"pk": self.password_process.id},
            ),
            {
                "password": "wrong-password",
            },
        )

        self.assertEqual(response.status_code, 403)

    # ======================================================
    # FORM
    # ======================================================

    def test_form_list(self):
        response = self.client.get(
            reverse("form-list")
        )

        self.assertEqual(response.status_code, 200)

        returned_ids = [
            str(item["id"])
            for item in response.data
        ]

        self.assertIn(
            str(self.form.id),
            returned_ids,
        )

    def test_create_form(self):
        response = self.client.post(
            reverse("form-list"),
            {
                "visibility": "public",
                "process": self.process.id,
                "category": self.category.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)

        self.assertIn(
            "form",
            response.data,
        )

        self.assertIn(
            "public_link",
            response.data,
        )

    def test_retrieve_form_without_password(self):
        response = self.client.get(
            reverse(
                "form-detail",
                kwargs={"id": self.form.id},
            )
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            str(response.data["id"]),
            str(self.form.id),
        )

    def test_retrieve_password_protected_form(self):
        response = self.client.get(
            reverse(
                "form-detail",
                kwargs={"id": self.password_form.id},
            )
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.data["detail"],
            "this form is password protected",
        )

    def test_form_unlock_with_correct_password(self):
        response = self.client.post(
            reverse(
                "form-unlock",
                kwargs={"id": self.password_form.id},
            ),
            {
                "password": "form123",
            },
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            str(response.data["id"]),
            str(self.password_form.id),
        )

    def test_form_unlock_with_wrong_password(self):
        response = self.client.post(
            reverse(
                "form-unlock",
                kwargs={"id": self.password_form.id},
            ),
            {
                "password": "wrong-password",
            },
        )

        self.assertEqual(response.status_code, 403)

    # ======================================================
    # QUESTION
    # ======================================================

    def test_question_list(self):
        response = self.client.get(
            reverse("question-list")
        )

        self.assertEqual(response.status_code, 200)

        returned_ids = [
            item["id"]
            for item in response.data
        ]

        self.assertIn(
            self.text_question.id,
            returned_ids,
        )

    def test_create_question(self):
        response = self.client.post(
            reverse("question-list"),
            {
                "text": "What is your job?",
                "form": self.form.id,
                "is_required": True,
                "type": "text",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)

        question = Question.objects.get(
            text="What is your job?"
        )

        self.assertEqual(
            question.form,
            self.form,
        )

    def test_retrieve_question(self):
        response = self.client.get(
            reverse(
                "question-detail",
                kwargs={"id": self.text_question.id},
            )
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.data["id"],
            self.text_question.id,
        )

    def test_update_question(self):
        response = self.client.patch(
            reverse(
                "question-detail",
                kwargs={"id": self.text_question.id},
            ),
            {
                "text": "Updated question",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        self.text_question.refresh_from_db()

        self.assertEqual(
            self.text_question.text,
            "Updated question",
        )

    def test_delete_question(self):
        question_id = self.text_question.id

        response = self.client.delete(
            reverse(
                "question-detail",
                kwargs={"id": question_id},
            )
        )

        self.assertEqual(response.status_code, 204)

        self.assertFalse(
            Question.objects.filter(
                id=question_id
            ).exists()
        )

    # ======================================================
    # QUESTION OPTION
    # ======================================================

    def test_question_option_list(self):
        response = self.client.get(
            reverse("question-option-list")
        )

        self.assertEqual(response.status_code, 200)

        returned_ids = [
            item["id"]
            for item in response.data
        ]

        self.assertIn(
            self.option_iran.id,
            returned_ids,
        )

    def test_retrieve_question_option(self):
        response = self.client.get(
            reverse(
                "question-option-detail",
                kwargs={"id": self.option_iran.id},
            )
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.data["id"],
            self.option_iran.id,
        )

    def test_update_question_option(self):
        response = self.client.patch(
            reverse(
                "question-option-detail",
                kwargs={"id": self.option_iran.id},
            ),
            {
                "value": "Updated Iran",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        self.option_iran.refresh_from_db()

        self.assertEqual(
            self.option_iran.value,
            "Updated Iran",
        )

    def test_delete_question_option(self):
        option_id = self.option_iran.id

        response = self.client.delete(
            reverse(
                "question-option-detail",
                kwargs={"id": option_id},
            )
        )

        self.assertEqual(response.status_code, 204)

        self.assertFalse(
            QuestionOption.objects.filter(
                id=option_id
            ).exists()
        )

    # ======================================================
    # SUBMIT ANSWER
    # ======================================================

    def test_submit_text_answer(self):
        response = self.client.post(
            reverse("submit_answer"),
            [
                {
                    "question": self.text_question.id,
                    "value": "Ali",
                }
            ],
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            Submission.objects.count(),
            1,
        )

        submission = Submission.objects.first()

        self.assertEqual(
            submission.form,
            self.form,
        )

        self.assertEqual(
            submission.user,
            self.user,
        )

        answer = Answer.objects.get(
            submission=submission
        )

        self.assertEqual(
            answer.question,
            self.text_question,
        )

        self.assertEqual(
            answer.value,
            "Ali",
        )

    def test_submit_number_answer(self):
        response = self.client.post(
            reverse("submit_answer"),
            [
                {
                    "question": self.number_question.id,
                    "value": "25",
                }
            ],
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        answer = Answer.objects.latest("id")

        self.assertEqual(
            answer.question,
            self.number_question,
        )

        self.assertEqual(
            answer.value,
            "25",
        )

    def test_submit_select_answer(self):
        response = self.client.post(
            reverse("submit_answer"),
            [
                {
                    "question": self.select_question.id,
                    "options": [
                        self.option_iran.id,
                    ],
                }
            ],
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        submission = Submission.objects.latest("id")

        answer = Answer.objects.get(
            submission=submission
        )

        self.assertEqual(
            answer.question,
            self.select_question,
        )

        selected_option = AnswerOption.objects.get(
            answer=answer
        )

        self.assertEqual(
            selected_option.option,
            self.option_iran,
        )

    def test_submit_checkbox_answer(self):
        response = self.client.post(
            reverse("submit_answer"),
            [
                {
                    "question": self.checkbox_question.id,
                    "options": [
                        self.hobby_programming.id,
                        self.hobby_sport.id,
                    ],
                }
            ],
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        submission = Submission.objects.latest("id")

        answer = Answer.objects.get(
            submission=submission
        )

        selected_options = AnswerOption.objects.filter(
            answer=answer
        )

        self.assertEqual(
            selected_options.count(),
            2,
        )

    def test_submit_answer_requires_at_least_one_answer(self):
        response = self.client.post(
            reverse("submit_answer"),
            [],
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_submit_text_answer_without_value_fails(self):
        response = self.client.post(
            reverse("submit_answer"),
            [
                {
                    "question": self.text_question.id,
                }
            ],
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_submit_number_answer_with_invalid_value_fails(self):
        response = self.client.post(
            reverse("submit_answer"),
            [
                {
                    "question": self.number_question.id,
                    "value": "not-a-number",
                }
            ],
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_submit_select_without_option_fails(self):
        response = self.client.post(
            reverse("submit_answer"),
            [
                {
                    "question": self.select_question.id,
                }
            ],
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_submit_select_with_multiple_options_fails(self):
        response = self.client.post(
            reverse("submit_answer"),
            [
                {
                    "question": self.select_question.id,
                    "options": [
                        self.option_iran.id,
                        self.option_germany.id,
                    ],
                }
            ],
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_submit_select_with_value_fails(self):
        response = self.client.post(
            reverse("submit_answer"),
            [
                {
                    "question": self.select_question.id,
                    "value": "Iran",
                    "options": [
                        self.option_iran.id,
                    ],
                }
            ],
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_submit_checkbox_without_options_fails(self):
        response = self.client.post(
            reverse("submit_answer"),
            [
                {
                    "question": self.checkbox_question.id,
                }
            ],
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_submit_answers_from_different_forms_fails(self):
        other_form = Form.objects.create(
            visibility="public",
            process=self.process,
            category=self.category,
        )

        other_question = Question.objects.create(
            text="Other question",
            form=other_form,
            type="text",
        )

        response = self.client.post(
            reverse("submit_answer"),
            [
                {
                    "question": self.text_question.id,
                    "value": "Ali",
                },
                {
                    "question": other_question.id,
                    "value": "Test",
                },
            ],
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    # ======================================================
    # AUTHENTICATION
    # ======================================================

    def test_category_requires_authentication(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(
            reverse("category-list")
        )

        self.assertEqual(response.status_code, 401)

    def test_process_requires_authentication(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(
            reverse("process-list")
        )

        self.assertEqual(response.status_code, 401)

    def test_question_requires_authentication(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(
            reverse("question-list")
        )

        self.assertEqual(response.status_code, 401)

    def test_question_option_requires_authentication(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(
            reverse("question-option-list")
        )

        self.assertEqual(response.status_code, 401)