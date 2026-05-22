from enum import StrEnum


class PermissionEnum(StrEnum):
    USERS_READ = 'users_read'
    USERS_CREATE = 'users_create'
    USERS_UPDATE = 'users_update'
    USERS_DELETE = 'users_delete'

    INVOICES_READ = 'invoices_read'
    INVOICES_EXTRACT = 'invoices_extract'

    INVOICE_ITEMS_READ = 'invoice_items_read'

    ROLES_READ = 'roles_read'
    ROLES_CREATE = 'roles_create'
    ROLES_UPDATE = 'roles_update'
    ROLES_DELETE = 'roles_delete'
    ROLES_ASSIGN = 'roles_assign'
