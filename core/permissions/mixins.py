from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from ..models.access_control import Role
from ..constants import Actions, Roles, ROLE_PERMISSIONS

class ResourceMixin(models.Model):
    roles = GenericRelation(Role)
    created_by = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def assign_role(self, user, role_name):
        role = Role.objects.create(
            user=user,
            role=role_name,
            content_object=self
        )
        
        # Create permissions for role
        for action in ROLE_PERMISSIONS[role_name]:
            role.permissions.create(action=action)
            
        return role
    
    def assign_role_if_allowed(self, assigner, user, role_name):
        """Assign role if assigner has permission"""
        if self.can_perform(assigner, Actions.MANAGE_ROLES):
            return self.assign_role(user, role_name)
        return None

    def remove_role_if_allowed(self, assigner, user):
        """Remove role if assigner has permission"""
        if self.can_perform(assigner, Actions.MANAGE_ROLES):
            return self.roles.filter(user=user).delete()
        return None

    def get_user_roles(self, user):
        return self.roles.filter(user=user)

    def can_perform(self, user, action):
        return self.roles.filter(
            user=user,
            permissions__action=action
        ).exists()