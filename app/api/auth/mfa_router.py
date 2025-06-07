from fastapi import APIRouter, Depends, HTTPException, status
import pyotp, qrcode, io, base64
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth.deps import current_active_user, get_async_session
from app.api.auth.models import User

router = APIRouter(prefix="/mfa", tags=["mfa"])


@router.post("/setup")
async def mfa_setup(
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Generate or return existing TOTP secret as a data-URI QR code."""
    if not user.mfa_secret:
        user.mfa_secret = pyotp.random_base32()
        session.add(user)
        await session.commit()
        await session.refresh(user)

    totp = pyotp.TOTP(user.mfa_secret)
    uri = totp.provisioning_uri(name=user.email, issuer_name="SecureVote")

    buf = io.BytesIO()
    qrcode.make(uri).save(buf, format="PNG")
    qr_b64 = base64.b64encode(buf.getvalue()).decode()

    return {"otpauth_url": uri, "qr": f"data:image/png;base64,{qr_b64}"}


@router.post("/verify")
async def mfa_verify(code: str, user: User = Depends(current_active_user)):
    if not user.mfa_secret:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "MFA not enabled")
    if not pyotp.TOTP(user.mfa_secret).verify(code):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid TOTP")
    return {"detail": "MFA verified"}
