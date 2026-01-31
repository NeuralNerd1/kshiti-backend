from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from .models import Company, CompanyUser
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model
from .models import CompanyUser, Company

User = get_user_model()


def authenticate_user(*, company_slug, email, password):
    # 1. Authenticate by email explicitly
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        raise Exception("Invalid email or password")

    if not user.check_password(password):
        raise Exception("Invalid email or password")

    if not user.is_active:
        raise Exception("User account is disabled")

    # 2. Ensure company mapping exists
    try:
        company_user = user.company_membership
    except CompanyUser.DoesNotExist:
        raise Exception("User is not associated with any company")

    company = company_user.company

    # 3. Validate company context
    if company.slug != company_slug:
        raise Exception("User does not belong to this company")

    if company.status != Company.STATUS_ACTIVE or not company.is_login_allowed:
        raise Exception("Company access is disabled")

    return {
        "user": user,
        "company": company,
    }


def logout_user(*, request):
    logout(request)

from .models import CompanyUser


def reset_password(*, email, new_password):
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        raise PermissionDenied("User not found")

    # Ensure user is mapped to a company
    try:
        company_user = CompanyUser.objects.get(user=user)
    except CompanyUser.DoesNotExist:
        raise PermissionDenied("User is not assigned to a company")

    company = company_user.company

    if company.status != company.STATUS_ACTIVE or not company.is_login_allowed:
        raise PermissionDenied("Company access is disabled")

    user.set_password(new_password)
    user.save(update_fields=["password"])

    return True
