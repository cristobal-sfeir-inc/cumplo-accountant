"""FastAPI application entry point for cumplo-accountant."""

from logging import CRITICAL, DEBUG, basicConfig, getLogger

import google.cloud.logging
from cumplo_common.dependencies import authenticate
from cumplo_common.middlewares import PubSubMiddleware
from fastapi import Depends, FastAPI

from cumplo_accountant.dependencies import login
from cumplo_accountant.routers import balance, credentials
from cumplo_accountant.utils.constants import IS_TESTING, LOG_FORMAT

getLogger("cumplo_common").setLevel(DEBUG)

# NOTE: Mute noisy third-party loggers
for module in ("google", "urllib3", "werkzeug"):
    getLogger(module).setLevel(CRITICAL)


if IS_TESTING:
    basicConfig(level=DEBUG, format=LOG_FORMAT)
else:
    client = google.cloud.logging.Client()
    client.setup_logging(log_level=DEBUG)


app = FastAPI(dependencies=[Depends(authenticate)])
app.add_middleware(PubSubMiddleware)

app.include_router(balance.router, dependencies=[Depends(login)])
app.include_router(credentials.router)
