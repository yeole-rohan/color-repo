from django.shortcuts import render, redirect
from .models import Banner, HomeBanner, ThemeCategory, Theme, Product, Image, Cart, User, CreatorDesign, Address, Order, Wishlist
from .forms import RegisterUser, CreatorDesignForm, UpdateProfile, AddressForm, CollaborateForm
from django.contrib.auth.forms import AuthenticationForm,PasswordChangeForm
from django.http import JsonResponse
from django.contrib.auth import login
from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import HttpResponse
from django.contrib.auth.decorators import login_required
import razorpay
from django.core.mail import send_mail
import random



# Project Views
def user_design(request, id):
    get_all_theme_categories = ThemeCategory.objects.all()
    get_all_themes = Theme.objects.all()
    get_home_banners = HomeBanner.objects.first()
    get_products_by_user = Product.objects.filter(creator = id).order_by('-date')
    creator = User.objects.get(id=id) 
    return render(request, template_name="pages/user-design-listing.html", context={'get_home_banners' : get_home_banners, 'get_all_themes' : get_all_themes,'get_all_theme_categories' : get_all_theme_categories, 'get_products_by_user' : get_products_by_user, 'creator' : creator})

def edit_address(request, id):
    get_all_theme_categories = ThemeCategory.objects.all()
    get_all_themes = Theme.objects.all()

    address = Address.objects.get(id=id)
    form = AddressForm(request.POST or None, instance=address)
    if request.method == "POST" and "new-address" in request.POST:
        form = AddressForm(request.POST or None, instance=address)
        print(form)
        if form.is_valid():
            form = form.save(commit=False)
            form.user = request.user
            form.save()
            return redirect('color:order-summary')
    return render(request, template_name="pages/edit-address.html", context={'form' : form})

@login_required
def order_summary(request):
    get_all_theme_categories = ThemeCategory.objects.all()
    get_all_themes = Theme.objects.all()

    cart_total = 0
    gst = 0
    whole_total = 0
    product_object_list = ''

    #for cart counter, fetching products ids added by customer from cookies
    if 'product_ids' in request.COOKIES: 
        product_ids = request.COOKIES['product_ids']
        counter=product_ids.split('|')
        ids = set(counter)
        product_object_list = Product.objects.all().filter(id__in=ids)
        for p in product_object_list:
            added_to_cart = Cart.objects.create(user=request.user, product=Product.objects.get(id=p.id))
            added_to_cart.save()
            cart_total = cart_total + p.price
            if p.price > 1000:
                price_gst = int((p.price/100)*12)
                gst = gst + price_gst
                print("above 1000 {}".format(gst))
            else:
                price_gst = int((p.price/100)*5)
                print("gst cal {}".format(price_gst))
                gst = gst + price_gst
        print("all {}".format(gst))
    shipping  = ("Free" if cart_total > 700 else 50) 
    whole_total =  (whole_total + gst + cart_total + shipping if shipping != "Free" else whole_total + gst + cart_total)
    get_address_of_user = Address.objects.filter(user = request.user.id)
    # Razor payment processing
    # Converting paise into ruppes by multiplying 100
    order_amount = whole_total * 100
    order_currency = 'INR'
    order_receipt = 'order_rcptid_11'
    client = razorpay.Client(auth = ('rzp_test_X31npZU5HW34Kd', 'yZekFv7QzislrEBeRgTksV2A'))
    payment = client.order.create(dict(amount=order_amount, currency=order_currency, receipt=order_receipt, payment_capture='0'))

    print(request.method)
    if request.method == "POST" and 'razorpay_order_id' in request.POST:
        get_post = request.POST
        order_id = ''
        params_dict = {} 
        for key, value in get_post.items():
            if key == "razorpay_order_id":
                params_dict['razorpay_order_id'] = value
                order_id = value
            elif key == "razorpay_payment_id":
                params_dict['razorpay_payment_id'] = value
            elif key == "razorpay_signature":
                params_dict['razorpay_signature'] = value
        status = client.utility.verify_payment_signature(params_dict)
        if status:
            return render(request, 'payment-unsuccessful.html',context= {'status': 'Payment was unsuccesfull!!!'})
        else:
            order_creation = Order.objects.create(user=request.user, order_amount=whole_total, razor_payment_id=params_dict['razorpay_payment_id'], razor_order_id=params_dict['razorpay_order_id'], razor_signature=params_dict['razorpay_signature'])
            order_creation.save()
            response = redirect('color:dashboard')
            response.delete_cookie('product_ids')
            return response

    if request.method =="POST" and "remove-address" in request.POST:
        add_id = request.POST['remove-address-id']
        get_address = Address.objects.get(id=add_id)
        get_address.delete()
        return redirect('color:order-summary')

    

    form = AddressForm(request.POST or None)
    if request.method == "POST" and "new-address" in request.POST:
        form = AddressForm(request.POST or None)
        print(form)
        if form.is_valid():
            form = form.save(commit=False)
            form.user = request.user
            form.save()
            return redirect('color:order-summary')
    return render(request, template_name="pages/order-summary.html", context={"form": form, 'get_address_of_user' : get_address_of_user, "cart_total" : cart_total, "gst" : gst, "whole_total" : whole_total , "shipping" : shipping, 'payment' : payment, 'order_amount' : order_amount, 'get_all_theme_categories' : get_all_theme_categories, 'get_all_themes' : get_all_themes})

