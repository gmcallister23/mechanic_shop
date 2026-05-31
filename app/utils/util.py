import jwt
from datetime import datetime, timezone, timedelta

SECRET_KEY = 'super secret secrets'

def encode_token(customer_id):
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(day=0, hours=1),
        'iat': datetime.now(timezone.utc),
        'sub': customer_id,
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token