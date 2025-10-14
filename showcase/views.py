from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import DemoUser, DemoTask, DemoReport
from .odoo_client import odoo_client
import json
import logging

logger = logging.getLogger(__name__)

def landing_page(request):
    """Main landing page with hero section - now with real Odoo data"""
    try:
        # Get real statistics from Odoo
        stats = odoo_client.get_task_statistics()
        context = {
            'total_tasks': stats.get('active_tasks', 0) + stats.get('completed_tasks', 0),
            'completed_tasks': stats.get('completed_tasks', 0),
            'active_users': stats.get('total_users', 0),
            'total_reports': stats.get('total_reports', 0),
        }
    except Exception as e:
        logger.error(f"Failed to get Odoo statistics: {e}")
        # Fallback to demo data
        context = {
            'total_tasks': DemoTask.objects.count(),
            'completed_tasks': DemoTask.objects.filter(status='completed').count(),
            'active_users': DemoUser.objects.count(),
            'total_reports': DemoReport.objects.count(),
        }
    
    return render(request, 'showcase/landing.html', context)

def dashboard(request):
    """Interactive demo dashboard - now with real Odoo data"""
    try:
        # Get real data from Odoo using individual calls (more reliable)
        odoo_tasks = odoo_client.get_telegram_tasks()
        odoo_users = odoo_client.get_users(50)
        odoo_reports = odoo_client.get_reports(20)
        odoo_vehicles = odoo_client.get_vehicles(20)
        stats = odoo_client.get_task_statistics()
        
        # Debug logging
        logger.info(f"Demo dashboard - Tasks: {len(odoo_tasks) if isinstance(odoo_tasks, list) else 'Error'}")
        logger.info(f"Demo dashboard - Users: {odoo_users.get('success', False) if isinstance(odoo_users, dict) else 'Error'}")
        logger.info(f"Demo dashboard - Vehicles: {odoo_vehicles.get('success', False) if isinstance(odoo_vehicles, dict) else 'Error'}")
        
        # Transform Odoo data for template - matching real dashboard format exactly
        tasks = []
        for task in odoo_tasks[:10] if isinstance(odoo_tasks, list) else []:
            # Enhanced task data transformation with proper field mapping (same as real version)
            assigned_user = task.get('assigned_user_id')
            telegram_user = task.get('telegram_user_id')
            
            # Determine user name - prioritize telegram user for display (same logic as real)
            user_display = 'Unassigned'
            if telegram_user and isinstance(telegram_user, list) and len(telegram_user) > 1:
                user_display = f"{telegram_user[1]} (Telegram)"
            elif assigned_user and isinstance(assigned_user, list) and len(assigned_user) > 1:
                user_display = assigned_user[1]
            elif task.get('user_id'):
                # Fallback to user_id if assigned_user_id not available
                if isinstance(task['user_id'], list) and len(task['user_id']) > 1:
                    user_display = task['user_id'][1]
                elif isinstance(task['user_id'], str):
                    user_display = task['user_id']
            
            tasks.append({
                'id': task.get('id'),
                'title': task.get('title', task.get('name', 'Untitled Task')),  # Try title first, then name
                'description': task.get('description', ''),
                'state': task.get('state', 'draft'),
                'priority': task.get('priority', '1'),
                'user_display': user_display,
                'telegram_user_id': telegram_user[0] if telegram_user and isinstance(telegram_user, list) else telegram_user,
                'create_date': task.get('create_date'),
                'deadline': task.get('deadline'),
            })
        
        # Sort tasks by ID descending (newest first, same as real dashboard)
        tasks.sort(key=lambda x: x.get('id', 0), reverse=True)
        
        users = []
        for user in odoo_users.get("users", []) if isinstance(odoo_users, dict) else []:
            users.append({
                'id': user.get('id'),
                'name': user.get('name', 'Unknown'),
                'first_name': user.get('name', 'Unknown'),
                'last_name': user.get('last_name', ''),
                'username': user.get('username', ''),
                'telegram_id': user.get('telegram_id'),
                'is_admin': user.get('is_admin', False),
            })
        
        reports = []
        for report in odoo_reports[:5] if isinstance(odoo_reports, list) else []:
            reports.append({
                'id': report.get('id'),
                'message': report.get('message', 'No message'),
                'photo_url': report.get('photo_url'),
                'created_at': report.get('create_date'),
                'task_name': report.get('task_id', [None, 'Unknown Task'])[1] if report.get('task_id') else 'Unknown Task'
            })

        vehicles = []
        if isinstance(odoo_vehicles, dict) and odoo_vehicles.get('success'):
            for vehicle in odoo_vehicles.get('vehicles', []):
                vehicles.append({
                    'id': vehicle.get('id'),
                    'name': vehicle.get('name', 'Unknown Vehicle'),
                    'license_plate': vehicle.get('license_plate', ''),
                    'driver_name': vehicle.get('driver_name', ''),
                    'brand': vehicle.get('brand', ''),
                    'model': vehicle.get('model', ''),
                })
        
        # Add fallback test data if no real data was retrieved
        test_users = [
            {'id': 1, 'name': 'Demo User', 'first_name': 'Demo User', 'username': 'demo_user'},
            {'id': 2, 'name': 'Test User', 'first_name': 'Test User', 'username': 'test_user'},
        ]
        test_vehicles = [
            {'id': 1, 'name': 'Demo Vehicle 1', 'license_plate': 'ABC-123'},
            {'id': 2, 'name': 'Demo Vehicle 2', 'license_plate': 'XYZ-789'},
        ]
        
        context = {
            'tasks': tasks,
            'users': users if users else test_users,
            'reports': reports,
            'vehicles': vehicles if vehicles else test_vehicles,
            'active_tasks': stats.get('active_tasks', 0) if isinstance(stats, dict) else 0,
            'completed_tasks': stats.get('completed_tasks', 0) if isinstance(stats, dict) else 0,
            'total_users': stats.get('total_users', 0) if isinstance(stats, dict) else 0,
            'total_reports': stats.get('total_reports', 0) if isinstance(stats, dict) else 0,
            'using_real_data': True,
        }
        
    except Exception as e:
        logger.error(f"Failed to get Odoo data: {e}")
        # Fallback to demo data
        tasks = DemoTask.objects.all().order_by('-created_at')[:10]
        users = DemoUser.objects.all()
        reports = DemoReport.objects.all().order_by('-created_at')[:5]
        
        context = {
            'tasks': tasks,
            'users': users,
            'reports': reports,
            'vehicles': [],  # Empty vehicles for fallback
            'active_tasks': DemoTask.objects.filter(status='assigned').count(),
            'completed_tasks': DemoTask.objects.filter(status='completed').count(),
            'total_users': DemoUser.objects.count(),
            'total_reports': DemoReport.objects.count(),
            'using_real_data': False,
            'error': 'Unable to connect to Odoo system',
        }
    
    return render(request, 'showcase/dashboard.html', context)

