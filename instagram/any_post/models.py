from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save

from rest_framework.authtoken.models import Token


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class AuditModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    latest_edit = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ImagePost(AuditModel):
    caption = models.TextField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    the_image = models.ImageField(upload_to=f"posts/{user}")
    like = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.caption[:25] + '...' + f"{self.user.username}"


class Comment(AuditModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    opinion = models.TextField()
    like = models.PositiveIntegerField()
    post = models.ForeignKey(ImagePost, on_delete=models.CASCADE)


class TheFollowing(AuditModel):
    CHOICE_FIELD = [('a', 'accept'), ('p', 'pending')]
    follower = models.ForeignKey(settings.AUTH_USER_MODEL,
                                 on_delete=models.CASCADE, related_name="follower")
    followed = models.ForeignKey(settings.AUTH_USER_MODEL,
                                 on_delete=models.CASCADE, related_name="followed")
    status = models.CharField(choices=CHOICE_FIELD, max_length=1, default='p')

    class Meta:
        unique_together = ('follower', 'followed',)

    def __str__(self):
        return f"{self.follower}  ==>  {self.followed}"