def view_cart(request): 
    get_all_theme_categories = ThemeCategory.objects.all()
    get_all_themes = Theme.objects.all()

    cart_total = 0
    gst = 0
    whole_total = 0
    shipping = ''
    product_object_list = ''
    product_count_in_cart = 0
    product_id_in_cart = ''
    if not request.user.is_authenticated:
        print("not athenticated")
        #for cart counter, fetching products ids added by customer from cookies
        if 'product_ids' in request.COOKIES: 
            product_ids = request.COOKIES['product_ids']
            counter=product_ids.split('|')
            ids = set(counter)
            product_object_list = Product.objects.all().filter(id__in=ids)
            for p in product_object_list:
                cart_total = cart_total + p.price
                if p.price > 1000:
                    price_gst = int((p.price/100)*12)
                    gst = gst + price_gst
                    print("above 1000 {}".format(gst))
                else:
                    price_gst = int((p.price/100)*5)
                    print("gst cal {}".format(price_gst))
                    gst = gst + price_gst
            print("all {}".format(gst))
            product_count_in_cart=len(set(counter))
        else:
            product_count_in_cart=0
        shipping  = ("Free" if cart_total > 700 else 50) 
        whole_total =  (whole_total + gst + cart_total + shipping if shipping != "Free" else whole_total + gst + cart_total)
    
        ''' Removing cart product '''
        if request.method == "POST" and "remove" in request.POST:
            prod_id = request.POST['prod-value']
            if 'product_ids' in request.COOKIES:
                product_ids = request.COOKIES['product_ids']
                product_id_in_cart=product_ids.split('|')
                product_id_in_cart=list(set(product_id_in_cart))
                product_id_in_cart.remove(str(prod_id))
                product_object_list = Product.objects.filter(id__in=product_id_in_cart)
                product_count_in_cart = len(product_id_in_cart)
                
            value = ''
            for i in range(len(product_id_in_cart)):
                if i==0:
                    value=value+product_id_in_cart[0]
                else:
                    value=value+"|"+product_id_in_cart[i]
            cart_total = 0
            gst = 0
            whole_total = 0
            if product_object_list: 
                for p in product_object_list:
                    cart_total = cart_total + p.price
                    if p.price > 1000:
                        price_gst = int((p.price/100)*12)
                        gst = gst + price_gst
                        print("above 1000 {}".format(gst))
                    else:
                        price_gst = int((p.price/100)*5)
                        print("gst cal {}".format(price_gst))
                        gst = gst + price_gst
            shipping  = ("Free" if cart_total > 700 else 50) 
            whole_total =  (whole_total + gst + cart_total + shipping if shipping != "Free" else whole_total + gst + cart_total)
            response = render(request, template_name="pages/cart.html", context={'product_object_list' : product_object_list ,'product_count_in_cart':product_count_in_cart, "cart_total" : cart_total, "gst" : gst, "whole_total" : whole_total , "shipping" : shipping, 'get_all_theme_categories' : get_all_theme_categories, 'get_all_themes' : get_all_themes})

            if value=="":
                response.delete_cookie('product_ids')
            response.set_cookie('product_ids',value)
            
        return response
    cart_list = []
    product_list = []
    if request.user.is_authenticated:
        if 'product_ids' in request.COOKIES:
            product_ids = request.COOKIES['product_ids']
            counter=product_ids.split('|')
            ids = set(counter)
            product_object_list = Product.objects.all().filter(id__in=ids)
            for p_obj in product_object_list:
                add_obj_to_cart = Cart.objects.create(user=p_obj.creator, product=Product.objects.get(id=p_obj.id))
                add_obj_to_cart.save()
            product_count_in_cart=len(set(counter))
            response = render(request, template_name="pages/cart.html", context={'product_object_list' : product_object_list ,'product_count_in_cart':product_count_in_cart, "cart_total" : cart_total, "gst" : gst, "whole_total" : whole_total, "shipping" : shipping, 'get_all_theme_categories' : get_all_theme_categories, 'get_all_themes' : get_all_themes})
            response.delete_cookie('product_ids')
            return response
        else:
            if request.method == "POST" and "remove" in request.POST:
                prod_id = request.POST['prod-value']
                get_product = Cart.objects.filter(product_id = prod_id)
                get_product.delete()
                get_cart = Cart.objects.filter(user=request.user)
                print(get_cart)
                for cart in get_cart:
                    cart_list.append(cart)
                for p in cart_list:
                    print(type(p.product))
                    id = str(p.product)
                    print(type(id))
                    get_product = Product.objects.get(id=id)
                    product_list.append(get_product)
                    cart_total = cart_total + get_product.price
                    if get_product.price > 1000:
                        price_gst = int((get_product.price/100)*12)
                        gst = gst + price_gst
                        print("above 1000 {}".format(gst))
                    else:
                        price_gst = int((get_product.price/100)*5)
                        print("gst cal {}".format(price_gst))
                        gst = gst + price_gst
                print(product_list)
            else:
                get_cart = Cart.objects.filter(user=request.user)
                for cart in get_cart:
                    cart_list.append(cart)
                for p in cart_list:
                    print(type(p.product))
                    id = str(p.product)
                    print(type(id))
                    get_product = Product.objects.get(id=id)
                    product_list.append(get_product)
                    cart_total = cart_total + get_product.price
                    if get_product.price > 1000:
                        price_gst = int((get_product.price/100)*12)
                        gst = gst + price_gst
                        print("above 1000 {}".format(gst))
                    else:
                        price_gst = int((get_product.price/100)*5)
                        print("gst cal {}".format(price_gst))
                        gst = gst + price_gst
                print(product_list)
                shipping  = ("Free" if cart_total > 700 else 50) 
                whole_total =  (whole_total + gst + cart_total + shipping if shipping != "Free" else whole_total + gst + cart_total)
                return render(request, template_name="pages/cart.html", context={'product_object_list' : product_list ,'product_count_in_cart':product_count_in_cart, "cart_total" : cart_total, "gst" : gst, "whole_total" : whole_total, "shipping" : shipping, 'get_all_theme_categories' : get_all_theme_categories, 'get_all_themes' : get_all_themes})
    return render(request, template_name="pages/cart.html", context={'product_object_list' : product_object_list ,'product_count_in_cart':product_count_in_cart, "cart_total" : cart_total, "gst" : gst, "whole_total" : whole_total, "shipping" : shipping, 'get_all_theme_categories' : get_all_theme_categories, 'get_all_themes' : get_all_themes})