def api_tasks(request):
    """API endpoint for tasks data - now with real Odoo data"""
    try:
        # Get real tasks from Odoo
        odoo_tasks = odoo_client.get_telegram_tasks()
        tasks = []
        
        for task in odoo_tasks:
            tasks.append({
                'id': task.get('id'),
                'title': task.get('name', 'Untitled Task'),
                'status': task.get('state', 'draft'),
                'created_at': task.get('create_date'),
                'deadline': task.get('deadline'),
                'description': task.get('description', ''),
                'user_name': task.get('user_id', [None, 'Unassigned'])[1] if task.get('user_id') else 'Unassigned'
            })
        
        return JsonResponse({
            'tasks': tasks,
            'using_real_data': True,
            'total_count': len(tasks)
        })
        
    except Exception as e:
        logger.error(f"API call failed: {e}")
        # Fallback to demo data
        tasks = DemoTask.objects.all().values(
            'id', 'title', 'status', 'priority', 'created_at'
        )
        return JsonResponse({
            'tasks': list(tasks),
            'using_real_data': False,
            'error': str(e)
        })

@csrf_exempt
def create_demo_task(request):
    """Create a demo task in Odoo"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            task_name = data.get('name', 'Demo Task')
            task_description = data.get('description', 'Created from Django showcase')
            
            # Create task in Odoo using the correct method
            if not odoo_client.authenticate():
                return JsonResponse({
                    'status': 'error',
                    'message': 'Failed to authenticate with Odoo'
                })
            
            result = odoo_client.create_task(task_name, task_description)
            
            if result['success']:
                return JsonResponse({
                    'status': 'success',
                    'task_id': result['task_id'],
                    'message': 'Task created in Odoo successfully!'
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': result.get('error', 'Failed to create task in Odoo')
                })
                
        except Exception as e:
            logger.error(f"Failed to create demo task: {e}")
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })
    
    return JsonResponse({'status': 'error', 'message': 'Only POST allowed'})

@csrf_exempt
def create_advanced_task_demo(request):
    """Create an advanced task in demo version - testing advanced functionality"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            title = data.get('title', '')
            description = data.get('description', '')
            priority = data.get('priority', '1')
            telegram_user_id = data.get('telegram_user_id')
            vehicle_id = data.get('vehicle_id')
            date_deadline = data.get('date_deadline')
            
            if not title:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Task title is required'
                })
            
            # Create task in Odoo using the same logic as real version
            if not odoo_client.authenticate():
                return JsonResponse({
                    'status': 'error',
                    'message': 'Failed to authenticate with Odoo'
                })
            
            result = odoo_client.create_task(
                title=title,
                description=description,
                priority=priority,
                telegram_user_id=int(telegram_user_id) if telegram_user_id else None,
                vehicle_id=int(vehicle_id) if vehicle_id else None,
                date_deadline=date_deadline
            )
            
            if result['success']:
                return JsonResponse({
                    'status': 'success',
                    'task_id': result['task_id'],
                    'message': 'Advanced task created in demo successfully!'
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': result.get('error', 'Failed to create advanced task in demo')
                })
                
        except Exception as e:
            logger.error(f"Failed to create advanced demo task: {e}")
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })
    
    return JsonResponse({'status': 'error', 'message': 'Only POST allowed'})

