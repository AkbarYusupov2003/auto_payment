from rest_framework import permissions


class CardOwnerPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return True
        # api_key = request.META.get('HTTP_API_KEY')
        # if settings.SPLAY_STAT_SECRET_KEY == api_key:
        #     return True
        # return False
    
    # def has_object_permission(self, request, view, obj):
    #     # Read permissions are allowed to any request,
    #     # so we'll always allow GET, HEAD or OPTIONS requests.
    #     if request.method in permissions.SAFE_METHODS:
    #         return True

    #     # obj here is a UserProfile instance
    #     return obj.user == request.user