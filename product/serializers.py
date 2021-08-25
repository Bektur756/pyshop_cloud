from rest_framework import serializers
from product.models import Product, ProductReview


# class ProductSerializer(serializers.Serializer):
#     title = serializers.CharField()
#     description = serializers.CharField()
#     price = serializers.DecimalField()

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'title', 'price')

class ProductDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'title', 'description', 'price', 'image')

class CreateProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

    def validate_price(self, price):
        if price < 0:
            raise serializers.ValidationError('Цена не может быть отрицательной')
        return price


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ProductReview
        fields = ('id', 'author','product', 'text', 'rating', 'created_at')

    def validate_product(self, product):
        request = self.context.get('request')
        user = request.user
        if self.Meta.model.objects.filter(product=product, author=user).exists():
            raise serializers.ValidationError('Вы уже оставляли отзыв вчера')
        return product

    def validate_rating(self, rating):
        if rating not in range(1, 6):
            raise serializers.ValidationError('Рейтинг может быть от одного до 5')
        return rating

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['author'] = request.user
        return super().create(validated_data)
