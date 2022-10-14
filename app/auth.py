from datetime import datetime
import pyotp
from bson.objectid import ObjectId
from pymongo.collection import ReturnDocument
from fastapi import APIRouter, status, HTTPException

from app.database import User
from . import schemas


def userEntity(user) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "otp_enabled": user["otp_enabled"],
        "otp_verified": user["otp_verified"],
        "otp_base32": user["otp_base32"],
        "otp_auth_url": user["otp_auth_url"],
        "created_at": user["created_at"],
        "updated_at": user["updated_at"]
    }


router = APIRouter()


@router.post('/register', status_code=status.HTTP_201_CREATED)
async def Create_User(payload: schemas.UserBaseSchema):
    user = User.find_one({'email': payload.email.lower()})
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail='Account already exist')

    payload.email = payload.email.lower()
    payload.created_at = datetime.utcnow()
    payload.updated_at = payload.created_at

    result = User.insert_one(payload.dict())

    return {'status': 'success', 'message': "Registered successfully, please login"}


@router.post('/login')
def Login(payload: schemas.LoginUserSchema):
    user = User.find_one({'email': payload.email.lower()})
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Incorrect Email or Password')

    return {'status': 'success', 'user': userEntity(user)}


@router.post('/otp/generate')
def Generate_OTP(payload: schemas.UserRequestSchema):
    otp_base32 = pyotp.random_base32()
    otp_auth_url = pyotp.totp.TOTP(otp_base32).provisioning_uri(
        name="admin@admin.com", issuer_name="codevoweb.com")

    if not ObjectId.is_valid(payload.user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Invalid id: {payload.user_id}")
    updated_user = User.find_one_and_update(
        {'_id': ObjectId(payload.user_id)}, {'$set': {"otp_auth_url": otp_auth_url, "otp_base32": otp_base32}}, return_document=ReturnDocument.AFTER)
    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No user with this id: {payload.user_id} found')

    return {'base32': otp_base32, "otpauth_url": otp_auth_url}


@router.post('/otp/verify')
def Verify_OTP(payload: schemas.UserRequestSchema):
    message = "Token is invalid or user doesn't exist"
    user = userEntity(User.find_one(
        {'_id': ObjectId(payload.user_id)}))
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=message)

    totp = pyotp.TOTP(user.get("otp_base32"))
    if not totp.verify(payload.token):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=message)
    updated_user = User.find_one_and_update(
        {'_id': ObjectId(payload.user_id)}, {'$set': {"otp_enabled": True, "otp_verified": True}}, return_document=ReturnDocument.AFTER)
    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No user with this id: {payload.user_id} found')

    return {'otp_verified': True, "user": userEntity(updated_user)}


@router.post('/otp/validate')
def Validate_OTP(payload: schemas.UserRequestSchema):
    message = "Token is invalid or user doesn't exist"
    user = userEntity(User.find_one(
        {'_id': ObjectId(payload.user_id)}))
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=message)

    if not user.get("otp_verified"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="OTP must be verified first")

    totp = pyotp.TOTP(user.get("otp_base32"))
    if not totp.verify(otp=payload.token, valid_window=1):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=message)

    return {'otp_valid': True}


@router.post('/otp/disable')
def Disable_OTP(payload: schemas.UserRequestSchema):
    if not ObjectId.is_valid(payload.user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Invalid id: {payload.user_id}")

    updated_user = User.find_one_and_update(
        {'_id': ObjectId(payload.user_id)}, {'$set': {"otp_enabled": False}}, return_document=ReturnDocument.AFTER)
    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No user with this id: {payload.user_id} found')

    return {'otp_disabled': True, 'user': userEntity(updated_user)}
