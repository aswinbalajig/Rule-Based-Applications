from django.db import models

# Create your models here.

class rules(models.Model):
    rule_name=models.CharField(max_length=255)
    rule_string=models.TextField()
    rule_ast=models.JSONField()

class operands(models.Model):
    rule=models.ForeignKey(rules,on_delete=models.CASCADE)
    name=models.CharField(max_length=255)
