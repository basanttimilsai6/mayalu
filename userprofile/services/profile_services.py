# from core.exceptions import ObjectNotFoundException
# from core.global_helpers import update_instance_values
# from django.contrib.postgres.expressions import ArraySubquery
# from django.db.models import (
#     Count,
#     F,
#     FloatField,
#     Func,
#     JSONField,
#     OuterRef,
#     Q,
#     QuerySet,
#     Sum,
#     Value,
# )
# from django.db.models.fields.json import KeyTextTransform
# from django.db.models.functions import Cast, Coalesce

# # from django.utils import timezone
# from order.models import ORDER_STATUS, OrderItem
# from referral.services.referral_complete_services import ReferralCompleteServices as rcs
# from rest_framework.exceptions import PermissionDenied
# from user_auth.models import User
# from user_profile.models import Address, Shop, UserProfile
# from user_profile.models import FavouriteProductSku
# from product.models import ProductSku
# from user_auth.models import AuthMeta

# class UserProfileServices:
#     @staticmethod
#     def get_user_profile_object(
#         user: User = None, id: int = None, raise_exception=False
#     ):
#         if user:
#             return user.user_profile
#         elif id:
#             try:
#                 return UserProfile.objects.get(id=id)
#             except UserProfile.DoesNotExist:
#                 if raise_exception:
#                     raise ObjectNotFoundException(f"Invalid user profile id: {id}")
#                 else:
#                     return None

#     @staticmethod
#     def get_user_profile_prefetched_queryset() -> QuerySet[UserProfile]:
#         # now = timezone.now()
#         product_sku_subquery = (
#             OrderItem.objects.filter(
#                 order__user_id=OuterRef("user_id"),
#                 order__status=ORDER_STATUS.delivered,
#             )
#             .annotate(
#                 product_sku=(
#                     Cast(
#                         KeyTextTransform("product_sku", "data"),
#                         JSONField(),
#                     )
#                 ),
#                 total_amount=Cast(
#                     KeyTextTransform("total_amount", "data"),
#                     FloatField(),
#                 ),
#             )
#             .values("product_sku")
#             .annotate(
#                 count=Count("product_sku"),
#                 total_amount=Sum("total_amount"),
#             )
#             .order_by("-total_amount", "-count")
#             .annotate(
#                 item=Cast(
#                     Func(
#                         Value("product_sku"),
#                         F("product_sku"),
#                         Value("count"),
#                         F("count"),
#                         Value("total_amount"),
#                         F("total_amount"),
#                         function="json_build_object",
#                     ),
#                     JSONField(),
#                 )
#             )
#             .values_list("item", flat=True)
#         )

#         brand_sku_subquery = (
#             OrderItem.objects.filter(
#                 order__user_id=OuterRef("user_id"),
#                 order__status=ORDER_STATUS.delivered,
#             )
#             .annotate(
#                 brand=(
#                     Cast(
#                         KeyTextTransform("brand", "data"),
#                         JSONField(),
#                     )
#                 ),
#                 total_amount=Cast(
#                     KeyTextTransform("total_amount", "data"),
#                     FloatField(),
#                 ),
#             )
#             .values("brand")
#             .annotate(
#                 count=Count("brand"),
#                 total_amount=Sum("total_amount"),
#             )
#             .order_by("-total_amount", "-count")
#             .annotate(
#                 item=Cast(
#                     Func(
#                         Value("brand"),
#                         F("brand"),
#                         Value("count"),
#                         F("count"),
#                         Value("total_amount"),
#                         F("total_amount"),
#                         function="json_build_object",
#                     ),
#                     JSONField(),
#                 )
#             )
#             .values_list("item", flat=True)
#         )

