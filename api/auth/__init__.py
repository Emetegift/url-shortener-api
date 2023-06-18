# from flask import jsonify, request
# from ..models import User, RevokedToken
# from flask_smorest import Blueprint, abort
# from flask.views import MethodView
# from ..schemas import UserSchema, LoginSchema
# from flask_jwt_extended import create_access_token,create_refresh_token,get_jwt_identity,jwt_required,get_jwt
# from ..utils import check_if_email_is_unique, check_if_username_is_unique
# from passlib.hash import pbkdf2_sha256 as sha256
# from datetime import timedelta
# from ..extensions import cache
# from werkzeug.security import generate_password_hash, check_password_hash

# blp = Blueprint("auth", __name__, description="Operations on Authentication")

    
    
# @blp.route('/register', methods=['POST'])
# def register():
#     data = request.get_json()
#     username = data.get('username')
#     first_name = data.get('first_name')
#     last_name = data.get('last_name')
#     email = data.get('email')
#     password = data.get('password')
#     confirm_password = data.get('confirm_password')

#     if not all([first_name, last_name, email, password, confirm_password, username]):
#         return jsonify({'error': 'Missing required fields.'}), 400

#     if password != confirm_password:
#         return jsonify({'error': 'Passwords do not match.'}), 400
    
#     password = sha256.hash(data["password"])
#     user = User(
#             username=data["username"].lower(),
#             email=data["email"].lower(),
#             first_name=data["first_name"].lower(),
#             last_name=data["last_name"].lower(),
#             password=password,
#         )
#     user.save()

#     return jsonify({'message': 'Registration successful.'}), 200
    


# @blp.route("/refresh")
# class TokenRefresh(MethodView):
#     # jwt_required simply means a token will be required to access this route
#     # for you to generate a token, you need too login first
#     @blp.doc(
#         description="Refresh an access token",
#         summary="Refresh an access token using a refresh token",
#     )
#     @jwt_required(refresh=True)
#     def post(self):
#         # get the current user's id, use it as an identity to create a new access token using the refresh token
#         current_user = get_jwt_identity()
#         new_token = create_access_token(
#             identity=current_user, expires_delta=timedelta(hours=2)
#         )

#         # return the new generated token
#         return {"access_token": new_token}
    
# @blp.route("/login")
# class LoginUserResource(MethodView):
#     @blp.arguments(LoginSchema)
#     # @blp.response(200)  # Specify the response schema
#     def post(self, user):
#         """Login a user"""
                
#         current_user = User.query.filter_by(email=user["email"].lower()).first()
#         if not current_user:
#             abort(404, message="User not found")
#         if not sha256.verify(user["password"], current_user.password):
#             abort(401, message="Invalid password")
#         access_token = cache.get(current_user.id)
#         if not access_token:
#             access_token = create_access_token(identity=current_user.id)
#             cache.set(current_user.id, access_token, timeout=None)
#         refresh_token = create_refresh_token(identity=current_user.id)
#         return {"access_token": access_token, "refresh_token": refresh_token}, 200

# @blp.route("/logout", methods=["DELETE"])
# @blp.doc(
#     description="Logout a user", summary="Logout a user by revoking their access token"
# )
# @jwt_required()
# def revoke_auth():
#     jti = get_jwt()["jti"]
#     current_user = get_jwt_identity()
#     cached_data = cache.get(current_user)
#     if cached_data:
#         cache.delete(current_user)
#     token = RevokedToken(jti=jti)
#     token.save()
#     return jsonify(msg="Successfully logged out")















from flask import jsonify, request
from ..models import User, RevokedToken
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from ..schemas import UserSchema, LoginSchema
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required, get_jwt
from ..utils import check_if_email_is_unique, check_if_username_is_unique
from passlib.hash import pbkdf2_sha256 as sha256
from datetime import timedelta
from ..extensions import cache
from werkzeug.security import generate_password_hash, check_password_hash

blp = Blueprint("auth", __name__, description="Operations on Authentication")

@blp.route('/register', methods=['POST'])
def register():
    data = request.get_json()  # Get JSON data from the request
    username = data.get('username')  # Get the 'username' field from the data
    first_name = data.get('first_name')  # Get the 'first_name' field from the data
    last_name = data.get('last_name')  # Get the 'last_name' field from the data
    email = data.get('email')  # Get the 'email' field from the data
    password = data.get('password')  # Get the 'password' field from the data
    confirm_password = data.get('confirm_password')  # Get the 'confirm_password' field from the data

    if not all([first_name, last_name, email, password, confirm_password, username]):
        # Check if any required field is missing
        return jsonify({'error': 'Missing required fields.'}), 400

    if password != confirm_password:
        # Check if the password and confirm_password fields match
        return jsonify({'error': 'Passwords do not match.'}), 400

    password = sha256.hash(data["password"])  # Hash the password using pbkdf2_sha256
    user = User(
        username=data["username"].lower(),
        email=data["email"].lower(),
        first_name=data["first_name"].lower(),
        last_name=data["last_name"].lower(),
        password=password,
    )
    user.save()  # Save the user object to the database

    return jsonify({'message': 'Registration successful.'}), 200


@blp.route("/refresh")
class TokenRefresh(MethodView):
    @blp.doc(
        description="Refresh an access token",
        summary="Refresh an access token using a refresh token",
    )
    @jwt_required(refresh=True)  # Requires a refresh token for access
    def post(self):
        current_user = get_jwt_identity()  # Get the current user's id from the JWT
        new_token = create_access_token(
            identity=current_user, expires_delta=timedelta(hours=2)
        )  # Generate a new access token using the current user's id

        return {"access_token": new_token}  # Return the new generated token


@blp.route("/login")
class LoginUserResource(MethodView):
    @blp.arguments(LoginSchema)
    def post(self, user):
        """Login a user"""
        current_user = User.query.filter_by(email=user["email"].lower()).first()
        # Find the user with the provided email in the database

        if not current_user:
            # If user not found, return an error response
            abort(404, message="User not found")

        if not sha256.verify(user["password"], current_user.password):
            # Verify the provided password with the stored hashed password
            abort(401, message="Invalid password")

        access_token = cache.get(current_user.id)
        if not access_token:
            # If no access token found in cache, create a new one and store it in cache
            access_token = create_access_token(identity=current_user.id)
            cache.set(current_user.id, access_token, timeout=None)

        refresh_token = create_refresh_token(identity=current_user.id)  # Generate a refresh token

        return {"access_token": access_token, "refresh_token": refresh_token}, 200


@blp.route("/logout", methods=["DELETE"])
@blp.doc(
    description="Logout a user", summary="Logout a user by revoking their access token"
)
@jwt_required()  # Requires a valid access token for access
def revoke_auth():
    jti = get_jwt()["jti"]  # Get the JWT ID from the current JWT
    current_user = get_jwt_identity()  # Get the current user's id from the JWT
    cached_data = cache.get(current_user)
    if cached_data:
        cache.delete(current_user)  # Delete the access token from the cache
    token = RevokedToken(jti=jti)
    token.save()  # Save the revoked token to the database

    return jsonify(msg="Successfully logged out")
