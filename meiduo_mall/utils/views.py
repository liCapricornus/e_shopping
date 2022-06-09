from django.http import JsonResponse
from django.contrib.auth.mixins import  AccessMixin,LoginRequiredMixin

# 方案一
# class LoginRequiredJSONMixin(AccessMixin):
#     """Verify that the current user is authenticated."""
#     def dispatch(self, request, *args, **kwargs):
#         if not request.user.is_authenticated:
#             return JsonResponse({'code':400,'errmsg':'没有登录！'})
#         return super().dispatch(request, *args, **kwargs)

# 方案二
class LoginRequiredJSONMixin(LoginRequiredMixin):

    def handle_no_permission(self):

        return JsonResponse({'code':400,'errmsg':'没有登录！'})