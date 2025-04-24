import os
import requests
from django.core.management.base import BaseCommand
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from tours.models import Destination, Hotel, Attraction, Excursion
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Downloads and assigns sample images to models'

    def download_image(self, url):
        """Download image from URL and return as Django File object"""
        try:
            response = requests.get(url, stream=True)
            if response.status_code != requests.codes.ok:
                return None
            
            img_temp = NamedTemporaryFile(delete=True)
            img_temp.write(response.content)
            img_temp.flush()
            
            return File(img_temp)
        except Exception as e:
            logger.error(f"Error downloading image from {url}: {str(e)}")
            return None

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting to download and assign sample images...')

        # Sample image URLs for different categories
        destination_images = {
            'Paris': 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34',
            'Tokyo': 'https://images.unsplash.com/photo-1540959733332-eab4deabeeaf',
            'New York': 'https://images.unsplash.com/photo-1522083165195-3424ed129620',
            'Rome': 'https://images.unsplash.com/photo-1552832230-c0197dd311b5',
            'Sydney': 'https://images.unsplash.com/photo-1506973035872-a4ec16b8e8d9',
        }

        hotel_images = [
            'https://images.unsplash.com/photo-1566073771259-6a8506099945',
            'https://images.unsplash.com/photo-1582719508461-905c673771fd',
            'https://images.unsplash.com/photo-1571896349842-33c89424de2d',
            'https://images.unsplash.com/photo-1520250497591-112f2f40a3f4',
            'https://images.unsplash.com/photo-1542314831-068cd1dbfeeb',
        ]

        attraction_images = [
            'https://images.unsplash.com/photo-1558383331-f520f2888351',  # Cultural
            'https://images.unsplash.com/photo-1516815231560-8f41ec531527',  # Nature
            'https://images.unsplash.com/photo-1569596082827-c5aa9d4fb508',  # Entertainment
            'https://images.unsplash.com/photo-1581539250439-c96689b516dd',  # Shopping
            'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4',  # Food
        ]

        excursion_images = [
            'https://images.unsplash.com/photo-1527631746610-bca00a040d60',  # Cultural tour
            'https://images.unsplash.com/photo-1533130061792-64b345e4a833',  # Adventure
            'https://images.unsplash.com/photo-1473163928189-364b2c4e1135',  # Shopping tour
            'https://images.unsplash.com/photo-1482049016688-2d3e1b311543',  # Food tour
            'https://images.unsplash.com/photo-1501555088652-021faa106b9b',  # Nature tour
        ]

        # Update destinations
        for destination in Destination.objects.all():
            if destination.name in destination_images:
                image_url = destination_images[destination.name]
                image_file = self.download_image(image_url)
                if image_file:
                    destination.image.save(
                        f"{destination.name.lower().replace(' ', '_')}.jpg",
                        image_file,
                        save=True
                    )
                    self.stdout.write(self.style.SUCCESS(f'Added image to destination: {destination.name}'))

        # Update hotels
        for hotel in Hotel.objects.all():
            image_url = hotel_images[hash(hotel.name) % len(hotel_images)]
            image_file = self.download_image(image_url)
            if image_file:
                hotel.image.save(
                    f"hotel_{hotel.name.lower().replace(' ', '_')}.jpg",
                    image_file,
                    save=True
                )
                self.stdout.write(self.style.SUCCESS(f'Added image to hotel: {hotel.name}'))

        # Update attractions
        for attraction in Attraction.objects.all():
            image_url = attraction_images[hash(attraction.name) % len(attraction_images)]
            image_file = self.download_image(image_url)
            if image_file:
                attraction.image.save(
                    f"attraction_{attraction.name.lower().replace(' ', '_')}.jpg",
                    image_file,
                    save=True
                )
                self.stdout.write(self.style.SUCCESS(f'Added image to attraction: {attraction.name}'))

        # Update excursions
        for excursion in Excursion.objects.all():
            image_url = excursion_images[hash(excursion.name) % len(excursion_images)]
            image_file = self.download_image(image_url)
            if image_file:
                excursion.image.save(
                    f"excursion_{excursion.name.lower().replace(' ', '_')}.jpg",
                    image_file,
                    save=True
                )
                self.stdout.write(self.style.SUCCESS(f'Added image to excursion: {excursion.name}'))

        self.stdout.write(self.style.SUCCESS('Successfully loaded all sample images!')) 