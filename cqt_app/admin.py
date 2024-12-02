from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

class UserAdmin(BaseUserAdmin):
    
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password', 'role', 'user_img', 'college_passout_img', 'experience_img', 'degree_img', 'designation', 'reporting', 'salary', 'address', 'education_detail', 'father_name', 'mother_name', 'siblings_name', 'phone_number', 'alt_phone_number')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'is_active', 'is_staff'),
        }),
    )
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('username',)
    filter_horizontal = ('groups', 'user_permissions',)

admin.site.register(User, UserAdmin)


from .models import Attendance

class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'check_in', 'check_out', 'break_in', 'break_out', 'total_hours', 'total_days', 'QR_string', 'location')
    search_fields = ('user__email', 'QR_string', 'location')
    fields = ('user', 'check_in', 'check_out', 'break_in', 'break_out', 'QR_string', 'location')
    readonly_fields = ('total_hours', 'total_days', 'created_at')
    date_hierarchy = 'check_in'
    ordering = ('-check_in',) 
admin.site.register(Attendance, AttendanceAdmin)

