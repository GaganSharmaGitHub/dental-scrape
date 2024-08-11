from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

import config


header_scheme = APIKeyHeader(name="x-key")


def verify_api_key(api_key: str = Security(header_scheme)):
    if api_key != config.SECURITY_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    return api_key
