"""Custom Authentication Class."""

import httpx
from django.contrib.auth.backends import BaseBackend
from django.http import HttpRequest
from pydantic import ValidationError

from apps.accounts.models import Account
from apps.libs import BLUESKY, BlueSkySessionRequest, BlueSkySessionResponse, Logger

logger = Logger(__name__)


class BlueSkyJWTBackend(BaseBackend):
    """BlueSky JWT Authentication Backend."""

    def authenticate(
        self, request: HttpRequest | None = None, **kwargs
    ) -> Account | None:
        """Authenticate user."""
        if not request:
            return None

        if auth_header := request.headers.get("Authorization"):
            _, token = auth_header.split()
            logger.debug(f"Authenticating user with token: {token[:5]}...{token[-5:]}")
            return Account.objects.filter(access_token=token).first()

        response = BlueSkySessionResponse.model_construct()

        try:
            data = BlueSkySessionRequest.from_request(request)
            response = BLUESKY.get_user_jwt(data.identifier, data.password)

            return Account.auth.retrieve_and_update_tokens(
                email=response.email,
                access=response.accessJwt,
                refresh=response.refreshJwt,
            )
        except Account.DoesNotExist:
            logger.info(f"Creating account for {data.identifier}")
            return Account.auth.create_from_api(
                email=response.email,
                handle=response.handle,
                access=response.accessJwt,
                refresh=response.refreshJwt,
            )
        except ValidationError as exc:
            logger.error(f"Error validating request: {exc.error_count()}")
            logger.debug(f"Validation errors: {exc.json(indent=2)}")

            return None
        except httpx.HTTPStatusError as exc:
            logger.error(f"Error getting user: {exc}")
            return None
