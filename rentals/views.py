from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404

from .forms import RentalItemForm, BookingForm
from .models import RentalItem, Booking


# ---------- helpers ----------

SORT_FIELDS = {
    'title':       'title',
    '-title':      '-title',
    'price':       'price',
    '-price':      '-price',
    'created_at':  'created_at',
    '-created_at': '-created_at',
}
DEFAULT_SORT = '-created_at'


def _get_ordering(request):
    sort = request.GET.get('sort', DEFAULT_SORT)
    return SORT_FIELDS.get(sort, DEFAULT_SORT), sort


def _check_item_owner(request, item):
    """Возвращает True если текущий юзер — владелец или staff."""
    return request.user == item.owner or request.user.is_staff


# ---------- RentalItem CRUD ----------

def item_list_view(request):
    ordering, sort_param = _get_ordering(request)
    qs = RentalItem.objects.select_related('owner').order_by(ordering)

    paginator = Paginator(qs, 6)
    page_obj  = paginator.get_page(request.GET.get('page'))

    return render(request, 'rentals/item_list.html', {
        'page_obj':   page_obj,
        'sort':       sort_param,
        'sort_fields': [
            ('-created_at', 'Новые'),
            ('created_at',  'Старые'),
            ('price',       'Цена ↑'),
            ('-price',      'Цена ↓'),
            ('title',       'Название А-Я'),
            ('-title',      'Название Я-А'),
        ],
    })


def item_detail_view(request, pk):
    item = get_object_or_404(RentalItem, pk=pk)
    booking_form = None

    if request.user.is_authenticated and request.user != item.owner:
        booking_form = BookingForm(request.POST or None)
        if request.method == 'POST' and booking_form.is_valid():
            booking = booking_form.save(commit=False)
            booking.renter = request.user
            booking.item   = item
            booking.save()
            messages.success(request, 'Бронирование успешно создано!')
            return redirect('rentals:item_detail', pk=pk)

    return render(request, 'rentals/item_detail.html', {
        'item':         item,
        'booking_form': booking_form,
        'is_owner':     request.user.is_authenticated and _check_item_owner(request, item),
    })


@login_required
def item_create_view(request):
    form = RentalItemForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        item = form.save(commit=False)
        item.owner = request.user
        item.save()
        messages.success(request, f'Объект «{item.title}» успешно добавлен.')
        return redirect('rentals:item_detail', pk=item.pk)

    return render(request, 'rentals/item_form.html', {
        'form':  form,
        'title': 'Добавить объект',
    })


@login_required
def item_edit_view(request, pk):
    item = get_object_or_404(RentalItem, pk=pk)

    if not _check_item_owner(request, item):
        messages.error(request, 'У вас нет прав для редактирования этого объекта.')
        return redirect('rentals:item_detail', pk=pk)

    form = RentalItemForm(request.POST or None, request.FILES or None, instance=item)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Объект «{item.title}» успешно обновлён.')
        return redirect('rentals:item_detail', pk=pk)

    return render(request, 'rentals/item_form.html', {
        'form':  form,
        'item':  item,
        'title': f'Редактировать: {item.title}',
    })


@login_required
def item_delete_view(request, pk):
    item = get_object_or_404(RentalItem, pk=pk)

    if not _check_item_owner(request, item):
        messages.error(request, 'У вас нет прав для удаления этого объекта.')
        return redirect('rentals:item_detail', pk=pk)

    if request.method == 'POST':
        title = item.title
        item.soft_delete()
        messages.success(request, f'Объект «{title}» удалён.')
        return redirect('rentals:item_list')

    return render(request, 'rentals/item_confirm_delete.html', {'item': item})


# ---------- Bookings ----------

@login_required
def my_bookings_view(request):
    bookings = (
        Booking.objects
        .filter(renter=request.user)
        .select_related('item', 'item__owner')
        .order_by('-created_at')
    )
    paginator = Paginator(bookings, 8)
    page_obj  = paginator.get_page(request.GET.get('page'))

    return render(request, 'rentals/my_bookings.html', {'page_obj': page_obj})


@login_required
def booking_cancel_view(request, pk):
    booking = get_object_or_404(Booking, pk=pk, renter=request.user)

    if booking.status not in ('pending', 'confirmed'):
        messages.error(request, 'Это бронирование нельзя отменить.')
        return redirect('rentals:my_bookings')

    if request.method == 'POST':
        booking.status = 'cancelled'
        booking.save(update_fields=['status'])
        messages.success(request, 'Бронирование отменено.')
        return redirect('rentals:my_bookings')

    return render(request, 'rentals/booking_confirm_cancel.html', {'booking': booking})


@login_required
def owner_bookings_view(request):
    """Владелец видит все брони на свои объекты."""
    bookings = (
        Booking.objects
        .filter(item__owner=request.user, item__is_deleted=False)
        .select_related('item', 'renter')
        .order_by('-created_at')
    )
    paginator = Paginator(bookings, 8)
    page_obj  = paginator.get_page(request.GET.get('page'))

    return render(request, 'rentals/owner_bookings.html', {'page_obj': page_obj})


@login_required
def booking_status_update_view(request, pk):
    """Владелец меняет статус брони."""
    booking = get_object_or_404(Booking, pk=pk, item__owner=request.user)

    allowed_transitions = {
        'pending':   ['confirmed', 'cancelled'],
        'confirmed': ['completed', 'cancelled'],
    }
    available = allowed_transitions.get(booking.status, [])

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in available:
            booking.status = new_status
            booking.save(update_fields=['status'])
            messages.success(request, f'Статус обновлён: {booking.get_status_display()}.')
        else:
            messages.error(request, 'Недопустимый переход статуса.')
        return redirect('rentals:owner_bookings')

    return render(request, 'rentals/booking_status_update.html', {
        'booking':   booking,
        'available': available,
    })