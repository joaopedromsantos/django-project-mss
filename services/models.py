from django.db import models
from django.utils import timezone
from inventory.models import Company, Weight, BagType


class Service(models.Model):
    # --- Relacionamentos (Foreign Keys) ---
    company = models.ForeignKey(Company, on_delete=models.PROTECT, verbose_name="Empresa")
    weight = models.ForeignKey(Weight, on_delete=models.PROTECT, verbose_name="Peso (Kg)")
    bag_type = models.ForeignKey(BagType, on_delete=models.PROTECT, verbose_name="Tipo de Saco")

    # --- Detalhes do Serviço ---
    oic = models.CharField(max_length=100, blank=True, null=True, verbose_name="OIC",
                           help_text="Ordem Interna de Compra ou identificador similar.")
    quantity = models.PositiveIntegerField(verbose_name="Quantidade")
    request_date = models.DateTimeField(default=timezone.now, verbose_name="Data do Pedido")

    # --- Status de Faturamento ---
    is_billed = models.BooleanField(default=False, verbose_name="Cobrado")
    billed_date = models.DateField(blank=True, null=True, verbose_name="Data da Cobrança",
                                       help_text="Preenchido apenas quando o serviço é marcado como cobrado.")

    # --- Contato e Observações ---
    email = models.TextField(max_length=254, blank=True, null=True, verbose_name="Email do Pedido")
    notes = models.TextField(blank=True, null=True, verbose_name="Observações")

    def __str__(self):
        return f"Serviço #{self.pk} para {self.company.name} - {self.request_date.strftime('%d/%m/%Y')}"

    class Meta:
        verbose_name = "Serviço"
        verbose_name_plural = "Serviços"
        ordering = ['-request_date']