from django.urls import path
from .views import (
    home, destinations, destination_detail, hotels, hotel_detail,
    export_user_data, account_delete,
    excursions, excursion_detail, about, add_review, add_to_favorites,
    remove_from_favorites, user_favorites, guide_detail,
    attraction_detail, search, attractions, user_profile, user_settings,
    user_bookings, signup, download_guide_pdf
)

urlpatterns = [
    path('', home, name='home'),
    path('destinations/', destinations, name='destinations'),
    path('destinations/<int:destination_id>/', destination_detail, name='destination_detail'),
    path('hotels/', hotels, name='hotels'),
    path('hotels/<int:hotel_id>/', hotel_detail, name='hotel_detail'),
    path('excursions/', excursions, name='excursions'),
    path('excursions/<int:excursion_id>/', excursion_detail, name='excursion_detail'),
    path('attractions/', attractions, name='attractions'),
    path('attractions/<int:attraction_id>/', attraction_detail, name='attraction_detail'),
    path('about/', about, name='about'),
    path('search/', search, name='search'),
    
    # User actions (requires login)
    path('add-review/<str:content_type>/<int:content_id>/', add_review, name='add_review'),
    path('add-to-favorites/<str:content_type>/<int:content_id>/', add_to_favorites, name='add_to_favorites'),
    path('remove-from-favorites/<int:favorite_id>/', remove_from_favorites, name='remove_from_favorites'),
    path('my-favorites/', user_favorites, name='user_favorites'),

    path('guides/<int:guide_id>/', guide_detail, name='guide_detail'),
    path('download-guide/<int:destination_id>/', download_guide_pdf, name='download_guide_pdf'),
    # User profile and account
    path('profile/', user_profile, name='profile'),
    path('settings/', user_settings, name='settings'),
    path('bookings/', user_bookings, name='bookings'),
    path('signup/', signup, name='signup'),
    path('export-data/', export_user_data, name='export_data'),
    path('account/delete/', account_delete, name='account_delete'),
]
