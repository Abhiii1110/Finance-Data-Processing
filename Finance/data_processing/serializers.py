from rest_framework import serializers
from .models import User,FinancialRecord

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role', 'is_active']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class FinancialRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialRecord
        fields = '__all__'
        read_only_fields = ['user']
    
    # Field-level validation
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

    def validate_type(self, value):
        if value not in ['income', 'expense']:
            raise serializers.ValidationError("Type must be 'income' or 'expense'.")
        return value

    # Object-level validation
    def validate(self, attrs):
        if attrs.get('type') == 'expense' and attrs.get('amount') > 100000:
            raise serializers.ValidationError("Expense too large, please review.")
        return attrs

class DashboardSerializer(serializers.Serializer):
    total_income = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_expense = serializers.DecimalField(max_digits=12, decimal_places=2)
    net_balance = serializers.DecimalField(max_digits=12, decimal_places=2)
    category_summary = serializers.DictField()
    recent_transactions = FinancialRecordSerializer(many=True)
    monthly_trends = serializers.DictField()