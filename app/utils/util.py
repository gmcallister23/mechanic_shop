import jwt
from datetime import datetime, timezone, timedelta
from functools import wraps
from flask import request, jsonify, g
import os



SECRET_KEY = os.environ.get('SECRET_KEY') or 'super_secret_secrets_super_secret_secrets'

def encode_token(customer_id):
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(hours=1),
        'iat': datetime.now(timezone.utc),
        'sub': str(customer_id)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        auth_header = request.headers.get('Authorization')

        print("headers:", dict(request.headers))

        if not auth_header:
            return jsonify({'message': 'Missing token'}), 401
        
            
        try:
            token = auth_header.strip().split()[1] 
            
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'], options={"verify_signature": True})
            print(data)
            customer_id = data['sub']
            
        except jwt.ExpiredSignatureError as e: 
                return jsonify({'message': 'token expired'}), 400
            
        except jwt.InvalidTokenError as e:
                return jsonify({'message': 'Invalid token'}), 400
        
        except Exception as e: 
             print("JWT FULL ERROR:", repr(e))
             return jsonify({"message": "Invalid token"}), 400
            
        g.customer_id = customer_id    
        return f(*args, **kwargs)
            
        
        
    return decorated

            