def wish_list(request):
    if request.method == "POST" and "remove" in request.POST:
        prod_id = request.POST["prod-value"]
        get_product = Wishlist.objects.filter(product_id = prod_id)
        get_product.delete()

    if request.method == "POST" and "move-to-cart" in request.POST:
        prod_id = request.POST["move-value-cart"]
        prod_obj = Product.objects.get(id=prod_id)
        added_to_cart = Cart.objects.create(user=request.user, product=Product.objects.get(id=prod_id))
        added_to_cart.save()
        get_product = Wishlist.objects.filter(product_id = prod_id)
        get_product.delete()

    get_all_theme_categories = ThemeCategory.objects.all()
    get_all_themes = Theme.objects.all()
    get_home_banners = HomeBanner.objects.first()
    wish_list_count = Wishlist.objects.filter(user=request.user.id).count()
    all_wish_list_for_current_user = Wishlist.objects.filter(user=request.user.id)
    wish_list_product = []
    for wish_list in all_wish_list_for_current_user:
        product = Product.objects.filter(id=wish_list.product_id)
        wish_list_product.append(product)
    print(wish_list_product)
    response = render(request, template_name="pages/wish-list.html", context={'get_home_banners' : get_home_banners, 'get_all_theme_categories' : get_all_theme_categories, 'get_all_themes' : get_all_themes, 'wish_list_count' : wish_list_count, 'wish_list_product' : wish_list_product})
    return response
    # render(request, template_name="pages/wish-list.html", context={})

