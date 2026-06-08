from django.test import TestCase
from django.urls import reverse

from .models import Task


class TaskModelTests(TestCase):
    def test_task_string_representation_uses_title(self):
        task = Task.objects.create(title="Ship portfolio app")

        self.assertEqual(str(task), "Ship portfolio app")


class TaskViewTests(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        User.objects.create_user(username="tester@example.com", password="Tester@12345")
        self.client.login(username="tester@example.com", password="Tester@12345")

    def test_task_list_displays_tasks(self):
        Task.objects.create(title="Write README", priority=Task.Priority.HIGH)

        response = self.client.get(reverse("tasks:list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Write README")

    def test_task_can_be_created(self):
        response = self.client.post(
            reverse("tasks:create"),
            {"title": "Create demo", "priority": Task.Priority.MEDIUM},
        )

        self.assertRedirects(response, reverse("tasks:list"))
        self.assertTrue(Task.objects.filter(title="Create demo").exists())

    def test_task_can_be_toggled(self):
        task = Task.objects.create(title="Toggle me")

        response = self.client.post(reverse("tasks:toggle", args=[task.pk]))

        task.refresh_from_db()
        self.assertRedirects(response, reverse("tasks:list"))
        self.assertTrue(task.completed)

    def test_task_list_can_filter_active_tasks(self):
        Task.objects.create(title="Active task")
        Task.objects.create(title="Finished task", completed=True)

        response = self.client.get(reverse("tasks:list"), {"status": "active"})

        self.assertContains(response, "Active task")
        self.assertNotContains(response, "Finished task")

    def test_anonymous_user_is_redirected_to_login(self):
        self.client.logout()

        response = self.client.get(reverse("tasks:list"))

        self.assertRedirects(response, f"{reverse('login')}?next={reverse('tasks:list')}")


class AuthViewTests(TestCase):
    def test_login_page_loads(self):
        response = self.client.get(reverse("login"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Login to manage your tasks.")
        self.assertContains(response, "Create an account")

    def test_signup_page_loads(self):
        response = self.client.get(reverse("tasks:signup"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create your TaskFlow account.")

    def test_signup_creates_and_logs_in_user(self):
        from django.contrib.auth import get_user_model

        response = self.client.post(
            reverse("tasks:signup"),
            {
                "username": "newuser@example.com",
                "password1": "ComplexPass987!",
                "password2": "ComplexPass987!",
            },
        )

        self.assertRedirects(response, reverse("tasks:list"))
        user = get_user_model().objects.get(username="newuser@example.com")
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.pk)
