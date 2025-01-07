from rest_framework import permissions
from ..constants import Actions

class AbacPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
            
        # Always allow listing
        if view.action == 'list':
            return True
            
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user
        
        if user.is_superuser:
            return True

        action_map = {
            'retrieve': Actions.GET,
            'update': Actions.EDIT,
            'partial_update': Actions.EDIT,
            'destroy': Actions.DELETE,
            'create': Actions.CREATE
        }
        
        required_action = action_map.get(view.action)
        if not required_action:
            return False
            
        return obj.can_perform(user, required_action)