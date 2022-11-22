from django.urls import path,include


from .views import(
    BrandList,
    CartList,
    CreateDeleteLikeView,
    LoginView,
    ProductList, 
    Register,
    StripeCheckOutView
)  
from rest_framework .routers import DefaultRouter


router = DefaultRouter()

router.register('register', Register)
router.register('product', ProductList)
router.register('brand', BrandList)
router.register('cart', CartList)
router.register('like', CreateDeleteLikeView)
router.register('chekout', StripeCheckOutView,basename='chekout-detail')
urlpatterns = [
    path('',include(router.urls)),
    path('login/', LoginView.as_view(), name = 'login'),
]

