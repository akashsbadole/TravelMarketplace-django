# Generated manually for Destination model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0003_auto_20251113_0112'),
    ]

    operations = [
        migrations.CreateModel(
            name='Destination',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Destination name', max_length=100)),
                ('slug', models.SlugField(help_text='URL-friendly version of the name', max_length=100, unique=True)),
                ('description', models.TextField(help_text='Detailed description of the destination')),
                ('country', models.CharField(help_text='Country name', max_length=100)),
                ('city', models.CharField(blank=True, help_text='City name (if applicable)', max_length=100)),
                ('region', models.CharField(choices=[('europe', 'Europe'), ('asia', 'Asia'), ('americas', 'Americas'), ('africa', 'Africa'), ('oceania', 'Oceania'), ('middle_east', 'Middle East')], help_text='Geographical region', max_length=20)),
                ('image_url', models.URLField(help_text='URL to destination image', max_length=500)),
                ('gallery_images', models.JSONField(blank=True, default=list, help_text='List of additional image URLs')),
                ('popular_attractions', models.JSONField(default=list, help_text='List of popular attractions')),
                ('best_time_to_visit', models.CharField(choices=[('spring', 'Spring'), ('summer', 'Summer'), ('autumn', 'Autumn'), ('winter', 'Winter'), ('all_year', 'All Year Round')], help_text='Best season to visit', max_length=20)),
                ('average_rating', models.DecimalField(decimal_places=2, default=0.0, help_text='Average rating (0-5)', max_digits=3)),
                ('price_range', models.CharField(choices=[('budget', 'Budget ($)'), ('moderate', 'Moderate ($$)'), ('premium', 'Premium ($$$)'), ('luxury', 'Luxury ($$$$)')], help_text='Price range category', max_length=20)),
                ('requirements_count', models.PositiveIntegerField(default=0, help_text='Number of travel requirements for this destination')),
                ('view_count', models.PositiveIntegerField(default=0, help_text='Number of views')),
                ('is_featured', models.BooleanField(default=False, help_text='Whether this destination is featured')),
                ('is_active', models.BooleanField(default=True, help_text='Whether this destination is active')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'Destinations',
                'ordering': ['-is_featured', '-average_rating', 'name'],
                'indexes': [
                    models.Index(fields=['slug'], name='pages_destination_slug_idx'),
                    models.Index(fields=['country'], name='pages_destination_country_idx'),
                    models.Index(fields=['region'], name='pages_destination_region_idx'),
                    models.Index(fields=['is_featured'], name='pages_destination_is_featured_idx'),
                    models.Index(fields=['is_active'], name='pages_destination_is_active_idx'),
                ],
            },
        ),
    ]