# ============================================================
# django-odata response serialization
#
# (C) Tiago Almeida 2017
#
# 
#
# ============================================================
import json
import pprint
import django_odata.metadata as metadata
from django.core.serializers.python import Serializer
from django.core.serializers.json import DjangoJSONEncoder


class GenericOdataJsonSerializer(object):
	@staticmethod
	def serialize(obj):
		"""
		Inserts obj as the value of property "d" in an 
		outer object and converts this to a json.
		"""
		wrapped = {'d':obj}
		result = json.dumps(wrapped, separators=(',', ':'))
		return result


class OdataJsonSerializer(Serializer):
    def __init__(self, service_root, set_name):
        super().__init__()
        self._set_name = set_name
        self._svc_root = service_root

    def _get_obj_uri(self, obj):
        return self._svc_root + self._set_name +  '(%s)/' % obj.pk

    def _get_obj_type(self, obj):
        return self._set_name

    def get_dump_object(self, obj):
        data = self._current
        if not self.selected_fields or 'id' in self.selected_fields:
          data['id'] = obj.id
        # Inject the odata metadata info
        data['__metadata'] = {
          'uri': self._get_obj_uri(obj),
          'type': self._get_obj_type(obj)
        }
        return data

    def end_object(self, obj):
        if not self.first:
          self.stream.write(', ')
        json.dump(self.get_dump_object(obj), self.stream,
            cls=DjangoJSONEncoder)
        self._current = None

    def start_serialization(self):
        """
        Starts output by wrapping the array in a
        d.results object
        """
        self.stream.write('{"d":{"results":[')

    def end_serialization(self):
        self.stream.write("]}}")

    def getvalue(self):
        return super(Serializer, self).getvalue()


class ODataV4JSONSerializer(object):
    """
    For entitysets we need to return an object with
    @odata.context and value. Value is an array of serialized entries
    For entity we need to return the object with an injected
    property @odata.context
    """
    @staticmethod
    def from_django_query(django_query):
        """
        Initializes an ODataV4JSONSerializer from the result of a django query.
        """
        serializer = ODataV4JSONSerializer()
        serializer.django_query = django_query
        return serializer
    

    def entity_odata_context(self, model_name):
        """
        Needs to return a string with the value of odata.context property of
        an entity.
        e.g.
        http://services.odata.org/V4/Northwind/Northwind.svc/$metadata#Categories/$entity
        """
        return 'TODO'

    
    def entity_to_json(self):
        """
        Are we returning an entity or an entity set?
        TODO we assume an entity for now.
        """
        app = 'webapp' # TODO!
        obj = self.django_query.get()
        # Get the model name of this object 
        model_name = obj.__class__.__name__ # TODO
        meta = metadata.get_odata_entity_by_model_name(app, model_name)
        # We need to map each field of the meta to the obj.
        # meta is an instande of ODataEntity
        result = {}
        result['@odata.context'] = self.entity_odata_context(model_name)
        for f in meta.fields:
            result[f.name] = obj[f.name] # TODO Serialize based on type
        return json.dump(result)


    def to_json(self):
        """
        Are we returning an entity or an entity set?
        TODO we assume an entity for now.
        """
        return self.entity_to_json()


class OrmQueryResult(object):
    def __init__(self, django_query):
        self._django_query = django_query
    
    def serialize(self, format=None):
        """
        Serializes the query result according to format
        """
        serialzer = ODataV4JSONSerializer.from_django_query() # todo
        return pprint.pprint(self._django_query)