from django.db import models
from django.urls import reverse
from django.utils.text import slugify


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

    class Meta:
        verbose_name = 'Исполнитель'
        verbose_name_plural = 'Исполнители'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('catalog:artist_detail', kwargs={'slug': self.slug})


class Release(models.Model):
    RELEASE_TYPES = [
        ('single', 'Сингл'),
        ('ep', 'EP'),
        ('album', 'Альбом'),
    ]

    title = models.CharField(max_length=255, verbose_name='Название')
    slug = models.SlugField(unique=True, blank=True)
    artist = models.ForeignKey(
        Artist,
        on_delete=models.CASCADE,
        related_name='releases',
        verbose_name='Исполнитель'
    )
    release_type = models.CharField(
        max_length=10,
        choices=RELEASE_TYPES,
        default='album',
        verbose_name='Тип релиза'
    )
    cover = models.ImageField(
        upload_to='releases/',
        blank=True,
        null=True,
        verbose_name='Обложка'
    )
    release_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Дата релиза'
    )
    yandex_id = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True,
        verbose_name='ID Яндекс.Музыки'
    )
    average_score = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=0,
        verbose_name='Средний балл'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Релиз'
        verbose_name_plural = 'Релизы'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.artist.name} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.artist.name}-{self.title}")
            slug = base_slug
            counter = 1
            while Release.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('catalog:release_detail', kwargs={'slug': self.slug})

    def update_average_score(self):
        reviews = self.reviews.all()
        if reviews.exists():
            avg = sum(r.total_score for r in reviews) / reviews.count()
            self.average_score = round(avg, 2)
            self.save(update_fields=['average_score'])
