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
        validated_data['rule_string']=self.context['rule_string']
        if(not json_data['valid']):
            raise serializers.ValidationError(json_data['content'])
        else:
            rule=models.rules(rule_ast=json_data['content'],**validated_data)
            rule.save()
            return rule

    
class ruleCombineSerializer(serializers.Serializer):
    #gets list of rules_id
    rule_name=serializers.CharField(max_length=255)
    ids=serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )

class ruleEvaluvateSerializer(serializers.Serializer):
    data=serializers.JSONField()

