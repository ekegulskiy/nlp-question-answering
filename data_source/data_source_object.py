class DataSourceObject:
    def __init__(self, obj_with_fields):
        self._object = obj_with_fields

    def object_value(self, field):
        """

        :param field:
        :return: the value of the field
        """
        if field in self._object:
            return self._object[field]