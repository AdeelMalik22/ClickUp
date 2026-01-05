



class IsOwnerOrReadOnly:
    """
    Custom permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True

        # Write permissions are only allowed to the owner of the snippet.
        return obj.owner == request.user

    def has_permission(self, request, view):
        # Allow read-only access for any request
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True

        # Write permissions are only allowed to authenticated users
        return request.user and request.user.is_authenticated