from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """Custom exception handler for consistent API responses"""
    response = exception_handler(exc, context)

    if response is not None:
        # Format error response
        error_data = {
            'success': False,
            'message': 'An error occurred.',
            'errors': response.data
        }
        response.data = error_data
    else:
        # Handle unhandled exceptions
        response = Response({
            'success': False,
            'message': 'Internal server error.',
            'errors': {'detail': str(exc)}
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return response


def success_response(data=None, message='Success', status_code=200):
    """Helper for consistent success responses"""
    response = {
        'success': True,
        'message': message,
    }
    if data is not None:
        response['data'] = data
    return Response(response, status=status_code)


def error_response(message='Error', errors=None, status_code=400):
    """Helper for consistent error responses"""
    response = {
        'success': False,
        'message': message,
    }
    if errors is not None:
        response['errors'] = errors
    return Response(response, status=status_code)
