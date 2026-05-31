from django.contrib import admin
from .models import User, FinancialRecord

# ------------------------
# User Admin
# ------------------------
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('username', 'email')
    ordering = ('username',)


# ------------------------
# FinancialRecord Admin
# ------------------------
@admin.register(FinancialRecord)
class FinancialRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount', 'type', 'category', 'date', 'created_at', 'updated_at')
    list_filter = ('type', 'category', 'date', 'created_at')
    search_fields = ('category', 'notes', 'user__username')
    ordering = ('-date',)