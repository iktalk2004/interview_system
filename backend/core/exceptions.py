from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        custom_response_data = {
            'error': {
                'code': response.status_code,
                'message': str(exc),
                'details': response.data
            }
        }
        response.data = custom_response_data
        
        logger.error(
            f"API Error: {exc}",
            extra={
                'status_code': response.status_code,
                'path': context['request'].path,
                'method': context['request'].method,
            }
        )
    else:
        logger.critical(
            f"Unhandled Exception: {exc}",
            exc_info=True,
            extra={
                'path': context['request'].path,
                'method': context['request'].method,
            }
        )
        response = Response(
            {
                'error': {
                    'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'message': 'Internal server error',
                    'details': {}
                }
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return response
