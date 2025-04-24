from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Phone Number")
    address = models.TextField(blank=True, null=True, verbose_name="Address")
    bio = models.TextField(blank=True, null=True, verbose_name="Bio")
    image = models.ImageField(upload_to='profiles/', blank=True, null=True, verbose_name="Profile Image")
    preferred_destinations = models.ManyToManyField('Destination', blank=True, related_name='profiles', verbose_name="Preferred Destinations")
    travel_interests = models.ManyToManyField('InterestTag', blank=True, related_name='profiles', verbose_name="Travel Interests")
    accommodation_preferences = models.CharField(max_length=20, blank=True, null=True, verbose_name="Accommodation Preferences")
    preferred_currency = models.CharField(max_length=3, blank=True, null=True, verbose_name="Preferred Currency")
    preferred_language = models.CharField(max_length=2, blank=True, null=True, verbose_name="Preferred Language")
    email_notifications = models.BooleanField(default=True, verbose_name="Email Notifications")
    promotional_emails = models.BooleanField(default=True, verbose_name="Promotional Emails")
    booking_reminders = models.BooleanField(default=True, verbose_name="Booking Reminders")
    travel_tips = models.BooleanField(default=True, verbose_name="Travel Tips")
    price_alerts = models.BooleanField(default=True, verbose_name="Price Alerts")

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    try:
        instance.profile.save()
    except ObjectDoesNotExist:
        Profile.objects.create(user=instance)


class Destination(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    image = models.ImageField(upload_to='destinations/', null=True, blank=True)
    cover_image = models.ImageField(upload_to='destinations/covers/', null=True, blank=True,
                                    help_text="Large hero image for the destination page")
    climate = models.CharField(max_length=100, blank=True)
    vacation_type = models.CharField(max_length=100, blank=True)
    featured = models.BooleanField(default=False)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Hotel(models.Model):
    ACCOMMODATION_TYPES = [
        ('hotel', 'Hotel'),
        ('hostel', 'Hostel'),
        ('apartment', 'Apartment'),
        ('villa', 'Villa'),
        ('resort', 'Resort'),
    ]

    name = models.CharField(max_length=255)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='hotels')
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.FloatField()
    image = models.ImageField(upload_to='hotels/', null=True, blank=True)
    cover_image = models.ImageField(upload_to='hotels/covers/', null=True, blank=True,
                                    help_text="Large hero image for the hotel detail page")
    gallery_images = models.JSONField(default=list, blank=True, help_text="List of image URLs for the hotel gallery")
    description = models.TextField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    accommodation_type = models.CharField(max_length=20, choices=ACCOMMODATION_TYPES, default='hotel')
    amenities = models.JSONField(default=dict, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    booking_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Attraction(models.Model):
    ATTRACTION_TYPES = [
        ('cultural', 'Cultural'),
        ('nature', 'Nature'),
        ('entertainment', 'Entertainment'),
        ('shopping', 'Shopping'),
        ('food', 'Food & Dining'),
        ('sports', 'Sports & Activities'),
    ]

    name = models.CharField(max_length=255)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='attractions')
    description = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    image = models.ImageField(upload_to='attractions/', null=True, blank=True)
    cover_image = models.ImageField(upload_to='attractions/covers/', null=True, blank=True,
                                    help_text="Large hero image for the attraction page")
    attraction_type = models.CharField(max_length=20, choices=ATTRACTION_TYPES, default='cultural')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    opening_hours = models.CharField(max_length=255, blank=True)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    attraction = models.ForeignKey(Attraction, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    author = models.CharField(max_length=255)
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=True)

    def __str__(self):
        reviewed_item = self.hotel or self.attraction or self.destination
        return f"Review by {self.author} for {reviewed_item.name if reviewed_item else 'unknown'}"


