from django.db import models


class Company(models.Model):
    """Represents a company involved in the inventory and orders."""
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Weight(models.Model):
    """Represents different weight categories for bags."""
    name = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name


class BagType(models.Model):
    """Represents the type of bag used."""
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name


# class Order(models.Model):
#     """Represents an order with billing details."""
#     company = models.ForeignKey(Company, on_delete=models.PROTECT)
#     weight = models.ForeignKey(Weight, on_delete=models.PROTECT)
#     bag_type = models.ForeignKey(BagType, on_delete=models.PROTECT)
#     quantity = models.PositiveIntegerField()
#     oic = models.IntegerField()
#     order_date = models.DateField(auto_now_add=True)
#     billed_date = models.DateField(null=True, blank=True)
#     is_billed = models.BooleanField(default=False)
#     email_link = models.URLField(max_length=255, null=True, blank=True)
#     notes = models.TextField(null=True, blank=True)
# 
#     def __str__(self):
#         return f"Order {self.id} - {self.quantity}x {self.bag_type} ({self.weight})"


class InventoryFlow(models.Model):
    """Represents the flow of inventory (stock movements)."""
    company = models.ForeignKey(Company, on_delete=models.PROTECT)
    weight = models.ForeignKey(Weight, on_delete=models.PROTECT)
    bag_type = models.ForeignKey(BagType, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    movement_date = models.DateTimeField(auto_now_add=True)
    invoice = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.quantity}x {self.bag_type} ({self.weight}) - {self.movement_date}"


class TotalStock(models.Model):
    """Represents the total stock available per company, weight, and bag type."""
    company = models.ForeignKey(Company, on_delete=models.PROTECT)
    weight = models.ForeignKey(Weight, on_delete=models.PROTECT)
    bag_type = models.ForeignKey(BagType, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('company', 'weight', 'bag_type')

    def __str__(self):
        return f"{self.company} - {self.quantity}x {self.bag_type} ({self.weight})"
