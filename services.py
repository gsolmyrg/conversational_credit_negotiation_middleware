from uuid import NAMESPACE_DNS, uuid5

from clients import CrewaiClient, WhatsappClient
from models import DebtNegotiationRequestBody, Message, WhatsappRequestBody


class MessageSubmissionService:
    def __init__(self):
        self._crewai_client = CrewaiClient()
        self._whatsapp_client = WhatsappClient()

    def kickoff_interaction(self, request: DebtNegotiationRequestBody):
        conversation_id = str(uuid5(NAMESPACE_DNS, request.persona.cellphone))

        inputs = {
            "id": conversation_id,
            "debt_negotiation": request.model_dump(),
        }
        kickoff_id = self._crewai_client.kickoff(inputs)
        result_json = self._crewai_client.status(kickoff_id)
        assistant_message = Message(**result_json["history"][-1])
        self._whatsapp_client.send_text(
            number=request.persona.cellphone, text=assistant_message.content
        )
        return assistant_message

    def handle_whatsapp_interaction(self, request: WhatsappRequestBody):
        if request.data.get("key", {}).get("fromMe") or not request.data.get(
            "message", {}
        ).get("conversation"):
            return

        conversation_id = str(
            uuid5(NAMESPACE_DNS, request.data["key"]["remoteJid"].split("@")[0])
        )

        user_message = Message(
            role="user", content=request.data["message"]["conversation"]
        )
        inputs = {"id": conversation_id, "user_message": user_message.model_dump()}
        kickoff_id = self._crewai_client.kickoff(inputs)
        result_json = self._crewai_client.status(kickoff_id)

        if not result_json:
            return Message(role="assistant", content="")

        assistant_message = Message(**result_json["history"][-1])
        self._whatsapp_client.send_text(
            number=request.data["key"]["remoteJid"].split("@")[0],
            text=assistant_message.content,
        )
        return assistant_message
