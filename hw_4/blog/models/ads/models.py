# ads/models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Advertisement(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=False)
    
    class Meta:
        permissions = [
            ('can_moderate_ads', 'Может модерировать объявления'),
        ]
    
    def can_edit(self, user):
        if user.is_superuser:
            return True
        if user.groups.filter(name='admin').exists():
            return True
        return self.author == user
    
    def can_delete(self, user):
        if user.is_superuser:
            return True
        if user.groups.filter(name='admin').exists():
            return True
        return self.author == user and not self.is_published