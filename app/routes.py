from http import HTTPStatus
from fastapi import APIRouter, UploadFile, File

from app.dependencies import rate_limiter
from app.service import process_csv, fetch_provider_npi
from fastapi.requests import Request

claims = APIRouter()


@claims.get("/healthz")
async def check_healthz():
    return "OK", HTTPStatus.OK


@claims.post("/upload")
async def upload_file(request: Request, file: UploadFile = File(...)):
    """
    Upload a csv data of claims
    :param request:
    :param file:
    :return:
    """
    contents = await file.read()
    return await process_csv(contents, request)


@claims.get("/provider")
@rate_limiter  # rate limiter for the following request
async def fetch_providers(request: Request, max_providers_count: int = 10):
    """
    top 10 providers based on net fee
    :param max_providers_count:
    :param request:
    :return:
    """
    # we can queue a queuing mechanism like APACHE KAFKA and publish our data to a specific topic
    # The downstream payments service consume from the topic and concurrency can be managed and data loss can avoided
    return await fetch_provider_npi(request, max_providers_count)
