# generated by datamodel-codegen:
#   filename:  observations/propeller.json
#   timestamp: 2022-01-12T08:16:31+00:00

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from ..core import location, wrench


class Propeller(BaseModel):
    sensor_id: str = Field(..., title='Physical sensor id')
    rpm: float = Field(
        ...,
        description='Propeller RPM in revolutions per minute',
        title='Propeller RPM',
    )
    pitch_angle: Optional[float] = Field(
        None, description='Propeller pitch angle', title='Pitch angle'
    )
    location: Optional[location.Location] = Field(
        None, description='Location of the propeller in the BF frame of reference.'
    )
    wrench: Optional[wrench.Wrench] = None
