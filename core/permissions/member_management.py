from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.db import models
import datetime
from rest_framework.pagination import PageNumberPagination

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
    
    @action(detail=True, methods=['get'], url_path='member-stats')
    def get_member_stats(self, request, pk=None):
        """
        Get member statistics from the through model of members ManyToManyField
        """
        obj = self.get_object()
        through_model = obj.members.through
    
        try:
            stats = through_model.objects.get(
                **{
                    f'{obj._meta.model_name}_id': obj.id,
                    'user_id': request.user.id
                }
            )
            
            excluded_fields = ['id', 'user_id', f'{obj._meta.model_name}_id']
            stats_data = {}
            
            for field in stats._meta.fields:
                if field.name not in excluded_fields:
                    value = getattr(stats, field.name)
                    # Handle model instances
                    if isinstance(value, models.Model):
                        stats_data[field.name] = value.id
                    # Handle date/datetime
                    elif isinstance(value, (datetime.date, datetime.datetime)):
                        stats_data[field.name] = value.isoformat()
                    else:
                        stats_data[field.name] = value
            
            return Response(stats_data)
            
        except through_model.DoesNotExist:
            return Response(
                {'error': 'You are not a member of this object'},
                status=404
            )
        
    @action(detail=False, methods=['get'], url_path='my-participated')
    def get_participated_resources(self, request):
        """Get all resources where user is a member with relationship details"""
        through_model = self.get_queryset().model.members.through
        page_size = request.query_params.get('page_size', 10)
        
        # Get all relationships for this user
        relationships = through_model.objects.filter(
            user_id=request.user.id
        ).select_related('user')
        
        # Apply pagination
        paginator = PageNumberPagination()
        paginator.page_size = page_size
        page = paginator.paginate_queryset(relationships, request)
        
        # Process member details
        resources_data = []
        for rel in page:
            # Get relationship stats
            stats = {}
            excluded_fields = ['id', 'user_id', f'{self.get_queryset().model._meta.model_name}_id']
            
            for field in rel._meta.fields:
                if field.name not in excluded_fields:
                    value = getattr(rel, field.name)
                    if isinstance(value, models.Model):
                        stats[field.name] = str(value.id)
                    elif isinstance(value, (datetime.date, datetime.datetime)):
                        stats[field.name] = value.isoformat()
                    else:
                        stats[field.name] = value
            
            resources_data.append({
                'stats': stats
            })
        
        return paginator.get_paginated_response(resources_data)