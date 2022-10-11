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
