from rest_framework import serializers
from . import views
from . import models

class ruleStoreModelSerializer(serializers.ModelSerializer):
    class Meta:
        model=models.rules
        fields=['id','rule_name','rule_string']
    
    id=serializers.IntegerField(read_only=True)
    def create(self, validated_data):
        json_data=self.context['data']
        if(json_data['valid']):
            rule=models.rules(rule_ast=json_data['content'],**validated_data)
            rule.save()
        else:
            return serializers.ValidationError(json_data['content'])
        return rule

    
class ruleCombineSerializer(serializers.Serializer):
    #gets list of rules_id
    ids=serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )

class ruleEvaluvateSerializer(serializers.Serializer):
    data=serializers.JSONField()

