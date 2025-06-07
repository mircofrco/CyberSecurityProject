import os, asyncio
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

SENDGRID_KEY = os.getenv("SENDGRID_API_KEY")      # put in .env / secrets

async def send_verification_email(email: str, token: str):
    """Fire-and-forget e-mail; falls back to console print when no API key."""
    link = f"https://your-domain/verify?token={token}"

    if not SENDGRID_KEY:
        print(f"[DEV] Verify {email} via {link}")
        return

    sg = SendGridAPIClient(SENDGRID_KEY)
    message = Mail(
        from_email="no-reply@vote.local",
        to_emails=email,
        subject="Confirm your e-mail",
        html_content=f"Click <a href='{link}'>here</a> to verify your address.",
    )
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, sg.send, message)
