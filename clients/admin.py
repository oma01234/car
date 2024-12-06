from django.contrib import admin
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages

from .models import *


@admin.action(description='Delete selected users and their corresponding clients')
def delete_users_and_clients(modeladmin, request, queryset):
    for user in queryset:
        try:
            client = Client.objects.get(username=user.username)
            client.delete()
            user.delete()
            messages.success(request, f'Successfully deleted user and client: {user.username}')
        except ObjectDoesNotExist:
            messages.warning(request, f'Client with user {user.username} does not exist.')
        except Exception as e:
            messages.error(request, f'Error deleting user {user.username}: {e}')



@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('First_name', 'Last_name', 'username', 'email', 'phone_number', 'date_created', 'is_client')
    search_fields = ('First_name', 'Last_name', 'username', 'email')


class CustomUsersAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    actions = [delete_users_and_clients]


class CarAdmin(admin.ModelAdmin):
    list_display = ('make', 'model', 'owner', 'price_per_day', 'is_active', 'available_for_testing')
    list_filter = ('is_active', 'available_for_testing')
    search_fields = ('make', 'model', 'owner__username')

    # Add more fields for detailed view
    fieldsets = (
        ('Car Details', {
            'fields': ('make', 'model', 'price_per_day', 'description', 'is_active', 'available_for_testing', 'test_drive_fee', 'test_location')
        }),
        ('Owner Details', {
            'fields': ('owner',)
        }),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(owner=request.user)


admin.site.unregister(User)
admin.site.register(User, CustomUsersAdmin)
admin.site.register(Car, CarAdmin)
admin.site.register(Review)
admin.site.register(CarMaintenance)
admin.site.register(DamageReport)
admin.site.register(MaintenanceReminder)
