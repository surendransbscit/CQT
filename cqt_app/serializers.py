from rest_framework import serializers
from .models import *
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password


# login 
class CustomLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        return attrs
    
    
# Password Change
User = get_user_model()

class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        validate_password(value) 
        return value

    def validate(self, attrs):
        user = self.context['request'].user
        if not user.check_password(attrs['old_password']):
            raise serializers.ValidationError({"old_password": "Old password is incorrect."})
        return attrs



# Attendance 

class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['id', 'user', 'check_in', 'check_out', 'total_hours', 'QR_string', 'location']
        read_only_fields = ['check_in', 'check_out', 'total_hours']


# Work From Home Attendance
class WorkFromHomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields=['id','user','check_in','check_out','start','end','location','reporting','reason']


# Leave 
class LeaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leave
        fields = ['id', 'user', 'title', 'start_date', 'end_date', 'reason', 'day_out', 'is_approved', 'total_days']
        read_only_fields = ['id', 'is_approved', 'total_days']



        
# Profile
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'email',
            'user_img',
            'college_passout_img',
            'experience_img',
            'degree_img',
            'phone_number',
            'alt_phone_number',
            'designation',
            'reporting',
            'salary',
            'address',
            'education_detail',
            'father_name',
            'mother_name',
            'siblings_name',
        ]



# Project
class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'user', 'task_name', 'task_description', 'task_priority', 'created_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user'] = {
            'message' : 'Successfully',
            'id': instance.user.id,
            'username': instance.user.username
        }
        
        return representation
    
    

# Holiday
class HolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Holiday
        fields = ['id', 'start_date', 'end_date', 'reason']
        
    
# Leave Approval
class LeaveApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leave
        fields = ['id', 'user', 'title', 'start_date', 'end_date', 'reason', 'is_approved']

    def update(self, instance, validated_data):
        # Update the instance with the new approval status
        instance.is_approved = validated_data.get('is_approved', instance.is_approved)
        instance.save()
        return instance




