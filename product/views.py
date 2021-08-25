from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import viewsets, mixins
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, DestroyAPIView, UpdateAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from django_filters import rest_framework as filters
from rest_framework import filters as rest_filters

from product.models import Product, ProductReview
from product.permissions import IsAuthorOrIsAdmin
from product.serializers import (ProductSerializer, ProductDetailsSerializer,
                                 CreateProductSerializer, ReviewSerializer)


def test_view(request):
    return HttpResponse('Hello World!')

@api_view(['GET'])
def products_list(request):
    products = Product.objects.all()

    # [product1], [product2], [product3]
    serializer = ProductSerializer(products, many=True)
    # {id : 1 , title : 2}
    return Response(serializer.data)

# class ProductsListView(APIView):
#     def get(self, request):
#         products = Product.objects.all()
#         serializer = ProductSerializer(products, many=True)
#         return Response(serializer.data)
#
# class ProductsListView(ListAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer
#
# class ProductsDetailsView(RetrieveAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductDetailsSerializer
#
# class CreateProductView(CreateAPIView):
#     queryset = Product.objects.all()
#     serializer_class = CreateProductSerializer
#
# class UpdateProductView(UpdateAPIView):
#     queryset = Product.objects.all()
#     serializer_class = CreateProductSerializer
#
# class DeleteProductView(DestroyAPIView):
#     queryset = Product.objects.all()
#     serializer_class = CreateProductSerializer

class ProductFilter(filters.FilterSet):
    price_from = filters.NumberFilter('price', 'gte')
    price_to = filters.NumberFilter('price', 'lte')
    class Meta:
        model = Product
        fields = ('price_from', 'price_to')

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    filter_backends = [filters.DjangoFilterBackend,
                       rest_filters.SearchFilter,
                       rest_filters.OrderingFilter]
    # filterset_fields = ('price')
    filterset_class = ProductFilter
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'price']

    # def get_queryset(self):
    #     queryset = super().get_queryset()
    #     print(queryset)
    #     print(self.request.query_params)
    #     price_from = self.request.query_params.get('price_from')
    #     price_to = self.request.query_params.get('price_to')
    #     queryset = queryset.filter(price__gte=price_from, price__lte=price_to)
    #     return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductSerializer
        elif self.action == 'retrieve':
            return ProductDetailsSerializer
        return CreateProductSerializer

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsAdminUser()]
        return []

    #api/v1/product/id/reviews
    @action(['GET'], detail=True)
    def reviews(self, request, pl=None):
        product = self.get_object()
        reviews = ProductReview.objexts.filter(product=product)
        reviews = product.reviews.all()
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=200)

#Создает только залогиненный пользователь
# Редактировать или удалять может либо админ, либо автор

class ReviewViewSet(mixins.CreateModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
    queryset = ProductReview.objects.all()
    serializer_class = ReviewSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAuthorOrIsAdmin()]
        return []

# #CRUO(Create, Retrieve, Update, Delete)
#         POST    GET    POST, PATCH, DELETE

#TODO: Импорт, экспорт данных
#TODO:отзывы ViewSet, листинг отзывав будет в товарах, детали не нужны
#TODO: сделать обновление товара
#TODO: удаление товара
#TODO: создавать, редактировать и удалять продукты могут только админы
#TODO: пагинация (разбивка листинга на страницы)
#TODO: фильтрация
#TODO: поиск продуктов по названию и описанию
#TODO:ограничение количества запросов
#TODO:тесты
#TODO: разобрать взаимодействие

# Application Programming Interface
# паттерн MVC


# REST - архитектурный подход
# 1. Модель клиент - сервер
# 2. Отсутствие состояния
# 3. Кэширование
# 4. Единообразие интерфейса
    # 1. Определение ресурсов
    #     URI ('api/v1/products/1/')
    # 2. Управление ресурсов через представление
    # 3. Самодостаточные сообщения
    # 4. Гипермедиа
