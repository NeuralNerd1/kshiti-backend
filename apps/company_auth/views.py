from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from .serializers import PasswordResetSerializer
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from .models import Company
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import CompanyPublicSerializer



from .serializers import (
    LoginSerializer,
    SessionSerializer,
    LogoutSerializer,
)
from .services import authenticate_user, logout_user, reset_password

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = authenticate_user(
                company_slug=serializer.validated_data["company_slug"],
                email=serializer.validated_data["email"],
                password=serializer.validated_data["password"],
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user = result["user"]
        company = result["company"]

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "email": user.email,
                },
                "company": {
                    "id": company.id,
                    "name": company.name,
                    "slug": company.slug,
                },
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        return Response(
            {"status": "logged_out"},
            status=status.HTTP_200_OK,
        )


class SessionView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    def get(self, request):
        user = request.user

        try:
            company_user = user.company_membership
        except Exception:
            return Response(
                {"authenticated": False},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        company = company_user.company

        if company.status != Company.STATUS_ACTIVE or not company.is_login_allowed:
            return Response(
                {"authenticated": False},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return Response(
            {
                "authenticated": True,
                "user_id": user.id,
                "email": user.email,
                "company_id": company.id,
                "company_slug": company.slug,
                "display_name": _get_display_name(user),
                "avatar_url": _get_avatar_url(user, request),
            },
            status=status.HTTP_200_OK,
        )


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            reset_password(
                email=serializer.validated_data["email"],
                new_password=serializer.validated_data.get(
                    "new_password", get_random_string(12)
                ),
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_403_FORBIDDEN,
            )

        return Response(
            {"status": "password_reset_success"},
            status=status.HTTP_200_OK,
        )
    
class CompanyBootstrapListView(APIView):
    """
    Bootstrap-only API.
    Purpose:
    - Allow user to select company context
    - No business decisions
    - No auth required
    """

    permission_classes = [AllowAny]

    def get(self, request):
        companies = Company.objects.all().order_by("name")
        serializer = CompanyPublicSerializer(companies, many=True)
        return Response(serializer.data)


class CompanyProjectsPublicView(APIView):
    """
    Public API for listing active projects of a company.
    Used by the browser extension to allow project selection before login.
    Returns minimal data only: id, name, element_capture_enabled.
    """

    permission_classes = [AllowAny]

    def get(self, request, slug):
        from apps.company_operations.models import Project

        company = get_object_or_404(Company, slug=slug)
        projects = Project.objects.filter(
            company=company,
            status=Project.STATUS_ACTIVE,
        ).order_by("name")

        return Response([
            {
                "id": p.id,
                "name": p.name,
                "element_capture_enabled": p.element_capture_enabled,
            }
            for p in projects
        ])


# ---------------------------------------------------------------------------
# Helpers for profile data
# ---------------------------------------------------------------------------

def _get_display_name(user):
    try:
        name = user.profile.display_name
        return name if name else user.email
    except Exception:
        return user.email


def _get_avatar_url(user, request=None):
    try:
        return user.profile.avatar_url(request)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Profile views
# ---------------------------------------------------------------------------

class UserProfileView(APIView):
    """
    GET  /auth/profile/  — returns current user profile
    PATCH /auth/profile/ — updates display_name
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "email": user.email,
            "display_name": _get_display_name(user),
            "avatar_url": _get_avatar_url(user, request),
        })

    def patch(self, request):
        from .models import UserProfile
        user = request.user
        profile, _ = UserProfile.objects.get_or_create(user=user)
        display_name = request.data.get("display_name", "").strip()
        profile.display_name = display_name
        profile.save(update_fields=["display_name", "updated_at"])
        return Response({
            "display_name": _get_display_name(user),
            "avatar_url": _get_avatar_url(user, request),
        })


class AvatarUploadView(APIView):
    """
    POST   /auth/profile/avatar/ — uploads avatar image (multipart/form-data)
    DELETE /auth/profile/avatar/ — removes avatar
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from .models import UserProfile
        user = request.user
        avatar_file = request.FILES.get("avatar")
        if not avatar_file:
            return Response({"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)

        allowed = ["image/jpeg", "image/png", "image/webp", "image/gif"]
        if avatar_file.content_type not in allowed:
            return Response({"error": "Unsupported file type."}, status=status.HTTP_400_BAD_REQUEST)

        profile, _ = UserProfile.objects.get_or_create(user=user)
        if profile.avatar:
            profile.avatar.delete(save=False)
        profile.avatar = avatar_file
        profile.save(update_fields=["avatar", "updated_at"])
        return Response({
            "avatar_url": _get_avatar_url(user, request),
        })

    def delete(self, request):
        from .models import UserProfile
        user = request.user
        try:
            profile = user.profile
            if profile.avatar:
                profile.avatar.delete(save=False)
                profile.avatar = None
                profile.save(update_fields=["avatar", "updated_at"])
        except Exception:
            pass
        return Response({"avatar_url": None})
