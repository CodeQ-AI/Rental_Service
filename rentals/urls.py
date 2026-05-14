from django.urls import path
from . import views

app_name = 'rentals'

urlpatterns = [
    # RentalItem
    path('',                          views.item_list_view,   name='item_list'),
    path('items/<int:pk>/',           views.item_detail_view, name='item_detail'),
    path('items/create/',             views.item_create_view, name='item_create'),
    path('items/<int:pk>/edit/',      views.item_edit_view,   name='item_edit'),
    path('items/<int:pk>/delete/',    views.item_delete_view, name='item_delete'),

    # Bookings — арендатор
    path('bookings/my/',              views.my_bookings_view,     name='my_bookings'),
    path('bookings/<int:pk>/cancel/', views.booking_cancel_view,  name='booking_cancel'),

    # Bookings — владелец
    path('bookings/incoming/',                    views.owner_bookings_view,        name='owner_bookings'),
    path('bookings/<int:pk>/status/',             views.booking_status_update_view, name='booking_status_update'),
]