import os
import random
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from app.models import Category, Seller, Product  # Replace 'myapp' with your app name
from faker import Faker

fake = Faker()

def seed_categories(n=5):
    categories = []
    for _ in range(n):
        name = fake.word().capitalize()
        category = Category.objects.create(
            name=name,
            description=fake.text(max_nb_chars=200),
        )
        categories.append(category)
    return categories

def seed_sellers(n=5):
    sellers = []
    for _ in range(n):
        user = User.objects.create_user(
            username=fake.unique.user_name(),
            email=fake.email(),
            password="password123",
        )
        seller = Seller.objects.create(
            user=user,
            name=fake.company(),
            description=fake.text(max_nb_chars=200),
        )
        sellers.append(seller)
    return sellers

def seed_products(categories, sellers, n=20):
    products = []
    for _ in range(n):
        user = random.choice(User.objects.all())
        product = Product.objects.create(
            user=user,
            name=fake.unique.word().capitalize(),
            description=fake.text(max_nb_chars=300),
            category=random.choice(categories),
            seller=random.choice(sellers),
            price=round(random.uniform(10.0, 500.0), 2),
        )
        products.append(product)
    return products

class Command(BaseCommand):
    help = "Seed the database with sample data"

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding data...")

        # Clear existing data
        # Product.objects.all().delete()
        # Seller.objects.all().delete()
        # Category.objects.all().delete()
        # User.objects.filter(is_staff=False).delete()

        # Seed new data
        categories = seed_categories()
        sellers = seed_sellers()
        seed_products(categories, sellers)

        self.stdout.write("Seeding completed!")
