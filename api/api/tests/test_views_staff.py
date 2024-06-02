import uuid
from api.models import Token, Event, Staff
from users.models import User
from ..serializers import StaffSerializer
from ..permissions import assign_permissions
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from django.db.models import Q


class StaffViewTest(APITestCase):
    def create_unique_email(self):
        return f'{uuid.uuid4()}@gmail.com'

    def create_unique_username(self):
        return f'user_{uuid.uuid4().hex[:10]}'

    def setUpResponseData(self):
        self.response_data_total = StaffSerializer(
            [self.staff1, self.staff2], many=True).data
        self.response_data_staff1 = StaffSerializer(
            [self.staff1], many=True).data

    def setUpUser(self):
        self.user_staff1 = User.objects.create(
            username=self.create_unique_username(), email=self.create_unique_email(), first_name='Staff1', last_name='Member1')
        self.user_staff2 = User.objects.create(
            username=self.create_unique_username(), email=self.create_unique_email(), first_name='Staff2', last_name='Member2')
        self.admin = User.objects.create(
            username=self.create_unique_username(), email=self.create_unique_email(), first_name='Admin', last_name='User')

    def setUpEvent(self):
        self.token = Token.objects.create()
        self.event = Event.objects.create(name='Evento 1', token=self.token)

    def setUpGroup(self):
        self.group = Group.objects.create(name='staff_member')
        self.group2 = Group.objects.create(name='staff_manager')
        self.group3 = Group.objects.create(name='app_admin')
        self.group4 = Group.objects.create(name='event_admin')
        self.user_staff1.groups.add(self.group)
        self.user_staff2.groups.add(self.group)
        self.admin.groups.add(self.group4)

    def setUpPermissions(self):
        self.content_type = ContentType.objects.get_for_model(Event)
        self.permission = Permission.objects.filter(
            content_type=self.content_type).filter(Q(codename__icontains='view') | Q(codename__icontains='change')).exclude(codename__icontains='change_event')
        assign_permissions(self.admin, self.group4, self.event)

    def setUpStaff(self):
        self.staff1 = Staff.objects.create(
            user=self.user_staff1, event=self.event, registration_email='example@email.com', full_name='Staff1')
        self.staff2 = Staff.objects.create(
            user=self.user_staff2, event=self.event, registration_email='example2@email.com', full_name='Staff2')

    def setUp(self):
        self.setUpEvent()
        self.setUpUser()
        self.setUpGroup()
        self.setUpPermissions()
        self.setUpStaff()
        self.setUpResponseData()

    def test_add_staff_member(self):
        """Test adding a staff member to an event."""
        url = reverse('api:staff')
        data = {'token_code': self.token.token_code,
                'email': self.staff1.registration_email}
        self.client.force_authenticate(user=self.user_staff1)
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user_staff1.events.count(), 1)
        self.assertEqual(self.staff1.user, self.user_staff1)
        for permission in self.permission:
            self.assertTrue(self.user_staff1.has_perm(
                permission.codename, self.event))

    def test_add_staff_member_without_token(self):
        """Test adding a staff member without a token."""
        url = reverse('api:staff')
        self.client.force_authenticate(user=self.user_staff1)
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_staff_member_with_invalid_token(self):
        """Test adding a staff member with an invalid token."""
        url = reverse('api:staff')
        data = {'token_code': 'invalid_token'}
        self.client.force_authenticate(user=self.user_staff1)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_staff_member_with_unauthenticated_user(self):
        """Test adding a staff member without authentication."""
        url = reverse('api:staff')
        data = {'token_code': self.token.token_code}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_add_staff_member_with_another_user(self):
        """Test adding a staff member with another user."""
        url = reverse('api:staff')
        data = {'token_code': self.token.token_code,
                'email': self.staff1.registration_email}
        # User different from the one in the data
        self.client.force_authenticate(user=self.user_staff2)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.user_staff1.events.count(), 0)

    def test_add_staff_member_with_invalid_email(self):
        """Test adding a staff member with an invalid email."""
        url = reverse('api:staff')
        data = {'token_code': self.token.token_code, 'email': 'invalid_email'}
        self.client.force_authenticate(user=self.user_staff1)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_staff_member_without_email(self):
        """Test adding a staff member without an email."""
        url = reverse('api:staff')
        data = {'token_code': self.token.token_code}
        self.client.force_authenticate(user=self.user_staff1)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_staff_member_without_token_and_email(self):
        """Test adding a staff member without a token and email."""
        url = reverse('api:staff')
        self.client.force_authenticate(user=self.user_staff1)
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_staff_member_with_invalid_token_and_valid_email(self):
        """Test adding a staff member with an invalid token and email."""
        url = reverse('api:staff')
        data = {'token_code': 'invalid_token',
                'email': self.staff1.registration_email}
        self.client.force_authenticate(user=self.user_staff1)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_staff_members(self):
        """Test getting staff members from an event."""
        self.user_staff1.events.add(self.event)
        self.user_staff2.events.add(self.event)
        url = f'{reverse("api:staff")}?event_id={self.event.id}'
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, self.response_data_total)

    def test_get_staff_members_exlcuding_other_groups(self):
        """Test getting staff members from an event excluding other groups."""
        self.user_staff1.events.add(self.event)
        self.user_staff2.events.add(self.event)
        # self.user_staff2.groups.add(self.group2, self.group3, self.group4)
        self.staff2.is_manager = True
        self.staff2.save()
        url = f'{reverse("api:staff")}?event_id={self.event.id}'
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data, self.response_data_total)
        self.assertNotIn(self.user_staff2, response.data)
        self.assertEqual(response.data, self.response_data_staff1)

    def test_get_staff_members_without_event_id(self):
        """Test getting staff members without an event id."""
        url = reverse('api:staff')
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_staff_members_with_unauthenticated_user(self):
        """Test getting staff members without authentication."""
        url = f'{reverse("api:staff")}?event_id={self.event.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_staff_members_with_unauthorized_user(self):
        """Test getting staff members with an unauthorized user."""
        url = f'{reverse("api:staff")}?event_id={self.event.id}'
        self.client.force_authenticate(user=self.user_staff1)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def tearDown(self):
        User.objects.all().delete()
        Event.objects.all().delete()
        Group.objects.all().delete()
        Permission.objects.all().delete()
        Staff.objects.all().delete()
        self.client.logout()
        self.client.force_authenticate(user=None)
        if Token.objects.exists():
            Token.objects.all().delete()


