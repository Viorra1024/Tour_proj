from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, Http404
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import timedelta
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Avg, Q, Count
from .models import Destination, Hotel, Attraction, Excursion, Review, Guide, Favorite, InterestTag, Profile  # Import
from .forms import UserUpdateForm, ProfileUpdateForm
from django.db import models
from .tasks import generate_guide_pdf_task
from django.conf import settings
from django.contrib.auth import logout
from io import BytesIO
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.http import require_POST
from django.http import JsonResponse
import os

# --- Импорт xhtml2pdf ---
XHTML2PDF_AVAILABLE = False  # <-- Инициализируем значением по умолчанию
try:
    from xhtml2pdf import pisa

    XHTML2PDF_AVAILABLE = True  # Перезаписываем при успехе
except ImportError:
    print("XHTML2PDF ERROR: Could not import xhtml2pdf.")
    # Остается False


def home(request):
    featured_destinations = Destination.objects.filter(featured=True)[:6]
    top_hotels = Hotel.objects.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')[:4]
    popular_excursions = Excursion.objects.order_by('-created_at')[:4]

    context = {
        'featured_destinations': featured_destinations,
        'top_hotels': top_hotels,
        'popular_excursions': popular_excursions,
    }
    return render(request, 'tourgid/home.html', context)


def destinations(request):
    # Get filter parameters from request
    country = request.GET.get('country', '')
    climate = request.GET.get('climate', '')
    vacation_type = request.GET.get('vacation_type', '')

    # Start with all destinations
    destinations_list = Destination.objects.all()

    # Apply filters if provided
    if country:
        destinations_list = destinations_list.filter(country__icontains=country)
    if climate:
        destinations_list = destinations_list.filter(climate__icontains=climate)
    if vacation_type:
        destinations_list = destinations_list.filter(vacation_type__icontains=vacation_type)

    # Pagination
    paginator = Paginator(destinations_list, 9)  # Show 9 destinations per page
    page = request.GET.get('page')
    destinations = paginator.get_page(page)

    # Get unique countries for filtering
    countries = Destination.objects.values_list('country', flat=True).distinct()

    context = {
        'destinations': destinations,
        'countries': countries,
        'selected_country': country,
        'selected_climate': climate,
        'selected_vacation_type': vacation_type,
    }
    return render(request, 'tourgid/destinations.html', context)


def destination_detail(request, destination_id):
    destination = get_object_or_404(Destination, id=destination_id)
    hotels = destination.hotels.all()
    attractions = destination.attractions.all()
    excursions = destination.excursions.all()
    reviews = destination.reviews.filter(approved=True)

    # Calculate average rating
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0

    context = {
        'destination': destination,
        'hotels': hotels,
        'attractions': attractions,
        'excursions': excursions,
        'reviews': reviews,
        'avg_rating': avg_rating,
    }
    return render(request, 'tourgid/destination_detail.html', context)


def hotels(request):
    # Get filter parameters
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    rating = request.GET.get('rating')
    accommodation_type = request.GET.get('accommodation_type', '')
    destination = request.GET.get('destination', '')

    # Start with all hotels
    hotels_list = Hotel.objects.all()

    # Apply filters
    if min_price:
        hotels_list = hotels_list.filter(price_per_night__gte=min_price)
    if max_price:
        hotels_list = hotels_list.filter(price_per_night__lte=max_price)
    if rating:
        hotels_list = hotels_list.filter(rating__gte=rating)
    if accommodation_type:
        hotels_list = hotels_list.filter(accommodation_type=accommodation_type)
    if destination:
        try:
            hotels_list = hotels_list.filter(destination__id=int(destination))
        except (ValueError, TypeError):
            hotels_list = hotels_list.none()

    # Sorting
    sort_by = request.GET.get('sort', 'rating')
    if sort_by == 'price_low':
        hotels_list = hotels_list.order_by('price_per_night')
    elif sort_by == 'price_high':
        hotels_list = hotels_list.order_by('-price_per_night')
    elif sort_by == 'rating':
        hotels_list = hotels_list.order_by('-rating')

    # Pagination
    paginator = Paginator(hotels_list, 9)
    page = request.GET.get('page')
    hotels = paginator.get_page(page)

    # Get all destinations for filtering
    destinations = Destination.objects.all()

    context = {
        'hotels': hotels,
        'destinations': destinations,
        'min_price': min_price,
        'max_price': max_price,
        'rating': rating,
        'accommodation_type': accommodation_type,
        'selected_destination': destination,
        'sort': sort_by,
        'accommodation_types': Hotel.ACCOMMODATION_TYPES,
    }
    return render(request, 'tourgid/hotels.html', context)


