from rest_framework import viewsets, filters
from rest_framework.views import APIView, exception_handler
from rest_framework.response import Response
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from collections import defaultdict

from .models import User, FinancialRecord
from .serializers import UserSerializer, FinancialRecordSerializer, DashboardSerializer
from .permissions import (
    CanViewDashboard,
    IsAdminUserCustom,
    IsAuthenticatedAndActive,
    IsViewerOrAbove,
    RoleBasedRecordPermission
)

# ----------------------------
# Custom Exception Handler
# ----------------------------
def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        response.data = {
            'error': True,
            'status_code': response.status_code,
            'message': response.data
        }

    return response

# ----------------------------
# User Management (Admin only)
# ----------------------------
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUserCustom]

# ----------------------------
# Financial Records
# ----------------------------
class FinancialRecordViewSet(viewsets.ModelViewSet):
    serializer_class = FinancialRecordSerializer
    permission_classes = [IsAuthenticatedAndActive, RoleBasedRecordPermission]
    queryset = FinancialRecord.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['category', 'type']
    ordering_fields = ['date', 'amount']

    def get_queryset(self):
        user = self.request.user

        if user.role == 'admin':
            queryset = FinancialRecord.objects.all()
        else:
            queryset = FinancialRecord.objects.filter(user=user)

        # Optional filters
        category = self.request.query_params.get('category')
        record_type = self.request.query_params.get('type')
        date = self.request.query_params.get('date')

        if category:
            queryset = queryset.filter(category__icontains=category)
        if record_type:
            queryset = queryset.filter(type=record_type)
        if date:
            queryset = queryset.filter(date=date)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# ----------------------------
# Dashboard View
# ----------------------------
class DashboardView(APIView):
    permission_classes = [IsViewerOrAbove]

    def get(self, request):
        user = request.user

        # Admin → all records, others → own records
        if user.role == 'admin':
            queryset = FinancialRecord.objects.all()
        else:
            queryset = FinancialRecord.objects.filter(user=user)

        # Total Income
        total_income = queryset.filter(type='income').aggregate(total=Sum('amount'))['total'] or 0
        # Total Expense
        total_expense = queryset.filter(type='expense').aggregate(total=Sum('amount'))['total'] or 0
        # Net Balance
        net_balance = total_income - total_expense

        # Category-wise Summary
        category_data = queryset.values('category', 'type').annotate(total=Sum('amount'))
        category_summary = defaultdict(lambda: {'income': 0, 'expense': 0})
        for item in category_data:
            category_summary[item['category']][item['type']] = item['total']

        # Recent Transactions
        recent_transactions = queryset.order_by('-date')[:5]

        # ===== Monthly Trends =====
        monthly_data = queryset.annotate(month=TruncMonth('date')) \
                               .values('month', 'type') \
                               .annotate(total=Sum('amount'))

        # Add this code here
        monthly_trends = defaultdict(lambda: {'income': 0, 'expense': 0})
        for item in monthly_data:
            month = item['month'].strftime('%Y-%m')
            monthly_trends[month][item['type']] = item['total']

        # Prepare response
        response_data = {
            "total_income": total_income,
            "total_expense": total_expense,
            "net_balance": net_balance,
            "category_summary": category_summary,
            "recent_transactions": recent_transactions,
            "monthly_trends": monthly_trends,
        }

        serializer = DashboardSerializer(response_data)
        return Response(serializer.data)