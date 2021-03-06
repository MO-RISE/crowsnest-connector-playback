# generated by datamodel-codegen:
#   filename:  observations/rudder.json
#   timestamp: 2022-01-23T15:49:03+00:00

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from ..core import location, wrench


class Rudder(BaseModel):
    sensor_id: str = Field(..., title='Physical sensor id')
    angle: float = Field(
        ...,
        description='Rudder angle in degrees, positive when trailing edge points to port',
        title='Rudder angle',
    )
    flap_angle: Optional[float] = Field(
        0.0,
        description='Rudder flap angle in degrees, positive when trailing edge points to port',
        title='Rudder flap angle',
    )
    location: Optional[location.Location] = Field(
        None, description='Location of the rudder in the BF frame of reference.'
    )
    wrench: Optional[wrench.Wrench] = None
