from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from tours.models import Destination, Hotel, Attraction, Excursion, Review, Guide, Favorite
from django.utils.text import slugify
import random
from datetime import timedelta
from django.utils import timezone

class Command(BaseCommand):
    help = 'Loads sample data for the Tourist Guide application'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting to load sample data...'))
        
        # Create admin user if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'adminpassword')
            self.stdout.write(self.style.SUCCESS('Admin user created'))
        
        # Create regular users
        user_names = ['john', 'emma', 'michael', 'sophia', 'william']
        users = []
        for name in user_names:
            if not User.objects.filter(username=name).exists():
                user = User.objects.create_user(
                    username=name,
                    email=f'{name}@example.com',
                    password=f'{name}password',
                    first_name=name.capitalize(),
                    last_name='Doe'
                )
                users.append(user)
                self.stdout.write(self.style.SUCCESS(f'User {name} created'))
        
        if not users:
            users = User.objects.all()
        
        # Create sample destinations
        destinations = []
        
        destination_data = [
            {
                'name': 'Paris',
                'country': 'France',
                'city': 'Paris',
                'description': 'The City of Light, famous for the Eiffel Tower, Louvre Museum, and exquisite cuisine.',
                'image': 'destinations/paris.jpg',
                'vacation_type': 'Cultural',
            },
            {
                'name': 'Tokyo',
                'country': 'Japan',
                'city': 'Tokyo',
                'description': 'A bustling metropolis that perfectly blends ultramodern and traditional, from neon-lit skyscrapers to historic temples.',
                'image': 'destinations/tokyo.jpg',
                'vacation_type': 'Urban',
            },
            {
                'name': 'New York',
                'country': 'USA',
                'city': 'New York',
                'description': 'The Big Apple featuring iconic landmarks like Times Square, Central Park, and the Statue of Liberty.',
                'image': 'destinations/newyork.jpg',
                'vacation_type': 'Urban',
            },
            {
                'name': 'Rome',
                'country': 'Italy',
                'city': 'Rome',
                'description': 'The Eternal City with a rich history spanning over 2,500 years, home to the Colosseum and Vatican City.',
                'image': 'destinations/rome.jpg',
                'vacation_type': 'Historical',
            },
            {
                'name': 'Sydney',
                'country': 'Australia',
                'city': 'Sydney',
                'description': 'Harbor city known for its iconic Opera House, beautiful beaches, and vibrant culture.',
                'image': 'destinations/sydney.jpg',
                'vacation_type': 'Beach',
            },
        ]
        
        for data in destination_data:
            if not Destination.objects.filter(name=data['name']).exists():
                destination = Destination.objects.create(
                    name=data['name'],
                    country=data['country'],
                    city=data['city'],
                    description=data['description'],
                    climate=random.choice(['Tropical', 'Temperate', 'Mediterranean', 'Desert', 'Continental']),
                    vacation_type=data['vacation_type'],
                    featured=random.choice([True, False]),
                    latitude=random.uniform(-90, 90),
                    longitude=random.uniform(-180, 180),
                )
                destinations.append(destination)
                self.stdout.write(self.style.SUCCESS(f'Destination {data["name"]} created'))
        
        if not destinations:
            destinations = Destination.objects.all()
        
        # Create sample hotels
        hotels = []
        hotel_names = [
            "Grand Hotel", "Royal Palace", "Ocean View", "City Center", 
            "Luxury Inn", "Heritage Suites", "Business Plaza", "Riverside Lodge"
        ]
        
        for destination in destinations:
            for i in range(random.randint(2, 3)):
                name = f"{destination.name} {hotel_names[random.randint(0, len(hotel_names)-1)]}"
                if not Hotel.objects.filter(name=name, destination=destination).exists():
                    hotel = Hotel.objects.create(
                        name=name,
                        destination=destination,
                        price_per_night=random.randint(80, 500),
                        rating=random.uniform(3.0, 5.0),
                        description=f"A wonderful hotel in the heart of {destination.name}.",
                        address=f"{random.randint(1, 999)} Main Street, {destination.name}",
                        accommodation_type=random.choice(['hotel', 'hostel', 'apartment', 'villa', 'resort']),
                        amenities={"wifi": True, "pool": random.choice([True, False]), "spa": random.choice([True, False]), "restaurant": random.choice([True, False])},
                        latitude=destination.latitude + random.uniform(-0.01, 0.01) if destination.latitude else random.uniform(-90, 90),
                        longitude=destination.longitude + random.uniform(-0.01, 0.01) if destination.longitude else random.uniform(-180, 180),
                        booking_url="https://example.com/booking",
                    )
                    hotels.append(hotel)
                    self.stdout.write(self.style.SUCCESS(f'Hotel {name} created'))
        
        if not hotels:
            hotels = Hotel.objects.all()
        
        # Create sample attractions
        attractions = []
        attraction_types = [
            ('cultural', 'Cultural'),
            ('nature', 'Nature'),
            ('entertainment', 'Entertainment'),
            ('shopping', 'Shopping'),
            ('food', 'Food & Dining'),
            ('sports', 'Sports & Activities'),
        ]
        
        for destination in destinations:
            for i in range(random.randint(3, 5)):
                type_tuple = random.choice(attraction_types)
                name = f"{destination.name} {type_tuple[1]}"
                if not Attraction.objects.filter(name=name, destination=destination).exists():
                    attraction = Attraction.objects.create(
                        name=name,
                        destination=destination,
                        description=f"A must-visit {type_tuple[1].lower()} attraction in {destination.name}.",
                        latitude=destination.latitude + random.uniform(-0.02, 0.02) if destination.latitude else random.uniform(-90, 90),
                        longitude=destination.longitude + random.uniform(-0.02, 0.02) if destination.longitude else random.uniform(-180, 180),
                        attraction_type=type_tuple[0],
                        price=random.randint(0, 30) if random.choice([True, False]) else None,
                        opening_hours=f"{random.randint(8, 10)}:00 - {random.randint(17, 20)}:00",
                        website="https://example.com/attraction",
                    )
                    attractions.append(attraction)
                    self.stdout.write(self.style.SUCCESS(f'Attraction {name} created'))
        
        if not attractions:
            attractions = Attraction.objects.all()
        
        # Create sample excursions
        excursions = []
        excursion_types = [
            ('cultural', 'Cultural'),
            ('adventure', 'Adventure'),
            ('shopping', 'Shopping'),
            ('food', 'Food & Culinary'),
            ('nature', 'Nature'),
            ('historical', 'Historical'),
        ]
        
        for destination in destinations:
            for i in range(random.randint(2, 4)):
                type_tuple = random.choice(excursion_types)
                name = f"{destination.name} {type_tuple[1]}"
                if not Excursion.objects.filter(name=name, destination=destination).exists():
                    excursion = Excursion.objects.create(
                        name=name,
                        destination=destination,
                        description=f"Explore {destination.name} with our {type_tuple[1].lower()} tour.",
                        price=random.randint(30, 150),
                        duration=f"{random.randint(2, 8)} hours",
                        excursion_type=type_tuple[0],
                        meeting_point=f"Main entrance of {destination.name} {random.choice(['Museum', 'Hotel', 'Station'])}",
                        booking_url="https://example.com/booking",
                    )
                    # Add some attractions to the excursion
                    dest_attractions = [a for a in attractions if a.destination == destination]
                    if dest_attractions:
                        for _ in range(min(2, len(dest_attractions))):
                            excursion.included_attractions.add(random.choice(dest_attractions))
                    
                    excursions.append(excursion)
                    self.stdout.write(self.style.SUCCESS(f'Excursion {name} created'))
        
        if not excursions:
            excursions = Excursion.objects.all()
        
        # Create sample guides
        guides = []
        guide_topics = ["Complete Travel Guide", "Weekend Itinerary", "Family Travel Guide", "Budget Travel Guide", "Luxury Experience"]
        
        for destination in destinations:
            for i in range(random.randint(1, 2)):
                title = f"{destination.name} {guide_topics[random.randint(0, len(guide_topics)-1)]}"
                if not Guide.objects.filter(title=title, destination=destination).exists():
                    guide = Guide.objects.create(
                        title=title,
                        user=random.choice(users) if random.choice([True, False]) else None,
                        destination=destination,
                        content=f"This comprehensive guide will help you explore {destination.name} like a local. From hidden gems to must-see attractions, we've got you covered.",
                        is_public=random.choice([True, False]),
                    )
                    
                    # Add some attractions to the guide
                    dest_attractions = [a for a in attractions if a.destination == destination]
                    if dest_attractions:
                        for _ in range(min(3, len(dest_attractions))):
                            guide.attractions.add(random.choice(dest_attractions))
                    
                    guides.append(guide)
                    self.stdout.write(self.style.SUCCESS(f'Guide {title} created'))
        
        if not guides:
            guides = Guide.objects.all()
        
        # Create sample reviews
        for i in range(30):
            user = random.choice(users)
            
            # Randomly choose what type of object to review
            review_type = random.choice(['hotel', 'attraction', 'destination'])
            
            if review_type == 'hotel' and hotels:
                obj = random.choice(hotels)
                Review.objects.create(
                    user=user,
                    hotel=obj,
                    author=user.get_full_name() or user.username,
                    rating=random.randint(3, 5),
                    comment=f"{'Great' if random.randint(3, 5) > 3 else 'Good'} hotel, {'would' if random.choice([True, False]) else 'might'} stay again.",
                    approved=True,
                )
                self.stdout.write(self.style.SUCCESS(f'Review for hotel {obj.name} created'))
                
            elif review_type == 'attraction' and attractions:
                obj = random.choice(attractions)
                Review.objects.create(
                    user=user,
                    attraction=obj,
                    author=user.get_full_name() or user.username,
                    rating=random.randint(3, 5),
                    comment=f"{'Amazing' if random.randint(3, 5) > 3 else 'Interesting'} attraction, {'definitely' if random.choice([True, False]) else ''} worth a visit.",
                    approved=True,
                )
                self.stdout.write(self.style.SUCCESS(f'Review for attraction {obj.name} created'))
                
            elif destinations:
                obj = random.choice(destinations)
                Review.objects.create(
                    user=user,
                    destination=obj,
                    author=user.get_full_name() or user.username,
                    rating=random.randint(3, 5),
                    comment=f"{'Loved' if random.randint(3, 5) > 3 else 'Enjoyed'} my trip to {obj.name}, {'would' if random.choice([True, False]) else 'might'} visit again.",
                    approved=True,
                )
                self.stdout.write(self.style.SUCCESS(f'Review for destination {obj.name} created'))
                
        # Create sample favorites
        for user in users:
            # Add some favorite destinations
            for _ in range(random.randint(1, 3)):
                if destinations:
                    destination = random.choice(destinations)
                    if not Favorite.objects.filter(user=user, destination=destination).exists():
                        Favorite.objects.create(
                            user=user,
                            destination=destination,
                        )
                        self.stdout.write(self.style.SUCCESS(f'Favorite destination {destination.name} created for {user.username}'))
            
            # Add some favorite hotels
            for _ in range(random.randint(1, 2)):
                if hotels:
                    hotel = random.choice(hotels)
                    if not Favorite.objects.filter(user=user, hotel=hotel).exists():
                        Favorite.objects.create(
                            user=user,
                            hotel=hotel,
                        )
                        self.stdout.write(self.style.SUCCESS(f'Favorite hotel {hotel.name} created for {user.username}'))
            
            # Add some favorite attractions
            for _ in range(random.randint(1, 2)):
                if attractions:
                    attraction = random.choice(attractions)
                    if not Favorite.objects.filter(user=user, attraction=attraction).exists():
                        Favorite.objects.create(
                            user=user,
                            attraction=attraction,
                        )
                        self.stdout.write(self.style.SUCCESS(f'Favorite attraction {attraction.name} created for {user.username}'))
            
            # Add some favorite excursions
            for _ in range(random.randint(0, 2)):
                if excursions:
                    excursion = random.choice(excursions)
                    if not Favorite.objects.filter(user=user, excursion=excursion).exists():
                        Favorite.objects.create(
                            user=user,
                            excursion=excursion,
                        )
                        self.stdout.write(self.style.SUCCESS(f'Favorite excursion {excursion.name} created for {user.username}'))
        
        self.stdout.write(self.style.SUCCESS('Successfully loaded sample data!')) 