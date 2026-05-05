from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    friends = models.ManyToManyField('self', blank=True)

    def __str__(self):
        return self.username


class Profile(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    bio = models.TextField(blank=True)
    birth_date = models.DateField(blank=True, null=True)
    height_cm = models.PositiveIntegerField(blank=True, null=True)
    weight_kg = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
    )
    daily_calorie_goal = models.PositiveIntegerField(default=2000)
    show_diary_to_friends = models.BooleanField(default=True)

    def __str__(self):
        return f'Profile: {self.user.username}'


class FriendRequest(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_ACCEPTED = 'accepted'
    STATUS_REJECTED = 'rejected'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_ACCEPTED, 'Accepted'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    from_user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='sent_friend_requests',
    )
    to_user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='received_friend_requests',
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['from_user', 'to_user'],
                name='unique_friend_request',
            ),
        ]

    def __str__(self):
        return f'{self.from_user} -> {self.to_user} ({self.status})'
