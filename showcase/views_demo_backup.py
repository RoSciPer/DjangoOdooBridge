from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import DemoUser, DemoTask, DemoReport
import json

def landing_page(request):
    """Main landing page with hero section"""
    context = {
        'total_tasks': DemoTask.objects.count(),
        'completed_tasks': DemoTask.objects.filter(status='completed').count(),
        'active_users': DemoUser.objects.count(),
    }
    return render(request, 'showcase/landing.html', context)

def dashboard(request):
    """Interactive demo dashboard"""
    tasks = DemoTask.objects.all().order_by('-created_at')[:10]
    users = DemoUser.objects.all()
    reports = DemoReport.objects.all().order_by('-created_at')[:5]
    
    context = {
        'tasks': tasks,
        'users': users, 
        'reports': reports,
    }
    return render(request, 'showcase/dashboard.html', context)

def api_tasks(request):
    """API endpoint for tasks data"""
    tasks = DemoTask.objects.all().values(
        'id', 'title', 'status', 'priority', 'created_at'
    )
    return JsonResponse({'tasks': list(tasks)})

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
