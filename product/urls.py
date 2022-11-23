from django.urls import path,include


from .views import(
    BrandList,
    CartList,
    CreateDeleteLikeView,
    LoginView,
    PaymentViewSet,
    ProductList, 
    Register,
    StripeCheckoutSessionCreateAPIView,
    StripeWebhookAPIView,
)  
from rest_framework .routers import DefaultRouter


router = DefaultRouter()

router.register('register', Register)
router.register('product', ProductList)
router.register('brand', BrandList)
router.register('cart', CartList)
router.register('like', CreateDeleteLikeView)
router.register('payment', PaymentViewSet)
urlpatterns = [
    path('',include(router.urls)),
    path('login/', LoginView.as_view(), name = 'login'),
    path('create-checkout-session/',
         StripeCheckoutSessionCreateAPIView.as_view()),
    path('webhook/', StripeWebhookAPIView.as_view()),

]

