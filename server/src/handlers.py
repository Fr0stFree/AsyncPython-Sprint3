import asyncio
import datetime as dt

from server.src.models.client import ClientManager
from server.src.models.request import Request
from server.src.router import Router
from shared.schemas.actions import BroadcastMessagePayload, SendMessagePayload, ActionTypes
from shared.schemas.notifications import BroadcastMessageNotificationPayload, \
    BroadcastMessageNotificationFrame, ErrorNotificationFrame, ErrorNotificationPayload


router = Router()


@router.on_action(ActionTypes.BROADCAST_MESSAGE)
async def on_broadcast_message(request: Request) -> None:
    incoming_payload = BroadcastMessagePayload.model_validate(request.frame.payload)
    outgoing_payload = BroadcastMessageNotificationPayload(
        text=incoming_payload.text,
        sender=request.client.user.id,
        created_at=dt.datetime.now(dt.UTC),
    )
    frame = BroadcastMessageNotificationFrame(payload=outgoing_payload)
    clients = ClientManager.get_current()
    tasks = [client.send(frame) for client in clients.all()]
    await asyncio.gather(*tasks)
    request.logger.info("Message broadcasted successfully")


@router.on_action(ActionTypes.SEND_MESSAGE)
async def on_send_message(request: Request) -> None:
    incoming_payload = SendMessagePayload.model_validate(request.frame.payload)
    clients = ClientManager.get_current()
    client = clients.get(incoming_payload.to)
    if client is None:
        outgoing_payload = ErrorNotificationPayload(
            text=f"User '{incoming_payload.to}' not found",
            created_at=dt.datetime.now(dt.UTC),
        )
        await request.reply(ErrorNotificationFrame(payload=outgoing_payload))
        request.logger.info("User '%s' not found", incoming_payload.to)
    else:
        outgoing_payload = BroadcastMessageNotificationPayload(
            text=incoming_payload.text,
            sender=request.client.user.id,
            created_at=dt.datetime.now(dt.UTC),
        )
        frame = BroadcastMessageNotificationFrame(payload=outgoing_payload)
        await client.send(frame)
        request.logger.info("Message sent to '%s'", incoming_payload.to)


async def on_error(request: Request, error: Exception) -> None:
    payload = ErrorNotificationPayload(
        text=f"Something went wrong: {error}",
        created_at=dt.datetime.now(dt.UTC),
    )
    frame = ErrorNotificationFrame(payload=payload)
    request.logger.exception("Error occurred while handling request")
    await request.reply(frame)


@router.on_action(ActionTypes.LOGOUT)
async def on_logout(request: Request) -> None:
    clients = ClientManager.get_current()
    await clients.drop(request.client)
    request.logger.info("Client '%s' dropped", request.client.user.id)


async def on_unknown_action(request: Request) -> None:
    payload = ErrorNotificationPayload(text="Unknown command", created_at=dt.datetime.now(dt.UTC))
    frame = ErrorNotificationFrame(payload=payload)
    await request.reply(frame)
    request.logger.info("Unknown command received from '%s'", request.client.user.id)
