# generated by datamodel-codegen:
#   filename:  envelope.json
#   timestamp: 2022-01-23T13:15:05+00:00

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from pydantic import AnyUrl, BaseModel, Extra, Field


class Envelope(BaseModel):
    class Config:
        extra = Extra.forbid

    sent_at: datetime = Field(
        ...,
        description='Date and time when the message was sent from the application processing the raw sensor data, expressed according to the ISO 8601 standard.',
        examples=['2021-10-07T20:20:39.345+00:00'],
        title='Sent at',
    )
    message_type: AnyUrl = Field(
        ...,
        description='A reference URL to a json-schema defining the message type carried by this envelope.',
        title='Message type',
    )
    message: Dict[str, Any] = Field(
        ..., description='The message contained by this envelope.', title='Message'
    )
