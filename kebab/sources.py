import abc
import copy
import deprecation
import logging
import os
import queue  # using python-future for 2/3 compatibility
import threading
import time

# noinspection PyCompatibility,PyPackageRequirements
from typing import List, Dict
from urllib.request import OpenerDirector

import yaml

from kebab.openers import DEFAULT_OPENER
from kebab.utils import (
    update_recursively,
    lookup_recursively,
    fill_recursively,
    deprecated_alias,
)

_logger = logging.getLogger(__name__)
_DISABLE_RELOAD = -1

DEFAULT_URL_ENVVAR = "CONF_URL"


class ContextExtension(object):
    @property
    @abc.abstractmethod
    def keyword(self):
        return ""

    @abc.abstractmethod
    def handle(self, source, extension_context):
        pass


class KebabSource(dict):
    _context_extensions = {}  # type: Dict[str, ContextExtension]

    @classmethod
    def register_extension(cls, extension):
        if issubclass(extension, ContextExtension):
            extension = extension()
        if isinstance(extension, ContextExtension):
            KebabSource._context_extensions[extension.keyword] = extension

    def __init__(self, **kwargs):
        # Variables for sources reload (first load is also a reload).
        super(KebabSource, self).__init__(**kwargs)
        self._last_reload_timestamp = 0  # type: float
        self._reload_lock = threading.RLock()
        self._reload_timer = None
        self._reload_disabled = threading.Event()
        self._cached_context = {}

    def __repr__(self):
        return self.__class__.__name__

    def __getitem__(self, key):
        return self.get(key)

    def __len__(self):
        return len(self.get())

    def has_key(self, k):
        return k in self.get()

    def keys(self):
        return self.get().keys()

    def values(self):
        return self.get().values()

    def items(self):
        return self.get().items()

    def __cmp__(self, dict_):
        return self.get().__cmp__(dict_)

    def __contains__(self, item):
        return item in self.get()

    def __iter__(self):
        return iter(self.get())

    @abc.abstractmethod
    def _load_context(self):
        return {}

    def _load_context_recursively(self):
        _logger.debug(f"loading {self}")

        _context = self._load_context()

        for keyword, extension in KebabSource._context_extensions.items():
            if keyword in _context:
                extension_context = _context.pop(keyword)
                _context = update_recursively(
                    _context, extension.handle(self, extension_context)
                )

        return _context

    def disable_reload(self):
        self._reload_disabled.set()

    def reload(self, reload_interval_in_secs=_DISABLE_RELOAD, skip_first=False):
        """

        :param float|int reload_interval_in_secs:
        :param bool skip_first: if False, reload immediately, otherwise, reload after
                                the interval
        :return:
        """
        if (
            self._reload_disabled.is_set()
            and self._reload_timer
            and threading.current_thread().ident == self._reload_timer.ident
        ):
            _logger.debug(f"reload timer is disabled for {self}")
            self._reload_timer = None
            self._reload_disabled = threading.Event()
            return self

        if not skip_first:
            # noinspection PyBroadException
            try:
                _context = self._load_context_recursively()

                # lock only when switch
                with self._reload_lock:
                    self._cached_context = _context
                    self._last_reload_timestamp = time.time()
            except Exception as e:
                _logger.warning(
                    f"failed to reload, will use the cached value for {self}\n {e}"
                )

        # reload periodically if reload_interval_in_secs > 0
        if reload_interval_in_secs > 0:
            if (
                self._reload_timer
                and threading.current_thread().ident != self._reload_timer.ident
            ):
                _logger.debug(f"reload timer was already set for {self}")
                self._reload_timer.args = (reload_interval_in_secs, False)
            else:
                if not self._reload_timer:
                    _logger.info(
                        f"setting timer to reload per {reload_interval_in_secs} secs "
                        f"for {self} "
                    )
                # noinspection PyTypeChecker
                self._reload_timer = threading.Timer(
                    interval=reload_interval_in_secs,
                    function=self.reload,
                    args=(reload_interval_in_secs, False),
                )
                self._reload_timer.setDaemon(True)
                self._reload_timer.start()

        return self

    def _get_context(self):
        if not self._cached_context:
            self.reload()

        return self._cached_context

    @property
    def last_reload_timestamp(self):
        return self._last_reload_timestamp

    @deprecated_alias(default_value="default")
    def get(
        self,
        config_name=".",
        default=None,
        required=False,
        expected_type=None,
        masked=False,
    ):
        """
        :param str config_name: The key to retrieve the config value. If '.', return the
                        whole context
        :param object default: The default value to fall back to if config_name not
                        found
        :param bool required: When the required value is not found, throw exception if
                        set True, return None otherwise.
                        Default is False.
        :param type expected_type: Expected type of the value, ignored if default
                        presents.
        :param bool masked: The value will be logged as "*" if set True. This is useful
                        when a value is a secret.
        :rtype str|int|bool|list[str]:

        Function to get a config value. This is a facade function which will retrieve
        all sources, with the following precedence:
            1. environment variable
            2. sources (a list of sources)
            3. default, if specified

        This function will raise exception if all the below is True
            1. config_name not found
            2. default not set
            3. required is True
        Otherwise, it could return None.

        Note that the type of the default becomes the expected_type if presents,
        the original expected_type will be ignored in that case.

        The parameter `default_value` is deprecated, use `default` instead
        """

        if not config_name:
            raise ValueError("Please specify a config_name")

        if default is not None:
            # set expected type based on default value (and ignore the original
            # expected_type
            if expected_type is not None and type(default) != expected_type:
                raise ValueError(
                    "You specified default of type {}, but expected_type={}".format(
                        type(default), expected_type
                    )
                )
            expected_type = type(default)

        # If the value is not yet set but exists in source:
        if config_name == ".":
            config_value = self._get_context()
        else:
            config_name = config_name.lstrip(".")
            config_value = lookup_recursively(
                self._get_context(), key=config_name, default=default
            )

        # if None, give empty values
        if config_value is None:
            # fail if required
            if required:
                raise KeyError(f"Missing value for {config_name}")

        config_value = self._cast(config_value, expected_type)

        printed_value = "*" * len(str(config_value)) if masked else config_value
        _logger.debug(f"read config: {config_name} = {printed_value}")

        return config_value

    @staticmethod
    def _cast(config_value, expected_type):
        """
        Re-cast types if the config_value is not the expected_type.
        If config_value is None, use default value of expected_type with default
        constructor (expected_type())

        ============= ============ ============
        expected_type config_value return_value
        ============= ============ ============
        not None      None         expected_type()
        KebabConfig   not None     expected_type(literal(**config_value))
        None          None         config_value
        None          not None     config_value
        same type     same type    config_value
        diff type     diff type    expected_type(config_value)
        ============= ============ ============

        The exceptions:
        1. If expected value is bool, it will only be True if the config_value (after
            cast to str) is 'true', 'yes' and '1' (case insensitive)
        2. If expected value is list, it will be split by list_delimiter_char (default
            ',') (after cast to str)


        :param Any config_value:
        :param type expected_type:
        """
        if expected_type is not None:
            if config_value is None:
                return expected_type()
            elif not isinstance(config_value, expected_type):
                if expected_type == bool:
                    # noinspection PyCompatibility
                    if isinstance(config_value, str):
                        v = config_value.lower()
                        if v in ("1", "true", "yes", "on", "enable"):
                            return True
                        return False
                    return bool(config_value)
                elif hasattr(expected_type, "__kebab_config__"):
                    return expected_type(literal(**config_value))
                else:
                    return expected_type(config_value)
        return config_value

    def subsource(self, config_name, reload_interval_in_secs=_DISABLE_RELOAD):
        """
        Caveats:

        When parent KebabSource reloads, SubSource is not effected the updated values in
            KebabSource.
        In another word, reload in SubSource is limited and is not encouraged to use at
            the moment.

        :param str config_name: config_name
        :param int|float reload_interval_in_secs: same as parent param
        :rtype: KebabSource
        """
        source = SubSource(self, config_name)
        source.reload(reload_interval_in_secs=reload_interval_in_secs)
        return source

    @deprecation.deprecated(
        deprecated_in="0.4.0",
        removed_in="0.5.0",
        details="Use the get function instead (with expected_type=config_class)",
    )
    def cast(self, config_name, config_class, *args, **kwargs):
        """
        Caveats:

        When parent KebabSource reloads, SubSource is not effected the updated values in
            KebabSource.
        In another word, reload in SubSource is limited and is not encouraged to use at
            the moment.

        :param str config_name: the config_name must be a dictionary
        :param type config_class: the config_class to cast to
        :return: the instance of the config_class
        """
        source = self if config_name == "." else SubSource(self, config_name)
        return config_class(source, *args, **kwargs)


