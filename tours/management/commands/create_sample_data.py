from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from tours.models import Destination, Hotel, Attraction, Excursion
from django.utils.text import slugify
import random

class Command(BaseCommand):
    help = 'Creates sample data for the TourGid website'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Creating sample data...'))
        
        # Create destinations
        destinations = [
            {
                'name': 'Paris',
                'description': 'The City of Light, known for its stunning architecture, art museums, and romantic atmosphere.',
                'country': 'France',
                'city': 'Paris',
                'climate': 'Temperate',
                'vacation_type': 'City',
                'featured': True,
                'latitude': 48.8566,
                'longitude': 2.3522,
            },
            {
                'name': 'Bali',
                'description': 'A beautiful Indonesian island known for its forested volcanic mountains, iconic rice paddies, beaches, and coral reefs.',
                'country': 'Indonesia',
                'city': 'Denpasar',
                'climate': 'Tropical',
                'vacation_type': 'Beach',
                'featured': True,
                'latitude': -8.4095,
                'longitude': 115.1889,
            },
            {
                'name': 'Tokyo',
                'description': 'Japan\'s busy capital, featuring a mix of ultramodern and traditional elements, from neon-lit skyscrapers to historic temples.',
                'country': 'Japan',
                'city': 'Tokyo',
                'climate': 'Temperate',
                'vacation_type': 'City',
                'featured': True,
                'latitude': 35.6762,
                'longitude': 139.6503,
            },
            {
                'name': 'Barcelona',
                'description': 'A vibrant city known for its stunning architecture, rich culture, and beautiful beaches.',
                'country': 'Spain',
                'city': 'Barcelona',
                'climate': 'Mediterranean',
                'vacation_type': 'City',
                'featured': True,
                'latitude': 41.3851,
                'longitude': 2.1734,
            },
            {
                'name': 'Santorini',
                'description': 'Famous for its dramatic views, stunning sunsets, white-washed houses, and blue-domed churches.',
                'country': 'Greece',
                'city': 'Fira',
                'climate': 'Mediterranean',
                'vacation_type': 'Beach',
                'featured': True,
                'latitude': 36.3932,
                'longitude': 25.4615,
            },
            {
                'name': 'New York City',
                'description': 'One of the world\'s most iconic cities, known for its skyscrapers, Broadway shows, and cultural diversity.',
                'country': 'United States',
                'city': 'New York',
                'climate': 'Temperate',
                'vacation_type': 'City',
                'featured': True,
                'latitude': 40.7128,
                'longitude': -74.0060,
            },
        ]

        created_destinations = []
        for dest_data in destinations:
            dest, created = Destination.objects.get_or_create(
                name=dest_data['name'],
                defaults=dest_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created destination: {dest.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Destination already exists: {dest.name}'))
            created_destinations.append(dest)

        # Create hotels for each destination
        hotel_names = [
            'Grand Hotel', 'Luxury Resort & Spa', 'City View Hotel', 
            'Beach Paradise Resort', 'Metropolitan Inn', 'Harmony Suites',
            'Ocean Breeze Hotel', 'Downtown Boutique Hotel', 'The Royal Palace',
            'Sunset Villa Resort'
        ]
        
        for dest in created_destinations:
            for i in range(3):  # Create 3 hotels per destination
                hotel_name = f"{dest.name} {hotel_names[random.randint(0, len(hotel_names) - 1)]}"
                hotel, created = Hotel.objects.get_or_create(
                    name=hotel_name,
                    destination=dest,
                    defaults={
                        'price_per_night': random.randint(100, 500),
                        'rating': random.randint(3, 5),
                        'description': f'A beautiful hotel in the heart of {dest.name}, offering comfort and luxury.',
                        'address': f'{random.randint(1, 999)} Main Street, {dest.city}, {dest.country}',
                        'accommodation_type': random.choice(['hotel', 'resort', 'apartment', 'villa']),
                        'amenities': {
                            'wifi': True,
                            'pool': random.choice([True, False]),
                            'spa': random.choice([True, False]),
                            'restaurant': random.choice([True, False]),
                            'gym': random.choice([True, False]),
                            'parking': True,
                            'ac': True,
                        },
                        'latitude': dest.latitude + (random.random() - 0.5) * 0.1,
                        'longitude': dest.longitude + (random.random() - 0.5) * 0.1,
                        'booking_url': 'https://example.com/booking',
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created hotel: {hotel.name}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Hotel already exists: {hotel.name}'))

        # Create attractions for each destination
        attraction_types = ['cultural', 'nature', 'entertainment', 'shopping', 'food', 'sports']
        attraction_names = [
            'Museum', 'Park', 'Monument', 'Tower', 'Cathedral', 'Palace', 
            'Market', 'Garden', 'Square', 'Theater', 'Stadium', 'Beach',
            'Mountain', 'Castle', 'Temple', 'Gallery', 'Zoo'
        ]
        
        for dest in created_destinations:
            for i in range(4):  # Create 4 attractions per destination
                attraction_name = f"{dest.name} {attraction_names[random.randint(0, len(attraction_names) - 1)]}"
                attraction_type = attraction_types[random.randint(0, len(attraction_types) - 1)]
                
                attraction, created = Attraction.objects.get_or_create(
                    name=attraction_name,
                    destination=dest,
                    defaults={
                        'description': f'A must-visit {attraction_type} attraction in {dest.name}.',
                        'latitude': dest.latitude + (random.random() - 0.5) * 0.1,
                        'longitude': dest.longitude + (random.random() - 0.5) * 0.1,
                        'attraction_type': attraction_type,
                        'price': random.randint(0, 50),
                        'opening_hours': '9:00 AM - 5:00 PM',
                        'website': 'https://example.com/attraction',
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created attraction: {attraction.name}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Attraction already exists: {attraction.name}'))

        # Create excursions for each destination
        excursion_types = ['cultural', 'adventure', 'shopping', 'food', 'nature', 'historical']
        excursion_names = [
            'City Tour', 'Culinary Experience', 'Nature Hike', 'Cultural Heritage Tour',
            'Adventure Day Trip', 'Historical Walking Tour', 'Shopping Excursion',
            'Local Cuisine Exploration', 'Night City Tour', 'Photography Tour'
        ]
        
        for dest in created_destinations:
            attractions = Attraction.objects.filter(destination=dest)
            for i in range(3):  # Create 3 excursions per destination
                excursion_name = f"{dest.name} {excursion_names[random.randint(0, len(excursion_names) - 1)]}"
                excursion_type = excursion_types[random.randint(0, len(excursion_types) - 1)]
                
                excursion, created = Excursion.objects.get_or_create(
                    name=excursion_name,
                    destination=dest,
                    defaults={
                        'description': f'An exciting {excursion_type} excursion in {dest.name}, perfect for travelers.',
                        'price': random.randint(50, 200),
                        'duration': f'{random.randint(2, 8)} hours',
                        'excursion_type': excursion_type,
                        'meeting_point': f'Central point in {dest.name}',
                        'booking_url': 'https://example.com/excursion',
                    }
                )
                if created:
                    # Add random attractions to this excursion
                    for attraction in attractions[:min(len(attractions), 2)]:
                        excursion.included_attractions.add(attraction)
                    self.stdout.write(self.style.SUCCESS(f'Created excursion: {excursion.name}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Excursion already exists: {excursion.name}'))

        self.stdout.write(self.style.SUCCESS('Successfully created sample data!')) 