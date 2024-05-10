from guardian.shortcuts import assign_perm
from django.contrib.auth.models import Permission
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from api.models import Event
from users.models import User
from typing import Optional
from django.db.models import QuerySet


class AddPermissions():

    def assign_permissions(self, user: User, group: Group, event: Event) -> Optional[QuerySet[Permission]]:
        """ Atribui permissões ao usuário em nível de objeto de acordo com o grupo fornecido.
        Args:
            user (User): Usuário ao qual as permissões serão atribuídas
            group (Group): Grupo do usuário
            event (Event): Evento ao qual as permissões serão atribuídas
        """
        permissions = self.add_permissions(group)
        for permission in permissions:
            assign_perm(permission, user, event)
        return group

    def add_permissions(self, group: Group):
        content_type = self.get_content_type(Event)
        permissions = self.get_permissions(content_type)

        group_permissions = {
            "event_admin": permissions.filter(Q(codename__icontains='change') | Q(codename__icontains='delete') | Q(codename__icontains='view') | Q(codename__icontains='add')).exclude(codename__icontains='add_event'),
            "staff_manager": permissions.filter(Q(codename__icontains='view_event') | Q(codename__icontains='sumula') | Q(codename__icontains='player')).exclude(codename__icontains='player_delete'),
            "staff_member": permissions.filter(Q(codename__icontains='view') | Q(codename__icontains='change')).exclude(codename__icontains='add'),
            "player": permissions.filter(Q(codename__icontains='view')).exclude(codename__icontains='add'),
        }
        if group.name in group_permissions:
            return group_permissions[group.name]

    def get_content_type(self, model):
        return ContentType.objects.get_for_model(model)

    def get_permissions(self, content_type):
        return Permission.objects.filter(content_type=content_type)
