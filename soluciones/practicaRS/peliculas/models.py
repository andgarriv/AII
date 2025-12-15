from django.db import models

# Modelo para películas
class Pelicula(models.Model):
    idPelicula = models.IntegerField(primary_key=True)
    titulo = models.CharField(max_length=255)
    director = models.CharField(max_length=255)
    idIMDB = models.IntegerField()
    generos = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.titulo} ({self.idIMDB})"

# Modelo para puntuaciones
class Puntuacion(models.Model):
    idUsuario = models.IntegerField()
    pelicula = models.ForeignKey(Pelicula, on_delete=models.CASCADE)
    puntuacion = models.IntegerField()

    def save(self, *args, **kwargs):
        if 10 > int(self.puntuacion) > 50 and int(self.puntuacion) % 5 != 0:
            raise ValueError("La puntuación debe estar entre 10 y 50 en incrementos de 5.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Usuario {self.idUsuario} - {self.pelicula.titulo}: {self.puntuacion}"
