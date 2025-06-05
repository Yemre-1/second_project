from django.shortcuts import render , HttpResponse , redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import EmailVerificationToken  , Category, Comment, UserProfile, Product, Cart, Order, OrderItem , CartItem
from django.urls import reverse
from django.shortcuts import get_object_or_404 
from django.contrib.sites.shortcuts import get_current_site
from .forms import CheckOutForm , CommentForm
from django.db.models import Q

def home(request):
    products = Product.objects.all()
    return render(request,'main/home.html', {'products':products})

def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email= request.POST['email']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            return render(request, 'main/signup.html' , {'error': 'kullanıcı adı zaten kayıtlı'})
        user = User.objects.create_user(username=username, password=password, email=email )
        user.is_active=False
        user.save()
        token = EmailVerificationToken.objects.create(user=user)
        current_site=get_current_site(request)
        verification_link=f"http://{current_site.domain}{reverse('verify_regist', args=[str(token.token)])}"
        send_mail(
            subject="E-posta Doğrulama",
            message=f"Merhaba {user.username}, hesabınızı doğrulamak için aşağıdaki bağlantıya tıklayın:\n\n{verification_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )
        return render(request, 'registration/emailverification.html')
    return render(request, 'main/signup.html')

def verify_regist(request,token):
    verification= get_object_or_404(EmailVerificationToken, token=token)
    user = verification.user
    user.is_active= True
    user.save()
    verification.delete()
    return render(request, 'registration/emailverified.html')
    
def login_view(request):
    if request.method=='POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username , password=password)
        if user:
            login(request,user)
            return redirect('home')
        else:
            return render(request, 'main/login.html' , {'error': 'kullanıcı adı ya da şifre yanlış'})
    return render(request, 'main/login.html')

def logout_view(requset):
    logout(requset)
    return redirect('home')

def product_list(request):
    products = Product.objects.all()
    return render(request, 'main/product_list.html', {'products':products})

@login_required
def profile_view(request):
    profile = request.user.userprofile
    return render(request, 'main/profile.html' , {'user' : request.user, 'profile':profile})

@login_required
def edit_profile(request):
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        new_username = request.POST.get('username')
        new_email = request.POST.get('email')
        avatar = request.FILES.get('avatar')

        # Kullanıcı adı çakışması kontrolü
        if new_username != user.username and User.objects.filter(username=new_username).exists():
            messages.error(request, "Bu kullanıcı adı zaten kullanılıyor.")
            return redirect('edit_profile')

        # E-posta çakışması kontrolü
        if new_email != user.email and User.objects.filter(email=new_email).exists():
            messages.error(request, "Bu e-posta adresi zaten kullanılıyor.")
            return redirect('edit_profile')

        # Kullanıcı adı ve e-posta güncelle
        user.username = new_username
        user.email = new_email  # bunu da güncelle ki e-posta karşılaştırması çalışsın

        # Avatar güncelleme
        if avatar:
            profile.avatar = avatar

        # Her durumda profil kaydedilsin
        profile.save()
        user.save()

        # E-posta değişmişse doğrulama maili gönder
        if new_email != request.user.email:
            token = EmailVerificationToken.objects.create(user=user, new_email=new_email)
            verification_link = request.build_absolute_uri(
                reverse('verify_email', kwargs={'token': str(token.token)})
            )
            send_mail(
                subject="E-posta Adresi Doğrulama",
                message=f"E-posta adresinizi doğrulamak için aşağıdaki bağlantıya tıklayın:\n\n{verification_link}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[new_email],
            )
            messages.info(request, "Yeni e-posta adresinize bir doğrulama bağlantısı gönderildi.")
        else:
            messages.success(request, "Profiliniz başarıyla güncellendi.")

        return redirect('profile')

    return render(request, 'main/editprofile.html', {'user': user, 'profile': profile})


def verify_email(request, token):
    # Token kaydını bul, yoksa 404
    record = get_object_or_404(EmailVerificationToken, token=token)
    user = record.user

    # E-posta güncelle
    user.email = record.new_email
    user.save()

    # Tokeni sil
    record.delete()

    messages.success(request, "E-posta adresiniz başarıyla doğrulandı ve güncellendi.")
    return redirect('profile')
@login_required
def add_to_cart(request, product_id):
    product= get_object_or_404(Product, id= product_id)
    cart,created = Cart.objects.get_or_create(user=request.user)
    cart_item,item_created=CartItem.objects.get_or_create(cart=cart, product=product)
    if not item_created:
        cart_item.quantity+=1
        cart_item.save()
    return redirect('cart_detail')
@login_required  
def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user= request.user)
    items= cart.items.all()
    total_price=sum(item.get_total_price() for item in items)

    return render(request, 'main/cart_detail.html',{
        'cart': cart,
        'items':items,
        'total_price':total_price

    })  
@login_required
def increase_quantity(request, item_id):
    item= get_object_or_404(CartItem, id= item_id, cart__user = request.user)
    item.quantity+=1
    item.save()
    return redirect('cart_detail')
@login_required
def decrease_quantity(request, item_id):
    item= get_object_or_404(CartItem, id=item_id, cart__user = request.user)
    if item.quantity>1:
        item.quantity-=1
        item.save()
    else:
        item.delete()
    return redirect('cart_detail') 
@login_required
def remove_item(request, item_id):
    item= get_object_or_404(CartItem, id = item_id, cart__user = request.user)
    item.delete()
    return redirect('cart_detail')
@login_required
def checkout_view(request):
    try:
        cart = Cart.objects.get(user=request.user)  # Tek bir sepet al
    except Cart.DoesNotExist:
        return redirect('cart_detail')

    if request.method == "POST":
        form = CheckOutForm(request.POST)
        if form.is_valid():
            order = Order.objects.create(
                user=request.user,
                address=form.cleaned_data['address'],
                phone=form.cleaned_data['phone']
            )

            for item in cart.items.all():  # Burada artık cart bir nesne
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity
                )
                product = item.product
                product.stock = product.stock - item.quantity
                product.save()    

            cart.delete()  # Sipariş sonrası sepet silinir

            return render(request, 'main/order_success.html', {'order': order})
    else:
        form = CheckOutForm()

    return render(request, 'main/checkout.html', {'form': form})
@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('created_at')
    return render(request, 'main/order_list.html', {'orders':orders})
@login_required
def order_detail(request, order_id):
    order= get_object_or_404(Order, id = order_id, user=request.user)
    items= OrderItem.objects.filter(order=order)
    return render(request, 'main/order_detail.html' , {'order':order , 'items':items}) 

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    comments = product.comments.order_by('-created_at')
    if request.method=='POST':
        if request.user.is_authenticated:
            form = CommentForm(request.POST)
            if form.is_valid():
                Comment.objects.create(
                    product=product,
                    user = request.user,
                    content= form.cleaned_data['content']
                )
                return redirect('product_detail', product_id=product.id)
        else:
            return redirect('login')
    else:
        form=CommentForm()
    context={
        'product':product,
        'comments':comments,
        'form':form,
    }            

    return render(request, 'main/product_detail.html', context)
def category_detail(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = category.products.all()

    categories = Category.objects.all()  # Tüm kategoriler sidebar için
    context = {
        'category': category,
        'products': products,
        'categories': categories,
        'current_category_id': category.id,  # Aktif kategoriyi belirlemek için
    }
    return render(request, 'main/category_detail.html', context)
def product_search(request):
    query= request.GET.get('q','')
    products = Product.objects.filter(name__icontains=query) if query else []
    context ={
        'query':query,
        'products':products,
    }
    return render(request, 'main/search_results.html',context)