"""Python API wrapper for Clouding.io"""


class CloudingException(Exception):
    """Base Clouding exception."""


class CloudingAuthenticationException(CloudingException):
    """Clouding authentication exception."""


class CloudingBadRequestException(CloudingException):
    """Clouding bad request exception."""


class CloudingConnectionException(CloudingException):
    """Clouding connection exception."""


class CloudingInvalidAPIResponseException(CloudingException):
    """Clouding invalid API response exception."""