#         queryset = (
#             UserProfile.objects.select_related(
#                 "shop", "user__loyalty", "user__cashback"
#             )
#             .prefetch_related(
#                 "addresses__province",
#                 "addresses__city",
#                 "addresses__area",
#                 "user__basket",
#             )
#             .annotate(
#                 total_orders=Count("user__orders"),
#                 # total_orders_this_month=Count(
#                 #     "user__orders",
#                 #     filter=Q(
#                 #         user__orders__created_at__year=now.year,
#                 #         user__orders__created_at__month=now.month,
#                 #     ),
#                 # ),
#                 total_order_amount=Coalesce(
#                     Sum("user__orders__total_paid_amount", output_field=FloatField()),
#                     0.0,
#                 ),
#                 # total_order_amount_this_month=Coalesce(
#                 #     Sum(
#                 #         "user__orders__total_paid_amount",
#                 #         filter=Q(
#                 #             user__orders__created_at__year=now.year,
#                 #             user__orders__created_at__month=now.month,
#                 #         ),
#                 #         output_field=FloatField(),
#                 #     ),
#                 #     0.0,
#                 # ),
#                 successful_orders=Count(
#                     "user__orders",
#                     filter=Q(
#                         user__orders__status=ORDER_STATUS.delivered,
#                     ),
#                 ),
#                 successful_orders_amount=Coalesce(
#                     Sum(
#                         "user__orders__total_paid_amount",
#                         filter=Q(
#                             user__orders__status=ORDER_STATUS.delivered,
#                         ),
#                         output_field=FloatField(),
#                     ),
#                     0.0,
#                 ),
#                 most_bought_product_sku=ArraySubquery(product_sku_subquery[:5]),
#                 most_bought_brand=ArraySubquery(brand_sku_subquery[:5]),
#             )
#             .order_by("id")
#         )
#         return queryset

#     @staticmethod
#     def get_all_user_profiles():
#         return UserProfile.objects.all()
    
#     @staticmethod
#     def get_all_user_login_at(user):
#         data = AuthMeta.objects.get(user=user).last_login_at
#         if data:
#             return data
#         else:
#             return None
    
#     @staticmethod
#     def get_all_user_active_at(user):
#         data = AuthMeta.objects.get(user=user).last_active_at
#         if data:
#             return data
#         else:
#             return None

#     @staticmethod
#     def create_user_profile(user: User):
#         """To be called when user is created for the first time."""
#         user_profile = UserProfile.objects.create(user=user)
#         ShopServices.create_shop(user_profile=user_profile)
#         return user_profile

#     @staticmethod
#     def update_user_profile(user_profile: UserProfile, data: dict):
#         update_instance_values(user_profile, data)
#         user_profile.save()
#         return user_profile

#     @staticmethod
#     def request_for_verification(user_profile: UserProfile):
#         user_profile.is_submitted = True
#         user_profile.save()
#         return user_profile

#     @staticmethod
#     def revoke_request_for_verification(user_profile: UserProfile):
#         user_profile.is_submitted = False
#         user_profile.save()
#         return user_profile

#     @staticmethod
#     def verify_user_profile(user_profile: UserProfile):
#         user_profile.is_verified = True
#         user_profile.save()
#         # Give referral bonus to the user on verify
#         rcs.mark_referral_used(user=user_profile.user, complete_request_from="verify")
#         return user_profile

#     @staticmethod
#     def unverify_user_profile(user_profile: UserProfile):
#         user_profile.is_submitted = False
#         user_profile.is_verified = False
#         user_profile.save()
#         return user_profile

#     @staticmethod
#     def profile_completeness(instance: UserProfile):
#         # TODO: Calculate profile completeness of the user profile.
#         pass

#     @staticmethod
#     def remove_user_group(group_id: int, ids: list):
#         users = User.objects.filter(user_profile__id__in=ids)
#         [user.groups.remove(group_id) for user in users]


# class ShopServices:
#     @staticmethod
#     def get_shop_object(user_profile: UserProfile):
#         return user_profile.shop

#     @staticmethod
#     def create_shop(user_profile: UserProfile):
#         return Shop.objects.create(user_profile=user_profile)

#     @staticmethod
#     def update_shop(instance: Shop, data: dict):
#         update_instance_values(instance, data)
#         instance.save()
#         return instance


