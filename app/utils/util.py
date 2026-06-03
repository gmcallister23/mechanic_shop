import jwt
from datetime import datetime, timezone, timedelta
from functools import wraps
from flask import request, jsonify



SECRET_KEY = 'super secret secrets'

def encode_token(customer_id):
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(hours=1),
        'iat': datetime.now(timezone.utc),
        'sub': customer_id,
    }

    token = jwt.encode(payload, SECRET_KEY, algorithms=['HS256'])
    return token

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        

        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return jsonify({'message': 'Missing token'}), 401
        
            
        try:
            token = auth_header.split('')[1] 
            
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            print(data)
            customer_id = data['sub']
            
        except jwt.ExpiredSignatureError as e: 
                return jsonify({'message': 'token expired'}), 400
            
        except jwt.InvalidTokenError as e:
                return jsonify({'message': 'Invalid token'}), 400
            
        return f(customer_id, *args, **kwargs)
            
        
        
    return decorated

            