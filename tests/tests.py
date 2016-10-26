# ============================================================
# Tests for the django-odata reusable app
#
# (C) Tiago Almeida 2016
#
# 
#
# ============================================================
import unittest
from django.test import TestCase
from .models import *
import django_odata.odata as odata


class OrderByTestCase(TestCase):
	def setUp(self):
		Tag.objects.create(name="tag2")
		Tag.objects.create(name="tag1")
		Tag.objects.create(name="tag3")
		Tag.objects.create(name="tag3")
		self.tags_count = 4

	
	def test_orderby_simple(self):
		"""
		Tests $order_by=<property name>
		"""
		set_sorted_name = odata.set_order_by(Tag.objects.all(), 'name')
		self.assertEquals(len(set_sorted_name), self.tags_count)
		self.assertEquals(set_sorted_name[0].name, 'tag1')

	
	def test_orderby_desc(self):
		"""
		Tests $order_by=<property name> desc
		"""
		set_rsorted_name = odata.set_order_by(Tag.objects.all(), 
			'name desc')
		self.assertEquals(len(set_rsorted_name), self.tags_count)
		self.assertEquals(set_rsorted_name[0].name, 'tag3')


	def test_orderby_asc(self):
		"""
		Tests $order_by=<property name> asc
		"""
		set_rsorted_name = odata.set_order_by(Tag.objects.all(), 
			'name asc')
		self.assertEquals(len(set_rsorted_name), self.tags_count)
		self.assertEquals(set_rsorted_name[0].name, 'tag1')
		self.assertEquals(set_rsorted_name[1].name, 'tag2')


	def test_orderby_multiple1(self):
		"""
		Tests $order_by=<property name> asc,<property name> desc
		"""
		set_rsorted_name = odata.set_order_by(Tag.objects.all(), 
			'name asc,id desc')
		self.assertEquals(set_rsorted_name[2].name, 'tag3')
		self.assertEquals(set_rsorted_name[2].id, 4)
		self.assertEquals(set_rsorted_name[3].name, 'tag3')
		self.assertEquals(set_rsorted_name[3].id, 3)	



class OrderBySubobjectTestCase(TestCase):
	def setUp(self):
		sub = Sub.objects.create(name='Subobject2')
		Main.objects.create(name='Mainobject2', rel=sub)
		sub = Sub.objects.create(name='Subobject1')
		Main.objects.create(name='Mainobject1', rel=sub)
		sub = Sub.objects.create(name='Subobject3')
		Main.objects.create(name='Mainobject3', rel=sub)
	

	def test_orderby_property_path(self):
		"""
		Tests $order_by=<property name>/<property name>
		"""
		set_sorted_name = odata.set_order_by(Main.objects.all(), 
			'rel/name')
		self.assertEquals(set_sorted_name[0].name, 'Mainobject1')
		self.assertEquals(set_sorted_name[1].name, 'Mainobject2')
		self.assertEquals(set_sorted_name[2].name, 'Mainobject3')


	def test_orderby_property_path_asc(self):
		"""
		Tests $order_by=<property name>/<property name>
		"""
		set_sorted_name = odata.set_order_by(Main.objects.all(), 
			'rel/name asc')
		self.assertEquals(set_sorted_name[0].name, 'Mainobject1')
		self.assertEquals(set_sorted_name[1].name, 'Mainobject2')
		self.assertEquals(set_sorted_name[2].name, 'Mainobject3')


	def test_orderby_property_path_desc(self):
		"""
		Tests $order_by=<property name>/<property name>
		"""
		set_sorted_name = odata.set_order_by(Main.objects.all(), 
			'rel/name desc')
		self.assertEquals(set_sorted_name[0].name, 'Mainobject3')
		self.assertEquals(set_sorted_name[1].name, 'Mainobject2')
		self.assertEquals(set_sorted_name[2].name, 'Mainobject1')



class FilterParseTestCase(TestCase):
	"""
	Makes sure we can parse all $filter expressions
	"""
	def _parse_validate(self, expression, exp_path, exp_op, exp_val):
		m = odata.odata_filter_parse(expression)
		self.assertEquals( m.group('val'), exp_val )
		self.assertEquals( m.group('op'), exp_op )
		self.assertEquals( m.group('path'), exp_path )

	def test1(self):
		return self._parse_validate('id eq 2', 'id', 'eq', '2')
	def test2(self):
		return self._parse_validate('id ne 2', 'id', 'ne', '2')
	def test3(self):
		return self._parse_validate('id gt 4', 'id', 'gt', '4')
	def test4(self):
		return self._parse_validate('id lt 3', 'id', 'lt', '3')
	def test5(self):
		return self._parse_validate('id le 6', 'id', 'le', '6')
	def test6(self):
		return self._parse_validate('id ge -1', 'id', 'ge', '-1')
	def test7(self):
		return self._parse_validate('id ge -14', 'id', 'ge', '-14')
	def test8(self):
		return self._parse_validate('id ge 23', 'id', 'ge', '23')
	def test9(self):
		return self._parse_validate('id ge field', 'id', 'ge', 'field')
	# TODO: test cases for failure/invalid filters


class FilterTestCase(TestCase):
	" Tests for $filter "

	def setUp(self):
		Tag.objects.create(name="tag2")
		Tag.objects.create(name="tag1")
		Tag.objects.create(name="tag3")
		Tag.objects.create(name="tag3")
		self.tags_count = 4
		for x in range(0,10):
			Number.objects.create(value=x)

	def test(self):
		"""
		"""
		tag_set = odata.set_filter(Tag.objects.all(), 
			'name eq tag3')
		self.assertEquals(len(tag_set), 2)
		self.assertEquals(tag_set[0].name, 'tag3')

	def testNumericEquality(self):
		num_set = odata.set_filter(Number.objects.all(), 
			'value eq 1')
		self.assertEquals(len(num_set), 1)
		self.assertEquals(num_set[0].value, 1)

	def testNumericGreaterThan(self):
		num_set = odata.set_filter(Number.objects.all(), 
			'value gt 2')
		self.assertEquals(len(num_set), 7)

	def testNumericLessThan(self):
		num_set = odata.set_filter(Number.objects.all(), 
			'value lt 2')
		self.assertEquals(len(num_set), 2)

	def testNumericGreaterThanOrEqual(self):
		num_set = odata.set_filter(Number.objects.all(), 
			'value ge 2')
		self.assertEquals(len(num_set), 8)

	def testNumericLessThanOrEqual(self):
		num_set = odata.set_filter(Number.objects.all(), 
			'value le 2')
		self.assertEquals(len(num_set), 3)

	def testNumericLessThanOrEqual(self):
		num_set = odata.set_filter(Number.objects.all(), 
			'value ne 2')
		self.assertEquals(len(num_set), 9)