def hotel_detail(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)
    reviews = hotel.reviews.filter(approved=True)

    # Related hotels in the same destination
    related_hotels = Hotel.objects.filter(destination=hotel.destination).exclude(id=hotel.id)[:4]

    context = {
        'hotel': hotel,
        'reviews': reviews,
        'related_hotels': related_hotels,
    }
    return render(request, 'tourgid/hotel_detail.html', context)


def excursions(request):
    # --- Получаем параметры из GET-запроса ---
    search_query = request.GET.get('search', '')  # Поле поиска
    destination_id = request.GET.get('destination', '')  # ID Направления
    excursion_type = request.GET.get('excursion_type', '')  # Тип экскурсии
    selected_tags_slugs = request.GET.getlist('tags')  # Список слагов тегов
    sort_by = request.GET.get('sort', 'popularity')  # Сортировка (по умолчанию - популярность)
    # max_price = request.GET.get('max_price') # Этот фильтр не используется в твоем новом шаблоне, убираем пока

    # Start with all excursions, prefetch related objects
    excursions_list = Excursion.objects.prefetch_related('tags', 'destination').all()

    # --- Применяем фильтры ---
    # 1. Фильтр по поисковому запросу (имя, описание, имя направления)
    if search_query:
        excursions_list = excursions_list.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(destination__name__icontains=search_query)
        )

    # 2. Фильтр по Направлению (по ID)
    if destination_id:
        try:
            excursions_list = excursions_list.filter(destination__id=int(destination_id))
        except (ValueError, TypeError):
            pass  # Игнорируем некорректный ID

    # 3. Фильтр по Типу экскурсии
    if excursion_type:
        # Убедимся, что значение есть в списке допустимых типов
        valid_types = [choice[0] for choice in Excursion.EXCURSION_TYPES]
        if excursion_type in valid_types:
            excursions_list = excursions_list.filter(excursion_type=excursion_type)
        # Если excursion_type был взят из твоих предыдущих option ('Guided Tour', 'Adventure'),
        # а в модели EXCURSION_TYPES ключи другие ('cultural', 'adventure'),
        # нужно будет либо согласовать значения, либо сделать маппинг.
        # Пока оставляем так, предполагая, что значения совпадают с ключами в EXCURSION_TYPES.

    # 4. Фильтр по Тегам интересов
    if selected_tags_slugs:
        excursions_list = excursions_list.filter(tags__slug__in=selected_tags_slugs).distinct()

    # --- Применяем сортировку ---
    if sort_by == 'price_low':
        excursions_list = excursions_list.order_by('price')
    elif sort_by == 'price_high':
        excursions_list = excursions_list.order_by('-price')
    elif sort_by == 'duration':
        # Сортировка по duration может быть сложной, если это строка ("3 hours", "Full day")
        # Для корректной сортировки лучше хранить длительность в числовом виде (например, в минутах)
        # Пока оставим сортировку по строке, но результат может быть неидеальным
        excursions_list = excursions_list.order_by('duration')
    elif sort_by == 'popularity':
        # Определим "популярность", например, по количеству бронирований или добавлений в избранное (если есть такие связи)
        # Пока просто сортируем по ID (новые сверху) как заглушку
        excursions_list = excursions_list.order_by('-id')
        # В реальном приложении здесь нужна более сложная логика или аннотация
    else:  # По умолчанию (или если sort_by == 'popularity')
        excursions_list = excursions_list.order_by('-id')  # Например, новые сверху

    # Pagination
    paginator = Paginator(excursions_list, 9)  # Используй свое количество на страницу
    page = request.GET.get('page')
    excursions_page = paginator.get_page(page)  # Используем excursions_page, чтобы не перекрыть имя модели

    # Get data for filters
    all_destinations = Destination.objects.all()
    all_tags = InterestTag.objects.all()
    # Получаем типы экскурсий из модели
    excursion_types_choices = Excursion.EXCURSION_TYPES

    context = {
        'excursions': excursions_page,  # Передаем страницу пагинатора
        'all_destinations': all_destinations,  # Для селекта направлений
        'excursion_types': excursion_types_choices,  # Для селекта типов
        'all_tags': all_tags,  # Для чекбоксов тегов
        'selected_tags': selected_tags_slugs,  # Выбранные слаги тегов
        'selected_destination_id': destination_id,  # Выбранный ID направления
        'selected_type': excursion_type,  # Выбранный тип
        'search_query': search_query,  # Поисковый запрос
        'sort_by': sort_by,  # Текущая сортировка
    }
    return render(request, 'tourgid/excursions.html', context)


