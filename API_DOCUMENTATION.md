# ClickUp API Documentation

## Base URL
```
http://localhost:8000/api
```

## Authentication
All endpoints (except user creation and token endpoints) require JWT authentication.

### Get Access Token
**POST** `/token/`
```json
{
    "username": "user@example.com",
    "password": "password123"
}
```

**Response:**
```json
{
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Refresh Token
**POST** `/token/refresh/`
```json
{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

## User Endpoints

### List Users
**GET** `/users/`
- **Authentication:** Required
- **Query Parameters:**
  - `search`: Search by name, username, or email
  - `role`: Filter by role (user, admin, manager, guest)
  - `is_active`: Filter by active status (true/false)
  - `ordering`: Order by `created_at` or `username` (prefix with `-` for descending)
  - `page`: Page number (default: 1)

**Response:**
```json
{
    "count": 10,
    "next": "http://localhost:8000/users/?page=2",
    "previous": null,
    "results": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "John Doe",
            "username": "johndoe",
            "email": "john@example.com",
            "is_active": true,
            "role": "user",
            "created_at": "2026-01-01T10:00:00Z",
            "updated_at": "2026-01-02T15:30:00Z"
        }
    ]
}
```

### Create User
**POST** `/users/`
- **Authentication:** Not required
- **Body:**
```json
{
    "name": "Jane Smith",
    "username": "janesmith",
    "email": "jane@example.com",
    "password": "securepassword123",
    "password2": "securepassword123",
    "role": "user"
}
```

### Get User Details
**GET** `/users/{id}/`
- **Authentication:** Required
- **Response:** User object with additional fields (is_staff, is_superuser)

### Update User
**PUT/PATCH** `/users/{id}/`
- **Authentication:** Required (admin only or self-update)
- **Body:** Partial or full user object

### Delete User
**DELETE** `/users/{id}/`
- **Authentication:** Required (admin only)

---

## Workspace Endpoints

### List Workspaces
**GET** `/workspaces/`
- **Authentication:** Required
- **Query Parameters:**
  - `search`: Search by name or description
  - `ordering`: Order by `created_at` or `name`
  - `page`: Page number

**Response:**
```json
{
    "count": 5,
    "results": [
        {
            "id": "650e8400-e29b-41d4-a716-446655440000",
            "name": "My Workspace",
            "description": "Main workspace",
            "created_by": "550e8400-e29b-41d4-a716-446655440000",
            "created_by_username": "johndoe",
            "created_at": "2026-01-01T10:00:00Z",
            "updated_at": "2026-01-02T15:30:00Z",
            "memberships": [
                {
                    "id": "750e8400-e29b-41d4-a716-446655440000",
                    "user": "550e8400-e29b-41d4-a716-446655440000",
                    "user_name": "johndoe",
                    "user_id": "550e8400-e29b-41d4-a716-446655440000",
                    "user_email": "john@example.com",
                    "role": "owner",
                    "joined_at": "2026-01-01T10:00:00Z"
                }
            ],
            "member_count": 1
        }
    ]
}
```

### Create Workspace
**POST** `/workspaces/`
- **Authentication:** Required
- **Body:**
```json
{
    "name": "New Project Workspace",
    "description": "Workspace for new project"
}
```

### Get Workspace Details
**GET** `/workspaces/{id}/`
- **Authentication:** Required

### Update Workspace
**PUT/PATCH** `/workspaces/{id}/`
- **Authentication:** Required (owner only)
- **Body:** Partial or full workspace object

### Delete Workspace
**DELETE** `/workspaces/{id}/`
- **Authentication:** Required (owner only)

---

## Workspace Members Endpoints

### List Workspace Members
**GET** `/add/members/`
- **Authentication:** Required
- **Query Parameters:**
  - `workspace`: Filter by workspace ID
  - `role`: Filter by role (owner, manager, member, guest)
  - `ordering`: Order by `joined_at`
  - `page`: Page number

**Response:**
```json
{
    "count": 3,
    "results": [
        {
            "id": "850e8400-e29b-41d4-a716-446655440000",
            "workspace": "650e8400-e29b-41d4-a716-446655440000",
            "user": "550e8400-e29b-41d4-a716-446655440000",
            "user_name": "johndoe",
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
            "user_email": "john@example.com",
            "role": "owner",
            "joined_at": "2026-01-01T10:00:00Z"
        }
    ]
}
```

### Add Member to Workspace
**POST** `/add/members/`
- **Authentication:** Required (workspace owner/manager only)
- **Body:**
```json
{
    "workspace": "650e8400-e29b-41d4-a716-446655440000",
    "user": "560e8400-e29b-41d4-a716-446655440000",
    "role": "member"
}
```

### Update Member Role
**PUT/PATCH** `/add/members/{id}/`
- **Authentication:** Required (workspace owner/manager only)
- **Body:**
```json
{
    "role": "manager"
}
```

### Remove Member from Workspace
**DELETE** `/add/members/{id}/`
- **Authentication:** Required (workspace owner/manager only)

---

## Project Endpoints

### List Projects
**GET** `/projects/`
- **Authentication:** Required (admin only)
- **Query Parameters:**
  - `workspace`: Filter by workspace ID
  - `created_by`: Filter by creator
  - `search`: Search by name or description
  - `ordering`: Order by `created_at` or `name`
  - `page`: Page number

**Response:**
```json
{
    "count": 2,
    "results": [
        {
            "id": "950e8400-e29b-41d4-a716-446655440000",
            "name": "Website Redesign",
            "workspace": "650e8400-e29b-41d4-a716-446655440000",
            "description": "Full website redesign project",
            "created_by": "550e8400-e29b-41d4-a716-446655440000",
            "created_at": "2026-01-05T10:00:00Z",
            "updated_at": "2026-01-06T15:30:00Z"
        }
    ]
}
```

### Create Project
**POST** `/projects/`
- **Authentication:** Required (admin only)
- **Body:**
```json
{
    "name": "Mobile App",
    "workspace": "650e8400-e29b-41d4-a716-446655440000",
    "description": "Native iOS and Android app"
}
```

### Get Project Details
**GET** `/projects/{id}/`
- **Authentication:** Required (admin only)

### Update Project
**PUT/PATCH** `/projects/{id}/`
- **Authentication:** Required (admin only)

### Delete Project
**DELETE** `/projects/{id}/`
- **Authentication:** Required (admin only)

---

## Task Endpoints

### List Tasks
**GET** `/tasks/`
- **Authentication:** Required
- **Query Parameters:**
  - `project`: Filter by project ID
  - `status`: Filter by status (todo, in_progress, review, completed, on_hold, cancelled)
  - `priority`: Filter by priority (low, medium, high, urgent)
  - `assignee`: Filter by assignee ID
  - `reporter`: Filter by reporter ID
  - `search`: Search by title or description
  - `ordering`: Order by `created_at`, `due_date`, or `title`
  - `page`: Page number

**Response:**
```json
{
    "count": 10,
    "results": [
        {
            "id": "a50e8400-e29b-41d4-a716-446655440000",
            "title": "Design homepage",
            "description": "Create mockups for homepage",
            "status": "in_progress",
            "priority": "high",
            "project": "950e8400-e29b-41d4-a716-446655440000",
            "reporter": "550e8400-e29b-41d4-a716-446655440000",
            "assignee": "560e8400-e29b-41d4-a716-446655440000",
            "created_at": "2026-01-05T10:00:00Z",
            "updated_at": "2026-01-06T15:30:00Z",
            "due_date": "2026-01-20T23:59:59Z",
            "is_completed": false
        }
    ]
}
```

### Create Task
**POST** `/tasks/`
- **Authentication:** Required
- **Body:**
```json
{
    "title": "Fix login bug",
    "description": "Users unable to login with email",
    "status": "todo",
    "priority": "urgent",
    "project": "950e8400-e29b-41d4-a716-446655440000",
    "assignee": "560e8400-e29b-41d4-a716-446655440000",
    "due_date": "2026-01-15T23:59:59Z"
}
```

### Get Task Details
**GET** `/tasks/{id}/`
- **Authentication:** Required

### Update Task
**PUT/PATCH** `/tasks/{id}/`
- **Authentication:** Required (reporter/assignee only)
- **Note:** Status and is_completed cannot be updated via this endpoint
- **Body:** Partial or full task object

### Update Task Status
**PATCH** `/tasks/{id}/update_status/`
- **Authentication:** Required (reporter/assignee only)
- **Body:**
```json
{
    "status": "review"
}
```

### Delete Task
**DELETE** `/tasks/{id}/`
- **Authentication:** Required (reporter/assignee/superuser only)

---

## Task Comment Endpoints

### List Task Comments
**GET** `/tasks/{task_id}/comments/`
- **Authentication:** Required
- **Query Parameters:**
  - `ordering`: Order by `created_at` (default: descending)
  - `page`: Page number

**Response:**
```json
{
    "count": 3,
    "results": [
        {
            "id": "b50e8400-e29b-41d4-a716-446655440000",
            "task": "a50e8400-e29b-41d4-a716-446655440000",
            "user": "550e8400-e29b-41d4-a716-446655440000",
            "user_name": "johndoe",
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
            "comment": "Started working on this task",
            "edited": false,
            "created_at": "2026-01-06T10:00:00Z",
            "updated_at": "2026-01-06T10:00:00Z"
        }
    ]
}
```

### Create Comment
**POST** `/tasks/{task_id}/comments/`
- **Authentication:** Required
- **Body:**
```json
{
    "task": "a50e8400-e29b-41d4-a716-446655440000",
    "comment": "Just completed the design mockups"
}
```

### Update Comment
**PUT/PATCH** `/tasks/{task_id}/comments/{id}/`
- **Authentication:** Required (comment author or superuser only)
- **Body:**
```json
{
    "comment": "Updated comment with more details"
}
```

### Delete Comment
**DELETE** `/tasks/{task_id}/comments/{id}/`
- **Authentication:** Required (comment author or superuser only)

---

## Error Responses

All error responses follow this format:

```json
{
    "detail": "Error message"
}
```

or for field validation errors:

```json
{
    "field_name": ["Error message for this field"]
}
```

### Common HTTP Status Codes
- `200 OK`: Successful GET/PUT/PATCH request
- `201 Created`: Successful POST request
- `204 No Content`: Successful DELETE request
- `400 Bad Request`: Invalid data or validation error
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: User doesn't have permission
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

---

## Rate Limiting
Currently no rate limiting is configured. Consider adding for production.

## Pagination
Default page size is 20 items. Use `page` query parameter to navigate.

**Example:** `/tasks/?page=2` gets the second page of tasks.


