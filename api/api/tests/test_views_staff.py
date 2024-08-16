import uuid
from api.models import Token, Event, Staff
from users.models import User
from ..serializers import StaffSerializer
from ..permissions import assign_permissions
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from django.db.models import Q
from django.core.files.uploadedfile import SimpleUploadedFile
from decouple import config
from guardian.shortcuts import get_perms, remove_perm


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
        self.user_staff3 = User.objects.create(
            username=self.create_unique_username(), email=self.create_unique_email(), first_name='Staff3', last_name='Member3')
        self.admin = User.objects.create(
            username=self.create_unique_username(), email=self.create_unique_email(), first_name='Admin', last_name='User')

    def setUpEvent(self):
        self.token = Token.objects.create()
        self.event = Event.objects.create(name='Evento 1', token=self.token)
        self.token2 = Token.objects.create()
        self.event2 = Event.objects.create(name='Evento 2', token=self.token2)

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
            user=self.user_staff1, event=self.event, registration_email=self.user_staff1.email, full_name='Staff1')
        self.staff2 = Staff.objects.create(
            user=self.user_staff2, event=self.event, registration_email=self.user_staff2.email, full_name='Staff2')
        self.staff3 = Staff.objects.create(
            user=self.user_staff3, event=self.event2, registration_email=self.user_staff1.email, full_name='Staff1')

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
        data = {'join_token': self.event.join_token, }
        self.client.force_authenticate(user=self.user_staff1)
        self.staff1.user = None
        self.staff1.save()
        response = self.client.post(url, data, format='json')
        self.staff1.refresh_from_db()
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
        data = {'join_token': 'invalid_token'}
        self.client.force_authenticate(user=self.user_staff1)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_staff_member_with_unauthenticated_user(self):
        """Test adding a staff member without authentication."""
        url = reverse('api:staff')
        data = {'join_token': self.event.join_token}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_add_staff_member_with_another_staff_from_other_event(self):
        """Test adding a staff member with another user."""
        url = reverse('api:staff')
        data = {'join_token': self.event.join_token}
        # User different from the one in the data
        self.client.force_authenticate(user=self.user_staff3)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.user_staff1.events.count(), 0)

    def test_get_staff_members(self):
        """Test getting staff members from an event."""
        self.user_staff1.events.add(self.event)
        self.user_staff2.events.add(self.event)
        url = f'{reverse("api:staff")}?event_id={self.event.id}'
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, self.response_data_total)

    def test_get_staff_members_with_managers(self):
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
        self.assertEqual(response.data[1]['is_manager'], True)

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
        ), first_name='USer Staff', last_name='Member do teste')
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
        self.data = {'email': self.staff.registration_email}
        self.url = f'{reverse("api:staff-manager")}?event_id={self.event.id}'

    def test_add_staff_manager(self):
        """Test adding a staff manager to an event."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
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


class AddStaffMembersTestCase(APITestCase):

    def setUpFiles(self):
        self.xlsx_path = config("XLSX_FILE_PATH")
        self.csv_path = config("CSV_FILE_PATH")

        # Setup Excel file
        self.excel_file = open(self.xlsx_path, 'rb')
        self.excel_content = self.excel_file.read()
        self.excel_uploaded_file = SimpleUploadedFile(
            "Exemplo.xlsx", self.excel_content, content_type="multipart/form-data")
        # Setup CSV file
        self.csv_file = open(self.csv_path, 'r')
        self.csv_content = self.csv_file.read()
        self.csv_uploaded_file = SimpleUploadedFile(
            "Exemplo.csv", self.csv_content.encode('utf-8'), content_type="multipart/form-data")

    def setUpEvent(self):
        self.token = Token.objects.create()
        self.event = Event.objects.create(name='Evento 1', token=self.token)

    def setUpGroup(self):
        self.group3 = Group.objects.create(name='app_admin')
        self.group4 = Group.objects.create(name='event_admin')
        self.user.groups.add(self.group4)

    def setUpPermissions(self):
        self.content_type = ContentType.objects.get_for_model(Event)
        assign_permissions(self.user, self.group4, self.event)

    def setUp(self):
        self.user = User.objects.create_user(
            username='admin', email='admin@email.com')
        self.setUpEvent()
        self.setUpFiles()
        self.setUpGroup()
        self.setUpPermissions()
        self.url = f"{reverse('api:upload-staff')}?event_id={self.event.id}"

        self.client.force_authenticate(user=self.user)

    def test_add_staff_members_with_valid_data_xlsx(self):

        data = {'event_id': self.event.id, 'file': self.excel_uploaded_file}
        response = self.client.post(self.url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data, 'Monitores adicionados com sucesso!'
        )
        self.assertIsNotNone(Staff.objects.filter(event=self.event))

    def test_add_staff_members_with_valid_data_csv(self):

        data = {'event_id': self.event.id, 'file': self.csv_uploaded_file}
        response = self.client.post(self.url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data, 'Monitores adicionados com sucesso!'
        )
        self.assertIsNotNone(Staff.objects.filter(event=self.event))

    def test_add_staff_members_with_invalid_event_id(self):
        url = f'{reverse("api:upload-staff")}?event_id=99999'
        data = {'event_id': 999, 'file': self.excel_uploaded_file}
        response = self.client.post(url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_staff_members_with_missing_event_id(self):
        url = f'{reverse("api:upload-staff")}'
        data = {'file': self.excel_uploaded_file}
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_staff_members_with_invalid_file(self):
        url = f'{reverse("api:upload-staff")}?event_id={self.event.id}'
        data = {'event_id': self.event.id, 'file': 'invalid_file'}
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_staff_members_without_permission(self):
        self.remove_permissions()
        data = {'event_id': self.event.id, 'file': self.excel_uploaded_file}
        response = self.client.post(self.url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def remove_permissions(self):
        perm = get_perms(self.user, self.event)
        for p in perm:
            remove_perm(p, self.user, self.event)

    def tearDown(self):
        self.client.logout()
        Event.objects.all().delete()
        User.objects.all().delete()
        self.excel_file.close()
        self.csv_file.close()
        Token.objects.all().delete()


class AddSingleStaffTestCase(APITestCase):

    def create_unique_email(self):
        return f'{uuid.uuid4()}@gmail.com'

    def create_unique_username(self):
        return f'user_{uuid.uuid4().hex[:10]}'

    def setUpUser(self):
        self.admin = User.objects.create(
            username=self.create_unique_username(), email=self.create_unique_email(), first_name='User', last_name='Zero')
        self.user_not_admin = User.objects.create(username=self.create_unique_username(
        ), email=self.create_unique_email(), first_name='User', last_name='One')

    def setUpEvent(self):
        self.token = Token.objects.create()
        self.event = Event.objects.create(name='Evento 1', token=self.token)

    def setUpGroup(self):
        self.group_admin = Group.objects.create(name='event_admin')

    def setUpPermissions(self):
        assign_permissions(self.admin, self.group_admin, self.event)

    def setUp(self):
        self.setUpUser()
        self.setUpEvent()
        self.setUpGroup()
        self.setUpPermissions()
        self.url = f'{reverse("api:add-staff")}?event_id={self.event.id}'
        self.data = {
            "full_name": "João Da Silva",
            "registration_email": "joao@email.com",
            "is_manager": False
        }
        self.client = APIClient()

    def test_add_staff_member_valid_data(self):
        Staff.objects.all().delete()
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        staff = Staff.objects.get(event=self.event)
        self.assertEqual(staff.full_name, self.data['full_name'])
        self.assertEqual(staff.registration_email,
                         self.data['registration_email'])
        self.assertEqual(staff.is_manager, self.data['is_manager'])

    def test_add_staff_manager_valid_data(self):
        self.data['is_manager'] = True
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        staff = Staff.objects.get(event=self.event)
        self.assertEqual(staff.is_manager, True)

    def test_add_staff_member_invalid_data(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_staff_member_without_permission(self):
        self.client.force_authenticate(user=self.user_not_admin)
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_add_staff_member_without_event_id(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            reverse('api:add-staff'), self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_staff_member_with_invalid_event_id(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            f'{reverse("api:add-staff")}?event_id=99999', self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class EditStaffDataTestCase(APITestCase):
    def create_unique_email(self):
        return f'{uuid.uuid4()}@gmail.com'

    def create_unique_username(self):
        return f'user_{uuid.uuid4().hex[:10]}'

    def setUpUser(self):
        self.admin = User.objects.create(
            username=self.create_unique_username(), email=self.create_unique_email(), first_name='User', last_name='Zero')
        self.user_not_admin = User.objects.create(username=self.create_unique_username(
        ), email=self.create_unique_email(), first_name='User', last_name='One')

    def setUpEvent(self):
        self.token = Token.objects.create()
        self.event = Event.objects.create(name='Evento 1', token=self.token)

    def setUpGroup(self):
        self.group_admin = Group.objects.create(name='event_admin')

    def setUpPermissions(self):
        assign_permissions(self.admin, self.group_admin, self.event)

    def setUpStaff(self):
        self.staff = Staff.objects.create(
            user=self.admin, event=self.event, registration_email=self.admin.email, full_name=self.admin.get_full_name())

    def setUp(self):
        self.setUpUser()
        self.setUpEvent()
        self.setUpGroup()
        self.setUpStaff()
        self.setUpPermissions()
        self.url = f'{reverse("api:staff")}?event_id={self.event.id}'
        self.data = {
            'id': self.staff.id,
            "full_name": "João Da Silva",
            "is_manager": False,
            "new_email": "novo@email.com"
        }
        self.client = APIClient()

    def test_edit_staff_data_valid_request(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.put(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        staff = Staff.objects.get(event=self.event)
        self.assertEqual(staff.full_name, self.data['full_name'])
        self.assertEqual(staff.registration_email,
                         self.data['new_email'])
        self.assertEqual(staff.is_manager, self.data['is_manager'])

    def test_edit_staff_data_invalid_request(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.put(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_edit_staff_unauthenticated_user(self):
        response = self.client.put(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