class ImportExtension(ContextExtension):
    @property
    def keyword(self):
        return "__import__"

    def handle(self, source, extension_context):
        root = literal(__import__=extension_context)
        context = {}
        source_queue = queue.Queue()
        source_queue.put(root)
        while not source_queue.empty():
            source = source_queue.get()  # type: KebabSource
            try:
                # noinspection PyProtectedMember
                next_context = source._load_context()

                # reload other source from __import__ section
                for url in next_context.pop("__import__", []):
                    source_queue.put(UrlSource(url))

                context = update_recursively(context, next_context)
            except Exception as e:
                _logger.warning(f"failed to load source of {source}, will skip\n{e}")
        return context


class ReloadExtension(ContextExtension):
    @property
    def keyword(self):
        return "__reload__"

    def handle(self, source, extension_context):
        try:
            # the source can define its own reload_interval_in_secs in the __reload__
            # section
            if "reload_interval_in_secs" in extension_context:
                reload_interval_in_secs = float(
                    extension_context["reload_interval_in_secs"]
                )

                source.reload(
                    reload_interval_in_secs=reload_interval_in_secs,
                    skip_first=True,
                )
        except Exception as e:
            _logger.warning(
                f"failed to load __reload__ section of {self}, will ignore\n{e}"
            )


class StrSource(KebabSource):
    def __init__(self, content, **kwargs):
        """
        :param str string:
        :param kwargs:
        """
        super(StrSource, self).__init__(**kwargs)
        self._content = content

    def _load_context(self):
        return yaml.safe_load(self._content)


