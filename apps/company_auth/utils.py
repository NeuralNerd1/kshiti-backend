from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from .models import CompanyUser


def get_company_from_request(request):
    """
    Resolve company from the authenticated user's active company membership.
    """
    if not hasattr(request.user, "company_membership"):
        raise PermissionDenied("User has no company membership")

    return request.user.company_membership.company


def get_company_user(request, company):
    """
    Resolve active CompanyUser for request.user + company.
    """
    cu = CompanyUser.objects.filter(
        company=company,
        user=request.user,
    ).first()

    if not cu or not cu.is_active:
        raise PermissionDenied("Inactive or invalid company user")

    return cu
