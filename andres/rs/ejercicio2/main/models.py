from django.db import models


# Create your models here.
class Artista(models.Model):
    artistaId = models.AutoField(primary_key=True)
    nombre = models.TextField(verbose_name='Nombre del Artista', unique=True)
    url = models.URLField(verbose_name='URL del Artista', null=True, blank=True)
    imagen = models.URLField(verbose_name='URL de la Imagen', null=True, blank=True)

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ['nombre']


class Etiqueta(models.Model):
    tagId = models.AutoField(primary_key=True)
    tagValue = models.TextField(verbose_name='Nombre de la Etiqueta', unique=True)

    def __str__(self):
        return self.tagValue

    class Meta:
        ordering = ['tagValue']


class UsuarioArtista(models.Model):
    id = models.AutoField(primary_key=True)
    usuarioId = models.TextField()
    artistaId = models.ForeignKey(Artista, on_delete=models.CASCADE)
    tiempoEscucha = models.IntegerField(verbose_name='Tiempo de Escucha (minutos)', default=0)

    def __str__(self):
        return f'Usuario: {self.usuarioId} - Artista: {self.artistaId.nombre}'

    class Meta:
        ordering = ('usuarioId', 'artistaId')
        unique_together = ('usuarioId', 'artistaId')


class UsuarioEtiquetaArtista(models.Model):
    id = models.AutoField(primary_key=True)
    usuarioId = models.TextField()
    artistaId = models.ForeignKey(Artista, on_delete=models.CASCADE)
    tagId = models.ForeignKey(Etiqueta, on_delete=models.CASCADE)

    def __str__(self):
        return f'Usuario: {self.usuarioId} - Artista: {self.artistaId.nombre} - Etiqueta: {self.tagId.tagValue}'

    class Meta:
        ordering = ('usuarioId', 'artistaId', 'tagId')
        unique_together = ('usuarioId', 'artistaId', 'tagId')
