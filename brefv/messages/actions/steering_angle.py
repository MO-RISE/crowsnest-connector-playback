# generated by datamodel-codegen:
#   filename:  actions/steering_angle.json
#   timestamp: 2022-01-23T15:49:03+00:00

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class SteeringOrderAngle(BaseModel):
    target_unit_id: str = Field(..., title='Targeted steering unit ID')
    angle: float = Field(
        ...,
        description='Rudder angle in degrees, positive when trailing edge points to port (port angel negative)',
        title='Rudder angle',
    )
    flap_angle: Optional[float] = Field(
        0.0,
        description='Rudder flap angle in degrees, positive when trailing edge points to port',
        title='Rudder flap angle',
    )
