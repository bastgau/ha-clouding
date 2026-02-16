"""Python API wrapper for Clouding.io."""


class CloudingError(Exception):
    """Base Clouding exception."""


class CloudingAuthenticationError(CloudingError):
    """Clouding authentication exception."""


class CloudingBadRequestError(CloudingError):
    """Clouding bad request exception."""


class CloudingConnectionError(CloudingError):
    """Clouding connection exception."""


class CloudingInvalidAPIResponseError(CloudingError):
    """Clouding invalid API response exception."""