def my_profile(request):
    get_all_theme_categories = ThemeCategory.objects.all()
    get_all_themes = Theme.objects.all()

    get_home_banners = HomeBanner.objects.first()
    get_user = User.objects.get(id=request.user.id)
    change_pass = PasswordChangeForm(request.user)
    form = UpdateProfile(request.POST or None, instance=get_user)
    get_address_of_user = Address.objects.filter(user = request.user.id)

    if request.method == "POST" and 'update_profile' in request.POST:
        if form.is_valid(): 
            form.save()
            return redirect('color:my-profile')
    
    if request.method == 'POST' and 'update_pass' in request.POST:
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('color:my-profile')
        else:
            messages.error(request, 'Please correct the error below.')
    return render(request, template_name="pages/user-profile.html", context={'get_home_banners' : get_home_banners, 'form' : form, 'change_pass' : change_pass, 'get_address_of_user' : get_address_of_user,'get_all_theme_categories' : get_all_theme_categories, 'get_all_themes' : get_all_themes})

def user_commission(request):
    get_all_theme_categories = ThemeCategory.objects.all()
    get_all_themes = Theme.objects.all()

    print(request.COOKIES)
    return render(request, template_name="pages/user-commission.html", context={'get_all_theme_categories' : get_all_theme_categories, 'get_all_themes' : get_all_themes})
    
def user_products(request):
    get_all_theme_categories = ThemeCategory.objects.all()
    get_all_themes = Theme.objects.all()

    get_user_products  = Product.objects.filter(creator_id=request.user.id)
    get_user_product_count  = Product.objects.filter(creator_id=request.user.id).count()
    return render(request, template_name="pages/user-product.html", context={'get_user_products' : get_user_products, 'get_user_product_count' : get_user_product_count, 'get_all_theme_categories' : get_all_theme_categories, 'get_all_themes' : get_all_themes})

def upload_design(request):
    get_all_theme_categories = ThemeCategory.objects.all()
    get_all_themes = Theme.objects.all()

    creator_design_form = CreatorDesignForm(request.POST or None)
    if request.method == "POST":
        creator_design_form = CreatorDesignForm(request.POST or None, request.FILES)
        print(creator_design_form)
        if creator_design_form.is_valid():
            creator_design_form = creator_design_form.save(commit=False)
            creator_design_form.user = request.user
            creator_design_form.design_status = 'under_review'
            creator_design_form.save()
            return redirect('color:my-designs')
    return render(request, template_name="pages/design-upload.html", context={"form" : creator_design_form, 'get_all_theme_categories' : get_all_theme_categories, 'get_all_themes' : get_all_themes})

