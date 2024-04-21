from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from common.permissions import IsOwner


class BaseOwnerViewSet(viewsets.ModelViewSet):
    """
    Abstract base viewset to restrict object operations to the owner of the object only.
    """

    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        """
        Return objects related to the logged-in user only.
        """
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Automatically set the user of the created object to the logged-in user.
        """
        serializer.save(user=self.request.user)
