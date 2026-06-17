"""
End-to-end UI automation tests using pytest + Playwright.
Tests user registration, login, task creation, logout, and multi-user task isolation.

Run tests with:
    pytest tests/test_e2e_automation.py -v
    pytest tests/test_e2e_automation.py::test_full_workflow_single_user -v
    pytest tests/test_e2e_automation.py -k "isolation" -v
"""

import pytest
from datetime import datetime
from playwright.sync_api import Page, expect


BASE_URL = "http://127.0.0.1:8000"


class TestUserAuthentication:
    """Tests for user signup and login."""

    @pytest.mark.e2e
    @pytest.mark.auth
    def test_signup_new_user(self, page: Page):
        """Test user signup flow."""
        unique_id = datetime.now().strftime("%Y%m%d%H%M%S")
        username = f"testuser_{unique_id}"
        password = "TestPassword123!"
        
        # Navigate to signup page
        page.goto(f"{BASE_URL}/signup/", wait_until="networkidle")
        
        # Fill in signup form
        page.fill('input[name="username"]', username)
        page.fill('input[name="password1"]', password)
        page.fill('input[name="password2"]', password)
        
        # Submit form
        page.click('button[type="submit"]')
        
        # Should redirect to tasks page
        page.wait_for_url(f"{BASE_URL}/", wait_until="networkidle")
        assert BASE_URL in page.url
        
        print(f"✓ User {username} signed up successfully")

    @pytest.mark.e2e
    @pytest.mark.auth
    def test_login_existing_user(self, page: Page):
        """Test login with existing user."""
        username = "admin_temp"
        password = "TempPass123!"
        
        # Navigate to login
        page.goto(f"{BASE_URL}/login/", wait_until="networkidle")
        
        # Fill login form
        page.fill('input[name="username"]', username)
        page.fill('input[name="password"]', password)
        
        # Submit
        page.click('button[type="submit"]')
        
        # Should be on tasks page
        page.wait_for_url(f"{BASE_URL}/", wait_until="networkidle")
        assert BASE_URL in page.url
        print(f"✓ User {username} logged in successfully")


class TestTaskManagement:
    """Tests for task CRUD operations."""

    @pytest.mark.e2e
    @pytest.mark.tasks
    def test_create_task(self, page: Page):
        """Test creating a new task."""
        # Setup: Login first
        unique_id = datetime.now().strftime("%Y%m%d%H%M%S")
        username = f"taskuser_{unique_id}"
        password = "TestPassword123!"
        
        # Signup
        page.goto(f"{BASE_URL}/signup/", wait_until="networkidle")
        page.fill('input[name="username"]', username)
        page.fill('input[name="password1"]', password)
        page.fill('input[name="password2"]', password)
        page.click('button[type="submit"]')
        page.wait_for_url(f"{BASE_URL}/", wait_until="networkidle")
        
        # Create task
        page.click('a:has-text("Add your first task"), a:has-text("Add"), button:has-text("Add")')
        page.wait_for_selector('input[name="title"]')
        
        task_title = f"Test Task {unique_id}"
        task_description = "This is a test task"
        
        page.fill('input[name="title"]', task_title)
        page.fill('textarea[name="description"]', task_description)
        page.click('button[type="submit"]')
        
        # Verify task appears on list
        page.wait_for_url(f"{BASE_URL}/", wait_until="networkidle")
        expect(page).to_contain_text(task_title)
        
        print(f"✓ Task created: {task_title}")

    @pytest.mark.e2e
    @pytest.mark.tasks
    def test_task_persistence_after_logout_login(self, page: Page):
        """
        Test that tasks persist after logout and login.
        - Create user and tasks
        - Logout
        - Login again
        - Verify tasks are still there
        """
        unique_id = datetime.now().strftime("%Y%m%d%H%M%S")
        username = f"persistuser_{unique_id}"
        password = "TestPassword123!"
        
        # Step 1: Signup
        page.goto(f"{BASE_URL}/signup/", wait_until="networkidle")
        page.fill('input[name="username"]', username)
        page.fill('input[name="password1"]', password)
        page.fill('input[name="password2"]', password)
        page.click('button[type="submit"]')
        page.wait_for_url(f"{BASE_URL}/", wait_until="networkidle")
        print(f"[1] User {username} signed up")
        
        # Step 2: Create tasks
        task_titles = [
            f"Persist Task 1 - {unique_id}",
            f"Persist Task 2 - {unique_id}",
            f"Persist Task 3 - {unique_id}"
        ]
        
        for task_title in task_titles:
            page.click('a:has-text("Add your first task"), a:has-text("Add"), button:has-text("Add")')
            page.wait_for_selector('input[name="title"]')
            page.fill('input[name="title"]', task_title)
            page.fill('textarea[name="description"]', f"Description for {task_title}")
            page.click('button[type="submit"]')
            page.wait_for_url(f"{BASE_URL}/", wait_until="networkidle")
        
        print(f"[2] Created {len(task_titles)} tasks")
        
        # Verify all tasks are visible
        for task_title in task_titles:
            expect(page).to_contain_text(task_title)
        print("[3] All tasks verified on first login")
        
        # Step 3: Logout
        page.click('a:has-text("Logout"), button:has-text("Logout")')
        page.wait_for_url(f"{BASE_URL}/login/", wait_until="networkidle")
        print("[4] User logged out")
        
        # Step 4: Login again
        page.fill('input[name="username"]', username)
        page.fill('input[name="password"]', password)
        page.click('button[type="submit"]')
        page.wait_for_url(f"{BASE_URL}/", wait_until="networkidle")
        print("[5] User logged back in")
        
        # Step 5: Verify tasks still exist
        for task_title in task_titles:
            expect(page).to_contain_text(task_title)
        print("[6] ✓ All tasks persisted after re-login")


