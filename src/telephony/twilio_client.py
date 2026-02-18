from twilio.rest import Client
from src.config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER, TARGET_NUMBER, PUBLIC_BASE_URL


def place_test_call() -> str:
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    call = client.calls.create(
        to=TARGET_NUMBER,
        from_=TWILIO_FROM_NUMBER,
        url=f"{PUBLIC_BASE_URL}/twiml/start",
        method="POST",
    )
    return call.sid


if __name__ == "__main__":
    sid = place_test_call()
    print("CALL_SID:", sid)