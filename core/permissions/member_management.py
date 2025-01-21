from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from ..constants import Actions

class MemberManagementMixin:
    @action(detail=True, methods=['post'], url_path='add_member')
    def add_member(self, request, pk=None):
        obj = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response({'error': 'user_id is required'}, status=400)
            
        if not obj.can_perform(request.user, Actions.MANAGE_MEMBERS):
            return Response({'error': 'not authorized to manage members'}, status=403)
            
        user = get_object_or_404(User, id=user_id)
        obj.members.add(user)
        obj.assign_role(user, 'MEMBER')
        
        return Response({'status': 'member added'})
    
    @action(detail=True, methods=['post'], url_path='remove_member')
    def remove_member(self, request, pk=None):
        obj = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response({'error': 'user_id is required'}, status=400)
            
        if not obj.can_perform(request.user, Actions.MANAGE_MEMBERS):
            return Response({'error': 'not authorized to manage members'}, status=403)
            
        user = get_object_or_404(User, id=user_id)
        
        # Don't allow removing the owner
        owner_role = obj.roles.filter(user=user, role='OWNER').exists()
        if owner_role:
            return Response({'error': 'cannot remove owner'}, status=400)
            
        obj.members.remove(user)
        obj.roles.filter(user=user).delete()
        
        return Response({'status': 'member removed'})

    @action(detail=True, methods=['post'], url_path='join')
    def join_challenge(self, request, pk=None):
        obj = self.get_object()
        user = request.user
        
        if obj.members.filter(id=user.id).exists():
            return Response({'error': 'already a member'}, status=400)
            
        obj.members.add(user)
        obj.assign_role(user, 'MEMBER')
        
        return Response({'status': 'joined challenge'})
    
    @action(detail=True, methods=['post'], url_path='leave')  
    def leave_challenge(self, request, pk=None):
        obj = self.get_object()
        user = request.user

        if not obj.members.filter(id=user.id).exists():
            return Response({'error': 'not a member'}, status=400)
            
        owner_role = obj.roles.filter(user=user, role='OWNER').exists()
        if owner_role:
            return Response({'error': 'owner cannot leave challenge'}, status=400)
            
        obj.members.remove(user)
        obj.roles.filter(user=user).delete()
        
        return Response({'status': 'left challenge'})