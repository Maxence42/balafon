# -*- coding: utf-8 -*-
"""unit testing"""

from datetime import datetime, date, time
from decimal import Decimal
import logging

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from model_mommy import mommy
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from balafon.Store import models


class BaseTestCase(APITestCase):
    """Base class for test cases"""

    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.user = User.objects.create(username="toto", is_active=True, is_staff=True)
        self.user.set_password("abc")
        self.user.save()
        self.client = APIClient()
        self._login()

    def tearDown(self):
        logging.disable(logging.NOTSET)

    def _login(self):
        self.client.login(username="toto", password="abc")


class SalesByCategoryTest(BaseTestCase):
    """Test that we are getting store items"""

    def _get_dates(self, dates):
        """return dates"""
        return [
            {'date': datetime.combine(_date, time.min).isoformat()}
            for _date in dates
        ]

    def test_no_sales(self):
        """It should return all sales data"""

        family = mommy.make(models.StoreItemCategory, parent=None)
        category = mommy.make(models.StoreItemCategory, parent=family, name='MyCat', icon='send')

        url = reverse('store_stats_sales_by_category', args=[2016, 1, 2016, 3])

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data['data']
        months = response.data['months']

        self.assertEqual(len(months), 3)
        self.assertEqual(
            [dict(ordered_dict) for ordered_dict in months],
            self._get_dates([date(2016, 1, 1), date(2016, 2, 1), date(2016, 3, 1)])
        )

        self.assertEqual(len(data), 1)
        category_data = data[0]

        self.assertEqual(category_data['id'], category.id)
        self.assertEqual(category_data['name'], category.name)
        self.assertEqual(category_data['icon'], category.icon)
        self.assertEqual(
            [dict(ordered_dict) for ordered_dict in category_data['values']],
            [{'value': '0.00'}, {'value': '0.00'}, {'value': '0.00'}]
        )

    def test_one_sale(self):
        """It should return all sales data"""

        vat = mommy.make(models.VatRate, rate=Decimal(10))

        family = mommy.make(models.StoreItemCategory, parent=None)
        category1 = mommy.make(models.StoreItemCategory, parent=family)
        article1 = mommy.make(models.StoreItem, category=category1, pre_tax_price=Decimal(10), vat_rate=vat)

        sale1 = mommy.make(models.Sale)
        sale1.action.planned_date = datetime(2016, 1, 5, 12, 0)
        sale1.save()
        mommy.make(
            models.SaleItem, sale=sale1, item=article1, pre_tax_price=article1.pre_tax_price, quantity=1, vat_rate=vat
        )

        url = reverse('store_stats_sales_by_category', args=[2016, 1, 2016, 3])

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data['data']
        months = response.data['months']

        self.assertEqual(len(months), 3)
        self.assertEqual(
            [dict(ordered_dict) for ordered_dict in months],
            self._get_dates([date(2016, 1, 1), date(2016, 2, 1), date(2016, 3, 1)])
        )

        self.assertEqual(len(data), 1)
        category_data = data[0]

        self.assertEqual(category_data['id'], category1.id)
        self.assertEqual(category_data['name'], category1.name)
        self.assertEqual(category_data['icon'], category1.icon)
        self.assertEqual(
            [dict(ordered_dict) for ordered_dict in category_data['values']],
            [{'value': '10.00'}, {'value': '0.00'}, {'value': '0.00'}]
        )

    def test_one_sale_several_items(self):
        """It should return all sales data"""

        vat = mommy.make(models.VatRate, rate=Decimal(10))

        family = mommy.make(models.StoreItemCategory, parent=None)
        category1 = mommy.make(models.StoreItemCategory, parent=family)
        article1 = mommy.make(models.StoreItem, category=category1, pre_tax_price=Decimal(10), vat_rate=vat)
        article2 = mommy.make(models.StoreItem, category=category1, pre_tax_price=Decimal(20), vat_rate=vat)

        sale1 = mommy.make(models.Sale)
        sale1.action.planned_date = datetime(2016, 2, 5, 12, 0)
        sale1.save()
        mommy.make(
            models.SaleItem, sale=sale1, item=article1, quantity=1, pre_tax_price=article1.pre_tax_price, vat_rate=vat
        )
        mommy.make(
            models.SaleItem, sale=sale1, item=article2, quantity=2, pre_tax_price=article2.pre_tax_price, vat_rate=vat
        )

        url = reverse('store_stats_sales_by_category', args=[2016, 1, 2016, 3])

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data['data']
        months = response.data['months']

        self.assertEqual(len(months), 3)
        self.assertEqual(
            [dict(ordered_dict) for ordered_dict in months],
            self._get_dates([date(2016, 1, 1), date(2016, 2, 1), date(2016, 3, 1)])
        )

        self.assertEqual(len(data), 1)
        category_data = data[0]

        self.assertEqual(category_data['id'], category1.id)
        self.assertEqual(category_data['name'], category1.name)
        self.assertEqual(category_data['icon'], category1.icon)
        self.assertEqual(
            [dict(ordered_dict) for ordered_dict in category_data['values']],
            [{'value': '0.00'}, {'value': '50.00'}, {'value': '0.00'}]
        )

    def test_several_sales(self):
        """It should return all sales data"""

        vat = mommy.make(models.VatRate, rate=Decimal(10))

        family = mommy.make(models.StoreItemCategory, parent=None)

        category1 = mommy.make(models.StoreItemCategory, parent=family)
        article1 = mommy.make(models.StoreItem, category=category1, pre_tax_price=Decimal(10), vat_rate=vat)
        article2 = mommy.make(models.StoreItem, category=category1, pre_tax_price=Decimal(20), vat_rate=vat)

        category2 = mommy.make(models.StoreItemCategory, parent=family)
        article3 = mommy.make(models.StoreItem, category=category2, pre_tax_price=Decimal(1), vat_rate=vat)
        article4 = mommy.make(models.StoreItem, category=category2, pre_tax_price=Decimal(2), vat_rate=vat)

        sale1 = mommy.make(models.Sale)
        sale1.action.planned_date = datetime(2016, 1, 5, 12, 0)
        sale1.save()
        mommy.make(
            models.SaleItem, sale=sale1, item=article1, quantity=1, pre_tax_price=article1.pre_tax_price, vat_rate=vat
        )
        mommy.make(
            models.SaleItem, sale=sale1, item=article2, quantity=2, pre_tax_price=article2.pre_tax_price, vat_rate=vat
        )

        sale2 = mommy.make(models.Sale)
        sale2.action.planned_date = datetime(2016, 1, 5, 12, 0)
        sale2.save()
        mommy.make(
            models.SaleItem, sale=sale2, item=article1, quantity=1, pre_tax_price=article1.pre_tax_price, vat_rate=vat
        )
        mommy.make(
            models.SaleItem, sale=sale2, item=article3, quantity=1, pre_tax_price=article3.pre_tax_price, vat_rate=vat
        )

        sale3 = mommy.make(models.Sale)
        sale3.action.planned_date = datetime(2016, 3, 1, 0, 0)
        sale3.save()
        mommy.make(
            models.SaleItem, sale=sale3, item=article4, quantity=1, pre_tax_price=article4.pre_tax_price, vat_rate=vat
        )

        url = reverse('store_stats_sales_by_category', args=[2016, 1, 2016, 3])

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data['data']
        months = response.data['months']

        self.assertEqual(len(months), 3)
        self.assertEqual(
            [dict(ordered_dict) for ordered_dict in months],
            self._get_dates([date(2016, 1, 1), date(2016, 2, 1), date(2016, 3, 1)])
        )

        self.assertEqual(len(data), 2)
        data = sorted(data, key=lambda cat: cat['id'])
        category1_data = data[0]
        category2_data = data[1]

        self.assertEqual(category1_data['id'], category1.id)
        self.assertEqual(category1_data['name'], category1.name)
        self.assertEqual(category1_data['icon'], category1.icon)
        self.assertEqual(
            [dict(ordered_dict) for ordered_dict in category1_data['values']],
            [{'value': '60.00'}, {'value': '0.00'}, {'value': '0.00'}]
        )

        self.assertEqual(category2_data['id'], category2.id)
        self.assertEqual(category2_data['name'], category2.name)
        self.assertEqual(category2_data['icon'], category2.icon)
        self.assertEqual(
            [dict(ordered_dict) for ordered_dict in category2_data['values']],
            [{'value': '1.00'}, {'value': '0.00'}, {'value': '2.00'}]
        )

    def test_view_anonymous(self):
        """It should return http error"""

        self.client.logout()

        url = reverse('store_stats_sales_by_category', args=[2016, 1, 2016, 3])

        response = self.client.get(url, format='json')
        self.assertTrue(response.status_code in (status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED))

    def test_view_non_staff(self):
        """It should return http error"""

        self.user.is_staff = False
        self.user.save()

        url = reverse('store_stats_sales_by_category', args=[2016, 1, 2016, 3])

        response = self.client.get(url, format='json')
        self.assertTrue(response.status_code in (status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED))

    def test_one_sale_tag(self):
        """It should return all sales data"""

        vat = mommy.make(models.VatRate, rate=Decimal(10))

        family = mommy.make(models.StoreItemCategory, parent=None)
        category1 = mommy.make(models.StoreItemCategory, parent=family)
        tag1 = mommy.make(models.StoreItemTag)
        tag2 = mommy.make(models.StoreItemTag)
        tag3 = mommy.make(models.StoreItemTag)
        article1 = mommy.make(models.StoreItem, category=category1, pre_tax_price=Decimal(10), vat_rate=vat)
        article1.tags.add(tag1)
        article1.tags.add(tag2)
        article1.save()

        article2 = mommy.make(models.StoreItem, category=category1, pre_tax_price=Decimal(10), vat_rate=vat)
        article2.tags.add(tag1)
        article2.save()

        sale1 = mommy.make(models.Sale)
        sale1.action.planned_date = datetime(2016, 1, 5, 12, 0)
        sale1.save()
        mommy.make(
            models.SaleItem, sale=sale1, item=article1, pre_tax_price=article1.pre_tax_price, quantity=1, vat_rate=vat
        )
        mommy.make(
            models.SaleItem, sale=sale1, item=article2, pre_tax_price=article2.pre_tax_price, quantity=1, vat_rate=vat
        )

        url = reverse('store_stats_sales_by_tag', args=[2016, 1, 2016, 3])

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data['data']
        months = response.data['months']

        self.assertEqual(len(months), 3)
        self.assertEqual(
            [dict(ordered_dict) for ordered_dict in months],
            self._get_dates([date(2016, 1, 1), date(2016, 2, 1), date(2016, 3, 1)])
        )

        self.assertEqual(len(data), 3)

        data = sorted(data, key=lambda tag: tag['id'])
        tag1_data = data[0]
        tag2_data = data[1]
        tag3_data = data[2]

        self.assertEqual(tag1_data['id'], tag1.id)
        self.assertEqual(tag1_data['name'], tag1.name)
        self.assertEqual(tag1_data['icon'], tag1.icon)
        self.assertEqual(
            [dict(ordered_dict) for ordered_dict in tag1_data['values']],
            [{'value': '20.00'}, {'value': '0.00'}, {'value': '0.00'}]
        )

        self.assertEqual(tag2_data['id'], tag2.id)
        self.assertEqual(tag2_data['name'], tag2.name)
        self.assertEqual(tag2_data['icon'], tag2.icon)
        self.assertEqual(
            [dict(ordered_dict) for ordered_dict in tag2_data['values']],
            [{'value': '10.00'}, {'value': '0.00'}, {'value': '0.00'}]
        )

        self.assertEqual(tag3_data['id'], tag3.id)
        self.assertEqual(tag3_data['name'], tag3.name)
        self.assertEqual(tag3_data['icon'], tag3.icon)
        self.assertEqual(
            [dict(ordered_dict) for ordered_dict in tag3_data['values']],
            [{'value': '0.00'}, {'value': '0.00'}, {'value': '0.00'}]
        )

    def test_one_sale_category_item(self):
        """It should return all sales data"""

        vat = mommy.make(models.VatRate, rate=Decimal(10))

        family = mommy.make(models.StoreItemCategory, parent=None)
        category1 = mommy.make(models.StoreItemCategory, parent=family)
        category2 = mommy.make(models.StoreItemCategory, icon='blabla', parent=family)

        article1 = mommy.make(models.StoreItem, category=category1, pre_tax_price=Decimal(10), vat_rate=vat)
        article2 = mommy.make(models.StoreItem, category=category1, pre_tax_price=Decimal(10), vat_rate=vat)
        article3 = mommy.make(models.StoreItem, category=category2, pre_tax_price=Decimal(10), vat_rate=vat)

        sale1 = mommy.make(models.Sale)
        sale1.action.planned_date = datetime(2016, 1, 5, 12, 0)
        sale1.save()
        mommy.make(
            models.SaleItem, sale=sale1, item=article1, pre_tax_price=article1.pre_tax_price, quantity=1, vat_rate=vat
        )
        mommy.make(
            models.SaleItem, sale=sale1, item=article2, pre_tax_price=article2.pre_tax_price, quantity=2, vat_rate=vat
        )
        mommy.make(
            models.SaleItem, sale=sale1, item=article3, pre_tax_price=article3.pre_tax_price, quantity=1, vat_rate=vat
        )

        url = reverse('store_stats_sales_by_item_of_category', args=[category1.id, 2016, 1, 2016, 3])

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data['data']
        months = response.data['months']

        self.assertEqual(len(months), 3)
        self.assertEqual(
            [dict(ordered_dict) for ordered_dict in months],
            self._get_dates([date(2016, 1, 1), date(2016, 2, 1), date(2016, 3, 1)])
        )

        self.assertEqual(len(data), 2)

        data = sorted(data, key=lambda cat: cat['id'])
        article1_data = data[0]
        article2_data = data[1]

        self.assertEqual(article1_data['id'], article1.id)
        self.assertEqual(article1_data['name'], article1.name)
        self.assertEqual(article1_data['icon'], article1.category.icon)
        self.assertEqual(
            [dict(ordered_dict) for ordered_dict in article1_data['values']],
            [{'value': '10.00'}, {'value': '0.00'}, {'value': '0.00'}]
        )

        self.assertEqual(article2_data['id'], article2.id)
        self.assertEqual(article2_data['name'], article2.name)
        self.assertEqual(article2_data['icon'], article2.category.icon)
        self.assertEqual(
            [dict(ordered_dict) for ordered_dict in article2_data['values']],
            [{'value': '20.00'}, {'value': '0.00'}, {'value': '0.00'}]
        )

    def test_one_sale_family(self):
        """It should return all sales data"""

        vat = mommy.make(models.VatRate, rate=Decimal(10))

        family1 = mommy.make(models.StoreItemCategory, parent=None)
        family2 = mommy.make(models.StoreItemCategory, parent=None)
        category1 = mommy.make(models.StoreItemCategory, parent=family1)
        category2 = mommy.make(models.StoreItemCategory, parent=family1)
        category3 = mommy.make(models.StoreItemCategory, parent=family2)

        article1 = mommy.make(models.StoreItem, category=category1, pre_tax_price=Decimal(1), vat_rate=vat)
        article2 = mommy.make(models.StoreItem, category=category2, pre_tax_price=Decimal(2), vat_rate=vat)
        article3 = mommy.make(models.StoreItem, category=category3, pre_tax_price=Decimal(3), vat_rate=vat)

        sale1 = mommy.make(models.Sale)
        sale1.action.planned_date = datetime(2016, 1, 5, 12, 0)
        sale1.save()
        mommy.make(
            models.SaleItem, sale=sale1, item=article1, pre_tax_price=article1.pre_tax_price, quantity=1, vat_rate=vat
        )
        mommy.make(
            models.SaleItem, sale=sale1, item=article2, pre_tax_price=article2.pre_tax_price, quantity=2, vat_rate=vat
        )
        mommy.make(
            models.SaleItem, sale=sale1, item=article3, pre_tax_price=article3.pre_tax_price, quantity=3, vat_rate=vat
        )

        url = reverse('store_stats_sales_by_family', args=[2016, 1, 2016, 3])

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data['data']
        months = response.data['months']

        self.assertEqual(len(months), 3)
        self.assertEqual(
            [dict(ordered_dict) for ordered_dict in months],
            self._get_dates([date(2016, 1, 1), date(2016, 2, 1), date(2016, 3, 1)])
        )

        self.assertEqual(len(data), 2)

        data = sorted(data, key=lambda cat: cat['id'])
        family1_data = data[0]
        family2_data = data[1]

        self.assertEqual(family1_data['id'], family1.id)
        self.assertEqual(family1_data['name'], family1.name)
        self.assertEqual(family1_data['icon'], family1.icon)
        self.assertEqual(
            [dict(ordered_dict) for ordered_dict in family1_data['values']],
            [{'value': '5.00'}, {'value': '0.00'}, {'value': '0.00'}]
        )

        self.assertEqual(family2_data['id'], family2.id)
        self.assertEqual(family2_data['name'], family2.name)
        self.assertEqual(family2_data['icon'], family2.icon)
        self.assertEqual(
            [dict(ordered_dict) for ordered_dict in family2_data['values']],
            [{'value': '9.00'}, {'value': '0.00'}, {'value': '0.00'}]
        )

    def test_one_sale_family_item(self):
        """It should return all sales data"""

        vat = mommy.make(models.VatRate, rate=Decimal(10))

        family1 = mommy.make(models.StoreItemCategory, parent=None)
        family2 = mommy.make(models.StoreItemCategory, parent=None)
        category1 = mommy.make(models.StoreItemCategory, parent=family1)
        category2 = mommy.make(models.StoreItemCategory, parent=family1)
        category3 = mommy.make(models.StoreItemCategory, parent=family2)

        article1 = mommy.make(models.StoreItem, category=category1, pre_tax_price=Decimal(1), vat_rate=vat)
        article2 = mommy.make(models.StoreItem, category=category2, pre_tax_price=Decimal(2), vat_rate=vat)
        article3 = mommy.make(models.StoreItem, category=category3, pre_tax_price=Decimal(3), vat_rate=vat)

        sale1 = mommy.make(models.Sale)
        sale1.action.planned_date = datetime(2016, 1, 5, 12, 0)
        sale1.save()
        mommy.make(
            models.SaleItem, sale=sale1, item=article1, pre_tax_price=article1.pre_tax_price, quantity=1, vat_rate=vat
        )
        mommy.make(
            models.SaleItem, sale=sale1, item=article2, pre_tax_price=article2.pre_tax_price, quantity=2, vat_rate=vat
        )
        mommy.make(
            models.SaleItem, sale=sale1, item=article3, pre_tax_price=article3.pre_tax_price, quantity=3, vat_rate=vat
        )

        url = reverse('store_stats_sales_by_item_of_family', args=[family1.id, 2016, 1, 2016, 3])

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data['data']
        months = response.data['months']

        self.assertEqual(len(months), 3)
        self.assertEqual(
            [dict(ordered_dict) for ordered_dict in months],
            self._get_dates([date(2016, 1, 1), date(2016, 2, 1), date(2016, 3, 1)])
        )

        self.assertEqual(len(data), 2)

        data = sorted(data, key=lambda cat: cat['id'])
        family1_data = data[0]
        family2_data = data[1]

        self.assertEqual(family1_data['id'], category1.id)
        self.assertEqual(family1_data['name'], category1.name)
        self.assertEqual(family1_data['icon'], category1.icon)
        self.assertEqual(
            [dict(ordered_dict) for ordered_dict in family1_data['values']],
            [{'value': '1.00'}, {'value': '0.00'}, {'value': '0.00'}]
        )

        self.assertEqual(family2_data['id'], category2.id)
        self.assertEqual(family2_data['name'], category2.name)
        self.assertEqual(family2_data['icon'], category2.icon)
        self.assertEqual(
            [dict(ordered_dict) for ordered_dict in family2_data['values']],
            [{'value': '4.00'}, {'value': '0.00'}, {'value': '0.00'}]
        )

    def test_one_sale_tag_item(self):
        """It should return all sales data"""

        vat = mommy.make(models.VatRate, rate=Decimal(10))

        family = mommy.make(models.StoreItemCategory, parent=None)
        category1 = mommy.make(models.StoreItemCategory, icon='test', parent=family)

        tag1 = mommy.make(models.StoreItemTag)
        tag2 = mommy.make(models.StoreItemTag)

        article1 = mommy.make(models.StoreItem, category=category1, pre_tax_price=Decimal(10), vat_rate=vat)
        article2 = mommy.make(models.StoreItem, category=category1, pre_tax_price=Decimal(10), vat_rate=vat)
        article3 = mommy.make(models.StoreItem, category=category1, pre_tax_price=Decimal(10), vat_rate=vat)

        article1.tags.add(tag1)
        article1.save()

        article2.tags.add(tag2)
        article2.save()

        sale1 = mommy.make(models.Sale)
        sale1.action.planned_date = datetime(2016, 1, 5, 12, 0)
        sale1.save()
        mommy.make(
            models.SaleItem, sale=sale1, item=article1, pre_tax_price=article1.pre_tax_price, quantity=1, vat_rate=vat
        )
        mommy.make(
            models.SaleItem, sale=sale1, item=article2, pre_tax_price=article2.pre_tax_price, quantity=2, vat_rate=vat
        )
        mommy.make(
            models.SaleItem, sale=sale1, item=article3, pre_tax_price=article3.pre_tax_price, quantity=1, vat_rate=vat
        )

        url = reverse('store_stats_sales_by_item_of_tag', args=[tag1.id, 2016, 1, 2016, 3])

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data['data']
        months = response.data['months']

        self.assertEqual(len(months), 3)
        self.assertEqual(
            [dict(ordered_dict) for ordered_dict in months],
            self._get_dates([date(2016, 1, 1), date(2016, 2, 1), date(2016, 3, 1)])
        )

        self.assertEqual(len(data), 1)

        data = sorted(data, key=lambda cat: cat['id'])
        article1_data = data[0]

        self.assertEqual(article1_data['id'], article1.id)
        self.assertEqual(article1_data['name'], article1.name)
        self.assertEqual(article1_data['icon'], article1.category.icon)
        self.assertEqual(
            [dict(ordered_dict) for ordered_dict in article1_data['values']],
            [{'value': '10.00'}, {'value': '0.00'}, {'value': '0.00'}]
        )

    def test_total_sales(self):
        """It should return all sales data"""

        vat = mommy.make(models.VatRate, rate=Decimal(10))

        family = mommy.make(models.StoreItemCategory, parent=None)
        category1 = mommy.make(models.StoreItemCategory, icon='test', parent=family)
        category2 = mommy.make(models.StoreItemCategory, icon='test', parent=family)

        article1 = mommy.make(models.StoreItem, category=category1, pre_tax_price=Decimal(10), vat_rate=vat)
        article2 = mommy.make(models.StoreItem, category=category1, pre_tax_price=Decimal(10), vat_rate=vat)
        article3 = mommy.make(models.StoreItem, category=category2, pre_tax_price=Decimal(5), vat_rate=vat)

        sale1 = mommy.make(models.Sale)
        sale1.action.planned_date = datetime(2016, 1, 5, 12, 0)
        sale1.save()
        mommy.make(
            models.SaleItem, sale=sale1, item=article1, pre_tax_price=article1.pre_tax_price, quantity=1, vat_rate=vat
        )
        mommy.make(
            models.SaleItem, sale=sale1, item=article2, pre_tax_price=article2.pre_tax_price, quantity=2, vat_rate=vat
        )
        mommy.make(
            models.SaleItem, sale=sale1, item=article3, pre_tax_price=article3.pre_tax_price, quantity=1, vat_rate=vat
        )

        sale2 = mommy.make(models.Sale)
        sale2.action.planned_date = datetime(2016, 1, 12, 12, 0)
        sale2.save()
        mommy.make(
            models.SaleItem, sale=sale2, item=article2, pre_tax_price=article2.pre_tax_price, quantity=1, vat_rate=vat
        )
        mommy.make(
            models.SaleItem, sale=sale2, item=article3, pre_tax_price=article3.pre_tax_price, quantity=4, vat_rate=vat
        )

        sale3 = mommy.make(models.Sale)
        sale3.action.planned_date = datetime(2016, 2, 5, 12, 0)
        sale3.save()
        mommy.make(
            models.SaleItem, sale=sale3, item=article1, pre_tax_price=article1.pre_tax_price, quantity=5, vat_rate=vat
        )

        url = reverse('store_stats_total_sales', args=[2016, 1, 2016, 3])

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data['data']
        months = response.data['months']

        self.assertEqual(len(months), 3)
        self.assertEqual(
            [dict(ordered_dict) for ordered_dict in months],
            self._get_dates([date(2016, 1, 1), date(2016, 2, 1), date(2016, 3, 1)])
        )

        total_data = data[0]

        self.assertEqual(total_data['id'], 1)
        self.assertEqual(total_data['name'], _(u'Total'))
        self.assertEqual(total_data['icon'], 'piggy-bank')
        self.assertEqual(
            [dict(ordered_dict) for ordered_dict in total_data['values']],
            [{'value': '65.00'}, {'value': '50.00'}, {'value': '0.00'}]
        )
