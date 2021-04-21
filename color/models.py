from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, EmailValidator, validate_slug, URLValidator

# Create your models here.
class User(AbstractUser):
    gender = models.CharField(max_length=50, default="male")
    is_creator = models.BooleanField(default=False,null=True)
    phone_regex = RegexValidator(regex=r'^\d{10,10}$', message="Phone number must be entered in the format: '1234567890'. Up to 10 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=10, blank=True)

    class Meta:
        ordering = ['id']

class Banner(models.Model):
    img_height = models.PositiveIntegerField(default=330)
    img_width = models.PositiveIntegerField(default=330)
    first_image = models.ImageField( upload_to='banner/image/', height_field='img_height', width_field='img_width', max_length=None, blank=False)
    second_image = models.ImageField( upload_to='banner/image/',height_field='img_height', width_field='img_width', max_length=None,  blank=False)
    third_image = models.ImageField( upload_to='banner/image/', height_field='img_height', width_field='img_width', max_length=None, blank=False)
    long_banner_image = models.ImageField( upload_to='banner/image/', height_field='img_height', width_field='img_width', max_length=None, blank=False)

    def __str__(self):
        return str(self.first_image)
    
    class Meta:
        verbose_name = "Banner"
        verbose_name_plural = "Banners"
        ordering = ['id']
    
class HomeBanner(models.Model):
    banner_one = models.ImageField( upload_to='banner/image/', blank=False)
    banner_two = models.ImageField( upload_to='banner/image/', blank=False)
    banner_three = models.ImageField( upload_to='banner/image/', blank=False)
    banner_four = models.ImageField( upload_to='banner/image/', blank=False)
    

    class Meta:
        verbose_name = "HomeBanner"
        verbose_name_plural = "HomeBanners"
        ordering =['id']

    def __str__(self):
        return str(self.id)

class Theme(models.Model):
    theme = models.CharField( max_length=100) 
    date = models.DateTimeField( auto_now=True)
    theme_image = models.FileField( upload_to='product/image/',default="/media/image/temple.png", blank=False)
    class Meta:
        verbose_name = "Theme"
        verbose_name_plural = "Themes"
        ordering = ['id', 'theme', 'date']

    def __str__(self):
        return self.theme

class ThemeCategory(models.Model):
    theme = models.ManyToManyField("Theme", verbose_name="theme_category")
    category = models.CharField( max_length=100)
    date = models.DateTimeField( auto_now=True)
    category_image = models.FileField( upload_to='product/image/',default="/media/image/temple.png", blank=False)
    class Meta:
        verbose_name = "ThemeCategory"
        verbose_name_plural = "ThemeCategorys"
        ordering = [ 'id', 'category', 'date']

    def __str__(self):
        return self.category

class Product(models.Model):
    product_name = models.CharField( max_length=100, default="PUBG Grey T-shirt")
    creator = models.ForeignKey("User", verbose_name="Creator", on_delete=models.CASCADE)
    product_theme = models.ManyToManyField("Theme", verbose_name="Product Theme",  blank=True)
    prodcut_description = models.TextField()
    price = models.PositiveIntegerField()
    cult_member_price = models.PositiveIntegerField()
    product_image = models.FileField( upload_to='product/image/',default="/media/image/temple.png", blank=False)
    product_category = models.ManyToManyField("ThemeCategory", verbose_name="Product Theme Category",  blank=True)
    product_size = models.ManyToManyField("ProductSize", verbose_name="Product Size",  blank=True)
    product_related_to_gender = models.ManyToManyField("Gender", verbose_name="Gender",  blank=True)
    product_page_size = models.ManyToManyField("PageSize", verbose_name="Product Page Size",  blank=True)
    product_frame_size = models.ManyToManyField("FrameSize", verbose_name="Product Frame Size",  blank=True)
    product_color = models.ManyToManyField("Color", verbose_name="Add Hex code only for product")
    date = models.DateTimeField( auto_now=True)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Product"
        ordering = [ 'id', 'price', 'date']

    def __str__(self):
        return str(self.id)

class Color(models.Model):
    color = models.CharField(max_length=100)
    date = models.DateTimeField( auto_now=True)

    class Meta:
        verbose_name = "Color"
        verbose_name_plural = "Colors"

    def __str__(self):
        return str(self.color)


class ProductSize(models.Model):
    product_sizes = models.CharField( max_length=100)
    date = models.DateTimeField( auto_now=True)
    class Meta:
        verbose_name = "ProductSize"
        verbose_name_plural = "ProductSizes"
        ordering = [ 'id', 'date']


    def __str__(self):
        return str(self.product_sizes)

class Gender(models.Model):
    product_related_to_gender = models.CharField(max_length=50)
    date = models.DateTimeField( auto_now=True)

    class Meta:
        verbose_name = "Gender"
        verbose_name_plural = "Genders"
        ordering = [ 'id', 'date', 'product_related_to_gender']

    def __str__(self):
        return self.product_related_to_gender

class FrameSize(models.Model):
    size = models.CharField( max_length=50)
    date = models.DateTimeField( auto_now=True)

    class Meta:
        verbose_name = "FrameSize"
        verbose_name_plural = "FrameSizes"
        ordering = [ 'id', 'date', 'size']

    def __str__(self):
        return str(self.size)

class PageSize(models.Model):
    page_size = models.CharField(max_length=50)
    date = models.DateTimeField( auto_now=True)

    class Meta:
        verbose_name = "PageSize"
        verbose_name_plural = "PageSizes"
        ordering = [ 'id', 'date', 'page_size']

    def __str__(self):
        return self.page_size

class Image(models.Model):
    product_for = models.ForeignKey("Product", verbose_name="for_product_image", on_delete=models.CASCADE, default='/media/image/temple.png')
    product_images = models.ImageField( upload_to='product/image/')
    date = models.DateTimeField( auto_now=True)

    class Meta:
        verbose_name = "Image"
        verbose_name_plural = "Images"
        ordering = [ 'id', 'date']

    def __str__(self):
        return str(self.id)


class Cart(models.Model):
    user = models.ForeignKey("User", verbose_name="User Cart", on_delete=models.CASCADE)
    product = models.ForeignKey("Product", verbose_name="Product", on_delete=models.CASCADE)
    date = models.DateTimeField( auto_now=True)
    product_size = models.CharField( max_length=100, blank=True, null=True)
    product_color = models.CharField( max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = "Cart"
        verbose_name_plural = "Carts"

    def __str__(self):
        return str(self.user)
STATUS = [
    ('under_review', 'Under Review'),
    ('accepted', 'Accepted'),
    ('rejected', 'Rejected'),
]
class CreatorDesign(models.Model):
    user = models.ForeignKey("User", verbose_name="Creator User", on_delete=models.CASCADE)
    date = models.DateTimeField( auto_now=True)
    design_description = models.TextField()
    design_name = models.CharField(max_length=50, default="art")
    design_image = models.ImageField( upload_to='product/image/')
    design_status = models.CharField(choices=STATUS, max_length=50, default='under_review')

    class Meta:
        verbose_name = "CreatorDesign"
        verbose_name_plural = "CreatorDesigns"

    def __str__(self):
        return str(self.user)

class Address(models.Model):
    user = models.ForeignKey("User", verbose_name="User Address", on_delete=models.CASCADE)
    address = models.TextField()
    locality = models.CharField(max_length=100)
    landmark = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pin_code = models.CharField(max_length=10)
    date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Address"
        verbose_name_plural = "Address"

    def __str__(self):
        return str(self.user)

class Order(models.Model):
    user = models.ForeignKey("User", verbose_name="User Payment", on_delete=models.CASCADE)
    order_amount = models.IntegerField()
    razor_payment_id = models.CharField(max_length=10000)
    razor_order_id = models.CharField(max_length=10000)
    razor_signature = models.CharField(max_length=1000000)
    date = models.DateTimeField(auto_now=True)
    

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def __str__(self):
        return str(self.user)

class Wishlist(models.Model):
    user = models.ForeignKey("User", verbose_name="User Wish list", on_delete=models.CASCADE)
    product_id = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now=True)
    

    class Meta:
        verbose_name = "Wishlist"
        verbose_name_plural = "Wishlists"

    def __str__(self):
        return str(self.product_id)


# PRODUCT_SIZES = [
#     ('-', 'Not Applicable'),
#     ('xs','XS'),
#     ('s','S'),
#     ('m','M'),
#     ('l','L'),
#     ('xl','XL'),
#     ('xxl','XXL'),
# ]