# class AddressServices:
#     @staticmethod
#     def get_address_object(id: int, user_profile: UserProfile, raise_exception=False):
#         try:
#             address = Address.objects.get(id=id)
#             if address.user_profile != user_profile:
#                 raise PermissionDenied
#             return address
#         except Address.DoesNotExist:
#             if raise_exception:
#                 raise ObjectNotFoundException(f"Address does not exist for id:{id}")
#             return None

#     @staticmethod
#     def get_address_object_from_id(id: int, raise_exception=False):
#         try:
#             address = Address.objects.get(id=id)
#             return address
#         except Address.DoesNotExist:
#             if raise_exception:
#                 raise ObjectNotFoundException(f"Address does not exist for id:{id}")
#             return None

#     @staticmethod
#     def get_all_address_objects(user_profile: UserProfile):
#         return user_profile.addresses.all()

#     @staticmethod
#     def create_address(user_profile: UserProfile, data: dict):
#         if data.get("is_default", False):
#             Address.objects.filter(user_profile=user_profile).update(is_default=False)
#         return Address.objects.create(user_profile=user_profile, **data)

#     @staticmethod
#     def update_address(address_instance: Address, data: dict):
#         update_instance_values(instance=address_instance, validated_data=data)
#         address_instance.save()
#         if data.get("is_default", False):
#             Address.objects.filter(user_profile=address_instance.user_profile).exclude(
#                 id=address_instance.id
#             ).update(is_default=False)

#         return address_instance

#     @staticmethod
#     def delete_address(address_instance: Address):
#         address_instance.delete()


# class FavouriteServices:
#    @staticmethod
#    def get_all_fav_skus(usr):
#        return FavouriteProductSku.objects.filter(user=usr)
#    def get_fav_sku(usr,id):
#        return FavouriteProductSku.objects.get(user=usr,product_sku=id)
#    def get_sku(id):
#        return ProductSku.objects.get(id=id)
# # class SocialProfileServices:
# #     @staticmethod
# #     def get_social_profile_object(user: User):
# #         user_profile = UserProfileServices.get_user_profile_object(user=user)
# #         return user_profile.social_profile

# #     @staticmethod
# #     def create_social_profile(user: User):
# #         user_profile = UserProfileServices.get_user_profile_object(user=user)
# #         return SocialProfile.objects.create(user_profile=user_profile)

# #     @staticmethod
# #     def increase_loyalty_point(amount: int, instance: SocialProfile):
# #         instance.loyalty_points = instance.loyalty_points + amount
# #         instance.save()

# #     @staticmethod
# #     def decrease_loyalty_point(amount: int, instance: SocialProfile):
# #         instance.loyalty_points = instance.loyalty_points - amount
# #         instance.save()

# #     @staticmethod
# #     def increase_cash(amount: float, instance: SocialProfile):
# #         instance.cash = instance.cash + amount
# #         instance.save()

# #     @staticmethod
# #     def decrease_cash(amount: float, instance: SocialProfile):
# #         instance.cash = instance.cash - amount
# #         instance.save()

# #     @staticmethod
# #     def increase_total_transaction(amount: float, instance: SocialProfile):
# #         instance.total_transaction = instance.total_transaction + amount
# #         instance.save()

# #     @staticmethod
# #     def decrease_total_transaction(amount: float, instance: SocialProfile):
# #         instance.total_transaction = instance.total_transaction - amount
# #         instance.save()

# #     @staticmethod
# #     def increase_total_margin(amount: float, instance: SocialProfile):
# #         instance.total_margin = instance.total_margin + amount
# #         instance.save()

# #     @staticmethod
# #     def decrease_total_margin(amount: float, instance: SocialProfile):
# #         instance.total_margin = instance.total_margin - amount
# #         instance.save()

# #     @staticmethod
# #     def increase_total_credit(amount: float, instance: SocialProfile):
# #         instance.total_credit = instance.total_credit + amount
# #         instance.save()

# #     @staticmethod
# #     def decrease_total_credit(amount: float, instance: SocialProfile):
# #         instance.total_credit = instance.total_credit - amount
# #         instance.save()
