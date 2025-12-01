from django.db import models

class Temporada(models.Model):
    anyo = models.IntegerField()  # año inicial de la temporada

    def __str__(self):
        return f"Temporada {self.anyo}-{self.anyo + 1}"

class Jornada(models.Model):
    numero = models.IntegerField()
    fecha = models.CharField(max_length=200)
    temporada = models.ForeignKey(Temporada, on_delete=models.CASCADE)

    def __str__(self):
        return f"Jornada {self.numero} ({self.temporada.anyo})"

class Equipo(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    estadio = models.CharField(max_length=100, null=True, blank=True)
    fundacion = models.IntegerField(null=True, blank=True)  # antes anyo_fundacion
    aforo = models.IntegerField(null=True, blank=True)
    direccion = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.nombre

class Partido(models.Model):
    local = models.ForeignKey(Equipo, related_name='partidos_local', on_delete=models.CASCADE)
    visitante = models.ForeignKey(Equipo, related_name='partidos_visitante', on_delete=models.CASCADE)
    goles_local = models.PositiveIntegerField()
    goles_visitante = models.PositiveIntegerField()
    jornada = models.ForeignKey(Jornada, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.equipo_local} {self.goles_local} - {self.goles_visitante} {self.equipo_visitante}"
