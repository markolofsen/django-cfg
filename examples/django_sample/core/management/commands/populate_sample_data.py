"""
Django management command to populate sample data using Faker.
"""

import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from faker import Faker

from apps.blog.models import Category as BlogCategory, Post, Comment, Tag, PostLike
from apps.shop.models import Category as ShopCategory, Product, Order, OrderItem

User = get_user_model()
fake = Faker()


class Command(BaseCommand):
    help = 'Populate database with sample data using Faker'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=20,
            help='Number of users to create (default: 20)'
        )
        parser.add_argument(
            '--blog-categories',
            type=int,
            default=5,
            help='Number of blog categories to create (default: 5)'
        )
        parser.add_argument(
            '--posts',
            type=int,
            default=50,
            help='Number of blog posts to create (default: 50)'
        )
        parser.add_argument(
            '--comments',
            type=int,
            default=200,
            help='Number of comments to create (default: 200)'
        )
        parser.add_argument(
            '--shop-categories',
            type=int,
            default=8,
            help='Number of shop categories to create (default: 8)'
        )
        parser.add_argument(
            '--products',
            type=int,
            default=100,
            help='Number of products to create (default: 100)'
        )
        parser.add_argument(
            '--orders',
            type=int,
            default=30,
            help='Number of orders to create (default: 30)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before populating'
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            self.clear_data()

        self.stdout.write(self.style.SUCCESS('Starting data population...'))

        # Create superuser
        self.create_superuser()

        # Create users
        users = self.create_users(options['users'])
        self.stdout.write(self.style.SUCCESS(f'Created {len(users)} users'))

        # Create blog data
        blog_categories = self.create_blog_categories(options['blog_categories'])
        self.stdout.write(self.style.SUCCESS(f'Created {len(blog_categories)} blog categories'))

        tags = self.create_tags()
        self.stdout.write(self.style.SUCCESS(f'Created {len(tags)} tags'))

        posts = self.create_posts(options['posts'], users, blog_categories, tags)
        self.stdout.write(self.style.SUCCESS(f'Created {len(posts)} blog posts'))

        comments = self.create_comments(options['comments'], users, posts)
        self.stdout.write(self.style.SUCCESS(f'Created {len(comments)} comments'))

        likes = self.create_likes(users, posts)
        self.stdout.write(self.style.SUCCESS(f'Created {len(likes)} post likes'))

        # Create shop data
        shop_categories = self.create_shop_categories(options['shop_categories'])
        self.stdout.write(self.style.SUCCESS(f'Created {len(shop_categories)} shop categories'))

        products = self.create_products(options['products'], shop_categories)
        self.stdout.write(self.style.SUCCESS(f'Created {len(products)} products'))

        orders = self.create_orders(options['orders'], users, products)
        self.stdout.write(self.style.SUCCESS(f'Created {len(orders)} orders'))

        self.stdout.write(self.style.SUCCESS('✅ Sample data population completed!'))

    def clear_data(self):
        """Clear existing sample data."""
        PostLike.objects.all().delete()
        Comment.objects.all().delete()
        Post.objects.all().delete()
        Tag.objects.all().delete()
        BlogCategory.objects.all().delete()
        
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        Product.objects.all().delete()
        ShopCategory.objects.all().delete()
        
        # Profiles will be deleted automatically via CASCADE when users are deleted
        User.objects.filter(is_superuser=False).delete()

    def create_superuser(self):
        """Create superuser if it doesn't exist."""
        email = 'admin@example.com'
        username = 'admin'
        password = 'admin123'
        
        if not User.objects.filter(email=email).exists():
            superuser = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                first_name='Admin',
                last_name='User'
            )
            self.stdout.write(self.style.SUCCESS(f'✅ Superuser created: {email} | Password: {password}'))
        else:
            self.stdout.write(self.style.WARNING(f'⚠️  Superuser with email {email} already exists'))

    def create_users(self, count):
        """Create sample users with profiles."""
        users = []
        for _ in range(count):
            user = User.objects.create_user(
                username=fake.user_name(),
                email=fake.email(),
                password='password123',
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                is_active=True
            )
            
            users.append(user)
        
        return users

    def create_blog_categories(self, count):
        """Create blog categories."""
        categories = []
        category_names = [
            'Technology', 'Programming', 'Web Development', 'Mobile Apps',
            'Data Science', 'AI & Machine Learning', 'DevOps', 'Security',
            'Design', 'Business', 'Startups', 'Marketing'
        ]
        
        for i in range(min(count, len(category_names))):
            name = category_names[i]
            category = BlogCategory.objects.create(
                name=name,
                slug=name.lower().replace(' ', '-').replace('&', 'and'),
                description=fake.text(max_nb_chars=200)
            )
            categories.append(category)
        
        return categories

    def create_tags(self):
        """Create blog tags."""
        tag_names = [
            'python', 'django', 'javascript', 'react', 'vue', 'angular',
            'nodejs', 'api', 'database', 'postgresql', 'mongodb', 'redis',
            'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'devops',
            'testing', 'ci-cd', 'security', 'performance', 'optimization',
            'tutorial', 'guide', 'tips', 'best-practices', 'review'
        ]
        
        tags = []
        for name in tag_names:
            tag = Tag.objects.create(
                name=name,
                slug=name.lower().replace(' ', '-')
            )
            tags.append(tag)
        
        return tags

    def create_posts(self, count, users, categories, tags):
        """Create blog posts."""
        posts = []
        statuses = ['draft', 'published', 'archived']
        
        for _ in range(count):
            post = Post.objects.create(
                title=fake.sentence(nb_words=6).rstrip('.'),
                slug=fake.slug(),
                content=fake.text(max_nb_chars=2000),
                excerpt=fake.text(max_nb_chars=200),
                author=random.choice(users),
                category=random.choice(categories),
                status=random.choices(statuses, weights=[10, 80, 10])[0],
                is_featured=random.choice([True, False]),
                views_count=random.randint(0, 1000),
                created_at=fake.date_time_between(start_date='-1y', end_date='now', tzinfo=timezone.get_current_timezone()),
                updated_at=fake.date_time_between(start_date='-6m', end_date='now', tzinfo=timezone.get_current_timezone())
            )
            
            # Add random tags
            post_tags = random.sample(tags, random.randint(1, 5))
            post.tags.set(post_tags)
            
            posts.append(post)
        
        return posts

    def create_comments(self, count, users, posts):
        """Create blog comments."""
        comments = []
        published_posts = [p for p in posts if p.status == 'published']
        
        if not published_posts:
            return comments
        
        for _ in range(count):
            post = random.choice(published_posts)
            comment = Comment.objects.create(
                post=post,
                author=random.choice(users),
                content=fake.text(max_nb_chars=500),
                is_approved=random.choice([True, True, True, False]),  # 75% approved
                created_at=fake.date_time_between(
                    start_date=post.created_at,
                    end_date='now',
                    tzinfo=timezone.get_current_timezone()
                )
            )
            comments.append(comment)
        
        # Create some replies
        for _ in range(count // 4):
            parent = random.choice(comments)
            reply = Comment.objects.create(
                post=parent.post,
                parent=parent,
                author=random.choice(users),
                content=fake.text(max_nb_chars=300),
                is_approved=True,
                created_at=fake.date_time_between(
                    start_date=parent.created_at,
                    end_date='now',
                    tzinfo=timezone.get_current_timezone()
                )
            )
            comments.append(reply)
        
        return comments

    def create_likes(self, users, posts):
        """Create post likes."""
        likes = []
        published_posts = [p for p in posts if p.status == 'published']
        
        for post in published_posts:
            # Random number of likes per post
            num_likes = random.randint(0, min(len(users), 20))
            post_users = random.sample(users, num_likes)
            
            for user in post_users:
                like = PostLike.objects.create(
                    post=post,
                    user=user
                )
                likes.append(like)
        
        return likes

    def create_shop_categories(self, count):
        """Create shop categories."""
        categories = []
        category_data = [
            ('Electronics', 'Latest gadgets and electronic devices'),
            ('Clothing', 'Fashion and apparel for all ages'),
            ('Books', 'Wide selection of books and literature'),
            ('Home & Garden', 'Everything for your home and garden'),
            ('Sports & Outdoors', 'Sports equipment and outdoor gear'),
            ('Health & Beauty', 'Health and beauty products'),
            ('Toys & Games', 'Fun toys and games for everyone'),
            ('Automotive', 'Car parts and automotive accessories'),
            ('Food & Beverages', 'Gourmet food and beverages'),
            ('Art & Crafts', 'Creative supplies and handmade items')
        ]
        
        for i in range(min(count, len(category_data))):
            name, description = category_data[i]
            category = ShopCategory.objects.create(
                name=name,
                slug=name.lower().replace(' ', '-').replace('&', 'and'),
                description=description,
                is_active=True,
                products_count=0  # Will be updated when products are created
            )
            categories.append(category)
        
        return categories

    def create_products(self, count, categories):
        """Create shop products."""
        products = []
        
        for _ in range(count):
            category = random.choice(categories)
            product = Product.objects.create(
                name=fake.catch_phrase(),
                slug=fake.slug(),
                description=fake.text(max_nb_chars=1000),
                short_description=fake.text(max_nb_chars=200),
                price=Decimal(str(random.uniform(9.99, 999.99))).quantize(Decimal('0.01')),
                sale_price=Decimal(str(random.uniform(5, 800))).quantize(Decimal('0.01')) if random.choice([True, False]) else None,
                cost_price=Decimal(str(random.uniform(5, 500))).quantize(Decimal('0.01')),
                category=category,
                sku=fake.bothify(text='SKU-####-????').upper(),
                stock_quantity=random.randint(0, 100),
                status=random.choice(['active', 'active', 'active', 'inactive']),  # 75% active
                is_featured=random.choice([True, False]),
                is_digital=random.choice([True, False]),
                created_at=fake.date_time_between(start_date='-2y', end_date='now', tzinfo=timezone.get_current_timezone())
            )
            products.append(product)
            
            # Update category products count
            category.products_count += 1
            category.save()
        
        return products

    def create_orders(self, count, users, products):
        """Create shop orders."""
        orders = []
        active_products = [p for p in products if p.status == 'active' and p.stock_quantity > 0]
        
        if not active_products:
            return orders
        
        statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
        
        for _ in range(count):
            user = random.choice(users)
            order = Order.objects.create(
                order_number=fake.bothify(text='ORD-####-????').upper(),
                customer=user,
                status=random.choices(statuses, weights=[10, 20, 30, 35, 5])[0],
                total_amount=Decimal('0.00'),
                shipping_address=f"{fake.street_address()}, {fake.city()}, {fake.state_abbr()} {fake.zipcode()}",
                billing_address=f"{fake.street_address()}, {fake.city()}, {fake.state_abbr()} {fake.zipcode()}",
                customer_notes=fake.text(max_nb_chars=200) if random.choice([True, False]) else '',
                created_at=fake.date_time_between(start_date='-6m', end_date='now', tzinfo=timezone.get_current_timezone())
            )
            
            # Create order items
            num_items = random.randint(1, 5)
            order_products = random.sample(active_products, min(num_items, len(active_products)))
            total_amount = Decimal('0.00')
            
            for product in order_products:
                quantity = random.randint(1, 3)
                unit_price = product.price
                total_price = unit_price * quantity
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    unit_price=unit_price,
                    total_price=total_price
                )
                
                total_amount += total_price
            
            # Update order total
            order.total_amount = total_amount
            order.save()
            
            orders.append(order)
        
        return orders
