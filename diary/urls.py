from django.urls import path

from .views import (
    add_food_entry_view,
    add_product_view,
    diary_view,
    friend_diary_view,
    product_list_view,
)

urlpatterns = [
    path('products/', product_list_view, name='product_list'),
    path('products/add/', add_product_view, name='add_product'),
    path('diary/', diary_view, name='diary'),
    path('diary/add/', add_food_entry_view, name='add_food_entry'),
    path('diary/users/<str:username>/', friend_diary_view, name='friend_diary'),
    path(
        'diary/users/<str:username>/<str:date_str>/',
        friend_diary_view,
        name='friend_diary_by_date',
    ),
    path('diary/<str:date_str>/', diary_view, name='diary_by_date'),
]