def excursion_detail(request, excursion_id):
    excursion = get_object_or_404(Excursion, id=excursion_id)
    attractions = excursion.included_attractions.all()

    # Related excursions in the same destination
    related_excursions = Excursion.objects.filter(
        destination=excursion.destination
    ).exclude(id=excursion.id)[:4]

    context = {
        'excursion': excursion,
        'attractions': attractions,
        'related_excursions': related_excursions,
    }
    return render(request, 'tourgid/excursion_detail.html', context)


def about(request):
    return render(request, 'tourgid/about.html')


@login_required
def add_review(request, content_type, content_id):
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        if content_type == 'hotel':
            content_object = get_object_or_404(Hotel, id=content_id)
            review = Review(
                user=request.user,
                hotel=content_object,
                author=request.user.username,
                rating=rating,
                comment=comment
            )
        elif content_type == 'destination':
            content_object = get_object_or_404(Destination, id=content_id)
            review = Review(
                user=request.user,
                destination=content_object,
                author=request.user.username,
                rating=rating,
                comment=comment
            )
        elif content_type == 'attraction':
            content_object = get_object_or_404(Attraction, id=content_id)
            review = Review(
                user=request.user,
                attraction=content_object,
                author=request.user.username,
                rating=rating,
                comment=comment
            )

        review.save()

        # Redirect back to the detail page
        if content_type == 'hotel':
            return redirect('hotel_detail', hotel_id=content_id)
        elif content_type == 'destination':
            return redirect('destination_detail', destination_id=content_id)
        elif content_type == 'attraction':
            return redirect('attraction_detail', attraction_id=content_id)

    # If not POST or other error, redirect to home
    return redirect('home')


@login_required
def add_to_favorites(request, content_type, content_id):
    if request.method == 'POST':
        if content_type == 'destination':
            content_object = get_object_or_404(Destination, id=content_id)
            favorite, created = Favorite.objects.get_or_create(
                user=request.user,
                destination=content_object
            )
        elif content_type == 'hotel':
            content_object = get_object_or_404(Hotel, id=content_id)
            favorite, created = Favorite.objects.get_or_create(
                user=request.user,
                hotel=content_object
            )
        elif content_type == 'attraction':
            content_object = get_object_or_404(Attraction, id=content_id)
            favorite, created = Favorite.objects.get_or_create(
                user=request.user,
                attraction=content_object
            )
        elif content_type == 'excursion':
            content_object = get_object_or_404(Excursion, id=content_id)
            favorite, created = Favorite.objects.get_or_create(
                user=request.user,
                excursion=content_object
            )

        # Redirect back to the referring page
        next_url = request.POST.get('next', '/')
        return redirect(next_url)

    return redirect('home')


@login_required
def remove_from_favorites(request, favorite_id):
    favorite = get_object_or_404(Favorite, id=favorite_id, user=request.user)
    favorite.delete()
    next_url = request.POST.get('next', '/')
    return redirect(next_url)


@login_required
def user_favorites(request):
    favorites = Favorite.objects.filter(user=request.user)

    context = {
        'favorites': favorites,
    }
    return render(request, 'tourgid/user_favorites.html', context)


