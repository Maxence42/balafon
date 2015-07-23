# -*- coding: utf-8 -*-
"""REST api powered by django-rest-framework"""

from django.utils.translation import ugettext as _

from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from sanza.Crm.models import Action, ActionType
from sanza.Profile.models import ContactProfile
from sanza.Store.models import (
    SaleItem, StoreItem, StoreItemCategory, StoreItemTag, StoreManagementActionType, DeliveryPoint
)
from sanza.Store import serializers, settings
from sanza.Store.settings import get_cart_type_name
from sanza.Store.utils import notify_cart_to_admin, confirm_cart_to_user


def get_public_api_permissions():
    """get public api permissions"""
    if settings.is_public_api_allowed():
        return [permissions.IsAuthenticatedOrReadOnly]
    else:
        return [permissions.IsAuthenticated]


class SaleItemViewSet(viewsets.ModelViewSet):
    """returns sales items"""
    queryset = SaleItem.objects.all()
    serializer_class = serializers.SaleItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self, *args, **kwargs):
        if self.request.method in ('PUT', 'POST'):
            return serializers.UpdateSaleItemSerializer
        else:
            return super(SaleItemViewSet, self).get_serializer_class(*args, **kwargs)

    def get_queryset(self):
        """returns objects"""
        action_id = self.kwargs['action_id']
        return self.queryset.filter(sale__action__id=action_id)


class StoreItemViewSet(viewsets.ModelViewSet):
    """returns sales items"""
    queryset = StoreItem.objects.all()
    serializer_class = serializers.StoreItemSerializer
    permission_classes = get_public_api_permissions()

    def get_queryset(self):
        """returns objects"""
        name = self.request.GET.get('name', None)
        if name:
            return self.queryset.filter(name__icontains=name)[:20]

        fullname = self.request.GET.get('fullname', None)
        if fullname:
            return self.queryset.filter(name__icontains=fullname)

        category = self.request.GET.get('category', None)
        if category:
            return self.queryset.filter(category=category)

        tag = self.request.GET.get('tag', None)
        if tag:
            return self.queryset.filter(tags=tag)

        return self.queryset


class StoreItemCategoryViewSet(viewsets.ModelViewSet):
    """returns categories"""
    queryset = StoreItemCategory.objects.all()
    serializer_class = serializers.StoreItemCategorySerializer
    permission_classes = get_public_api_permissions()


class StoreItemTagViewSet(viewsets.ModelViewSet):
    """returns tags"""
    queryset = StoreItemTag.objects.all()
    serializer_class = serializers.StoreItemTagSerializer
    permission_classes = get_public_api_permissions()


class CartView(APIView):
    """post a cart"""
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        """receive a new cart"""

        cart_serializer = serializers.CartSerializer(data=request.data)
        if cart_serializer.is_valid():

            #Get Contact
            try:
                profile = ContactProfile.objects.get(user=request.user)
                contact = profile.contact
            except ContactProfile.DoesNotExist:
                return Response({'ok': False, 'message': _(u"You don't have a valid profile")})

            #Get Delivery point
            try:
                delivery_point = DeliveryPoint.objects.get(id=cart_serializer.validated_data["delivery_point"])
            except DeliveryPoint.DoesNotExist:
                return Response({'ok': False, 'message': _(u"Invalid delivery point")})

            #Create a new Sale
            action_type_name = get_cart_type_name()
            action_type = ActionType.objects.get_or_create(name=action_type_name)[0]

            #Force this type to be managed by the store
            StoreManagementActionType.objects.get_or_create(action_type=action_type)

            notes = cart_serializer.validated_data["notes"].strip()
            if notes:
                lines = notes.split('\n')
                subject = lines[0]
                detail = '\n'.join(lines[1:])
            else:
                subject = detail = ''

            action = Action.objects.create(
                planned_date=cart_serializer.validated_data['purchase_datetime'],
                subject=subject,
                detail=detail,
                status=action_type.default_status,
                type=action_type
            )
            action.contacts.add(contact)
            action.save()

            action.sale.delivery_point = delivery_point
            action.sale.save()

            #for each line add a sale item
            for index, item in enumerate(cart_serializer.validated_data['items']):

                try:
                    store_item = StoreItem.objects.get(id=item['id'])
                except StoreItem.DoesNotExist:
                    #ignore if not existing
                    continue

                SaleItem.objects.create(
                    sale=action.sale,
                    quantity=item['quantity'],
                    item=store_item,
                    vat_rate=store_item.vat_rate,
                    pre_tax_price=store_item.pre_tax_price,
                    text=store_item.name,
                    order_index=index+1
                )

            confirm_cart_to_user(profile, action)
            notify_cart_to_admin(profile, action)

            #Done
            return Response({
                'ok': True,
                'deliveryDate': action.planned_date,
                'deliveryPlace': action.sale.delivery_point.name,
            })
        else:
            return Response(
                {
                    'ok': False,
                    'message': u', '.join([u'{0}: {1}'.format(*err) for err in cart_serializer.errors.items()])
                }
            )