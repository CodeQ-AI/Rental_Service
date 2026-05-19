from django.db import models
from django.conf import settings


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class AllObjectsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()


class RentalItem(models.Model):

    PROPERTY_TYPES = [
        ('apartment', 'Квартира'),
        ('house',  'Дом'),
        ('room',   'Комната'),
        ('office', 'Офис'),
        ('garage', 'Гараж'),
        ('other', 'Другое'),
    ]

    owner  = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='rental_items',
        verbose_name='Владелец'
    )
    title  = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    property_type = models.CharField(
        max_length=20,
        choices=PROPERTY_TYPES,
        default='apartment',
        verbose_name='Тип недвижимости'
    )
    address = models.CharField(max_length=300, blank=True, verbose_name='Адрес')
    rooms  = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Количество комнат')
    area  = models.DecimalField(max_digits=8, decimal_places=1, blank=True, null=True, verbose_name='Площадь (м²)')
    price  = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена (₸/сутки)')
    photo = models.ImageField(upload_to='rentals/', blank=True, null=True, verbose_name='Фото')
    is_deleted = models.BooleanField(default=False, verbose_name='Удалён')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects     = SoftDeleteManager()
    all_objects = AllObjectsManager()

    class Meta:
        verbose_name = 'Объект аренды'
        verbose_name_plural = 'Объекты аренды'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def soft_delete(self):
        self.is_deleted = True
        self.save(update_fields=['is_deleted'])

    def restore(self):
        self.is_deleted = False
        self.save(update_fields=['is_deleted'])

    def get_property_type_icon(self):
        icons = {
            'apartment': 'bi-building',
            'house': 'bi-house',
            'room':  'bi-door-open',
            'office': 'bi-briefcase',
            'garage': 'bi-car-front',
            'other': 'bi-three-dots',
        }
        return icons.get(self.property_type, 'bi-house')


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending',   'Ожидает'),
        ('confirmed', 'Подтверждён'),
        ('cancelled', 'Отменён'),
        ('completed', 'Завершён'),
    ]

    renter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name='Арендатор'
    )
    item = models.ForeignKey(
        RentalItem,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name='Объект аренды'
    )
    date_start  = models.DateField(verbose_name='Дата начала')
    date_end    = models.DateField(verbose_name='Дата окончания')
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Статус')
    total_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name='Итоговая сумма')
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.renter} → {self.item} [{self.date_start} / {self.date_end}]'

    def save(self, *args, **kwargs):
        if self.date_start and self.date_end:
            days = (self.date_end - self.date_start).days
            if days > 0:
                self.total_price = self.item.price * days
        super().save(*args, **kwargs)