@login_required
def generate_city_guide(request, destination_id):
    destination = get_object_or_404(Destination, id=destination_id)
    attractions = destination.attractions.all()

    # Create a basic guide (in a real app, this would be more sophisticated)
    guide = Guide.objects.create(
        title=f"Guide to {destination.name}",
        user=request.user,
        destination=destination,
        content=f"Explore the beautiful {destination.name} with our curated guide.",
        is_public=False
    )

    # Add attractions to the guide
    for attraction in attractions:
        guide.attractions.add(attraction)

    # In a real app, you'd generate a PDF here

    return redirect('guide_detail', guide_id=guide.id)


@login_required
def guide_detail(request, guide_id):
    guide = get_object_or_404(Guide, id=guide_id)

    # Check if the user has permission to view this guide
    if not guide.is_public and guide.user != request.user:
        return redirect('home')

    context = {
        'guide': guide,
        'attractions': guide.attractions.all(),
    }
    return render(request, 'tourgid/guide_detail.html', context)


def attraction_detail(request, attraction_id):
    attraction = get_object_or_404(Attraction, id=attraction_id)
    reviews = attraction.reviews.filter(approved=True)

    # Related attractions in the same destination
    related_attractions = Attraction.objects.filter(
        destination=attraction.destination
    ).exclude(id=attraction.id)[:4]

    context = {
        'attraction': attraction,
        'reviews': reviews,
        'related_attractions': related_attractions,
    }
    return render(request, 'tourgid/attraction_detail.html', context)


def search(request):
    query = request.GET.get('q', '')

    if query:
        destinations = Destination.objects.filter(
            Q(name__icontains=query) | Q(country__icontains=query) | Q(city__icontains=query)
        )

        hotels = Hotel.objects.filter(
            Q(name__icontains=query) | Q(destination__name__icontains=query)
        )

        attractions = Attraction.objects.filter(
            Q(name__icontains=query) | Q(destination__name__icontains=query)
        )

        excursions = Excursion.objects.filter(
            Q(name__icontains=query) | Q(destination__name__icontains=query)
        )
    else:
        destinations = Destination.objects.none()
        hotels = Hotel.objects.none()
        attractions = Attraction.objects.none()
        excursions = Excursion.objects.none()

    context = {
        'query': query,
        'destinations': destinations,
        'hotels': hotels,
        'attractions': attractions,
        'excursions': excursions,
    }

    return render(request, 'tourgid/search_results.html', context)


def attractions(request):
    """View function for listing all attractions."""
    attraction_list = Attraction.objects.all().order_by('-created_at')

    # Handle search and filtering
    query = request.GET.get('q', '')
    attraction_type = request.GET.get('type', '')

    if query:
        attraction_list = attraction_list.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(destination__name__icontains=query)
        )

    if attraction_type:
        attraction_list = attraction_list.filter(attraction_type=attraction_type)

    # Pagination
    paginator = Paginator(attraction_list, 12)  # Show 12 attractions per page
    page = request.GET.get('page')

    try:
        attractions = paginator.page(page)
    except PageNotAnInteger:
        attractions = paginator.page(1)
    except EmptyPage:
        attractions = paginator.page(paginator.num_pages)

    # Get attraction types for filter
    attraction_types = dict(Attraction.ATTRACTION_TYPES)

    # Get popular destinations (featured or with most attractions)
    popular_destinations = Destination.objects.filter(featured=True)[:4]
    if popular_destinations.count() < 4:
        # Add more destinations if we don't have enough featured ones
        existing_ids = list(popular_destinations.values_list('id', flat=True))
        more_destinations = Destination.objects.exclude(id__in=existing_ids).annotate(
            attraction_count=models.Count('attractions')
        ).order_by('-attraction_count')[:4 - popular_destinations.count()]
        popular_destinations = list(popular_destinations) + list(more_destinations)

    context = {
        'attractions': attractions,
        'query': query,
        'attraction_type': attraction_type,
        'attraction_types': attraction_types,
        'total_attractions': attraction_list.count(),
        'popular_destinations': popular_destinations,
    }

    return render(request, 'tourgid/attractions.html', context)