# 5. Слом
# 6. Код по требованию

# HTTP:
# 'GET',  'POST',     'PUT',  'PATCH',        'DELETE'
# list    create      update  partial_update   destroy
# retrieve

# all() - выдает весь список объектов модели
# SELECT * FROM product;

# Product.object.create() - создает новый объект
# INSERT INTO product ...

# Product.object.update() - обновляет выбранные объекты
# UPDATE product ...

# Product.object.delete() - удаляет объекты
# DELETE FROM product;

# Product.objects.filter(условие)
# SELECT * FROM product WHERE условие;

# Операции сравнения
# "="
# Product.objects.filter(price=10000)
# SELECT * FROM product WHERE price = 10000;

# ">"
# Product.objects.filter(price_gt=10000)
# SELECT * FROM product WHERE price > 10000;

# ">"
# Product.objects.filter(price_lt=10000)
# SELECT * FROM product WHERE price < 10000;

# "<="
# Product.objects.filter(price_lte=10000)
# SELECT * FROM product WHERE price <= 10000;

# ">="
# Product.objects.filter(price_gte=10000)
# SELECT * FROM product WHERE price >= 10000;

# BETWEEN
# Product.objects.filter(price__range=[50000, 80000])
# SELECT * FROM product WHERE price BETWEEN 5000 AND 8000;

# IN
# Product.objects.filter(price__in=[50000, 80000])
# SELECT * FROM product WHERE price IN (50000, 80000)

# LIKE
# ILIKE

# 'work%'
# Product.object.filter(title__startswith='Apple')
# SELECT * FROM product WHERE title LIKE 'Apple%';
# Product.object.filter(title__istartswith='Apple')
# SELECT * FROM product WHERE title ILIKE 'Apple%';

# -'%work'
# Product.object.filter(title__endswith='GB')
# SELECT * FROM product WHERE title LIKE '%GB';
# Product.object.filter(title__iendswith='GB')
# SELECT * FROM product WHERE title ILIKE '%GB';

# '%work%'
# Product.object.filter(title__contains='Samsung')
# SELECT * FROM product WHERE title LIKE '%Samsung%';
# Product.object.filter(title__icontains='Samsung')
# SELECT * FROM product WHERE title ILIKE '%Samsung%';

# 'work'
# Product.objects.filter(title__exact='Apple IPhone 12')
# SELECT * FROM product WHERE title LIKE 'Apple IPhone 12':
# Product.objects.filter(title__iexact='Apple IPhone 12')
# SELECT * FROM product WHERE title ILIKE 'Apple IPhone 12':

# ORDER BY
# Product.objects.order_by('price')
# SELECT * FROM product ORDER BY price ASC:
# Product.objects.order_by('-price')
# SELECT * FROM product ORDER BY price DESC:

# Product.objects.order_by('-price', 'title')
# SELECT * FROM product ORDER BY price DESC, title ASC:

# LIMIT
# Project.object.all()[:2]
# SELECT * FROM product LIMIT 2;

# Project.object.all()[3:6]
# SELECT * FROM product LIMIT 3 OFFSET 3;

# Project.object.first()
# SELECT * FROM product LIMIT 1;

# get() - возвращает один объект

# Product.objects.get(id=1)
# SELECT * FROM product WHERE id=1;

# DoesNotExist - возникает, если не найден ни один объект
# MultipleObjectsRetrieved - возникает, когда найдено больше одного объекта

# count() - возвращает количество результатов
# SELECT COUNT(*) FROM product;

# Product.object.filter(...).count()
# SELECT COUNT(*) FROM product WHERE ...

#exclude()
# Product.objects.filter(price__gt=10000)
# SELECT * FROM product WHERE price > 10000

# Product.objects.exclude(price _gt=10000)
# SELECT * FROM product WHERE NOT price > 10000;

# QuerySet - список объектов модели

# HTTP методы