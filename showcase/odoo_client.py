"""
Enhanced Odoo API Client for Django Showcase
Optimized for better performance and reliability
"""

import xmlrpc.client
import requests
import json
import logging
import time
from functools import wraps
from django.conf import settings
from django.core.cache import cache
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

def retry_on_failure(max_retries=3, delay=1):
    """Decorator to retry failed operations"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}")
                    time.sleep(delay * (attempt + 1))
            return None
        return wrapper
    return decorator

def cache_result(timeout=5):
    """Decorator to cache function results with Django cache fallback"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                cache_key = f"odoo_{func.__name__}_{hash(str(args) + str(kwargs))}"
                result = cache.get(cache_key)
                if result is None:
                    result = func(self, *args, **kwargs)
                    if result:
                        cache.set(cache_key, result, timeout)
                return result
            except Exception as cache_error:
                # Fallback to no caching if Django cache not available
                logger.warning(f"Cache not available, running without cache: {cache_error}")
                return func(self, *args, **kwargs)
        return wrapper
    return decorator

class OdooClient:
    def __init__(self):
        # Odoo connection settings
        self.url = "https://demo.bidsolana.xyz"
        self.db = "telegram_demo"
        self.username = "demo@bidsolana.xyz" 
        self.password = "123test"
        self.uid = None
        self._authenticated = False
        self._last_auth_time = None
        
        # Connection pooling with timeout
        self.common = xmlrpc.client.ServerProxy(
            f'{self.url}/xmlrpc/2/common',
            transport=xmlrpc.client.SafeTransport() if self.url.startswith('https') else None,
            allow_none=True
        )
        self.models = xmlrpc.client.ServerProxy(
            f'{self.url}/xmlrpc/2/object',
            transport=xmlrpc.client.SafeTransport() if self.url.startswith('https') else None,
            allow_none=True
        )
        
        # Performance tracking
        self.request_count = 0
        self.total_request_time = 0
        
    @retry_on_failure(max_retries=3, delay=1)
    def authenticate(self) -> bool:
        """Enhanced authentication with caching and retry logic"""
        try:
            # Check if already authenticated and not expired (5 minutes)
            current_time = time.time()
            if (self._authenticated and self._last_auth_time and 
                (current_time - self._last_auth_time) < 300):
                return True
            
            start_time = time.time()
            self.uid = self.common.authenticate(self.db, self.username, self.password, {})
            auth_time = time.time() - start_time
            
            self._authenticated = bool(self.uid)
            self._last_auth_time = current_time
            
            logger.info(f"Odoo authentication: {'success' if self.uid else 'failed'} "
                       f"(uid: {self.uid}, time: {auth_time:.2f}s)")
            return self._authenticated
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            self._authenticated = False
            return False
    
    @retry_on_failure(max_retries=2, delay=0.5)
    def execute_kw(self, model: str, method: str, args: List = None, kwargs: Dict = None):
        """Enhanced execute with performance tracking and error handling"""
        if not self.authenticate():
            logger.error("Failed to authenticate before API call")
            return None
                
        try:
            start_time = time.time()
            result = self.models.execute_kw(
                self.db, self.uid, self.password,
                model, method, args or [], kwargs or {}
            )
            
            # Track performance
            request_time = time.time() - start_time
            self.request_count += 1
            self.total_request_time += request_time
            
            if request_time > 2.0:  # Log slow requests
                logger.warning(f"Slow API call: {model}.{method} took {request_time:.2f}s")
            
            return result
        except Exception as e:
            logger.error(f"API call failed for {model}.{method}: {e}")
            print(f"DEBUG: API call failed for {model}.{method}: {e}")
            print(f"DEBUG: Args: {args}, Kwargs: {kwargs}")
            # Reset authentication on certain errors
            if "Access Denied" in str(e) or "Session expired" in str(e):
                self._authenticated = False
                self.uid = None
            return None
    
    def get_telegram_tasks(self) -> List[Dict]:
        """Get all telegram tasks"""
        try:
            # Search for task.manager records (correct model name) - newest first
            task_ids = self.execute_kw('task.manager', 'search', [[]], {'order': 'id desc'})
            if not task_ids:
                return []
                
            # Read task details with correct field names
            tasks = self.execute_kw('task.manager', 'read', [task_ids], {
                'fields': ['title', 'description', 'state', 'assigned_user_id', 'telegram_user_id', 'create_date', 'date_deadline', 'priority']
            })
            
            return tasks or []
        except Exception as e:
            print(f"Failed to get tasks: {e}")
            return []
    
    @cache_result(timeout=5)  # Cache for 5 seconds
    def get_users(self, limit=10):
        """Get Telegram users from Odoo with caching"""
        try:
            user_ids = self.execute_kw('telegram.user', 'search', [[]], {'limit': limit})
            
            if user_ids:
                users = self.execute_kw('telegram.user', 'read', [user_ids], {
                    'fields': ['id', 'name', 'telegram_id', 'username', 'active', 'create_date']
                })
                return {'success': True, 'users': users or []}
            else:
                return {'success': True, 'users': []}
        except Exception as e:
            logger.error(f"Failed to get users: {e}")
            return {'success': False, 'error': str(e)}

    def get_vehicles(self, limit=10):
        """Get vehicles from Odoo"""
        try:
            vehicle_ids = self.models.execute_kw(
                self.db, self.uid, self.password,
                'task.vehicle', 'search',
                [[]], {'limit': limit}
            )
            
            if vehicle_ids:
                vehicles = self.models.execute_kw(
                    self.db, self.uid, self.password,
                    'task.vehicle', 'read',
                    [vehicle_ids], {'fields': ['id', 'name', 'license_plate', 'driver_name', 'brand', 'model']}
                )
                return {'success': True, 'vehicles': vehicles}
            else:
                return {'success': True, 'vehicles': []}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def create_telegram_user(self, name, telegram_id, username=''):
        """Create a new Telegram user in Odoo"""
        try:
            user_data = {
                'name': name,
                'telegram_id': str(telegram_id),
                'username': username,
                'active': True,
            }
            
            logger.info(f"Creating Telegram user with data: {user_data}")
            
            # Use execute_kw method for proper authentication handling
            user_id = self.execute_kw('telegram.user', 'create', [user_data])
            
            if user_id:
                logger.info(f"Telegram user created successfully with ID: {user_id}")
                # Clear users cache after creating new user
                self.clear_users_cache()
                return {'success': True, 'user_id': user_id}
            else:
                raise Exception("User creation returned None")
        except Exception as e:
            logger.error(f"Failed to create Telegram user: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_reports(self, limit=10):
        """Get reports from Odoo"""
        try:
            report_ids = self.models.execute_kw(
                self.db, self.uid, self.password,
                'task.report', 'search',
                [[]], {'limit': limit, 'order': 'create_date desc'}
            )
            
            if report_ids:
                reports = self.models.execute_kw(
                    self.db, self.uid, self.password,
                    'task.report', 'read',
                    [report_ids], {'fields': ['id', 'name', 'description', 'create_date', 'photo_urls', 'telegram_user_id', 'state']}
                )
                return {'success': True, 'reports': reports}
            else:
                return {'success': True, 'reports': []}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_task_statistics(self) -> Dict:
        """Get task statistics"""
        try:
            # Count tasks by state using correct model name
            active_count = len(self.execute_kw('task.manager', 'search', [
                [('state', '=', 'assigned')]
            ]) or [])
            
            completed_count = len(self.execute_kw('task.manager', 'search', [
                [('state', '=', 'completed')]
            ]) or [])
            
            total_users = len(self.execute_kw('telegram.user', 'search', [[]]) or [])
            total_reports = len(self.execute_kw('task.report', 'search', [[]]) or [])
            
            return {
                'active_tasks': active_count,
                'completed_tasks': completed_count,
                'total_users': total_users,
                'total_reports': total_reports
            }
        except Exception as e:
            print(f"Failed to get statistics: {e}")
            return {
                'active_tasks': 0,
                'completed_tasks': 0,
                'total_users': 0,
                'total_reports': 0
            }
    
    @cache_result(timeout=5)  # Cache for 5 seconds
    def get_tasks(self, limit=10):
        """Get tasks from Odoo with enhanced caching"""
        try:
            task_ids = self.execute_kw('task.manager', 'search', [[]], {
                'limit': limit, 
                'order': 'create_date desc'
            })
            
            if task_ids:
                tasks = self.execute_kw('task.manager', 'read', [task_ids], {
                    'fields': ['id', 'title', 'description', 'state', 'priority', 
                              'assigned_user_id', 'telegram_user_id', 'create_date', 
                              'date_deadline', 'vehicle_id']
                })
                return {'success': True, 'tasks': tasks or []}
            else:
                return {'success': True, 'tasks': []}
        except Exception as e:
            logger.error(f"Failed to get tasks: {e}")
            return {'success': False, 'error': str(e)}

    def create_task(self, title, description='', assigned_user_id=None, telegram_user_id=None, 
                   vehicle_id=None, priority='1', state='draft', date_deadline=None):
        """Create a new task in Odoo with full field support"""
        try:
            task_data = {
                'title': title,
                'description': description,
                'state': state,
                'priority': priority,
            }
            
            # Properly handle both assigned_user_id and telegram_user_id
            if assigned_user_id:
                task_data['assigned_user_id'] = assigned_user_id
            
            if telegram_user_id:
                task_data['telegram_user_id'] = telegram_user_id
                # Don't automatically set assigned_user_id - let it be separate
                
            if vehicle_id:
                task_data['vehicle_id'] = vehicle_id
                
            if date_deadline:
                # Convert datetime-local format to Odoo format
                if 'T' in date_deadline:
                    # Convert from HTML datetime-local format (2025-10-20T15:30:00) to Odoo format
                    date_deadline = date_deadline.replace('T', ' ')
                task_data['date_deadline'] = date_deadline
            
            logger.info(f"Creating task with data: {task_data}")
            print(f"DEBUG: Creating task with data: {task_data}")
            
            # Use execute_kw method for proper authentication handling
            task_id = self.execute_kw('task.manager', 'create', [task_data])
            
            print(f"DEBUG: Task creation result: {task_id}")
            logger.info(f"Task creation result: {task_id}")
            
            if task_id:
                logger.info(f"Task created successfully with ID: {task_id}")
                print(f"DEBUG: Task created successfully with ID: {task_id}")
                # Clear cache after creating new task
                self.clear_tasks_cache()
                return {'success': True, 'task_id': task_id}
            else:
                print("DEBUG: Task creation returned None")
                raise Exception("Task creation returned None - check Odoo model fields")
        except Exception as e:
            logger.error(f"Failed to create task: {e}")
            return {'success': False, 'error': str(e)}
    
    def batch_create_tasks(self, tasks_data: List[Dict]) -> Dict:
        """Create multiple tasks in batch for better performance"""
        try:
            if not self.authenticate():
                return {'success': False, 'error': 'Authentication failed'}
            
            task_ids = []
            errors = []
            
            for i, task_data in enumerate(tasks_data):
                try:
                    result = self.create_task(**task_data)
                    if result['success']:
                        task_ids.append(result['task_id'])
                    else:
                        errors.append(f"Task {i+1}: {result['error']}")
                except Exception as e:
                    errors.append(f"Task {i+1}: {str(e)}")
            
            return {
                'success': len(task_ids) > 0,
                'task_ids': task_ids,
                'errors': errors,
                'created_count': len(task_ids),
                'error_count': len(errors)
            }
        except Exception as e:
            logger.error(f"Batch task creation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_dashboard_data(self) -> Dict:
        """Get all dashboard data in optimized batch"""
        try:
            start_time = time.time()
            
            # Use cached versions where possible
            tasks_result = self.get_tasks(15)
            users_result = self.get_users(20)
            reports_result = self.get_reports(10)
            vehicles_result = self.get_vehicles(15)
            
            end_time = time.time()
            logger.info(f"Dashboard data fetched in {end_time - start_time:.2f}s")
            
            return {
                'success': True,
                'data': {
                    'tasks': tasks_result,
                    'users': users_result,
                    'reports': reports_result,
                    'vehicles': vehicles_result
                },
                'fetch_time': end_time - start_time,
                'request_count': self.request_count,
                'avg_request_time': self.total_request_time / max(self.request_count, 1)
            }
        except Exception as e:
            logger.error(f"Failed to get dashboard data: {e}")
            return {'success': False, 'error': str(e)}
    
    def clear_cache(self):
        """Clear all Odoo-related cache"""
        try:
            cache_keys = [
                'odoo_get_tasks_*', 'odoo_get_users_*', 
                'odoo_get_reports_*', 'odoo_get_vehicles_*'
            ]
            for key_pattern in cache_keys:
                cache.delete_many(cache.keys(key_pattern))
            logger.info("Odoo cache cleared")
        except Exception as e:
            logger.warning(f"Cache clear failed: {e}")
    
    def clear_tasks_cache(self):
        """Clear only tasks cache"""
        try:
            # Try different cache clearing approaches
            if hasattr(cache, 'delete_pattern'):
                cache.delete_pattern('odoo_get_tasks_*')
            else:
                # Fallback: clear individual known keys
                for i in range(100):  # Clear up to 100 different cache variations
                    cache.delete(f'odoo_get_tasks_{i}')
            logger.info("Tasks cache cleared")
        except Exception as e:
            logger.warning(f"Tasks cache clear failed: {e}")
    
    def clear_users_cache(self):
        """Clear only users cache"""
        try:
            if hasattr(cache, 'delete_pattern'):
                cache.delete_pattern('odoo_get_users_*')
            else:
                # Fallback: clear individual known keys
                for i in range(100):
                    cache.delete(f'odoo_get_users_{i}')
            logger.info("Users cache cleared")
        except Exception as e:
            logger.warning(f"Users cache clear failed: {e}")
    
    def get_performance_stats(self) -> Dict:
        """Get connection performance statistics"""
        return {
            'total_requests': self.request_count,
            'total_time': self.total_request_time,
            'average_time': self.total_request_time / max(self.request_count, 1),
            'authenticated': self._authenticated,
            'last_auth_time': self._last_auth_time,
            'connection_health': 'good' if self._authenticated else 'poor'
        }
    
    def health_check(self) -> Dict:
        """Perform health check on Odoo connection"""
        try:
            start_time = time.time()
            auth_success = self.authenticate()
            auth_time = time.time() - start_time
            
            if not auth_success:
                return {
                    'status': 'unhealthy',
                    'auth_time': auth_time,
                    'error': 'Authentication failed'
                }
            
            # Test a simple query
            test_start = time.time()
            test_result = self.execute_kw('telegram.user', 'search', [[]], {'limit': 1})
            test_time = time.time() - test_start
            
            return {
                'status': 'healthy',
                'auth_time': auth_time,
                'query_time': test_time,
                'total_time': auth_time + test_time,
                'uid': self.uid,
                'performance': self.get_performance_stats()
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': time.time()
            }

# Global client instance with connection pooling
odoo_client = OdooClient()