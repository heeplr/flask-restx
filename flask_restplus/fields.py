# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from flask.ext.restful import fields as base_fields

from .utils import camel_to_dash
from .model import resolve_fields


class DetailsMixin(object):
    def __init__(self, *args, **kwargs):
        self.description = kwargs.pop('description', None)
        self.title = kwargs.pop('title', None)
        self.required = kwargs.pop('required', None)
        self.readonly = kwargs.pop('readonly', None)
        super(DetailsMixin, self).__init__(*args, **kwargs)


class MinMaxMixin(object):
    def __init__(self, *args, **kwargs):
        self.minimum = kwargs.pop('min', None)
        self.maximum = kwargs.pop('max', None)
        super(MinMaxMixin, self).__init__(*args, **kwargs)


class String(DetailsMixin, base_fields.String):
    def __init__(self, *args, **kwargs):
        self.enum = kwargs.pop('enum', None)
        self.discriminator = kwargs.pop('discriminator', None)
        super(String, self).__init__(*args, **kwargs)


class Integer(DetailsMixin, MinMaxMixin, base_fields.Integer):
    pass


class Float(DetailsMixin, MinMaxMixin, base_fields.Float):
    pass


class Arbitrary(DetailsMixin, MinMaxMixin, base_fields.Arbitrary):
    pass


class Boolean(DetailsMixin, base_fields.Boolean):
    pass


class DateTime(DetailsMixin, base_fields.DateTime):
    pass


class Raw(DetailsMixin, base_fields.Raw):
    pass


class Nested(DetailsMixin, base_fields.Nested):
    pass


class List(DetailsMixin, base_fields.List):
    pass


class Url(DetailsMixin, base_fields.Url):
    pass


class Fixed(DetailsMixin, MinMaxMixin, base_fields.Fixed):
    pass


class FormattedString(DetailsMixin, base_fields.FormattedString):
    pass


class ClassName(String):
    def __init__(self, dash=False, **kwargs):
        super(ClassName, self).__init__(**kwargs)
        self.dash = dash

    def output(self, key, obj):
        classname = obj.__class__.__name__
        return camel_to_dash(classname) if self.dash else classname


class Polymorph(Nested):
    def __init__(self, mapping, **kwargs):
        self.mapping = mapping
        super(Polymorph, self).__init__(None, **kwargs)

    def output(self, key, obj):
        value = base_fields.get_value(key if self.attribute is None else self.attribute, obj)
        if value is None:
            if self.allow_null:
                return None
            elif self.default is not None:
                return self.default

        if not hasattr(value, '__class__'):
            raise ValueError('Polymorph field only accept class instances')

        candidates = [fields for cls, fields in self.mapping.items() if isinstance(value, cls)]

        if len(candidates) <= 0:
            raise ValueError('Unknown class: ' + value.__class__.__name__)
        elif len(candidates) > 1:
            raise ValueError('Unable to determine a candidate for: ' + value.__class__.__name__)
        else:
            return base_fields.marshal(value, resolve_fields(candidates[0]))
