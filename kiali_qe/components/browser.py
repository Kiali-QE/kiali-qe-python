from widgetastic.browser import Browser
from selenium.common.exceptions import NoSuchElementException


class KialiBrowser(Browser):

    def __init__(
            self, selenium, kiali_version,
            plugin_class=None, logger=None, extra_objects=None):
        Browser.__init__(self, selenium, plugin_class=None, logger=None, extra_objects=None)
        self.kiali_version = kiali_version

    @property
    def product_version(self):
        return self.kiali_version

    def text_or_default(self, locator, default='None', *args, **kwargs):
        try:
            return self.text(locator, *args, **kwargs)
        except NoSuchElementException:
            return default

    # def element(self, locator, *args, **kwargs):
    #    kwargs['force_check_safe'] = True
    #    super(KialiBrowser, self).element(locator, *args, **kwargs)
