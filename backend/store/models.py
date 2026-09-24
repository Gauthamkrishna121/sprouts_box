from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=100)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50, default='1 kg', help_text="e.g., '1 kg', '500 g', 'bunch'")
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class SiteSettings(models.Model):
    # Contact Information
    phone_number = models.CharField(max_length=50, default="+91 98765 43210", help_text="Primary contact phone number")
    phone_hours = models.CharField(max_length=100, default="Mon – Sat: 8:00 AM – 8:00 PM", help_text="Operating hours for phone support")
    
    email_address = models.EmailField(default="hello@sproutsbox.in", help_text="Primary contact email address")
    email_note = models.CharField(max_length=100, default="Support & General Inquiries", help_text="Subtext under email address")
    
    address_line1 = models.CharField(max_length=255, default="Sprouts Box Eco Farm, Green Valley", help_text="Address Line 1")
    address_line2 = models.CharField(max_length=255, default="Kerala, India – 682001", help_text="Address Line 2")
    
    # Contact Page Header & Text
    contact_subtitle = models.CharField(max_length=200, default="Reach Out —", help_text="Subtitle above Contact Information header")
    contact_title = models.CharField(max_length=200, default="Contact Information", help_text="Main heading on Contact Information column")
    contact_intro = models.TextField(default="Whether you're looking for home delivery or want to partner with us, our team is ready to assist you.", help_text="Description paragraph under Contact Information heading")
    
    # Social Media Links
    instagram_url = models.CharField(max_length=500, blank=True, default="#", help_text="Instagram profile or page link")
    facebook_url = models.CharField(max_length=500, blank=True, default="#", help_text="Facebook profile or page link")
    youtube_url = models.CharField(max_length=500, blank=True, default="#", help_text="YouTube channel link")
    whatsapp_url = models.CharField(max_length=500, blank=True, default="#", help_text="WhatsApp contact/group link")
    
    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return "Site Customization & Contact Settings"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj = cls.objects.first()
        if not obj:
            obj = cls.objects.create(pk=1)
        return obj


