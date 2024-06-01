import csv
from http import HTTPStatus
from typing import List

import ulid
from fastapi.requests import Request
from app.models.db import Claim


async def process_csv(contents: bytes, request: Request):
    decoded_content = contents.decode('utf-8').splitlines()
    csv_reader = csv.DictReader(decoded_content)
    return await add_claim(csv_reader, request)


def clean_alias(alias):
    clean_str = ''.join(char.lower() for char in alias if char.isalpha() or char.isspace())
    return '_'.join(clean_str.split())


# method to add claim to database
async def add_claim(claims: csv.DictReader, request: Request):
    """

    :param claims:
    :param request:
    :return:
    """
    for claim in claims:
        data = {clean_alias(k): v for k, v in claim.items()}
        data["id"] = str(ulid.new())

        try:
            db_response = await request.app.db_helper.insert(model=Claim, insert_data=data)
        except Exception as ValueError:
            return {
                "success": False,
                "message": f"Failed to insert user due to query execution error{ValueError.__str__()}",
                "status_code": HTTPStatus.INTERNAL_SERVER_ERROR,
                "data": {},
            }

        if not db_response:
            return {
                "success": False,
                "message": "Failed to insert user due to query execution error",
                "status_code": HTTPStatus.INTERNAL_SERVER_ERROR,
                "data": {},
            }

    return {
        "success": True,
        "message": "Claim data saved",
        "status_code": HTTPStatus.OK,
        "data": {},
    }


async def fetch_provider_npi(request: Request, limit: int):
    """
    Fetch top 10 provider NPI based on net fee
    :param limit:
    :param request:
    :return:
    """
    columns = [
        Claim.provider_npi,
        Claim.net_fee
    ]

    status, data = await request.app.db_helper.select(model=Claim, columns=columns)

    if not data or not status:
        return {
            "success": status,
            "message": "provider NPI fetch failed",
            "status_code": HTTPStatus.OK,
            "data": {},
        }

    processed_data = await fetch_top_provider_npi(data, limit)  # process and find top 10 provider NPI

    return {
        "success": status,
        "message": "Top provider NPI based on net Fee",
        "status_code": HTTPStatus.OK,
        "data": processed_data,
    }


async def fetch_top_provider_npi(data: List[Claim], limit: int):
    """
    sort the data in hashMap and based on provider_npi
    fetch top 10
    :param limit:
    :param data:
    :return:
    """
    providers = {}

    for provider_info in data:

        providers[provider_info.provider_npi] = round(
            provider_info.net_fee or 0.0 + providers.get(provider_info.provider_npi, 0), 2)

    max_net_fee_providers = sorted(providers.items(), key=lambda item: item[1], reverse=True)[:limit]

    return max_net_fee_providers
