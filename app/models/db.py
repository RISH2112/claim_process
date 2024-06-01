from collections import deque
from datetime import datetime
from http import HTTPStatus
from typing import Optional

import requests
from pydantic import validator
from sqlmodel import Field, SQLModel


def parse_float(v):
    cleaned_value = ''.join(char for char in v if char.isalnum() or char == ".")
    return float(cleaned_value)


class Claim(SQLModel, table=True):
    id: str = Field(primary_key=True)
    service_date: datetime = Field(..., alias="service_date")
    submitted_procedure: str = Field(..., alias="submitted_procedure")
    plangroup: str = Field(..., alias="plangroup")
    subscriber: str = Field(..., alias="subscriber")
    provider_npi: str = Field(..., alias="provider_npi", min_length=10, max_length=10, description="Provider NPI")
    provider_fees: float = Field(..., alias="provider_fees")
    allowed_fees: float = Field(..., alias="allowed_fees")
    member_coinsurance: float = Field(..., alias="member_coinsurance")
    member_copay: float = Field(..., alias="member_copay")
    net_fee: float = Field(..., alias="net_fee")
    quadrant: Optional[str] = Field(default=None, alias="quadrant")

    class Config:
        tablename = "claim"

    @validator("submitted_procedure")
    def validate_submitted_procedure(cls, value):
        if not value.startswith('D'):
            raise ValueError('submitted procedure must start with the letter D')
        return value

    def __init__(self, **data):
        for key, value in data.items():
            if key in ["provider_fees", "allowed_fees", "member_coinsurance", "member_copay"]:
                data[key] = parse_float(data.get(key))
            elif key == "service_date":
                data[key] = datetime.strptime(value, '%m/%d/%y %H:%M')

        data["net_fee"] = data["provider_fees"] + data["member_coinsurance"] + data["member_copay"] - data[
            "allowed_fees"]
        super().__init__(**data)

