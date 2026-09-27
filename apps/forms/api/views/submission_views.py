from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from ..serializers.submission_serializer import SubmitAnswerSerializer
from ...models import Submission, Answer, AnswerOption
from django.db import transaction


class SubmitAnswerView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serialiser = SubmitAnswerSerializer(many=True, data=request.data)

        serialiser.is_valid(raise_exception=True)
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
            return Response({"message": "answer created successfuly"}, status=200)
        except Exception as e:
            print(e)
            return Response({"message": "answer created failed"}, status=400)