@csrf_exempt
def create_telegram_user_demo(request):
    """Create a new Telegram user in demo version with validation"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name', '').strip()
            telegram_id = data.get('telegram_id', '').strip()
            username = data.get('username', '').strip()
            
            # Basic validation
            if not name or not telegram_id:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Name and Telegram ID are required'
                })
            
            # Validate Telegram ID format (must be numeric)
            if not telegram_id.isdigit():
                return JsonResponse({
                    'status': 'error',
                    'message': 'Telegram ID must be a numeric value'
                })
            
            # Validate name length
            if len(name) < 2 or len(name) > 50:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Name must be between 2 and 50 characters'
                })
            
            # Validate username format if provided
            if username and not username.replace('_', '').replace('.', '').isalnum():
                return JsonResponse({
                    'status': 'error',
                    'message': 'Username can only contain letters, numbers, underscores and dots'
                })
            
            # Create user in Odoo
            if not odoo_client.authenticate():
                return JsonResponse({
                    'status': 'error',
                    'message': 'Failed to authenticate with Odoo system'
                })
            
            # Check if user already exists (using same method as real version)
            dashboard_data = odoo_client.get_dashboard_data()
            if dashboard_data['success']:
                users_data = dashboard_data['data']['users']
                if users_data['success']:
                    for user in users_data['users']:
                        if str(user.get('telegram_id')) == telegram_id:
                            return JsonResponse({
                                'status': 'error', 
                                'message': f'A user with Telegram ID {telegram_id} already exists'
                            })
            
            result = odoo_client.create_telegram_user(name, telegram_id, username)
            
            if result['success']:
                logger.info(f"New Telegram user created in demo: {name} (ID: {telegram_id})")
                return JsonResponse({
                    'status': 'success',
                    'user_id': result['user_id'],
                    'message': 'Telegram user created successfully!'
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': result.get('error', 'Failed to create user in Odoo')
                })
                
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON data'
            })
        except Exception as e:
            logger.error(f"Failed to create telegram user in demo: {e}")
            return JsonResponse({
                'status': 'error',
                'message': 'Internal server error. Please try again.'
            })
    
    return JsonResponse({'status': 'error', 'message': 'Only POST method allowed'})

@csrf_exempt  
def telegram_webhook(request):
    """Demo telegram webhook (simplified)"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Simulate processing
            return JsonResponse({'status': 'ok', 'processed': True})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Only POST allowed'})