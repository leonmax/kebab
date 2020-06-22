from kebab.sources import KebabSource


class Field:
    def __init__(self, config_name='.', default_value=None, required=False, expected_type=None, masked=False):
        self.config_name = config_name
        self.default_value = default_value
        self.required = required
        self.expected_type = expected_type
        self.masked = masked


def kebab_config(auto_repr=False):
    if not isinstance(auto_repr, bool):
        # Most likely auto_repr here is the klass when @kebab_config is used without parameters
        return kebab_config()(auto_repr)

    def _make_kebab_config_class(klass):
        if hasattr(klass, '__init__'):
            user_init = klass.__init__
        else:
            user_init = None

        def __init__(self, source: KebabSource, *args, **kwargs):
            if isinstance(source, KebabSource):
                for field_name, field in vars(klass).items():
                    if isinstance(field, Field):
                        setattr(self, field_name, source.get(**field.__dict__))
            if user_init:
                user_init(self, *args, **kwargs)
        setattr(klass, '__init__', __init__)

        if auto_repr:
            def __repr__(self):
                result = []
                for key, value in vars(self).items():
                    try:
                        if not key.startswith("__") and not key.endswith("__"):
                            #     value = getattr(self, key)
                            result.append(f'{key}: {value!r}')
                    except AttributeError:
                        continue
                return f'{self.__class__.__name__}({", ".join(result)})'
            setattr(klass, '__repr__', __repr__)

        return klass
    return _make_kebab_config_class


class KebabConfigMeta(type):
    def __new__(mcs, name, bases, namespace, **kwargs):
        new_cls = super(KebabConfigMeta, mcs).__new__(mcs, name, bases, namespace)
        return kebab_config()(new_cls)