class InterestTag(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название интереса")
    slug = models.SlugField(max_length=100, unique=True, help_text="Короткое имя для URL (например, history, food)")

    class Meta:
        verbose_name = "Тег интереса"
        verbose_name_plural = "Теги интересов"
        ordering = ['name']

    def __str__(self):
        return self.name


class Excursion(models.Model):
    EXCURSION_TYPES = [
        ('cultural', 'Cultural'),
        ('adventure', 'Adventure'),
        ('shopping', 'Shopping'),
        ('food', 'Food & Culinary'),
        ('nature', 'Nature'),
        ('historical', 'Historical'),
    ]

    name = models.CharField(max_length=255)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='excursions')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.CharField(max_length=100)  # e.g., "3 hours", "Full day"
    excursion_type = models.CharField(max_length=20, choices=EXCURSION_TYPES, default='cultural')
    image = models.ImageField(upload_to='excursions/', null=True, blank=True)
    cover_image = models.ImageField(upload_to='excursions/covers/', null=True, blank=True,
                                    help_text="Large hero image for the excursion page")
    gallery_images = models.JSONField(default=list, blank=True, help_text="List of image URLs for the excursion gallery")
    included_attractions = models.ManyToManyField(Attraction, related_name='excursions', blank=True)
    meeting_point = models.CharField(max_length=255, blank=True)
    booking_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    tags = models.ManyToManyField(
        InterestTag,
        blank=True,  # Позволяет экскурсии не иметь тегов
        related_name='excursions',
        verbose_name="Теги интересов"
    )

    # ---------------------------------

    def __str__(self):
        return self.name


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='bookings', null=True, blank=True)
    excursion = models.ForeignKey(Excursion, on_delete=models.CASCADE, related_name='bookings', null=True, blank=True)
    check_in_date = models.DateField(null=True, blank=True)
    check_out_date = models.DateField(null=True, blank=True)
    excursion_date = models.DateTimeField(null=True, blank=True)
    adults = models.PositiveIntegerField(default=1)
    children = models.PositiveIntegerField(default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    booking_reference = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.hotel:
            return f"Hotel booking for {self.hotel.name} by {self.user.username}"
        else:
            return f"Excursion booking for {self.excursion.name} by {self.user.username}"


class Guide(models.Model):
    title = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='guides', null=True, blank=True)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='guides')
    content = models.TextField()
    pdf_file = models.FileField(upload_to='guides/', null=True, blank=True)
    attractions = models.ManyToManyField(Attraction, related_name='guides', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Последнее обновление")
    is_public = models.BooleanField(default=False)

    class Meta:  # Добавим Meta для удобства
        ordering = ['-updated_at']
        verbose_name = "Путеводитель"
        verbose_name_plural = "Путеводители"

    def __str__(self):
        return f"Guide for {self.destination.name}: {self.title}"


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    # Используем verbose_name для лучшего отображения в админке, если будешь ее использовать
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='user_favorites', null=True,
                                    blank=True, verbose_name="Избранное направление")  # Изменил related_name чтобы не конфликтовать с user.favorites
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='user_favorites', null=True, blank=True,
                              verbose_name="Избранный отель")  # Изменил related_name
    attraction = models.ForeignKey(Attraction, on_delete=models.CASCADE, related_name='user_favorites', null=True,
                                  blank=True, verbose_name="Избранная достопримечательность")  # Изменил related_name
    excursion = models.ForeignKey(Excursion, on_delete=models.CASCADE, related_name='user_favorites', null=True,
                                  blank=True, verbose_name="Избранная экскурсия")  # Изменил related_name
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")

    # --- Добавляем класс Meta ---
    class Meta:
        ordering = ['-created_at']  # Сортировка по умолчанию
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"
        # Ограничение уникальности: один пользователь - один конкретный объект в избранном
        # Это предотвратит дублирование записей в базе данных
        unique_together = [
            ('user', 'destination'),
            ('user', 'hotel'),
            ('user', 'attraction'),
            ('user', 'excursion'),
        ]
        # Добавляем проверку, что хотя бы одно из полей объекта заполнено
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(destination__isnull=False) |
                    models.Q(hotel__isnull=False) |
                    models.Q(attraction__isnull=False) |
                    models.Q(excursion__isnull=False)
                ),
                name='at_least_one_favorite_item'
            )
        ]

    def __str__(self):
        # Твой метод __str__ остается без изменений
        if self.destination:
            return f"{self.user.username}'s favorite: {self.destination.name}"
        elif self.hotel:
            return f"{self.user.username}'s favorite: {self.hotel.name}"
        elif self.attraction:
            return f"{self.user.username}'s favorite: {self.attraction.name}"
        elif self.excursion:
            return f"{self.user.username}'s favorite: {self.excursion.name}"
        return f"{self.user.username}'s favorite (invalid state)"  # Добавил случай, если все поля null

    # Добавляем метод для очистки других полей при сохранении,
    # чтобы гарантировать, что только одно поле объекта заполнено.
    # Это логика уровня приложения, а не только БД.
    def save(self, *args, **kwargs):
        if self.destination:
            self.hotel = None
            self.attraction = None
            self.excursion = None
        elif self.hotel:
            self.destination = None
            self.attraction = None
            self.excursion = None
        elif self.attraction:
            self.destination = None
            self.hotel = None
            self.excursion = None
        elif self.excursion:
            self.destination = None
            self.hotel = None
            self.attraction = None
            self.attraction = None
        super().save(*args, **kwargs)  # Вызываем оригинальный метод save