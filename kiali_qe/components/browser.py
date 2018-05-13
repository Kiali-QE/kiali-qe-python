from widgetastic.browser import Browser


class KialiBrowser(Browser):

    def __init__(
            self, selenium, kiali_versions,
            plugin_class=None, logger=None, extra_objects=None):
        Browser.__init__(self, selenium, plugin_class=None, logger=None, extra_objects=None)
        self.kiali_versions = kiali_versions

    @property
    def product_version(self):
        return self.kiali_versions['core']

    # def element(self, locator, *args, **kwargs):
    #    kwargs['force_check_safe'] = True
    #    super(KialiBrowser, self).element(locator, *args, **kwargs)
