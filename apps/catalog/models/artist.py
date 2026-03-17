from django.db import models
from django.urls import reverse
from .utils import cyrillic_slugify
from .managers import ArtistManager


class Artist(models.Model):
    name = models.CharField(max_length=255, verbose_name='Имя исполнителя')
    slug = models.SlugField(unique=True, blank=True)
    yandex_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='ID Яндекс.Музыки'
    )
    image = models.ImageField(
        upload_to='artists/',
        blank=True,
        null=True,
        verbose_name='Изображение'
    )

    objects = ArtistManager()

    class Meta:
        verbose_name = 'Исполнитель'
        verbose_name_plural = 'Исполнители'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = cyrillic_slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('catalog:artist_detail', kwargs={'slug': self.slug})
