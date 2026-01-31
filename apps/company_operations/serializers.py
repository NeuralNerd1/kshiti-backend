from rest_framework import serializers
from .models import Role, Project
from apps.company_auth.models import CompanyUser
from .permissions import ALL_PERMISSION_KEYS


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = "__all__"

    def validate_permissions_json(self, value):
        invalid = set(value.keys()) - ALL_PERMISSION_KEYS
        if invalid:
            raise serializers.ValidationError(
                f"Invalid permission keys: {', '.join(invalid)}"
            )
        return value

    def validate(self, data):
        if self.instance and self.instance.is_system_role:
            raise serializers.ValidationError(
                "System roles cannot be modified."
            )
        return data


class CompanyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyUser
        fields = "__all__"

    def validate(self, data):
        role = data.get("role")
        company = data.get("company")

        if role.company and role.company != company:
            raise serializers.ValidationError(
                "Role does not belong to this company."
            )
        return data


class ProjectSerializer(serializers.ModelSerializer):
    project_admin = serializers.PrimaryKeyRelatedField(
        queryset=CompanyUser.objects.all()
    )

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "description",
            "max_team_members",
            "project_admin",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "status", "created_at"]

    def validate_project_admin(self, value):
        """
        Ensure project admin belongs to the same company.
        Company is injected from the view via serializer context.
        """
        company = self.context.get("company")
        if not company:
            raise serializers.ValidationError(
                "Company context is required."
              )  
        if value.company_id != company.id:
            raise serializers.ValidationError(
                "Project admin must belong to the same company."
            )
        return value
