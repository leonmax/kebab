from kebab.sources import KebabSource, literal


class Field:
    def __init__(
        self,
        config_name=None,
        default=None,
        required=False,
        expected_type=None,
        masked=False,
        **kwargs,
    ):
        self.config_name = config_name
        self.default = default
        self.required = required
        self.expected_type = expected_type
        self.masked = masked
        if "default_value" in kwargs:
            self.default_value = kwargs.pop("default_value")


def _make_init(klass):
    if hasattr(klass, "__init__"):
        user_init = klass.__init__
    else:
        user_init = None

    def __init__(self, source: KebabSource = None, *args, **kwargs):
        source = source or literal()
        if isinstance(source, KebabSource):
            for field_name, field in vars(klass).items():
                if isinstance(field, Field):
                    # use config_name as default name
                    if not field.config_name:
                        field.config_name = field_name
                    setattr(self, field_name, source.get(**field.__dict__))
        if user_init:
            user_init(self, *args, **kwargs)

    return __init__


def _make_repr(klass):
    def __repr__(self):
        result = []
        for key, value in vars(self).items():
            try:
                if not key.startswith("__") and not key.endswith("__"):
                    #     value = getattr(self, key)
                    result.append(f"{key}: {value!r}")
            except AttributeError:
                continue
        return f'{self.__class__.__name__}({", ".join(result)})'

    return __repr__


def config(auto_repr=False):
    if not isinstance(auto_repr, bool):
        # Most likely auto_repr here is the klass when @config is used without
        # parameters
        return config()(auto_repr)

    def _make_kebab_config_class(klass):
        setattr(klass, "__kebab_config__", True)
        setattr(klass, "__init__", _make_init(klass))
        if auto_repr:
            setattr(klass, "__repr__", _make_repr(klass))
        return klass

    return _make_kebab_config_class


class KebabConfigMeta(type):
    def __new__(mcs, name, bases, namespace, **kwargs):
        new_cls = super(KebabConfigMeta, mcs).__new__(mcs, name, bases, namespace)
        return config()(new_cls)
