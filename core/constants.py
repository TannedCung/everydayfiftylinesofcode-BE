from enum import Enum

class Roles(str, Enum):
    OWNER = 'OWNER'
    ADMIN = 'ADMIN' 
    MEMBER = 'MEMBER'

class Actions(str, Enum):
    DELETE = 'DELETE'
    GET = 'GET'
    EDIT = 'EDIT'
    CREATE = 'CREATE'
    MANAGE_ROLES = 'MANAGE_ROLES'
    MANAGE_MEMBERS = 'MANAGE_MEMBERS'  # Add this new action

ROLE_PERMISSIONS = {
    Roles.OWNER: [Actions.DELETE, Actions.GET, Actions.EDIT, Actions.CREATE, Actions.MANAGE_ROLES, Actions.MANAGE_MEMBERS],
    Roles.ADMIN: [Actions.GET, Actions.EDIT, Actions.CREATE, Actions.MANAGE_MEMBERS],
    Roles.MEMBER: [Actions.GET]
}