@login_required
def user_profile(request):
    """User profile view with bookings, favorites, and reviews"""
    user = request.user
    bookings = user.bookings.all().order_by('-created_at')[:5]
    favorites = user.favorites.all().order_by('-created_at')
    reviews = user.reviews.all().order_by('-created_at')[:5]

    context = {
        'user': user,
        'bookings': bookings,
        'favorites': favorites,
        'reviews': reviews,
    }
    return render(request, 'tourgid/profile.html', context)


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# Импортируй свои формы (нужно будет создать)
# from .forms import ProfileUpdateForm, UserUpdateForm, PreferencesForm

@login_required
def user_settings(request):
    # Получаем профиль пользователя (если он есть)
    # Это стандартный способ, если Profile связан с User через OneToOneField
    # и related_name не указан или равен 'profile'
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        # Если профиля нет, можно его создать или обработать ошибку
        profile = Profile.objects.create(user=request.user)
        # Или profile = None, и обрабатывать это ниже

    if request.method == 'POST':
        if 'save_profile' in request.POST:
            # --- ОБРАБОТКА ФОРМЫ ПРОФИЛЯ (РЕАЛИЗАЦИЯ) ---
            user_form = UserUpdateForm(request.POST, instance=request.user)
            # Передаем request.FILES для обработки загрузки изображения
            profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                messages.success(request, 'Ваш профиль успешно обновлен!')
                return redirect('settings') # Перезагружаем страницу настроек
            else:
                # Если есть ошибки, выводим их и рендерим шаблон снова
                messages.error(request, 'Пожалуйста, исправьте ошибки в форме профиля.')
                # Формы с ошибками будут переданы в контекст в блоке else ниже

        elif 'save_preferences' in request.POST:
             # ... (обработка формы предпочтений, пока заглушка) ...
             messages.info(request, 'Обработка формы предпочтений еще не реализована.')
             return redirect('settings')

        elif 'save_notifications' in request.POST:
             # ... (обработка формы уведомлений, пока заглушка) ...
             messages.info(request, 'Обработка формы уведомлений еще не реализована.')
             return redirect('settings')

        # Добавь elif для других кнопок...

    # --- ОБРАБОТКА GET-ЗАПРОСА или если POST не прошел валидацию ---
    # Создаем экземпляры форм для отображения (или передаем формы с ошибками из POST)
    # Если в POST были ошибки, сюда попадут формы с этими ошибками
    if request.method != 'POST' or 'save_profile' not in request.POST:
         user_form = UserUpdateForm(instance=request.user)
         profile_form = ProfileUpdateForm(instance=profile)
    # Добавь создание других форм (PreferencesForm, NotificationSettingsForm) здесь, если нужно

    # ... (остальной код для получения данных для GET, как было раньше) ...
    try:
        preferred_destination_ids = [dest.id for dest in request.user.profile.preferred_destinations.all()]
        travel_interest_ids = [interest.id for interest in request.user.profile.travel_interests.all()]
    except AttributeError:
         preferred_destination_ids = []
         travel_interest_ids = []

    continents = Destination.objects.values_list('country', flat=True).distinct()
    travel_interests = InterestTag.objects.all()


    context = {
        'user': request.user,
        'user_form': user_form, # Передаем формы в контекст
        'profile_form': profile_form,
        # 'preferences_form': preferences_form, # Если создана
        # 'notification_form': notification_form, # Если создана
        'preferred_destination_ids': preferred_destination_ids,
        'travel_interest_ids': travel_interest_ids,
        'continents': continents,
        'travel_interests': travel_interests,
    }
    return render(request, 'tourgid/settings.html', context)


@login_required
def user_bookings(request):
    """User bookings view"""
    bookings = request.user.bookings.all().order_by('-created_at')

    context = {
        'bookings': bookings,
    }
    return render(request, 'tourgid/bookings.html', context)