def my_designs(request):
    get_all_theme_categories = ThemeCategory.objects.all()
    get_all_themes = Theme.objects.all()

    get_current_login_user_designs = CreatorDesign.objects.filter(user = request.user)
    get_current_login_user_design_count = CreatorDesign.objects.filter(user = request.user).count()

    return render(request, template_name="pages/user-designs.html", context={'get_current_login_user_designs' : get_current_login_user_designs, 'get_current_login_user_design_count' : get_current_login_user_design_count, 'get_all_theme_categories' : get_all_theme_categories, 'get_all_themes' : get_all_themes})

def regsiter_user(request):
    get_all_theme_categories = ThemeCategory.objects.all()
    get_all_themes = Theme.objects.all()

    form = RegisterUser(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password2']
            form = form.save()
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('color:dashboard')
    return render(request, template_name="registration/register.html", context={'form' : form, 'get_all_theme_categories' : get_all_theme_categories, 'get_all_themes' : get_all_themes})

# Useless function
def login_user(request):
    get_all_theme_categories = ThemeCategory.objects.all()
    get_all_themes = Theme.objects.all()

    logout(request)
    username = password = ''
    if request.method == 'POST': 
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('color:dashboard')
    else:
        return redirect('color:dashboard')
    return render(request, template_name='dashboard.html', context={'get_all_theme_categories' : get_all_theme_categories, 'get_all_themes' : get_all_themes})

def dashboard(request):
    get_replaceable_banner = Banner.objects.first()
    get_home_banners = HomeBanner.objects.first()
    get_all_theme_categories = ThemeCategory.objects.all()
    get_all_themes = Theme.objects.all()
    get_six_theme_categories = ThemeCategory.objects.all().order_by('-date')[:6]
    get_six_themes = Theme.objects.all().order_by('-date')[:6]
    get_cult_favs = Product.objects.all().order_by('-date')[:4]
    response = render(request, template_name='dashboard.html', context={'get_all_theme_categories' : get_all_theme_categories, 'get_replaceable_banners' : get_replaceable_banner, 'get_home_banners' : get_home_banners, 'get_all_themes' : get_all_themes, 'get_cult_favs' : get_cult_favs, 'get_six_themes' : get_six_themes, 'get_six_theme_categories' : get_six_theme_categories })
    response.delete_cookie('usename')
    return response 
 
def product_details(request, id):
    get_all_theme_categories = ThemeCategory.objects.all()
    get_all_themes = Theme.objects.all()
    # Wishlist code
    if request.method=="POST" and "wish-full" in request.POST:
        if request.user.is_authenticated:
            wish_list = Wishlist.objects.filter(user=request.user, product_id = id)
            wish_list.delete()
    user_wish_list_product_id = ''
    try:
        user_wish_list_product_id = Wishlist.objects.filter(user=request.user, product_id = id)
    except:
        pass
    if request.method=="POST" and "wish-list" in request.POST:
        if request.user.is_authenticated:
            wish_list = Wishlist.objects.create(user=request.user, product_id = id)
            wish_list.save()

    get_single_product = Product.objects.get(id=id)
    get_images = Image.objects.filter(product_for=get_single_product.id)
    single_cat = []
    single_theme = []
    for get_cat in get_single_product.product_category.all():
        single_cat.append(get_cat)
    
    for get_theme in get_single_product.product_theme.all():
        single_theme.append(get_theme)
    get_similar_products_by_category = Product.objects.filter(product_category = single_cat[0]).order_by('-id')[:4]
    get_similar_products_by_theme = Product.objects.filter(product_theme = single_theme[0]).order_by('-id')[:4]
    ids = ''
    new_id = []
    if 'product_ids' in request.COOKIES:
        ids = request.COOKIES['product_ids']
        count=ids.split('|')
        ids = set(count)
        for i in ids:
            new_id.append(int(i))
    response = render(request, template_name="pages/product-details.html", context={'get_single_product' : get_single_product, 'get_images' : get_images, 'get_similar_products' : get_similar_products_by_category, 'get_similar_products_by_theme' : get_similar_products_by_theme, 'ids' : new_id, 'get_all_theme_categories' : get_all_theme_categories, 'get_all_themes' : get_all_themes, 'user_wish_list_product_id': user_wish_list_product_id})

    '''Adding products to Cart'''
    if request.method == "POST" and "cart" in request.POST:
        if 'product_ids' in request.COOKIES:
            product_ids = request.COOKIES['product_ids']
            if product_ids=="":
                product_ids=str(id)
                response.set_cookie('product_ids', product_ids)
            else:
                product_ids=product_ids+"|"+str(id)
                response.set_cookie('product_ids', product_ids)
        else:
            response.set_cookie('product_ids', id)
        return response
    return response

def search(request, cat, id):
    get_all_theme_categories = ThemeCategory.objects.all()
    get_all_themes = Theme.objects.all()
    get_home_banners = HomeBanner.objects.first()
    get_products_by_category_or_theme = ''
    try:
        get_products_by_category_or_theme = Product.objects.filter(product_category = id, product_theme = id).order_by('-date')
    except:
        pass
    paginator = Paginator(get_products_by_category_or_theme, 12)  # 1 posts in each page
    page = request.GET.get('page')
    try:
        get_products_by_category_or_theme = paginator.page(page)
    except PageNotAnInteger:
            # If page is not an integer deliver the first page
        get_products_by_category_or_theme = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        get_products_by_category_or_theme = paginator.page(paginator.num_pages)
    return render(request, template_name="pages/search.html", context={'get_all_theme_categories' : get_all_theme_categories, 'category_or_theme' : cat, 'get_all_themes' : get_all_themes, 'get_home_banners' : get_home_banners, 'get_products_by_category_or_theme' : get_products_by_category_or_theme, 'page': page})

def about(request):
    get_all_theme_categories = ThemeCategory.objects.all()
    get_all_themes = Theme.objects.all()

    return render(request, template_name = 'pages/about.html', context={'get_all_theme_categories' : get_all_theme_categories, 'get_all_themes' : get_all_themes})

def collaborate(request):
    get_all_theme_categories = ThemeCategory.objects.all()
    get_all_themes = Theme.objects.all()
    s = "abcdefghijklmnopqrstuvwxyz01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()?"
    passlen = 16
    password =  "".join(random.sample(s,passlen))
    print(password) 
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = CollaborateForm(request.POST or None, request.FILES)
        # check whether it's valid:
        if form.is_valid():
            full_name = form.cleaned_data['full_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            username = form.cleaned_data['username']
            design_desc = form.cleaned_data['design_desc']
            design_file = form.cleaned_data['design_file']
            design_name = form.cleaned_data['design_name']
            recipients = ['rayeole@gmail.com']
            print(full_name, email, phone_number, username, design_file, design_desc,design_name)
            user_create = User.objects.create(username=username, email=email, first_name=full_name, phone_number=phone_number)
            user_create.set_password(password)
            user_create.save()
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    create_design = CreatorDesign.objects.create(user=request.user,design_description=design_desc,design_name=design_name,design_image=design_file)
                    create_design.save()
            send_mail(design_name, design_desc, email, recipients)
            return redirect('color:my-designs')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = CollaborateForm()
    return render(request, template_name = 'pages/collaborate.html', context={'form' : form, 'get_all_theme_categories' : get_all_theme_categories, 'get_all_themes' : get_all_themes})

def membership(request):
    get_all_theme_categories = ThemeCategory.objects.all()
    get_all_themes = Theme.objects.all()

    return render(request, template_name = 'pages/membership.html', context={'get_all_theme_categories' : get_all_theme_categories, 'get_all_themes' : get_all_themes})