from django.db import models


# Create your models here.
class Pais(models.Model):
    idPais = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Pais"
        verbose_name_plural = "Paises"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Denominacion(models.Model):
    idDenominacion = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)
    pais = models.ForeignKey('Pais', on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Denominacion"
        verbose_name_plural = "Denominaciones"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Uva(models.Model):
    idUva = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Uva"
        verbose_name_plural = "Uvas"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Vino(models.Model):
    idVino = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)
    precio = models.DecimalField(max_digits=6, decimal_places=2)
    denominacion = models.ForeignKey('Denominacion', on_delete=models.CASCADE)
    uvas = models.ManyToManyField('Uva', related_name='vinos', blank=True)

    class Meta:
        verbose_name = "Vino"
        verbose_name_plural = "Vinos"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre
