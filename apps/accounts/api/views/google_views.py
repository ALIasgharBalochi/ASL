from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

# this view create refresh and access tokens after verifying/creating user in django
class GoogleJWTview(APIView):
    def get(self,request):
        user = request.user

        # creating tokens for our user
        refersh = RefreshToken.for_user(user=user)
        access = refersh.access_token

        return Response(
            {
                'refresh': str(refersh),
                'access' : str(access)
            }
        )