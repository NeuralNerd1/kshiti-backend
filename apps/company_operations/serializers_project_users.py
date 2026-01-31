from rest_framework import serializers
from apps.company_operations.models import ProjectUser, ProjectRole
from apps.company_auth.models import CompanyUser


class ProjectUserCreateSerializer(serializers.Serializer):
    company_user_id = serializers.IntegerField()
    role_id = serializers.IntegerField()

    def validate(self, data):
        project = self.context["project"]

        # Validate company user belongs to same company
        try:
            cu = CompanyUser.objects.get(
                id=data["company_user_id"],
                company=project.company,
            )
        except CompanyUser.DoesNotExist:
            raise serializers.ValidationError(
                "User does not belong to this company."
            )

        # Validate role belongs to this project
        try:
            role = ProjectRole.objects.get(
                id=data["role_id"],
                project=project,
            )
        except ProjectRole.DoesNotExist:
            raise serializers.ValidationError(
                "Invalid project role."
            )

        data["company_user"] = cu
        data["role"] = role
        return data


class ProjectUserUpdateSerializer(serializers.Serializer):
    role_id = serializers.IntegerField()

    def validate(self, data):
        project = self.context["project"]

        try:
            role = ProjectRole.objects.get(
                id=data["role_id"],
                project=project,
            )
        except ProjectRole.DoesNotExist:
            raise serializers.ValidationError(
                "Invalid project role."
            )

        data["role"] = role
        return data