def signup(request):
    """Обработка регистрации пользователя"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save() # Создает нового пользователя в базе

            # Опционально: Залогинить пользователя сразу после регистрации
            # login(request, user)

            messages.success(request, 'Вы успешно зарегистрированы! Теперь вы можете войти.')
            return redirect('login') # Используй имя URL для страницы входа
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
            # Ошибки будут доступны в шаблоне через {{ form.errors }}
    else:
        form = UserCreationForm()
    context = {'form': form}
    return render(request, 'tourgid/auth/signup.html', context)


@login_required
def download_guide_pdf(request, destination_id):
    # Check if the xhtml2pdf library is available
    if not XHTML2PDF_AVAILABLE:
        messages.error(request, "Error: PDF generation library (xhtml2pdf) is not installed.")
        return redirect('home')  # Redirect user to another view

    try:
        # Retrieve the destination object or return a 404 if not found
        destination = get_object_or_404(Destination, id=destination_id)
        user = request.user

        # Collect data for the context
        hotels = Hotel.objects.filter(destination=destination)[:5]
        attractions = Attraction.objects.filter(destination=destination)[:10]
        excursions = Excursion.objects.filter(destination=destination)[:5]
        context = {
            'destination': destination,
            'hotels': hotels,
            'attractions': attractions,
            'excursions': excursions,
            'user': user,
            'generation_date': timezone.now(),
            'STATIC_URL': settings.STATIC_URL,
            'MEDIA_URL': settings.MEDIA_URL,
        }

        # Render the HTML content
        try:
            html_string = render_to_string('tourgid/pdf/guide_template.html', context)
        except TemplateDoesNotExist:
            messages.error(request, "Template for the guide not found.")
            return redirect('some_view')

        # Generate the PDF
        result_buffer = BytesIO()
        try:
            def link_callback(uri, rel):
                """
                Resolves static and media file paths for the PDF renderer.
                """
                if uri.startswith(settings.MEDIA_URL):
                    path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
                elif uri.startswith(settings.STATIC_URL):
                    path = os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ""))
                elif uri.startswith(('http://', 'https://')):
                    return uri
                else:
                    return None

                if not os.path.isfile(path):
                    return None
                return path

            # Call xhtml2pdf to create the PDF
            pdf_status = pisa.CreatePDF(
                src=html_string,
                dest=result_buffer,
                link_callback=link_callback
            )
            if pdf_status.err:
                raise Exception(f"PDF generation error: {pdf_status.err}")
            pdf_bytes = result_buffer.getvalue()
        finally:
            result_buffer.close()

        # Return the response with the generated PDF
        if pdf_bytes:
            response = HttpResponse(pdf_bytes, content_type='application/pdf')
            filename_part = destination.slug if hasattr(destination, 'slug') else str(destination.id)
            filename = f"guide_{filename_part}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        else:
            messages.error(request, "Failed to generate the PDF file.")
            return redirect('some_view')

    except Http404:
        messages.error(request, "The requested destination was not found.")
        return redirect('some_view')
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('some_view')

@login_required
def export_user_data(request):
    # Здесь будет логика сбора данных пользователя
    # (профиль, бронирования, избранное и т.д.)
    # и формирования ответа (например, JSON или файл)
    user_data = {
        'username': request.user.username,
        'email': request.user.email,
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        # Добавь сюда другие данные...
        'message': 'Функция экспорта данных еще не реализована полностью.'
    }
    # Пока просто вернем JSON
    return JsonResponse(user_data)

@login_required
@require_POST # Эта функция должна принимать только POST-запросы
def account_delete(request):
    user = request.user
    password = request.POST.get('password_confirm') # Получаем пароль из формы

    if not password:
        messages.error(request, 'Пожалуйста, введите пароль для подтверждения.')
        return redirect('settings') # Возвращаем на страницу настроек

    # Проверяем пароль пользователя
    if not user.check_password(password):
        messages.error(request, 'Неверный пароль.')
        return redirect('settings') # Возвращаем на страницу настроек

    try:
        # Пароль верный, удаляем пользователя
        user_pk = user.pk # Сохраняем pk на всякий случай, если понадобится для логов
        user.delete()
        logout(request) # Разлогиниваем
        messages.success(request, 'Ваш аккаунт был успешно удален.')
        return redirect('home') # Перенаправляем на главную
    except Exception as e:
        # Обработка возможных ошибок при удалении
        messages.error(request, f'Произошла ошибка при удалении аккаунта: {e}')
        return redirect('settings')