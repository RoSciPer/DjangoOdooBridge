# Basic Django models for showcase
from django.db import models
from django.utils import timezone

class DemoUser(models.Model):
    telegram_id = models.CharField(max_length=50, unique=True)
    username = models.CharField(max_length=100, blank=True)
    first_name = models.CharField(max_length=100)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.first_name} (@{self.username})"

class DemoTask(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'), 
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'), 
        ('urgent', 'Urgent'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    assignee = models.ForeignKey(DemoUser, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.title} - {self.status}"

class DemoReport(models.Model):
    user = models.ForeignKey(DemoUser, on_delete=models.CASCADE)
    message = models.TextField()
    photo_url = models.URLField(blank=True)
    task = models.ForeignKey(DemoTask, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Report from {self.user.first_name}: {self.message[:50]}..."
