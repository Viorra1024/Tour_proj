from django.contrib import admin
from .models import Destination, Hotel, Attraction, Excursion, Review, Guide, Favorite, Booking, InterestTag

@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'city', 'featured', 'created_at')
    list_filter = ('country', 'featured', 'climate', 'vacation_type')
    search_fields = ('name', 'country', 'city', 'description')
    prepopulated_fields = {'name': ('city',)}
    list_editable = ('featured',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'country', 'city', 'featured')
        }),
        ('Media', {
            'fields': ('image', 'cover_image'),
            'classes': ('collapse',),
        }),
        ('Categories', {
            'fields': ('climate', 'vacation_type'),
        }),
        ('Map Information', {
            'fields': ('latitude', 'longitude'),
            'classes': ('collapse',),
        }),
    )

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ('name', 'destination', 'price_per_night', 'rating', 'accommodation_type')
    list_filter = ('destination', 'accommodation_type', 'rating')
    search_fields = ('name', 'description', 'address')
    list_editable = ('price_per_night', 'rating')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'destination', 'description', 'price_per_night', 'rating', 'accommodation_type')
        }),
        ('Media', {
            'fields': ('image', 'cover_image', 'gallery_images'),
            'classes': ('collapse',),
        }),
        ('Location', {
            'fields': ('address', 'latitude', 'longitude'),
            'classes': ('collapse',),
        }),
        ('Features', {
            'fields': ('amenities', 'booking_url'),
        }),
    )

@admin.register(Attraction)
class AttractionAdmin(admin.ModelAdmin):
    list_display = ('name', 'destination', 'attraction_type', 'price')
    list_filter = ('destination', 'attraction_type')
    search_fields = ('name', 'description')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'destination', 'description', 'attraction_type')
        }),
        ('Media', {
            'fields': ('image', 'cover_image'),
            'classes': ('collapse',),
        }),
        ('Details', {
            'fields': ('price', 'opening_hours', 'website'),
        }),
        ('Map Information', {
            'fields': ('latitude', 'longitude'),
        }),
    )

@admin.register(Excursion)
class ExcursionAdmin(admin.ModelAdmin):
    list_display = ('name', 'destination', 'price', 'duration', 'excursion_type')
    list_filter = ('destination', 'excursion_type')
    search_fields = ('name', 'description')
    filter_horizontal = ('included_attractions',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'destination', 'description', 'excursion_type')
        }),
        ('Media', {
            'fields': ('image', 'cover_image', 'gallery_images'),
            'classes': ('collapse',),
        }),
        ('Booking Details', {
            'fields': ('price', 'duration', 'meeting_point', 'booking_url'),
        }),
        ('Attractions', {
            'fields': ('included_attractions',),
            'classes': ('collapse',),
        }),
    )

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('author', 'rating', 'get_reviewed_item', 'created_at', 'approved')
    list_filter = ('rating', 'approved', 'created_at')
    search_fields = ('author', 'comment')
    list_editable = ('approved',)
    
    def get_reviewed_item(self, obj):
        if obj.hotel:
            return f"Hotel: {obj.hotel.name}"
        elif obj.attraction:
            return f"Attraction: {obj.attraction.name}"
        elif obj.destination:
            return f"Destination: {obj.destination.name}"
        return "Unknown"
    
    get_reviewed_item.short_description = 'Reviewed Item'

@admin.register(Guide)
class GuideAdmin(admin.ModelAdmin):
    list_display = ('title', 'destination', 'user', 'created_at', 'is_public')
    list_filter = ('destination', 'is_public', 'created_at')
    search_fields = ('title', 'content', 'destination__name')
    list_editable = ('is_public',)
    filter_horizontal = ('attractions',)

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_favorite_item', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username',)
    
    def get_favorite_item(self, obj):
        if obj.destination:
            return f"Destination: {obj.destination.name}"
        elif obj.hotel:
            return f"Hotel: {obj.hotel.name}"
        elif obj.attraction:
            return f"Attraction: {obj.attraction.name}"
        elif obj.excursion:
            return f"Excursion: {obj.excursion.name}"
        return "Unknown"
    
    get_favorite_item.short_description = 'Favorite Item'

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_booked_item', 'status', 'total_price', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'booking_reference')
    list_editable = ('status',)
    
    def get_booked_item(self, obj):
        if obj.hotel:
            return f"Hotel: {obj.hotel.name}"
        elif obj.excursion:
            return f"Excursion: {obj.excursion.name}"
        return "Unknown"
    
    get_booked_item.short_description = 'Booked Item'

@admin.register(InterestTag)
class InterestTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug') # Какие поля показывать в списке
    search_fields = ('name',)      # По каким полям искать
    prepopulated_fields = {'slug': ('name',)} # Автоматически заполнять slug из name (очень удобно!)