class UrlSource(KebabSource):
    def __init__(self, url, opener=None, **kwargs):
        """
        :param str url: a url of supported protocols in openers.DEFAULT_OPENER
        """
        super(UrlSource, self).__init__(**kwargs)
        self._opener = opener or DEFAULT_OPENER
        if ":" not in url:
            url = f"file://{os.path.abspath(url)}"
        self._url = url

    def __repr__(self):
        return f"{self.__class__.__name__}({self._url})"

    def _load_context(self):
        content = self._opener.open(self._url).read()
        return yaml.safe_load(content)


class DictSource(KebabSource):
    def __init__(self, dictionary=None, **kwargs):
        super(DictSource, self).__init__(**kwargs)
        self._dictionary = dictionary or {}

    def _load_context(self):
        return copy.deepcopy(self._dictionary)


class EnvVarSource(KebabSource, ContextExtension):
    """
    this class supports __env_map__ sections
    all environment variables keys under __env_map__ will be mapped
    the Kebab context key
    """

    def __init__(self, include_env_var=False, env_var_map=None, **kwargs):
        super(EnvVarSource, self).__init__(**kwargs)
        env_vars = dict(os.environ)
        self._dictionary = env_vars if include_env_var else {}
        if env_var_map:
            for env_key, var_key in env_var_map.items():
                if env_key in env_vars:
                    fill_recursively(self._dictionary, var_key, env_vars[env_key])

    def _load_context(self):
        return self._dictionary

    @property
    def keyword(self):
        return "__env_map__"

    def handle(self, source, extension_context):
        mapped_src = EnvVarSource(include_env_var=False, env_var_map=extension_context)
        # noinspection PyProtectedMember
        _env_context = mapped_src._load_context()
        return _env_context


