from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q, F
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

from .models import Service, BagType, Weight, Company
from inventory.models import TotalStock

@login_required
def total_services_list(request):
    query = Service.objects.all()

    # Filtro de busca para cada coluna
    company_filter = request.GET.get('company', '')
    weight_filter = request.GET.get('weight', '')
    bag_type_filter = request.GET.get('bag_type', '')
    oic_filter = request.GET.get('oic', '')

    if company_filter:
        query = query.filter(company_id=company_filter)
    if weight_filter:
        query = query.filter(weight_id=weight_filter)
    if bag_type_filter:
        query = query.filter(bag_type_id=bag_type_filter)
    if oic_filter:
        query = query.filter(oic__icontains=oic_filter)

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

    return render(request, 'services/services.html', context=context)

@login_required
@transaction.atomic
def create_service(request):
    if request.method != 'POST':
        messages.error(request, 'Ação permitida apenas via formulário.')
        return redirect('services:services_list')

    try:
        company_id = request.POST.get('company')
        weight_id = request.POST.get('weight')
        bag_type_id = request.POST.get('bag_type')
        quantity_str = request.POST.get('quantity')
        oic = request.POST.get('oic', '')
        email = request.POST.get('email', '')
        notes = request.POST.get('notes', '')
        request_date = request.POST.get('request_date')

        # 2. Validação dos dados
        if not all([company_id, weight_id, bag_type_id, quantity_str]):
            messages.error(request, 'Todos os campos obrigatórios devem ser preenchidos.')
            return redirect('services:services_list')

        quantity = int(quantity_str)
        if quantity <= 0:
            messages.error(request, 'A quantidade deve ser um número positivo.')
            return redirect('services:services_list')

        stock_record = TotalStock.objects.select_for_update().get(
            company_id=company_id,
            weight_id=weight_id,
            bag_type_id=bag_type_id,
        )

        # Verifica se há estoque suficiente
        if stock_record.quantity < quantity:
            messages.error(request, f"Estoque insuficiente. Disponível: {stock_record.quantity}.")
            return redirect('services:services_list')

        # Subtrai do estoque
        stock_record.quantity = F('quantity') - quantity
        stock_record.save()

        # Cria o novo serviço
        Service.objects.create(
            company_id=company_id,
            weight_id=weight_id,
            bag_type_id=bag_type_id,
            quantity=quantity,
            oic=oic,
            email=email,
            notes=notes,
            request_date=datetime.strptime(request_date, '%Y-%m-%d') if request_date else datetime.now(),
        )

        messages.success(request, 'Serviço adicionado e estoque atualizado com sucesso!')

    except TotalStock.DoesNotExist:
        messages.error(request, 'Não há um registro de estoque para este tipo de item. A operação foi cancelada.')
    except (ValueError, TypeError):
        messages.error(request, 'A quantidade informada é inválida.')
    except Exception as e:
        messages.error(request, f'Ocorreu um erro inesperado: {e}')

    return redirect('services:services_list')


def get_service_details(request, pk):
    """Fornece os dados de um serviço em formato JSON para o modal."""
    service = get_object_or_404(Service, pk=pk)
    data = {
        'company_id': service.company.id,
        'weight_id': service.weight.id,
        'bag_type_id': service.bag_type.id,
        'quantity': service.quantity,
        'oic': service.oic,
        'notes': service.notes,
        'is_billed': service.is_billed,
        'request_date': service.request_date.isoformat(),
        'billed_date': service.billed_date.isoformat() if service.billed_date else '',
        'email': service.email,
    }
    return JsonResponse(data)

@login_required
@transaction.atomic
def update_service(request, pk):
    """Atualiza uma marcação existente."""
    if request.method != 'POST':
        messages.error(request, 'Método não permitido.')
        return redirect('services:services_list')

    service = get_object_or_404(Service, pk=pk)
    
    try:
        service.oic = request.POST.get('oic', '')
        service.notes = request.POST.get('notes', '')
        service.is_billed = request.POST.get('is_billed') == 'on'
        service.save()
        messages.success(request, 'Marcação atualizada com sucesso!')
    except Exception as e:
        messages.error(request, f'Erro ao atualizar: {e}')
        
    return redirect('services:services_list')


@login_required
@transaction.atomic
def delete_service(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido.'}, status=405)

    try:
        service_to_delete = get_object_or_404(Service.objects.select_for_update(), pk=pk)

        stock_record = TotalStock.objects.select_for_update().get(
            company=service_to_delete.company,
            weight=service_to_delete.weight,
            bag_type=service_to_delete.bag_type,
        )

        stock_record.quantity = F('quantity') + service_to_delete.quantity
        stock_record.save()

        service_to_delete.delete()

        messages.success(request, 'Movimentação excluída e estoque atualizado com sucesso!')

    except Exception as e:
        messages.error(request, f'Erro ao excluir: {str(e)}')

    return redirect('services:services_list')