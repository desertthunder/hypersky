# ruff: noqa: N815
"""Account Management Views."""

import enum
import logging

import httpx
from django import forms
from django.contrib.auth import views
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView
from pydantic import BaseModel

from apps.accounts.models import Account


class BlueSkyFormatter(logging.Formatter):
    """Custom Formatter for BlueSky Logger."""

    DODGER_BLUE = "\033[38;5;25m"
    ERROR = "\033[91m"
    WARNING = "\033[93m"
    CRITICAL = "\033[95m"
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        """Format log record.

        Makes the log message dodgerblue.
        """
        message = super().format(record)
        match record.levelno:
            case logging.ERROR:
                return f"{self.ERROR}{message}{self.RESET}"
            case logging.WARNING:
                return f"{self.WARNING}{message}{self.RESET}"
            case logging.CRITICAL:
                return f"{self.CRITICAL}{message}{self.RESET}"
            case _:
                return f"{self.DODGER_BLUE}{message}{self.RESET}"


class BlueSkyLogger(logging.Logger):
    """BlueSky Logger."""

    def __init__(self, name: str = "blue_sky_service") -> None:
        """Initialize the BlueSky Logger."""
        super().__init__(name)
        self.setLevel(logging.DEBUG)

        handler = logging.StreamHandler()
        handler.setFormatter(BlueSkyFormatter())

        self.addHandler(handler)


blue_sky_logger = BlueSkyLogger()


class BlueSkySessionRequest(BaseModel):
    """BlueSky Session Request."""

    identifier: str
    password: str


class VerificationMethod(BaseModel):
    """Verification Method."""

    id: str
    type: str
    controller: str
    publicKeyMultibase: str


class Service(BaseModel):
    """Service."""

    id: str
    type: str
    serviceEndpoint: str


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

    def create_account(self) -> Account:
        """Create Account from BlueSky Session Response."""
        return Account.objects.create(
            email=self.email,
            handle=self.handle,
            access_token=self.accessJwt,
            refresh_token=self.refreshJwt,
        )


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

    def get_user_jwt(self, handle: str, password: str) -> BlueSkySessionResponse:
        """Get JWT for user."""
        url = BlueSkyEndpoints.URL.format(
            base_url=self.base_url,
            protocol=BlueSkyEndpoints.PROTOCOL,
            action=BlueSkyEndpoints.CREATE_SESSION,
        )
        headers = {"Content-Type": "application/json"}
        blue_sky_logger.debug(f"Constructed URL: {url}")

        resp = httpx.post(
            url,
            headers=headers,
            json=BlueSkySessionRequest(
                identifier=handle, password=password
            ).model_dump(),
        )

        if resp.is_error:
            blue_sky_logger.error(
                f"Error: {resp.text} | Status Code: {resp.status_code}",
            )

            resp.raise_for_status()
        else:
            blue_sky_logger.debug(f"Response: {resp.text}")
        response = BlueSkySessionResponse.from_response(resp.json())
        return response


BLUESKY = BlueSkyService()


class LoginView(views.LoginView):
    """Login view."""

    template_name = "login.dj"


class CustomUserCreationForm(forms.Form):
    """User creation form."""

    handle = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)


class RegisterView(CreateView):
    """User create view."""

    form_class = UserCreationForm
    template_name = "register.dj"
    success_url = reverse_lazy("login")
