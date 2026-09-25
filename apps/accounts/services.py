from common.utils.generate_otp import generate_otp
from common.utils.notification import send_email
from django_redis import get_redis_connection
from django.contrib.auth.hashers import make_password
import uuid


class AccountService:

    @staticmethod
    def generat_register_otp():
        registration_id = uuid.uuid4()
        code = generate_otp()

        if registration_id and code:
            return registration_id, code

        return None, None

    def send_email_registratoin(otp, email, subject):
        code = send_email(email, otp, subject)

        return code

    @staticmethod
    def set_data_registratoin_to_redis(data: dict, key, duratoin):
        try:
            if "password" in data:
                data["password"] = make_password(data["password"])
            redis = get_redis_connection("default")

            redis.hset(key, mapping=data)
            redis.expire(key, duratoin)
            return True
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def verify_otp(otp, key):
        redis = get_redis_connection("default")
        data = redis.hgetall(key)
        print(data)
        if not data:
            return False
        elif data[b"otp"].decode() == otp:
            redis.delete(key)
            return True
        else:
            return False

    @staticmethod
    def get_data_in_redis(key):
        redis = get_redis_connection("default")
        data = redis.hgetall(key)

        if not data:
            return None
        else:
            return data

    @staticmethod
    def regenerate_otp_registratoin(key, duration):
        code = generate_otp()
        redis = get_redis_connection("default")

        redis.hset(key, mapping={"otp": code})
        redis.expire(key, duration)

    @staticmethod
    def delete_registration_data(*args):
        redis = get_redis_connection("default")
        for i in args:
            redis.delete(i)
