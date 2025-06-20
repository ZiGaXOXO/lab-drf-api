from rest_framework import serializers
from .models import Todo

class TodoSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    class Meta:
        model = Todo
        fields = ['id', 'title', 'description', 'completed', 'created_at', 'updated_at', 'owner']
        # read_only_fields = ['id', 'created_at', 'updated_at', 'owner']
