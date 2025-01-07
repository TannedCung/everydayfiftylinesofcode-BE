from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from core.permissions.abac import AbacPermission
from core.serializers.role import RoleAssignmentSerializer


class AbacViewSetMixin:
    permission_classes = [AbacPermission]
    
    def perform_create(self, serializer):
        obj = serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def assign_role(self, request, pk=None):
        obj = self.get_object()
        serializer = RoleAssignmentSerializer(data=request.data)
        
        if serializer.is_valid():
            role = obj.assign_role_if_allowed(
                assigner=request.user,
                user=serializer.validated_data['user'],
                role_name=serializer.validated_data['role']
            )
            
            if role:
                return Response({'status': 'role assigned'})
            return Response(
                {'error': 'not authorized to assign roles'}, 
                status=403
            )
            
        return Response(serializer.errors, status=400)

    @action(detail=True, methods=['post'])
    def remove_role(self, request, pk=None):
        obj = self.get_object()
        serializer = RoleAssignmentSerializer(data=request.data)
        
        if serializer.is_valid():
            if obj.remove_role_if_allowed(
                assigner=request.user,
                user=serializer.validated_data['user']
            ):
                return Response({'status': 'role removed'})
            return Response(
                {'error': 'not authorized to remove roles'},
                status=403
            )
            
        return Response(serializer.errors, status=400)