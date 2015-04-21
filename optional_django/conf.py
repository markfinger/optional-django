import warnings
from . import six
from .exceptions import ConfigurationError
from .env import DJANGO_CONFIGURED, DJANGO_SETTINGS


class ConfigurationWarning(Warning):
    pass


class Conf(object):
    django_namespace = None
    _has_been_configured = False
    _configured_from_env = False
    _overrides = None
    _configurable = True

    def __init__(self):
        if self.django_namespace and DJANGO_CONFIGURED and DJANGO_SETTINGS:
            overrides = getattr(DJANGO_SETTINGS, self.django_namespace, None)
            if overrides:
                self._configured_from_env = True
                self.configure(**overrides)

        self._lock()

    def _unlock(self):
        super(Conf, self).__setattr__('_configurable', True)

    def _lock(self):
        super(Conf, self).__setattr__('_configurable', False)

    def configure(self, **kwargs):
        if self._has_been_configured:
            raise ConfigurationError(
                '{}.{} has already been configured'.format(
                    type(self).__module__,
                    type(self).__name__,
                )
            )

        self._unlock()

        for key, value in six.iteritems(kwargs):
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                warnings.warn('Unknown setting {}'.format(key))

        self._has_been_configured = True

        self._lock()

    def __setattr__(self, name, value):
        if not self._configurable:
            raise ConfigurationError('Use `.configure({}=<value>, ...)` to change settings'.format(name))
        super(Conf, self).__setattr__(name, value)