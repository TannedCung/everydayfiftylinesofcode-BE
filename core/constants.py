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

ROLE_PERMISSIONS = {
    Roles.OWNER: [Actions.DELETE, Actions.GET, Actions.EDIT, Actions.CREATE, Actions.MANAGE_ROLES],
    Roles.ADMIN: [Actions.GET, Actions.EDIT, Actions.CREATE],
    Roles.MEMBER: [Actions.GET]
}