class AddStaffManagerTestCase(APITestCase):
    def create_unique_email(self):
        return f'{uuid.uuid4()}@gmail.com'

    def create_unique_username(self):
        return f'user_{uuid.uuid4().hex[:10]}'

    def setUpUser(self):
        self.user = User.objects.create(username='staff_member', email=self.create_unique_email(
        ), first_name='Staff', last_name='Member')
        self.admin = User.objects.create(username='event_admin', email=self.create_unique_email(
        ), first_name='Event', last_name='Admin')

    def setUpEvent(self):
        self.token = Token.objects.create()
        self.event = Event.objects.create(name='Evento 1', token=self.token)

    def setUpGroup(self):
        self.group = Group.objects.create(name='staff_member')
        self.group2 = Group.objects.create(name='staff_manager')
        self.group3 = Group.objects.create(name='app_admin')
        self.group4 = Group.objects.create(name='event_admin')
        self.admin.groups.add(self.group4)

    def setUpPermissions(self):
        self.content_type = ContentType.objects.get_for_model(Event)
        self.permission = Permission.objects.filter(
            content_type=self.content_type).filter(Q(codename__icontains='view') | Q(codename__icontains='change')).exclude(codename__icontains='change_event')
        assign_permissions(self.admin, self.group4, self.event)

    def setUpStaffMember(self):
        self.staff = Staff.objects.create(
            user=self.user, event=self.event, registration_email='example@email.com', full_name=self.user.get_full_name())

    def setUp(self):
        self.setUpUser()
        self.setUpEvent()
        self.setUpGroup()
        self.setUpPermissions()
        self.setUpStaffMember()
        self.data = {'id': self.user.id, 'email': self.user.email}
        self.url = f'{reverse("api:staff-manager")}?event_id={self.event.id}'

    def test_add_staff_manager(self):
        """Test adding a staff manager to an event."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.groups.filter(name='staff_manager').exists())
        self.staff.refresh_from_db()
        self.assertEqual(self.staff.is_manager, True)
        for permission in self.permission:
            self.assertTrue(self.user.has_perm(
                permission.codename, self.event))

    def test_add_staff_manager_without_event_id(self):
        """Test adding a staff manager without an event id."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            reverse('api:staff-manager'), self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_staff_manager_without_staff_object(self):
        self.staff.delete()
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_staff_manager_with_unauthenticated_user(self):
        """Test adding a staff manager without authentication."""
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_add_staff_manager_with_unauthorized_user(self):
        """Test adding a staff manager with an unauthorized user."""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_add_staff_manager_with_invalid_event_id(self):
        """Test adding a staff manager with an invalid event id."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            f'{reverse("api:staff-manager")}?event_id=invalid_id', self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def tearDown(self):
        User.objects.all().delete()
        Event.objects.all().delete()
        Group.objects.all().delete()
        Permission.objects.all().delete()
        User.objects.all().delete()
        Event.objects.all().delete()
        Group.objects.all().delete()
        Permission.objects.all().delete()
        self.client.logout()
        self.client.force_authenticate(user=None)
        if Token.objects.exists():
            Token.objects.all().delete()

class AddStaffMembersViewTest(APITestCase):
    
