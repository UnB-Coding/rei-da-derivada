from rest_framework import status, response
from django.contrib.contenttypes.models import ContentType
from rest_framework import status, response
from django.contrib.auth.models import Permission


def handle_400_error(error_msg: str) -> response.Response:
    return response.Response(
        {
            "errors": error_msg
        }, status.HTTP_400_BAD_REQUEST)


def get_content_type(model):
    """ Returns the content type for a given model."""
    return ContentType.objects.get_for_model(model)


def get_permissions(content_type):
    """ Returns all permissions for a given content type."""
    return Permission.objects.filter(content_type=content_type)
