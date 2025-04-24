from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Avg, Count
from django.contrib.auth.models import User
from tours.models import Destination, Hotel, Attraction, Review, Excursion, Booking, Guide, Favorite
from .serializers import (
    UserSerializer, DestinationSerializer, HotelSerializer, AttractionSerializer,
    ReviewSerializer, ExcursionSerializer, BookingSerializer, GuideSerializer, ExcursionSerializer, FavoriteSerializer
)
from .filters import ExcursionFilter
from .permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from tours.tasks import get_weather_data, update_hotel_ratings, check_booking_status, send_booking_confirmation_email, generate_guide_pdf_task
from tours.utils.maps import get_coordinates_from_address, get_nearby_attractions, get_directions
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

class DestinationViewSet(viewsets.ModelViewSet):
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['country', 'climate', 'vacation_type', 'featured']
    search_fields = ['name', 'city', 'country', 'description']
    ordering_fields = ['name', 'created_at', 'country']
    
    @action(detail=True, methods=['get'])
    def hotels(self, request, pk=None):
        destination = self.get_object()
        hotels = Hotel.objects.filter(destination=destination)
        serializer = HotelSerializer(hotels, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def attractions(self, request, pk=None):
        destination = self.get_object()
        attractions = Attraction.objects.filter(destination=destination)
        serializer = AttractionSerializer(attractions, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def excursions(self, request, pk=None):
        destination = self.get_object()
        excursions = Excursion.objects.filter(destination=destination)
        serializer = ExcursionSerializer(excursions, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        destination = self.get_object()
        reviews = Review.objects.filter(destination=destination, approved=True)
        serializer = ReviewSerializer(reviews, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])  # Добавляем явное требование аутентификации
    def generate_guide(self, request, pk=None):
        """
        Запускает фоновую генерацию PDF-путеводителя для этого направления
        для текущего аутентифицированного пользователя.
        """
        destination = self.get_object()  # Получаем объект Destination по pk из URL
        user = request.user  # Получаем текущего пользователя

        # Опционально: Проверка, не генерируется ли гайд слишком часто
        # Например, проверить время последней генерации для этого юзера/направления
        # last_guide = Guide.objects.filter(user=user, destination=destination).order_by('-updated_at').first()
        # if last_guide and timezone.now() - last_guide.updated_at < timedelta(minutes=5):
        #     return Response({'message': 'Guide generation request too frequent. Please wait.'}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        # Запускаем нашу задачу в фоне, передавая ID направления и ID пользователя
        task = generate_guide_pdf_task.delay(destination.id, user.id)

        # Возвращаем ответ, что задача принята в обработку
        return Response({
            'message': f'Запрос на генерацию PDF-путеводителя для "{destination.name}" принят.',
            'task_id': task.id  # task.id можно использовать для отслеживания статуса задачи (более сложная реализация)
        },
            status=status.HTTP_202_ACCEPTED)  # Статус 202 Accepted означает, что запрос принят, но обработка еще не завершена
    @action(detail=True, methods=['get'])
    def weather(self, request, pk=None):
        """Get weather data for this destination"""
        destination = self.get_object()
        
        # Run the task synchronously for this API endpoint
        weather_data = get_weather_data.delay(destination.id)
        
        return Response({
            'message': f'Weather data request initiated for {destination.name}',
            'task_id': weather_data.id
        })

    @action(detail=True, methods=['get'])
    def nearby_attractions(self, request, pk=None):
        """Get nearby attractions using Google Maps API"""
        destination = self.get_object()
        
        if not destination.latitude or not destination.longitude:
            return Response({
                'error': 'Destination does not have coordinates'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get optional query parameters
        radius = request.query_params.get('radius', 5000)
        attraction_type = request.query_params.get('type', None)
        
        attractions = get_nearby_attractions(
            destination.latitude, 
            destination.longitude,
            radius=radius,
            attraction_type=attraction_type
        )
        
        return Response(attractions)

class HotelViewSet(viewsets.ModelViewSet):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['destination', 'accommodation_type', 'rating']
    search_fields = ['name', 'description', 'address', 'destination__name']
    ordering_fields = ['name', 'rating', 'price_per_night']
    
    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        hotel = self.get_object()
        reviews = Review.objects.filter(hotel=hotel, approved=True)
        serializer = ReviewSerializer(reviews, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        featured_hotels = Hotel.objects.annotate(
            review_count=Count('reviews'),
            avg_rating=Avg('reviews__rating')
        ).filter(review_count__gt=0).order_by('-avg_rating', '-rating')[:10]
        
        serializer = self.get_serializer(featured_hotels, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def update_all_ratings(self, request):
        """Update ratings for all hotels based on reviews"""
        task = update_hotel_ratings.delay()
        
        return Response({
            'message': 'Hotel ratings update initiated',
            'task_id': task.id
        })

    @action(detail=True, methods=['get'])
    def directions(self, request, pk=None):
        """Get directions to the hotel from a specified location"""
        hotel = self.get_object()
        
        if not hotel.latitude or not hotel.longitude:
            return Response({
                'error': 'Hotel does not have coordinates'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get query parameters
        origin_lat = request.query_params.get('origin_lat', None)
        origin_lng = request.query_params.get('origin_lng', None)
        mode = request.query_params.get('mode', 'driving')
        
        if not origin_lat or not origin_lng:
            return Response({
                'error': 'Origin coordinates are required (origin_lat, origin_lng)'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        directions = get_directions(
            float(origin_lat),
            float(origin_lng),
            hotel.latitude,
            hotel.longitude,
            mode=mode
        )
        
        if not directions:
            return Response({
                'error': 'Failed to get directions'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(directions)

class AttractionViewSet(viewsets.ModelViewSet):
    queryset = Attraction.objects.all()
    serializer_class = AttractionSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['destination', 'attraction_type']
    search_fields = ['name', 'description', 'destination__name']
    ordering_fields = ['name', 'price']
    
    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        attraction = self.get_object()
        reviews = Review.objects.filter(attraction=attraction, approved=True)
        serializer = ReviewSerializer(reviews, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def directions(self, request, pk=None):
        """Get directions to the attraction from a specified location"""
        attraction = self.get_object()
        
        if not attraction.latitude or not attraction.longitude:
            return Response({
                'error': 'Attraction does not have coordinates'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get query parameters
        origin_lat = request.query_params.get('origin_lat', None)
        origin_lng = request.query_params.get('origin_lng', None)
        mode = request.query_params.get('mode', 'driving')
        
        if not origin_lat or not origin_lng:
            return Response({
                'error': 'Origin coordinates are required (origin_lat, origin_lng)'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        directions = get_directions(
            float(origin_lat),
            float(origin_lng),
            attraction.latitude,
            attraction.longitude,
            mode=mode
        )
        
        if not directions:
            return Response({
                'error': 'Failed to get directions'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(directions)

class ExcursionViewSet(viewsets.ModelViewSet):
    queryset = Excursion.objects.prefetch_related('tags').all() # Добавили prefetch_related для оптимизации запроса тегов
    serializer_class = ExcursionSerializer
    permission_classes = [IsAdminOrReadOnly] # У тебя здесь могут быть другие permissions

    # --- ОБНОВЛЯЕМ НАСТРОЙКИ ФИЛЬТРАЦИИ ---
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    # filterset_fields = ['destination', 'excursion_type'] # <-- ЭТУ СТРОКУ УДАЛЯЕМ ИЛИ КОММЕНТИРУЕМ
    filterset_class = ExcursionFilter # <-- ДОБАВЛЯЕМ ЭТУ СТРОКУ, чтобы использовать наш класс фильтра
    search_fields = ['name', 'description', 'destination__name', 'meeting_point'] # Эти поля остаются для поиска
    ordering_fields = ['name', 'price', 'duration'] # Эти поля остаются для сортировки

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['hotel', 'attraction', 'destination', 'rating', 'approved']
    ordering_fields = ['created_at', 'rating']
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'hotel', 'excursion']
    ordering_fields = ['created_at', 'check_in_date', 'excursion_date']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Booking.objects.all()
        return Booking.objects.filter(user=user)
    
    def perform_create(self, serializer):
        import uuid
        booking_reference = str(uuid.uuid4()).upper()[:8]
        serializer.save(user=self.request.user, booking_reference=booking_reference)

    @action(detail=True, methods=['post'])
    def resend_confirmation(self, request, pk=None):
        """Resend booking confirmation email"""
        booking = self.get_object()
        
        if booking.status != 'confirmed':
            return Response({
                'error': 'Cannot send confirmation for a booking that is not confirmed'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        task = send_booking_confirmation_email.delay(booking.id)
        
        return Response({
            'message': f'Confirmation email sending initiated for booking {booking.id}',
            'task_id': task.id
        })
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def check_pending_bookings(self, request):
        """Check and update status of pending bookings"""
        task = check_booking_status.delay()
        
        return Response({
            'message': 'Pending bookings check initiated',
            'task_id': task.id
        })

class GuideViewSet(viewsets.ModelViewSet):
    serializer_class = GuideSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['destination', 'is_public']
    search_fields = ['title', 'content', 'destination__name']
    ordering_fields = ['created_at', 'title']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Guide.objects.all()
        return Guide.objects.filter(is_public=True) | Guide.objects.filter(user=user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

@method_decorator(csrf_exempt, name='dispatch')
class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]
    #,IsOwnerOrReadOnly
    
    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @csrf_exempt
    @api_view(['POST'])
    @action(detail=False, methods=['post'])
    def toggle_favorite(self, request):
        user = request.user
        
        destination_id = request.data.get('destination')
        hotel_id = request.data.get('hotel')
        attraction_id = request.data.get('attraction')
        excursion_id = request.data.get('excursion')
        
        if not any([destination_id, hotel_id, attraction_id, excursion_id]):
            return Response(
                {"error": "You must provide at least one of: destination, hotel, attraction, or excursion"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if favorite already exists
        favorite = None
        
        if destination_id:
            destination = get_object_or_404(Destination, pk=destination_id)
            favorite = Favorite.objects.filter(user=user, destination=destination).first()
            if not favorite:
                favorite = Favorite.objects.create(user=user, destination=destination)
                return Response(FavoriteSerializer(favorite).data, status=status.HTTP_201_CREATED)
        
        elif hotel_id:
            hotel = get_object_or_404(Hotel, pk=hotel_id)
            favorite = Favorite.objects.filter(user=user, hotel=hotel).first()
            if not favorite:
                favorite = Favorite.objects.create(user=user, hotel=hotel)
                return Response(FavoriteSerializer(favorite).data, status=status.HTTP_201_CREATED)
                
        elif attraction_id:
            attraction = get_object_or_404(Attraction, pk=attraction_id)
            favorite = Favorite.objects.filter(user=user, attraction=attraction).first()
            if not favorite:
                favorite = Favorite.objects.create(user=user, attraction=attraction)
                return Response(FavoriteSerializer(favorite).data, status=status.HTTP_201_CREATED)
                
        elif excursion_id:
            excursion = get_object_or_404(Excursion, pk=excursion_id)
            favorite = Favorite.objects.filter(user=user, excursion=excursion).first()
            if not favorite:
                favorite = Favorite.objects.create(user=user, excursion=excursion)
                return Response(FavoriteSerializer(favorite).data, status=status.HTTP_201_CREATED)
        
        # If we got here, the favorite exists, so we should delete it
        if favorite:
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        return Response(
            {"error": "Something went wrong."},
            status=status.HTTP_400_BAD_REQUEST
        ) 