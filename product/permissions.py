from rest_framework.permissions import BasePermission


class IsAuthorOrIsAdmin(BasePermission):
    # create, listing
    # def has_permission(self, request, view):

    # update, partial_update, destroy, retreive
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or request.user == obj.author