class TestMultiUserIsolation:
    """Tests for multi-user security and task isolation."""

    @pytest.mark.e2e
    @pytest.mark.isolation
    def test_users_cannot_see_each_others_tasks(self, context):
        """
        Test that different users cannot see each other's tasks.
        - Create User1, add tasks, logout
        - Create User2 in new context, verify User1's tasks NOT visible
        - Login as User1, verify User2's tasks NOT visible
        """
        unique_id = datetime.now().strftime("%Y%m%d%H%M%S")
        user1_name = f"user1_{unique_id}"
        user1_pass = "TestPassword123!"
        user2_name = f"user2_{unique_id}"
        user2_pass = "TestPassword456!"
        
        # === USER 1 SETUP ===
        page1 = context.new_page()
        
        # Signup User1
        page1.goto(f"{BASE_URL}/signup/", wait_until="networkidle")
        page1.fill('input[name="username"]', user1_name)
        page1.fill('input[name="password1"]', user1_pass)
        page1.fill('input[name="password2"]', user1_pass)
        page1.click('button[type="submit"]')
        page1.wait_for_url(f"{BASE_URL}/", wait_until="networkidle")
        print(f"[1] User1 {user1_name} signed up")
        
        # User1 creates tasks
        user1_tasks = [
            f"User1 Secret Project - {unique_id}",
            f"User1 Private Note - {unique_id}"
        ]
        
        for task_title in user1_tasks:
            page1.click('a:has-text("Add your first task"), a:has-text("Add"), button:has-text("Add")')
            page1.wait_for_selector('input[name="title"]')
            page1.fill('input[name="title"]', task_title)
            page1.fill('textarea[name="description"]', "User1 private data - should not be visible to others")
            page1.click('button[type="submit"]')
            page1.wait_for_url(f"{BASE_URL}/", wait_until="networkidle")
        
        print(f"[2] User1 created {len(user1_tasks)} tasks")
        
        # User1 logout
        page1.click('a:has-text("Logout"), button:has-text("Logout")')
        page1.wait_for_url(f"{BASE_URL}/login/", wait_until="networkidle")
        print("[3] User1 logged out")
        
        # === USER 2 SETUP ===
        page2 = context.new_page()
        
        # Signup User2
        page2.goto(f"{BASE_URL}/signup/", wait_until="networkidle")
        page2.fill('input[name="username"]', user2_name)
        page2.fill('input[name="password1"]', user2_pass)
        page2.fill('input[name="password2"]', user2_pass)
        page2.click('button[type="submit"]')
        page2.wait_for_url(f"{BASE_URL}/", wait_until="networkidle")
        print(f"[4] User2 {user2_name} signed up")
        
        # Verify User1's tasks are NOT visible to User2
        content = page2.content()
        for task_title in user1_tasks:
            assert task_title not in content, f"SECURITY ISSUE: User2 can see User1's task: {task_title}"
        print("[5] ✓ User1's tasks correctly hidden from User2")
        
        # User2 creates own tasks
        user2_tasks = [
            f"User2 Work Deadline - {unique_id}",
            f"User2 Meeting Notes - {unique_id}"
        ]
        
        for task_title in user2_tasks:
            page2.click('a:has-text("Add your first task"), a:has-text("Add"), button:has-text("Add")')
            page2.wait_for_selector('input[name="title"]')
            page2.fill('input[name="title"]', task_title)
            page2.fill('textarea[name="description"]', "User2 private data")
            page2.click('button[type="submit"]')
            page2.wait_for_url(f"{BASE_URL}/", wait_until="networkidle")
        
        print(f"[6] User2 created {len(user2_tasks)} tasks")
        
        # Verify User2 sees their tasks
        for task_title in user2_tasks:
            expect(page2).to_contain_text(task_title)
        print("[7] ✓ User2 can see their own tasks")
        
        # User2 logout
        page2.click('a:has-text("Logout"), button:has-text("Logout")')
        page2.wait_for_url(f"{BASE_URL}/login/", wait_until="networkidle")
        print("[8] User2 logged out")
        
        # === USER 1 LOGIN AGAIN ===
        page1.fill('input[name="username"]', user1_name)
        page1.fill('input[name="password"]', user1_pass)
        page1.click('button[type="submit"]')
        page1.wait_for_url(f"{BASE_URL}/", wait_until="networkidle")
        print("[9] User1 logged back in")
        
        # Verify User1 sees only their tasks
        for task_title in user1_tasks:
            expect(page1).to_contain_text(task_title)
        
        content = page1.content()
        for task_title in user2_tasks:
            assert task_title not in content, f"SECURITY ISSUE: User1 can see User2's task: {task_title}"
        
        print("[10] ✓ User1 can only see their own tasks (User2's tasks hidden)")
        print("\n✅ PASSED: Multi-user task isolation verified!")
        
        page1.close()
        page2.close()
