from django.urls import path

from apps.goods.views import IndexView,ListView,HotGoodsView,SKUSearchView
from apps.goods.views import DetailView,CategoryVisitCountView

urlpatterns = [
    path('index/',IndexView.as_view()),
    path('list/<category_id>/skus/',ListView.as_view()),
    path('hot/<category_id>/',HotGoodsView.as_view()),
    path('search/',SKUSearchView()),
    path('detail/<sku_id>/',DetailView.as_view()),
    path('detail/visit/<category_id>/',CategoryVisitCountView.as_view()),
]