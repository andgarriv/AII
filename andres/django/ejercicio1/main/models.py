from django.db import models


# Create your models here.
class Equipo(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    fundacion = models.PositiveIntegerField(verbose_name="Año de fundación", null=True, blank=True)
    estadio = models.CharField(max_length=100, blank=True)
    aforo = models.PositiveIntegerField(null=True, blank=True)
    direccion = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Equipo"
        verbose_name_plural = "Equipos"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Temporada(models.Model):
    anyo = models.PositiveIntegerField(verbose_name="Año", unique=True)

    class Meta:
        verbose_name = "Temporada"
        verbose_name_plural = "Temporadas"
        ordering = ['-anyo']

    def __str__(self):
        return str(self.anyo)


class Jornada(models.Model):
    numero = models.PositiveIntegerField(blank=True)
    fecha = models.CharField(max_length=100)
    temporada = models.ForeignKey(Temporada, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Jornada"
        verbose_name_plural = "Jornadas"
        ordering = ['temporada', 'numero']

    def __str__(self):
        return f"Temporada {self.temporada.anyo} - Jornada {self.numero}"


class Partido(models.Model):
    local = models.ForeignKey(
        Equipo,
        on_delete=models.CASCADE,
        related_name='partidos_local'
    )
    visitante = models.ForeignKey(
        Equipo,
        on_delete=models.CASCADE,
        related_name='partidos_visitante'
    )
    goles_local = models.PositiveIntegerField(null=True, blank=True)
    goles_visitante = models.PositiveIntegerField(null=True, blank=True)
    jornada = models.ForeignKey(Jornada, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = "Partido"
        verbose_name_plural = "Partidos"
        ordering = ['jornada']

    def __str__(self):
        return f"{self.local} vs {self.visitante} - {self.goles_local}:{self.goles_visitante}"
