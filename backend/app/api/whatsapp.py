import os

import httpx
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

load_dotenv()

router = APIRouter(
    prefix="/api/whatsapp",
    tags=["WhatsApp"],
)


# ============================================================
# CONFIGURATION
# ============================================================

WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

WHATSAPP_API_VERSION = "v25.0"


# ============================================================
# REQUEST SCHEMA
# ============================================================

class WhatsAppMessageRequest(BaseModel):
    to: str = Field(
        ...,
        description="Recipient WhatsApp number with country code, e.g. 919876543210",
    )

    message: str = Field(
        ...,
        min_length=1,
        description="Message to send",
    )


# ============================================================
# SEND TEXT MESSAGE
# ============================================================

@router.post("/send")
async def send_whatsapp_message(
    request: WhatsAppMessageRequest,
):

    # --------------------------------------------------------
    # Check configuration
    # --------------------------------------------------------

    if not WHATSAPP_ACCESS_TOKEN:
        raise HTTPException(
            status_code=500,
            detail="WHATSAPP_ACCESS_TOKEN is not configured in .env",
        )

    if not WHATSAPP_PHONE_NUMBER_ID:
        raise HTTPException(
            status_code=500,
            detail="WHATSAPP_PHONE_NUMBER_ID is not configured in .env",
        )

    # --------------------------------------------------------
    # Clean recipient number
    # --------------------------------------------------------

    recipient = request.to.strip()

    # Remove +, spaces, hyphens and brackets
    recipient = (
        recipient
        .replace("+", "")
        .replace(" ", "")
        .replace("-", "")
        .replace("(", "")
        .replace(")", "")
    )

    if not recipient.isdigit():
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid WhatsApp number. "
                "Use country code + number, e.g. 919876543210"
            ),
        )

    # --------------------------------------------------------
    # Meta WhatsApp Cloud API URL
    # --------------------------------------------------------

    url = (
        f"https://graph.facebook.com/"
        f"{WHATSAPP_API_VERSION}/"
        f"{WHATSAPP_PHONE_NUMBER_ID}/messages"
    )

    # --------------------------------------------------------
    # Headers
    # --------------------------------------------------------

    headers = {
        "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    # --------------------------------------------------------
    # WhatsApp message payload
    # --------------------------------------------------------

    payload = {
        "messaging_product": "whatsapp",
        "to": recipient,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": request.message,
        },
    }

    # --------------------------------------------------------
    # Send request to Meta
    # --------------------------------------------------------

    try:

        async with httpx.AsyncClient(timeout=30.0) as client:

            response = await client.post(
                url,
                headers=headers,
                json=payload,
            )

    except httpx.RequestError as e:

        raise HTTPException(
            status_code=502,
            detail=f"Unable to connect to Meta WhatsApp API: {str(e)}",
        )

    # --------------------------------------------------------
    # Handle Meta error
    # --------------------------------------------------------

    if response.status_code >= 400:

        try:
            error_data = response.json()
        except Exception:
            error_data = response.text

        raise HTTPException(
            status_code=response.status_code,
            detail={
                "message": "WhatsApp API request failed",
                "meta_response": error_data,
            },
        )

    # --------------------------------------------------------
    # Success
    # --------------------------------------------------------

    try:
        result = response.json()
    except Exception:
        result = {
            "raw_response": response.text
        }

    return {
        "success": True,
        "message": "WhatsApp message sent successfully",
        "recipient": recipient,
        "meta_response": result,
    }