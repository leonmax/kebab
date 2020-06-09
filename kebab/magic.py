from kebab.sources import KebabSource


class Field:
    def __init__(self, config_name='.', default_value=None, required=False, expected_type=None):
        self.config_name = config_name
        self.default_value = default_value
        self.required = required
        self.expected_type = expected_type


def kebab_config(klass):
    if hasattr(klass, '__init__'):
        user_init = klass.__init__
    else:
        user_init = None

    def __init__(self, source: KebabSource, *args, **kwargs):
        self.__config_names__ = []
        for field_name, field in klass.__dict__.items():
            if isinstance(field, Field):
                self.__config_names__.append(field.config_name)
                setattr(self, field_name, source.get(**field.__dict__))
        if user_init:
            user_init(self, *args, **kwargs)

    setattr(klass, '__init__', __init__)
    return klass


class KebabConfigMeta(type):
    def __new__(mcs, name, bases, attrs, **kwargs):
        new_cls = super(KebabConfigMeta, mcs).__new__(mcs, name, bases, attrs, **kwargs)
        return kebab_config(new_cls)