class UnionSource(DictSource):
    """
    This class supports __import__ and __reload__ sections
    All file under __import__ will be combined.
    In the __reload__ section, reload_interval_in_secs will be honored for the
    current source
    """

    def __init__(self, sources=None, **kwargs):
        super(UnionSource, self).__init__(**kwargs)

        if sources is None:
            sources = []
        elif isinstance(sources, KebabSource):
            sources = [sources]
        elif not any([isinstance(sources, t) for t in (list, tuple, set)]) or any(
            [not isinstance(s, KebabSource) for s in sources]
        ):
            raise ValueError(
                "Please pass in a single KebabSource or a list of KebabSource"
            )
        self._sources = sources

    def __repr__(self):
        reprs = [repr(r) for r in self._sources]
        return "{}([{}])".format(self.__class__.__name__, ", ".join(reprs))

    def _load_context(self):
        _context = {}
        for source in self._sources:
            next_context = source.reload()._get_context()
            _context = update_recursively(_context, next_context)

        return _context


class SubSource(KebabSource):
    def __init__(self, parent_source, config_name, **kwargs):
        """
        Caveats:

        When parent KebabSource reloads, SubSource is not effected. In another word,
        reload in SubSource is limited and is not encouraged to use at the moment.

        :param KebabSource parent_source:
        :param str config_name:
        """
        super(SubSource, self).__init__(**kwargs)
        self._parent_source = parent_source
        self._source_name = config_name

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self._parent_source)})"

    def _load_context(self):
        return self._parent_source.get(
            self._source_name, required=True, expected_type=dict
        )


def union(*sources, **kwargs):
    # """
    # The shortcut to create UnionSource
    # :param sources: a list of source to be union
    # :rtype: UnionSource
    # """
    return UnionSource(sources=sources, **kwargs)


def literal(**dictionary):
    """
    The shortcut to create DictSource
    :param dictionary: a list of key value pairs
    :rtype: DictSource
    """
    return DictSource(dictionary=dictionary)


def load_source(
    default_urls="app.yaml",
    fallback_dict=None,
    opener: OpenerDirector = None,
    include_env_var=False,
    env_var_map=None,
    url_envvar=DEFAULT_URL_ENVVAR,
    reload_interval_in_secs=_DISABLE_RELOAD,
):
    """

    :param str|list[str]|tuple[str] default_urls:
    :param dict fallback_dict:
    :param OpenerDirector opener:
    :param int|float reload_interval_in_secs:
    :param bool include_env_var:
    :param dict env_var_map: map Environment Variable key to a hierarchical key such as
                    NESTED_KEY -> nested.key
    :param str url_envvar: the environment variable key to load config url
    :return: the kebab source of these urls
    :rtype: KebabSource
    """
    if default_urls and isinstance(default_urls, str):
        default_urls = default_urls.split(",")
    urls = default_urls or []

    urls_from_env = os.getenv(url_envvar)
    if urls_from_env:
        urls = urls_from_env.split(",")

    sources = [UrlSource(url, opener=opener) for url in urls]  # type: List[KebabSource]

    if fallback_dict is not None and isinstance(fallback_dict, dict):
        sources.insert(0, DictSource(fallback_dict))

    if include_env_var or env_var_map:
        sources.append(
            EnvVarSource(include_env_var=include_env_var, env_var_map=env_var_map)
        )

    if len(sources) == 1:
        # for single url, do not read with union source so that self configured auto
        # reload will work
        source = sources[0]
    else:
        source = UnionSource(sources=sources)
    source.reload(reload_interval_in_secs=reload_interval_in_secs)
    return source


KebabSource.register_extension(ImportExtension)
KebabSource.register_extension(EnvVarSource)
KebabSource.register_extension(ReloadExtension)
