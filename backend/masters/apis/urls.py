from django.urls import path
from masters.apis.views import (
    CategoryDetailView,
    CategoryList,
)

urlpatterns = [
    path('category/', CategoryList.as_view({'get': 'list'}), name='category'),
    path('category/<int:id>', CategoryDetailView.as_view(), name='category_detail'),
]
