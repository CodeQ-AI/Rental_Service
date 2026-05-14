from django.contrib import admin
from .models import RentalItem, Booking


@admin.register(RentalItem)
class RentalItemAdmin(admin.ModelAdmin):
    list_display  = ('title', 'owner', 'price', 'is_deleted', 'created_at')
    list_filter   = ('is_deleted',)
    search_fields = ('title', 'owner__email')
    actions       = ['soft_delete_items', 'restore_items']

    def get_queryset(self, request):
        return RentalItem.all_objects.all()

    @admin.action(description='Мягко удалить выбранные')
    def soft_delete_items(self, request, queryset):
        queryset.update(is_deleted=True)

    @admin.action(description='Восстановить выбранные')
    def restore_items(self, request, queryset):
        queryset.update(is_deleted=False)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display  = ('renter', 'item', 'date_start', 'date_end', 'status', 'total_price', 'created_at')
    list_filter   = ('status',)
    search_fields = ('renter__email', 'item__title')
    readonly_fields = ('total_price', 'created_at')