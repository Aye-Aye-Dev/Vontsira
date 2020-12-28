'''
Created on 23 Dec 2020

@author: si
'''
from datetime import datetime

from sqlalchemy import Column, Integer, DateTime, inspect
from sqlalchemy.orm.dynamic import AppenderQuery


class BaseModel(object):
    id = Column(Integer, primary_key=True)
    last_updated = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        model_name = self.__class__.__name__
        return f'<{model_name} ({self.id})>'

    @property
    def all_base_classes(self):
        """
        returns: set of all classes self inherits from
        """
        def get_base_classes(cls_bases):
            r = set()
            for p_cls in cls_bases:
                if p_cls not in r:
                    r.add(p_cls)
                    r.update(get_base_classes(p_cls.__bases__))
            return r

        return get_base_classes(self.__class__.__bases__)

    def fields_in_class(self, cls):
        """
        returns: set of strings of field (aka Column) names
        """
        r = set()
        for attrib_name, v in cls.__dict__.items():
            if isinstance(v, Column):
                r.add(attrib_name)
        return r

    @property
    def base_model_fields(self):
        """
        return: set of (str) - of fields (aka Columns) in classes that self/cls inherits from
                    but not fields in self/cls itself.
        """
        if not hasattr(self, '_base_field_names'):
            self._base_field_names = set()
            for p_cls in list(self.all_base_classes):
                self._base_field_names.update(self.fields_in_class(p_cls))

        return self._base_field_names

    @property
    def all_field_names(self):
        """
        @return: list of (str) - all fields in model including those inherited from base model
        """
        if not hasattr(self, '_all_field_names'):
            self._all_field_names = []
            mapper = inspect(self)
            for column in mapper.attrs:
                self._all_field_names.append(column.key)

        return self._all_field_names

    @property
    def model_field_names(self):
        """
        @return: list of (str) - fields in model excluding base model
        """
        if not hasattr(self, '_model_field_names'):
            all_fields = set(self.all_field_names)
            base_model_fields = set(self.base_model_fields)
            self._model_field_names = list(all_fields - base_model_fields)

        return self._model_field_names

    def as_dict(self):
        """
        @return: dictionary this is safe to pass to jsonify
        """
        serialised = {}
        for column_key in self.all_field_names:

            column_value = getattr(self, column_key)
            if isinstance(column_value, BaseModel):
                # for now, don't get caught in a loop
                continue
            elif isinstance(column_value, list):
                # raise NotImplementedError(f'lists for column: {column_key}')
                serialised[column_key] = [item.as_dict() for item in column_value]
            elif isinstance(column_value, AppenderQuery):
                continue
            else:
                # TODO types, e.g convert from date to JSON safe string
                serialised[column_key] = column_value

        return serialised
