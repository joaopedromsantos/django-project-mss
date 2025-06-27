from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q, F
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

from .models import TotalStock, BagType, Weight, Company, InventoryFlow

@login_required
def total_stock_list(request):
    query = TotalStock.objects.all()

    # Filtro de busca para cada coluna
    company_filter = request.GET.get('company', '')
    weight_filter = request.GET.get('weight', '')
    bag_type_filter = request.GET.get('bag_type', '')

    if company_filter:
        query = query.filter(company_id=company_filter)
    if weight_filter:
        query = query.filter(weight_id=weight_filter)
    if bag_type_filter:
        query = query.filter(bag_type_id=bag_type_filter)

    company_choices = Company.objects.values_list('id', 'name').distinct()
    weight_choices = Weight.objects.values_list('id', 'name').distinct()
    bag_type_choices = BagType.objects.values_list('id', 'name').distinct()

    # Paginação
    paginator = Paginator(query, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    params = request.GET.copy()
    if 'page' in params:
        del params['page']

    # Context
    context = {
        'page_obj': page_obj,
        'current_filters': params.urlencode(),
        'company_filter': company_filter,
        'weight_filter': weight_filter,
        'bag_type_filter': bag_type_filter,
        'company_choices': company_choices,
        'weight_choices': weight_choices,
        'bag_type_choices': bag_type_choices,
    }

    return render(request, 'inventory/total_stock_list.html', context=context)


@login_required
def inventory_flow(request):
    query = InventoryFlow.objects.all().order_by('-movement_date')

    company_filter = request.GET.get('company', '')
    weight_filter = request.GET.get('weight', '')
    bag_type_filter = request.GET.get('bag_type', '')
    invoice_filter = request.GET.get('invoice', '')
    date_filter = request.GET.get('daterange', '')

    if company_filter:
        query = query.filter(company_id=company_filter)
    if weight_filter:
        query = query.filter(weight_id=weight_filter)
    if bag_type_filter:
        query = query.filter(bag_type_id=bag_type_filter)
    if invoice_filter:
        query = query.filter(invoice__icontains=invoice_filter)

    if date_filter:
        try:
            start_date_str, end_date_str = date_filter.split(' - ')
            start_date = datetime.strptime(start_date_str, '%d/%m/%Y').date()
            end_date = datetime.strptime(end_date_str, '%d/%m/%Y').date()
            query = query.filter(movement_date__date__range=(start_date, end_date))
        except (ValueError, TypeError):
            pass

    company_choices = Company.objects.values_list('id', 'name').distinct()
    weight_choices = Weight.objects.values_list('id', 'name').distinct()
    bag_type_choices = BagType.objects.values_list('id', 'name').distinct()

    # Paginação
    paginator = Paginator(query, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    params = request.GET.copy()
    if 'page' in params:
        del params['page']

    # Context
    context = {
        'page_obj': page_obj,
        'current_filters': params.urlencode(),
        'company_filter': company_filter,
        'weight_filter': weight_filter,
        'bag_type_filter': bag_type_filter,
        'company_choices': company_choices,
        'weight_choices': weight_choices,
        'bag_type_choices': bag_type_choices,
    }

    return render(request, 'inventory/inventory_flow.html', context=context)

@login_required
@transaction.atomic
def add_stock_view(request):
    if request.method == 'POST':
        try:
            company_id = request.POST.get('company', '')
            weight_id = request.POST.get('weight', '')
            bag_type_id = request.POST.get('bag_type', '')
            quantity = request.POST.get('quantity', '')
            invoice = request.POST.get('invoice', '')
            # Validação simples
            if not all([company_id, weight_id, bag_type_id, quantity]):
                return JsonResponse({'error': 'Todos os campos obrigatórios devem ser preenchidos.'}, status=400)

            try:
                quantity = int(quantity)
                if quantity <= 0:
                    raise ValueError("A quantidade deve ser um número positivo.")
            except (ValueError, TypeError):
                return JsonResponse({'error': 'A quantidade deve ser um número válido.'}, status=400)

            stock_record, created = TotalStock.objects.get_or_create(
                company_id=company_id,
                weight_id=weight_id,
                bag_type_id=bag_type_id,
                defaults={'quantity': 0}
            )

            stock_record.quantity = F('quantity') + quantity
            stock_record.save()

            InventoryFlow.objects.create(
                company_id=company_id,
                weight_id=weight_id,
                bag_type_id=bag_type_id,
                quantity=quantity,
                invoice=invoice
            )

            return JsonResponse({'status': 'success', 'message': 'Estoque adicionado com sucesso!'})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método inválido'}, status=405)


@login_required
@transaction.atomic
def delete_flow_view(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido.'}, status=405)

    try:
        flow_to_delete = get_object_or_404(InventoryFlow.objects.select_for_update(), pk=pk)

        stock_record = TotalStock.objects.select_for_update().get(
            company=flow_to_delete.company,
            weight=flow_to_delete.weight,
            bag_type=flow_to_delete.bag_type,
        )

        stock_record.quantity = F('quantity') - flow_to_delete.quantity
        stock_record.save()

        flow_to_delete.delete()

        messages.success(request, 'Movimentação excluída e estoque atualizado com sucesso!')

    except Exception as e:
        messages.error(request, f'Erro ao excluir: {str(e)}')

    return redirect('inventory:inventory_flow')