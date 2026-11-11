import logging

import httpx

from app.core.config import settings


logger = logging.getLogger(__name__)


class WhatsAppService:

    # =====================================================
    # PHONE NUMBER NORMALIZATION
    # =====================================================

    @staticmethod
    def _normalize_phone_number(phone: str) -> str:
        """
        Normalize and validate Indian WhatsApp phone numbers.

        Accepted examples:

            +91 93927 09706
                -> 919392709706

            91-93927-09706
                -> 919392709706

            9392709706
                -> 919392709706

            09392709706
                -> 919392709706

            00919392709706
                -> 919392709706

            919392709706
                -> 919392709706

        Returns:
            12-digit WhatsApp number in international format.

        Raises:
            ValueError if the number is invalid.
        """

        original_phone = str(phone or "").strip()

        if not original_phone:
            raise ValueError("Phone number is empty")

        # -------------------------------------------------
        # Keep digits only
        # -------------------------------------------------

        phone = "".join(
            character
            for character in original_phone
            if character.isdigit()
        )

        if not phone:
            raise ValueError(
                f"Invalid phone number: {original_phone}"
            )

        # -------------------------------------------------
        # Remove international dialing prefix 00
        # -------------------------------------------------

        if phone.startswith("00"):
            phone = phone[2:]

        # -------------------------------------------------
        # Remove leading 0
        # -------------------------------------------------

        if phone.startswith("0"):
            phone = phone[1:]

        # -------------------------------------------------
        # Handle India country code
        # -------------------------------------------------

        if phone.startswith("91"):
            indian_number = phone[2:]
        else:
            indian_number = phone

        # -------------------------------------------------
        # Indian mobile number must be exactly 10 digits
        # -------------------------------------------------

        if len(indian_number) != 10:
            raise ValueError(
                f"Invalid Indian mobile number: "
                f"{original_phone}. "
                f"Expected exactly 10 digits."
            )

        if not indian_number.isdigit():
            raise ValueError(
                f"Invalid phone number: {original_phone}"
            )

        # -------------------------------------------------
        # Indian mobile normally starts with 6, 7, 8 or 9
        # -------------------------------------------------

        if indian_number[0] not in "6789":
            raise ValueError(
                f"Invalid Indian mobile number: "
                f"{original_phone}"
            )

        # -------------------------------------------------
        # Final WhatsApp international format
        # -------------------------------------------------

        normalized = f"91{indian_number}"

        logger.info(
            "WhatsApp phone normalized: %s -> %s",
            original_phone,
            normalized,
        )

        return normalized

    # =====================================================
    # SEND TEMPLATE
    # =====================================================

    @staticmethod
    async def _send_template(
        recipient_phone: str,
        template_name: str,
        template_language: str,
        parameters: list,
        button_payload: str | None = None,
        button_index: str = "0",
    ):
        """
        Generic Meta WhatsApp template sender.

        Supports:

        1. Body parameters
        2. Optional Quick Reply button payload

        Example quick reply payload:

            ACCEPT_SERVICE:123
        """

        # -------------------------------------------------
        # Validate WhatsApp configuration
        # -------------------------------------------------

        if not getattr(
            settings,
            "WHATSAPP_ENABLED",
            False,
        ):
            logger.info(
                "WhatsApp notifications are disabled."
            )

            return {
                "success": False,
                "sent": False,
                "reason": (
                    "WhatsApp notifications disabled."
                ),
            }

        # -------------------------------------------------
        # Access Token
        # -------------------------------------------------

        access_token = getattr(
            settings,
            "WHATSAPP_ACCESS_TOKEN",
            None,
        )

        # -------------------------------------------------
        # Phone Number ID
        # -------------------------------------------------

        phone_number_id = getattr(
            settings,
            "WHATSAPP_PHONE_NUMBER_ID",
            None,
        )

        # -------------------------------------------------
        # Graph API Version
        # -------------------------------------------------

        graph_version = getattr(
            settings,
            "WHATSAPP_GRAPH_VERSION",
            "v25.0",
        )

        # -------------------------------------------------
        # Validate access token
        # -------------------------------------------------

        if not access_token:
            logger.error(
                "WHATSAPP_ACCESS_TOKEN is missing."
            )

            return {
                "success": False,
                "sent": False,
                "reason": (
                    "WhatsApp access token missing."
                ),
            }

        # -------------------------------------------------
        # Validate Phone Number ID
        # -------------------------------------------------

        if not phone_number_id:
            logger.error(
                "WHATSAPP_PHONE_NUMBER_ID is missing."
            )

            return {
                "success": False,
                "sent": False,
                "reason": (
                    "WhatsApp phone number ID missing."
                ),
            }

        # -------------------------------------------------
        # Normalize recipient phone
        # -------------------------------------------------

        try:
            recipient_phone = (
                WhatsAppService._normalize_phone_number(
                    recipient_phone
                )
            )

        except ValueError as exc:
            logger.error(
                "Invalid WhatsApp recipient phone "
                "'%s': %s",
                recipient_phone,
                exc,
            )

            return {
                "success": False,
                "sent": False,
                "reason": str(exc),
            }

        # -------------------------------------------------
        # Log recipient
        # -------------------------------------------------

        logger.info(
            "WhatsApp recipient after normalization: %s",
            recipient_phone,
        )

        # -------------------------------------------------
        # Validate template name
        # -------------------------------------------------

        if not template_name:

            logger.error(
                "WhatsApp template name is missing."
            )

            return {
                "success": False,
                "sent": False,
                "reason": (
                    "WhatsApp template name missing."
                ),
            }

        # -------------------------------------------------
        # Validate parameters
        # -------------------------------------------------

        if parameters is None:
            parameters = []

        if not isinstance(parameters, list):
            logger.error(
                "WhatsApp template parameters must "
                "be a list."
            )

            return {
                "success": False,
                "sent": False,
                "reason": (
                    "Template parameters must be a list."
                ),
            }

        # =================================================
        # META GRAPH API URL
        # =================================================

        url = (
            "https://graph.facebook.com/"
            f"{graph_version}/"
            f"{phone_number_id}/messages"
        )

        # =================================================
        # COMPONENTS
        # =================================================

        components = []

        # -------------------------------------------------
        # Body parameters
        # -------------------------------------------------

        if parameters:
            components.append(
                {
                    "type": "body",
                    "parameters": parameters,
                }
            )

        # -------------------------------------------------
        # Optional WhatsApp Quick Reply button
        # -------------------------------------------------

        if button_payload:

            components.append(
                {
                    "type": "button",
                    "sub_type": "quick_reply",
                    "index": str(button_index),
                    "parameters": [
                        {
                            "type": "payload",
                            "payload": str(
                                button_payload
                            ),
                        }
                    ],
                }
            )

        # =================================================
        # PAYLOAD
        # =================================================

        payload = {
            "messaging_product": "whatsapp",

            "to": recipient_phone,

            "type": "template",

            "template": {
                "name": template_name,

                "language": {
                    "code": (
                        template_language
                        or "en_US"
                    ),
                },

                "components": components,
            },
        }

        # =================================================
        # HEADERS
        # =================================================

        headers = {
            "Authorization": (
                f"Bearer {access_token}"
            ),

            "Content-Type": (
                "application/json"
            ),
        }

        # =================================================
        # SEND REQUEST
        # =================================================

        try:

            logger.info(
                "Sending WhatsApp template '%s' "
                "to %s",
                template_name,
                recipient_phone,
            )

            logger.debug(
                "WhatsApp payload: %s",
                payload,
            )

            async with httpx.AsyncClient(
                timeout=20.0
            ) as client:

                response = await client.post(
                    url,
                    headers=headers,
                    json=payload,
                )

            # =================================================
            # SUCCESS
            # =================================================

            if response.is_success:

                try:
                    data = response.json()

                except Exception:
                    data = {
                        "raw_response": (
                            response.text
                        )
                    }

                logger.info(
                    "WhatsApp template '%s' "
                    "sent successfully to %s",
                    template_name,
                    recipient_phone,
                )

                logger.info(
                    "WhatsApp Meta response: %s",
                    data,
                )

                return {
                    "success": True,
                    "sent": True,
                    "response": data,
                }

            # =================================================
            # META API ERROR
            # =================================================

            logger.error(
                "WhatsApp API error %s: %s",
                response.status_code,
                response.text,
            )

            try:
                error_data = response.json()

            except Exception:
                error_data = response.text

            return {
                "success": False,
                "sent": False,
                "status_code": (
                    response.status_code
                ),
                "error": error_data,
            }

        # =================================================
        # TIMEOUT
        # =================================================

        except httpx.TimeoutException:

            logger.exception(
                "WhatsApp request timed out."
            )

            return {
                "success": False,
                "sent": False,
                "error": (
                    "WhatsApp API request timed out."
                ),
            }

        # =================================================
        # HTTP ERROR
        # =================================================

        except httpx.HTTPError as exc:

            logger.exception(
                "WhatsApp HTTP request failed."
            )

            return {
                "success": False,
                "sent": False,
                "error": str(exc),
            }

        # =================================================
        # OTHER ERROR
        # =================================================

        except Exception as exc:

            logger.exception(
                "WhatsApp template '%s' failed.",
                template_name,
            )

            return {
                "success": False,
                "sent": False,
                "error": str(exc),
            }

    # =====================================================
    # NEW SERVICE REQUEST
    # =====================================================

    @staticmethod
    async def send_new_service_request(
        recipient_phone: str,
        ticket_number: str,
        customer_name: str,
        machine_number: str,
        priority: str,
        complaint: str,
        address: str,
    ):
        """
        Sends:

            new_service_request

        Template parameters:

            {{1}} Ticket
            {{2}} Customer
            {{3}} Machine
            {{4}} Priority
            {{5}} Complaint
            {{6}} Address
        """

        parameters = [

            # -------------------------------------------------
            # {{1}} Ticket
            # -------------------------------------------------

            {
                "type": "text",
                "text": str(
                    ticket_number or ""
                ),
            },

            # -------------------------------------------------
            # {{2}} Customer
            # -------------------------------------------------

            {
                "type": "text",
                "text": str(
                    customer_name or ""
                ),
            },

            # -------------------------------------------------
            # {{3}} Machine
            # -------------------------------------------------

            {
                "type": "text",
                "text": str(
                    machine_number or ""
                ),
            },

            # -------------------------------------------------
            # {{4}} Priority
            # -------------------------------------------------

            {
                "type": "text",
                "text": str(
                    priority or ""
                ),
            },

            # -------------------------------------------------
            # {{5}} Complaint
            # -------------------------------------------------

            {
                "type": "text",
                "text": str(
                    complaint or ""
                )[:500],
            },

            # -------------------------------------------------
            # {{6}} Address
            # -------------------------------------------------

            {
                "type": "text",
                "text": str(
                    address
                    or "Address not available"
                )[:1000],
            },
        ]

        return await WhatsAppService._send_template(

            recipient_phone=recipient_phone,

            template_name=getattr(
                settings,
                "WHATSAPP_TEMPLATE_NAME",
                "new_service_request",
            ),

            template_language=getattr(
                settings,
                "WHATSAPP_TEMPLATE_LANGUAGE",
                "en_US",
            ),

            parameters=parameters,
        )

    # =====================================================
    # ENGINEER ASSIGNED
    # =====================================================

    @staticmethod
    async def send_engineer_assigned(
        recipient_phone: str,
        ticket_number: str,
        customer_name: str,
        engineer_name: str,
        machine_number: str,
        address: str = "",
        complaint: str = "",
        priority: str = "",
        service_id=None,
    ):
        """
        Send NEW SERVICE ASSIGNED notification
        to the service engineer.

        Recommended Meta template:

            engineer_assigned

        Body parameters:

            {{1}} Engineer
            {{2}} Ticket
            {{3}} Customer
            {{4}} Machine
            {{5}} Address
            {{6}} Complaint
            {{7}} Priority

        Quick Reply Button:

            ACCEPT SERVICE

        Payload:

            ACCEPT_SERVICE:<service_id>
        """

        # -------------------------------------------------
        # Create button payload
        # -------------------------------------------------

        if service_id is not None:
            accept_payload = (
                f"ACCEPT_SERVICE:{service_id}"
            )

        else:
            # Fallback to ticket number if service ID
            # is not supplied.
            accept_payload = (
                f"ACCEPT_SERVICE:"
                f"{ticket_number}"
            )

        # -------------------------------------------------
        # Template parameters
        # -------------------------------------------------

        parameters = [

            # {{1}} Engineer
            {
                "type": "text",
                "text": str(
                    engineer_name
                    or "Service Engineer"
                ),
            },

            # {{2}} Ticket
            {
                "type": "text",
                "text": str(
                    ticket_number or ""
                ),
            },

            # {{3}} Customer
            {
                "type": "text",
                "text": str(
                    customer_name or ""
                ),
            },

            # {{4}} Machine
            {
                "type": "text",
                "text": str(
                    machine_number or ""
                ),
            },

            # {{5}} Address
            {
                "type": "text",
                "text": str(
                    address
                    or "Address not available"
                )[:1000],
            },

            # {{6}} Complaint
            {
                "type": "text",
                "text": str(
                    complaint
                    or "Not specified"
                )[:500],
            },

            # {{7}} Priority
            {
                "type": "text",
                "text": str(
                    priority
                    or "Normal"
                ),
            },
        ]

        logger.info(
            "Sending engineer assignment "
            "for ticket %s to engineer %s",
            ticket_number,
            engineer_name,
        )

        logger.info(
            "Engineer accept payload: %s",
            accept_payload,
        )

        # -------------------------------------------------
        # Send WhatsApp
        # -------------------------------------------------

        return await WhatsAppService._send_template(

            recipient_phone=recipient_phone,

            template_name=getattr(
                settings,
                "WHATSAPP_ENGINEER_ASSIGNED_TEMPLATE_NAME",
                "engineer_assigned",
            ),

            template_language=getattr(
                settings,
                "WHATSAPP_ENGINEER_ASSIGNED_TEMPLATE_LANGUAGE",
                getattr(
                    settings,
                    "WHATSAPP_TEMPLATE_LANGUAGE",
                    "en_US",
                ),
            ),

            parameters=parameters,

            button_payload=accept_payload,

            button_index="0",
        )

    # =====================================================
    # ENGINEER ACCEPTED - CUSTOMER NOTIFICATION
    # =====================================================

    @staticmethod
    async def send_engineer_accepted(
        recipient_phone: str,
        ticket_number: str,
        customer_name: str,
        engineer_name: str,
        machine_number: str = "",
    ):
        """
        Send notification to CUSTOMER when
        the assigned engineer accepts the service.

        Recommended Meta template:

            engineer_accepted

        Body parameters:

            {{1}} Customer
            {{2}} Ticket
            {{3}} Engineer
            {{4}} Machine

        Example message:

            Hello M Vishnu,

            Your service engineer Ravi Kumar has
            accepted service ticket ST20260903-00034.

            Machine:
            Canon imageRUNNER 2425

            The service engineer will reach you shortly.
        """

        parameters = [

            # -------------------------------------------------
            # {{1}} Customer
            # -------------------------------------------------

            {
                "type": "text",
                "text": str(
                    customer_name
                    or "Customer"
                ),
            },

            # -------------------------------------------------
            # {{2}} Ticket
            # -------------------------------------------------

            {
                "type": "text",
                "text": str(
                    ticket_number or ""
                ),
            },

            # -------------------------------------------------
            # {{3}} Engineer
            # -------------------------------------------------

            {
                "type": "text",
                "text": str(
                    engineer_name
                    or "Service Engineer"
                ),
            },

            # -------------------------------------------------
            # {{4}} Machine
            # -------------------------------------------------

            {
                "type": "text",
                "text": str(
                    machine_number
                    or "Machine"
                ),
            },
        ]

        logger.info(
            "Sending engineer accepted "
            "notification to customer %s "
            "for ticket %s",
            customer_name,
            ticket_number,
        )

        return await WhatsAppService._send_template(

            recipient_phone=recipient_phone,

            template_name=getattr(
                settings,
                "WHATSAPP_ENGINEER_ACCEPTED_TEMPLATE_NAME",
                "engineer_accepted",
            ),

            template_language=getattr(
                settings,
                "WHATSAPP_ENGINEER_ACCEPTED_TEMPLATE_LANGUAGE",
                getattr(
                    settings,
                    "WHATSAPP_TEMPLATE_LANGUAGE",
                    "en_US",
                ),
            ),

            parameters=parameters,
        )

    # =====================================================
    # SERVICE STATUS UPDATE
    # =====================================================

    @staticmethod
    async def send_service_status_update(
        recipient_phone: str,
        ticket_number: str,
        customer_name: str,
        status_value: str,
    ):
        """
        Sends:

            service_status_update

        Template parameters:

            {{1}} Ticket
            {{2}} Customer
            {{3}} Status
        """

        parameters = [

            # -------------------------------------------------
            # {{1}} Ticket
            # -------------------------------------------------

            {
                "type": "text",
                "text": str(
                    ticket_number or ""
                ),
            },

            # -------------------------------------------------
            # {{2}} Customer
            # -------------------------------------------------

            {
                "type": "text",
                "text": str(
                    customer_name or ""
                ),
            },

            # -------------------------------------------------
            # {{3}} Status
            # -------------------------------------------------

            {
                "type": "text",
                "text": str(
                    status_value or ""
                ),
            },
        ]

        return await WhatsAppService._send_template(

            recipient_phone=recipient_phone,

            template_name=getattr(
                settings,
                "WHATSAPP_STATUS_TEMPLATE_NAME",
                "service_status_update",
            ),

            template_language=getattr(
                settings,
                "WHATSAPP_STATUS_TEMPLATE_LANGUAGE",
                getattr(
                    settings,
                    "WHATSAPP_TEMPLATE_LANGUAGE",
                    "en_US",
                ),
            ),

            parameters=parameters,
        )