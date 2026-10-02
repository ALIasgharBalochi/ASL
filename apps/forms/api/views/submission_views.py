from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from ..serializers.submission_serializer import SubmitAnswerSerializer
from ...models import Submission, Answer, AnswerOption
from django.db import transaction
from drf_spectacular.utils import extend_schema
from ....reports.services import send_report_update
from uuid import uuid4
from rest_framework.exceptions import PermissionDenied
from ...services import can_access_form


class SubmitAnswerView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=SubmitAnswerSerializer,
    )
    def post(self, request):

        serialiser = SubmitAnswerSerializer(many=True, data=request.data)
        serialiser.is_valid(raise_exception=True)
        
        if not serialiser.validated_data:
            return Response({"message": "At least one answer is required"}, status=400)

        form = serialiser.validated_data[0]["question"].form

        if any(
            item["question"].form_id != form.id for item in serialiser.validated_data
        ):

            return Response(
                {"message": "All questions must belong to the same form."},
                status=400,
            )

        session_id = None

        if not request.user.is_authenticated:
            session_id = request.session.get("linear_session_id")

        if not session_id:
            session_id = str(uuid4())
            request.session["linear_session_id"] = session_id


        if not can_access_form(
            form,
            user=request.user,
            session_id=session_id,
        ):
            raise PermissionDenied("You must submit the previous form first.")

        try:
            with transaction.atomic():
                submission = Submission.objects.create(
                    form=serialiser.validated_data[0]["question"].form,
                    user=request.user if request.user.is_authenticated else None,
                )
                answere_create = []
                answere_option_create = []
                for answer_item in serialiser.validated_data:
                    answer = Answer(
                        submission=submission,
                        question=answer_item["question"],
                        value=answer_item.get("value"),
                    )
                    answere_create.append(answer)

                Answer.objects.bulk_create(answere_create)

                for answer, a_optoins_item in zip(
                    answere_create, serialiser.validated_data
                ):
                    for option in a_optoins_item.get("options", []):
                        answere_option_create.append(
                            AnswerOption(answer=answer, option=option)
                        )

                AnswerOption.objects.bulk_create(answere_option_create)

                transaction.on_commit(lambda: send_report_update(submission.form.id))
            return Response({"message": "answer created successfuly"}, status=200)
        except Exception as e:
            print(e)
            return Response({"message": "answer created failed"}, status=400)
