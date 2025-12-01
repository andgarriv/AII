from django.db import models

# Create your models here.
class Pais(models.Model):
    idPais = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Denominacion(models.Model):
    idDenominacion = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre
    
class Uva(models.Model):
    idUva = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Vino(models.Model):
    idVino = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    precio = models.FloatField()
    denominacion = models.ForeignKey(Denominacion, on_delete=models.CASCADE)
    uvas = models.ManyToManyField(Uva)

    def __str__(self):
        return self.nombre
    