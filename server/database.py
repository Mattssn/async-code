import os
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from supabase import create_client, Client
import json

logger = logging.getLogger(__name__)

# Initialize Supabase client (optional)
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')  # Use service role key for server operations

supabase: Optional[Client] = None

if supabase_url and supabase_key:
    try:
        supabase = create_client(supabase_url, supabase_key)
        logger.info("Supabase client initialized successfully")
    except Exception as e:
        logger.warning(f"Failed to initialize Supabase client: {e}")
        logger.warning("Running without Supabase - database operations will be disabled")
else:
    logger.warning("SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not configured")
    logger.warning("Running without Supabase - database operations will be disabled")

class DatabaseOperations:

    @staticmethod
    def is_available() -> bool:
        """Check if database is available"""
        return supabase is not None

    @staticmethod
    def create_project(user_id: str, name: str, description: str, repo_url: str,
                      repo_name: str, repo_owner: str, settings: Dict = None) -> Dict:
        """Create a new project"""
        if not supabase:
            logger.warning("Database not available - cannot create project")
            return None
        try:
            project_data = {
                'user_id': user_id,
                'name': name,
                'description': description,
                'repo_url': repo_url,
                'repo_name': repo_name,
                'repo_owner': repo_owner,
                'settings': settings or {},
                'is_active': True
            }

            result = supabase.table('projects').insert(project_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error creating project: {e}")
            raise
    
    @staticmethod
    def get_user_projects(user_id: str) -> List[Dict]:
        """Get all projects for a user"""
        if not supabase:
            logger.warning("Database not available - returning empty projects list")
            return []
        try:
            result = supabase.table('projects').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Error fetching user projects: {e}")
            raise
    
    @staticmethod
    def get_project_by_id(project_id: int, user_id: str) -> Optional[Dict]:
        """Get a specific project by ID for a user"""
        if not supabase:
            logger.warning("Database not available - cannot get project")
            return None
        try:
            result = supabase.table('projects').select('*').eq('id', project_id).eq('user_id', user_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error fetching project {project_id}: {e}")
            raise
    
    @staticmethod
    def update_project(project_id: int, user_id: str, updates: Dict) -> Optional[Dict]:
        """Update a project"""
        if not supabase:
            logger.warning("Database not available - cannot update project")
            return None
        try:
            updates['updated_at'] = datetime.utcnow().isoformat()
            result = supabase.table('projects').update(updates).eq('id', project_id).eq('user_id', user_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error updating project {project_id}: {e}")
            raise
    
    @staticmethod
    def delete_project(project_id: int, user_id: str) -> bool:
        """Delete a project"""
        if not supabase:
            logger.warning("Database not available - cannot delete project")
            return False
        try:
            result = supabase.table('projects').delete().eq('id', project_id).eq('user_id', user_id).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Error deleting project {project_id}: {e}")
            raise
    
    @staticmethod
    def create_task(user_id: str, project_id: int = None, repo_url: str = None,
                   target_branch: str = 'main', agent: str = 'claude',
                   chat_messages: List[Dict] = None) -> Dict:
        """Create a new task"""
        if not supabase:
            logger.warning("Database not available - cannot create task")
            return None
        try:
            task_data = {
                'user_id': user_id,
                'project_id': project_id,
                'repo_url': repo_url,
                'target_branch': target_branch,
                'agent': agent,
                'status': 'pending',
                'chat_messages': chat_messages or [],
                'execution_metadata': {}
            }

            result = supabase.table('tasks').insert(task_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            raise
    
    @staticmethod
    def get_user_tasks(user_id: str, project_id: int = None) -> List[Dict]:
        """Get all tasks for a user, optionally filtered by project"""
        if not supabase:
            logger.warning("Database not available - returning empty tasks list")
            return []
        try:
            query = supabase.table('tasks').select('*').eq('user_id', user_id)
            if project_id:
                query = query.eq('project_id', project_id)
            result = query.order('created_at', desc=True).execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Error fetching user tasks: {e}")
            raise
    
    @staticmethod
    def get_task_by_id(task_id: int, user_id: str) -> Optional[Dict]:
        """Get a specific task by ID for a user"""
        if not supabase:
            logger.warning("Database not available - cannot get task")
            return None
        try:
            result = supabase.table('tasks').select('*').eq('id', task_id).eq('user_id', user_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error fetching task {task_id}: {e}")
            raise
    
    @staticmethod
    def update_task(task_id: int, user_id: str, updates: Dict) -> Optional[Dict]:
        """Update a task"""
        if not supabase:
            logger.warning("Database not available - cannot update task")
            return None
        try:
            # Handle timestamps
            if 'status' in updates:
                if updates['status'] == 'running' and 'started_at' not in updates:
                    updates['started_at'] = datetime.utcnow().isoformat()
                elif updates['status'] in ['completed', 'failed', 'cancelled'] and 'completed_at' not in updates:
                    updates['completed_at'] = datetime.utcnow().isoformat()

            updates['updated_at'] = datetime.utcnow().isoformat()
            result = supabase.table('tasks').update(updates).eq('id', task_id).eq('user_id', user_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error updating task {task_id}: {e}")
            raise
    
    @staticmethod
    def add_chat_message(task_id: int, user_id: str, role: str, content: str) -> Optional[Dict]:
        """Add a chat message to a task"""
        if not supabase:
            logger.warning("Database not available - cannot add chat message")
            return None
        try:
            # Get current task
            task = DatabaseOperations.get_task_by_id(task_id, user_id)
            if not task:
                return None

            # Add new message
            chat_messages = task.get('chat_messages', [])
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
    
    @staticmethod
    def get_task_by_legacy_id(legacy_id: str) -> Optional[Dict]:
        """Get a task by its legacy UUID (for migration purposes)"""
        if not supabase:
            logger.warning("Database not available - cannot get task by legacy ID")
            return None
        try:
            result = supabase.table('tasks').select('*').eq('execution_metadata->>legacy_id', legacy_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error fetching task by legacy ID {legacy_id}: {e}")
            raise
    
    @staticmethod
    def migrate_legacy_task(legacy_task: Dict, user_id: str) -> Optional[Dict]:
        """Migrate a legacy task from the JSON storage to Supabase"""
        if not supabase:
            logger.warning("Database not available - cannot migrate legacy task")
            return None
        try:
            # Map legacy task structure to new structure
            task_data = {
                'user_id': user_id,
                'repo_url': legacy_task.get('repo_url'),
                'target_branch': legacy_task.get('branch', 'main'),
                'agent': legacy_task.get('model', 'claude'),
                'status': legacy_task.get('status', 'pending'),
                'container_id': legacy_task.get('container_id'),
                'commit_hash': legacy_task.get('commit_hash'),
                'git_diff': legacy_task.get('git_diff'),
                'git_patch': legacy_task.get('git_patch'),
                'changed_files': legacy_task.get('changed_files', []),
                'error': legacy_task.get('error'),
                'chat_messages': [{
                    'role': 'user',
                    'content': legacy_task.get('prompt', ''),
                    'timestamp': datetime.fromtimestamp(legacy_task.get('created_at', 0)).isoformat()
                }] if legacy_task.get('prompt') else [],
                'execution_metadata': {
                    'legacy_id': legacy_task.get('id'),
                    'migrated_at': datetime.utcnow().isoformat()
                }
            }

            # Set timestamps if available
            if legacy_task.get('created_at'):
                task_data['created_at'] = datetime.fromtimestamp(legacy_task['created_at']).isoformat()

            result = supabase.table('tasks').insert(task_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error migrating legacy task: {e}")
            raise
    
    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        if not supabase:
            logger.warning("Database not available - cannot get user")
            return None
        try:
            result = supabase.table('users').select('*').eq('id', user_id).single().execute()
            return result.data
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None