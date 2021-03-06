# generated by datamodel-codegen:
#   filename:  observations/ground_velocity.json
#   timestamp: 2022-01-23T15:49:03+00:00

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from ..core import location


class GroundVelocity(BaseModel):
    sensor_id: str = Field(..., title='Physical sensor id')
    location: Optional[location.Location] = Field(
        None,
        description='Location of the reporting sensor in the BF frame of reference.',
    )
    sog: float = Field(
        ...,
        description='Reported speed over ground.',
        title='Speed over ground [knots]',
    )
    sog_transverse_bow: Optional[float] = Field(
        None,
        description='Reported speed over ground transverse at bow.',
        title='Speed over ground [knots]',
    )
    sog_transverse_stern: Optional[float] = Field(
        None,
        description='Reported speed over ground transverse at stern.',
        title='Speed over ground [knots]',
    )
    cog: float = Field(
        ...,
        description='Reported course over ground [degrees] relative True North',
        title='Course over ground',
    )
