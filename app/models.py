from django.db import models
from django.contrib.auth.models import User

class Script(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='User')
    textarea1 = models.TextField(verbose_name='Textarea 1')
    textarea2 = models.TextField(verbose_name='Textarea 2')
    textarea3 = models.TextField(verbose_name='Textarea 3')
    textarea4 = models.TextField(verbose_name='Textarea 4')
    coin = models.IntegerField(verbose_name='Coin', default=10)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created Date')

class PostURL(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='User')
    post_char = models.CharField(max_length=10, unique=True, verbose_name='Post Char')
    claim_char = models.CharField(max_length=10, unique=True, verbose_name='Claim Char')
    token = models.IntegerField(default=10, verbose_name='Token')

    
class ClaimURL(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    posted_url = models.ForeignKey(PostURL, on_delete=models.CASCADE)
    claim_char = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.user.username} claimed {self.claim_char}"