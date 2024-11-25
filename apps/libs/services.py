# ruff: noqa: N815
"""Service layer.

Provides interface to interact with BlueSky/AT Protocol.
"""

import enum
import json
import typing

import httpx
from django.http import HttpRequest
from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import BaseModel

from apps.libs.logger import blue_sky_logger as logger


class BlueSkySessionRequest(BaseModel):
    """BlueSky Session Request."""

    identifier: str
    password: str

    @classmethod
    def from_request(cls: type[typing.Self], request: HttpRequest) -> typing.Self:
        """Create BlueSkySessionRequest from request."""
        return cls(**request.POST.dict())


class BlueSkySessionRequestFactory(ModelFactory["BlueSkySessionRequest"]):
    """BlueSky Session Request Factory."""

    __model__ = BlueSkySessionRequest


class VerificationMethod(BaseModel):
    """Verification Method."""

    id: str
    type: str
    controller: str
    publicKeyMultibase: str


class VerificationMethodFactory(ModelFactory["VerificationMethod"]):
    """Verification Method Factory."""

    __model__ = VerificationMethod


class Service(BaseModel):
    """Service."""

    id: str
    type: str
    serviceEndpoint: str


class ServiceFactory(ModelFactory["Service"]):
    """Service Factory."""

    __model__ = Service


class DidDoc(BaseModel):
    """DID Document."""

    id: str
    context: list[str]
    alsoKnownAs: list[str]
    verificationMethod: list[VerificationMethod]
    service: list[Service]

    @classmethod
    def from_response(cls, response: dict) -> "DidDoc":
        """Create DidDoc from response.

        This handles the @context key in the response.
        """
        doc = cls.model_construct(**response)
        doc.context = response["@context"]
        return cls.model_validate(doc)


class DidDocFactory(ModelFactory["DidDoc"]):
    """DidDoc Factory."""

    __model__ = DidDoc


class BlueSkySessionResponse(BaseModel):
    """BlueSky Session Response."""

    did: str
    didDoc: DidDoc
    handle: str
    email: str
    emailConfirmed: bool
    emailAuthFactor: bool
    accessJwt: str
    refreshJwt: str
    active: bool

    @classmethod
    def from_response(cls, response: dict) -> "BlueSkySessionResponse":
        """Create BlueSkySessionResponse from response."""
        resp = cls.model_construct(**response)
        resp.didDoc = DidDoc.from_response(response["didDoc"])
        return cls.model_validate(resp)


class BlueSkySessionResponseFactory(ModelFactory["BlueSkySessionResponse"]):
    """BlueSky Session Response Factory."""

    __model__ = BlueSkySessionResponse


class BlueSkyEndpoints(enum.StrEnum):
    """Endpoints for BlueSky AT Protocol Implementation."""

    BASE_URL = "https://bsky.social"
    PROTOCOL = "xrpc"
    CREATE_SESSION = "com.atproto.server.createSession"
    REFRESH_SESSION = "com.atproto.server.refreshSession"

    URL = "{base_url}/{protocol}/{action}"


class BlueSkyService:
    """API Handler Methods for BlueSky."""

    def __init__(self, base_url: str = BlueSkyEndpoints.BASE_URL) -> None:
        """BlueSky Service."""
        self.base_url = base_url

    def get_user_jwt(
        self, handle: str, password: str
    ) -> BlueSkySessionResponse:  # pragma: no cover
        """Get JWT for user."""
        url = BlueSkyEndpoints.URL.format(
            base_url=self.base_url,
            protocol=BlueSkyEndpoints.PROTOCOL,
            action=BlueSkyEndpoints.CREATE_SESSION,
        )
        headers = {"Content-Type": "application/json"}
        logger.debug(f"Constructed URL: {url}")

        resp = httpx.post(
            url,
            headers=headers,
            json=BlueSkySessionRequest(
                identifier=handle,
                password=password,
            ).model_dump(),
        )

        if resp.is_error:
            logger.error(f"Error: {resp.text} | Status Code: {resp.status_code}")
            resp.raise_for_status()

        data = resp.json()
        response = BlueSkySessionResponse.from_response(data)

        logger.debug(f"Response: {json.dumps(data, indent=2)}")

        return response
