# generated by datamodel-codegen:
#   filename:  observations/position.json
#   timestamp: 2022-01-12T08:16:31+00:00

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from ..core import location, position


class Position(BaseModel):
    sensor_id: str = Field(..., title='Physical sensor id')
    location: location.Location = Field(
        ...,
        description='Location of the reporting sensor in the BF frame of reference.',
    )
    position: position.Position
    semi_major_axis: Optional[float] = Field(
        None,
        description="Semi-major axis of the GNSS sensor's error ellipse for 1 standard deviation",
        title='Semi-major axis',
    )
    semi_minor_axis: Optional[float] = Field(
        None,
        description="Semi-minor axis of the GNSS sensor's error ellipse for 1 standard deviation",
        title='Semi-minor axis',
    )
    azimuth: Optional[float] = Field(
        None,
        description="Azimuth of the semi-major axis of the GNSS sensor's error ellipse with respect to True North in degrees",
        title='Azimuth',
    )