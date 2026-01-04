import psycopg2
from psycopg2.extras import RealDictCursor
import os
from contextlib import contextmanager
import logging
from typing import Dict, List, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://asynccode:asynccode_password@localhost:5432/asynccode')

def get_connection():
    """Get a database connection"""
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

@contextmanager
def get_cursor():
    """Context manager for database cursor"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def init_database():
    """Initialize database schema"""
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')

    with open(schema_path, 'r') as f:
        schema_sql = f.read()

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(schema_sql)
        conn.commit()
        logger.info("✅ Database schema initialized successfully")
    except Exception as e:
        logger.error(f"❌ Error initializing database: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

class DatabaseOperations:

    @staticmethod
    def is_available() -> bool:
        """Check if database is available"""
        try:
            conn = get_connection()
            conn.close()
            return True
        except:
            return False

    # User operations
    @staticmethod
    def create_user(email: str, password_hash: str, full_name: str = None) -> Optional[Dict]:
        """Create a new user"""
        try:
            with get_cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO users (email, password_hash, full_name)
                    VALUES (%s, %s, %s)
                    RETURNING id, email, full_name, created_at
                    """,
                    (email, password_hash, full_name)
                )
                return dict(cursor.fetchone())
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise

    @staticmethod
    def get_user_by_email(email: str) -> Optional[Dict]:
        """Get user by email"""
        try:
            with get_cursor() as cursor:
                cursor.execute(
                    "SELECT id, email, password_hash, full_name, github_username, github_token, created_at FROM users WHERE email = %s",
                    (email,)
                )
                result = cursor.fetchone()
                return dict(result) if result else None
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            raise

    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        try:
            with get_cursor() as cursor:
                cursor.execute(
                    "SELECT id, email, full_name, github_username, created_at FROM users WHERE id = %s",
                    (user_id,)
                )
                result = cursor.fetchone()
                return dict(result) if result else None
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            raise

    @staticmethod
    def update_user(user_id: int, updates: Dict) -> Optional[Dict]:
        """Update user"""
        try:
            set_clause = ', '.join([f"{k} = %s" for k in updates.keys()])
            values = list(updates.values()) + [user_id]

            with get_cursor() as cursor:
                cursor.execute(
                    f"UPDATE users SET {set_clause} WHERE id = %s RETURNING id, email, full_name, github_username",
                    values
                )
                result = cursor.fetchone()
                return dict(result) if result else None
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            raise

    # Project operations
    @staticmethod
    def create_project(user_id: int, name: str, description: str, repo_url: str,
                      repo_name: str, repo_owner: str, settings: Dict = None) -> Dict:
        """Create a new project"""
        try:
            with get_cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO projects (user_id, name, description, repo_url, repo_name, repo_owner, settings)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id, user_id, name, description, repo_url, repo_name, repo_owner, settings, created_at, updated_at
                    """,
                    (user_id, name, description, repo_url, repo_name, repo_owner, json.dumps(settings or {}))
                )
                return dict(cursor.fetchone())
        except Exception as e:
            logger.error(f"Error creating project: {e}")
            raise

    @staticmethod
    def get_user_projects(user_id: int) -> List[Dict]:
        """Get all projects for a user"""
        try:
            with get_cursor() as cursor:
                cursor.execute(
                    """
                    SELECT p.*,
                           COUNT(t.id) as task_count,
                           COUNT(CASE WHEN t.status = 'completed' THEN 1 END) as completed_tasks,
                           COUNT(CASE WHEN t.status = 'running' THEN 1 END) as active_tasks
                    FROM projects p
                    LEFT JOIN tasks t ON p.id = t.project_id
                    WHERE p.user_id = %s
                    GROUP BY p.id
                    ORDER BY p.created_at DESC
                    """,
                    (user_id,)
                )
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error fetching user projects: {e}")
            raise

    @staticmethod
    def get_project_by_id(project_id: int, user_id: int) -> Optional[Dict]:
        """Get a specific project by ID for a user"""
        try:
            with get_cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM projects WHERE id = %s AND user_id = %s",
                    (project_id, user_id)
                )
                result = cursor.fetchone()
                return dict(result) if result else None
        except Exception as e:
            logger.error(f"Error fetching project {project_id}: {e}")
            raise

    @staticmethod
    def update_project(project_id: int, user_id: int, updates: Dict) -> Optional[Dict]:
        """Update a project"""
        try:
            set_clause = ', '.join([f"{k} = %s" for k in updates.keys()])
            values = list(updates.values()) + [project_id, user_id]

            with get_cursor() as cursor:
                cursor.execute(
                    f"UPDATE projects SET {set_clause} WHERE id = %s AND user_id = %s RETURNING *",
                    values
                )
                result = cursor.fetchone()
                return dict(result) if result else None
        except Exception as e:
            logger.error(f"Error updating project {project_id}: {e}")
            raise

    @staticmethod
    def delete_project(project_id: int, user_id: int) -> bool:
        """Delete a project"""
        try:
            with get_cursor() as cursor:
                cursor.execute(
                    "DELETE FROM projects WHERE id = %s AND user_id = %s RETURNING id",
                    (project_id, user_id)
                )
                return cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"Error deleting project {project_id}: {e}")
            raise

    # Task operations
    @staticmethod
    def create_task(user_id: int, project_id: int = None, repo_url: str = None,
                   target_branch: str = 'main', agent: str = 'claude',
                   chat_messages: List[Dict] = None) -> Dict:
        """Create a new task"""
        try:
            with get_cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO tasks (user_id, project_id, repo_url, target_branch, agent, status, chat_messages)
                    VALUES (%s, %s, %s, %s, %s, 'pending', %s)
                    RETURNING *
                    """,
                    (user_id, project_id, repo_url, target_branch, agent, json.dumps(chat_messages or []))
                )
                return dict(cursor.fetchone())
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            raise

    @staticmethod
    def get_user_tasks(user_id: int, project_id: int = None, limit: int = None, offset: int = None) -> List[Dict]:
        """Get all tasks for a user, optionally filtered by project"""
        try:
            query = """
                SELECT t.*, p.name as project_name, p.repo_name, p.repo_owner
                FROM tasks t
                LEFT JOIN projects p ON t.project_id = p.id
                WHERE t.user_id = %s
            """
            params = [user_id]

            if project_id:
                query += " AND t.project_id = %s"
                params.append(project_id)

            query += " ORDER BY t.created_at DESC"

            if limit:
                query += " LIMIT %s"
                params.append(limit)
            if offset:
                query += " OFFSET %s"
                params.append(offset)

            with get_cursor() as cursor:
                cursor.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error fetching user tasks: {e}")
            raise

    @staticmethod
    def get_task_by_id(task_id: int, user_id: int = None) -> Optional[Dict]:
        """Get a specific task by ID"""
        try:
            query = """
                SELECT t.*, p.name as project_name, p.repo_name, p.repo_owner
                FROM tasks t
                LEFT JOIN projects p ON t.project_id = p.id
                WHERE t.id = %s
            """
            params = [task_id]

            if user_id:
                query += " AND t.user_id = %s"
                params.append(user_id)

            with get_cursor() as cursor:
                cursor.execute(query, params)
                result = cursor.fetchone()
                return dict(result) if result else None
        except Exception as e:
            logger.error(f"Error fetching task {task_id}: {e}")
            raise

    @staticmethod
    def update_task(task_id: int, user_id: int, updates: Dict) -> Optional[Dict]:
        """Update a task"""
        try:
            # Convert chat_messages to JSON if needed
            if 'chat_messages' in updates and isinstance(updates['chat_messages'], list):
                updates['chat_messages'] = json.dumps(updates['chat_messages'])

            set_clause = ', '.join([f"{k} = %s" for k in updates.keys()])
            values = list(updates.values()) + [task_id, user_id]

            with get_cursor() as cursor:
                cursor.execute(
                    f"UPDATE tasks SET {set_clause} WHERE id = %s AND user_id = %s RETURNING *",
                    values
                )
                result = cursor.fetchone()
                return dict(result) if result else None
        except Exception as e:
            logger.error(f"Error updating task {task_id}: {e}")
            raise

    @staticmethod
    def add_chat_message(task_id: int, user_id: int, role: str, content: str) -> Optional[Dict]:
        """Add a chat message to a task"""
        try:
            # Get current task
            task = DatabaseOperations.get_task_by_id(task_id, user_id)
            if not task:
                return None

            # Add new message
            chat_messages = json.loads(task.get('chat_messages', '[]')) if isinstance(task.get('chat_messages'), str) else task.get('chat_messages', [])
            new_message = {
                'role': role,
                'content': content,
                'timestamp': datetime.utcnow().isoformat()
            }
            chat_messages.append(new_message)

            # Update task
            return DatabaseOperations.update_task(task_id, user_id, {'chat_messages': chat_messages})
        except Exception as e:
            logger.error(f"Error adding chat message to task {task_id}: {e}")
            raise
