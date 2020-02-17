"""update this doc"""
from widgetastic.widget import View, Text
from kiali_qe.components import (
    Button,
    DropDown,
    TypeDropDown,
    ItemDropDown,
    Filter,
    ListViewIstioConfig,
    ListViewServices,
    ListViewWorkloads,
    ListViewApplications,
    ListViewOverview,
    TableView3ScaleConfig,
    Login,
    MainMenu,
    Notifications,
    SortDropDown,
    SortBar,
    CheckBoxFilter,
    NamespaceFilter,
    Actions,
    Traces,
    GraphLayout)
from kiali_qe.components import wait_displayed, wait_to_spinner_disappear

from kiali_qe.components.enums import (
    MainMenuEnum as MENU,
    UserMenuEnum as USER_MENU)
from kiali_qe.utils.log import logger
from kiali_qe.utils.conf import env as cfg
from wait_for import wait_for

XP_DROP_DOWN = '//*[contains(@class, "pf-c-select")]/*[contains(@aria-labelledby, "{}")]'
SORT_DROP_DOWN = '//*[contains(@class, "pf-l-toolbar__item")]' +\
    '//*[contains(@aria-labelledby, "{}")]/../..'
XP_BUTTON_SWITCH = '//*[contains(@class, "bootstrap-switch")]//*[text()="{}"]/../..'
REFRESH_BUTTON = '//button[@id="refresh_button"]'


class RootPage(View):
    PAGE_MENU = None

    def __init__(self, parent, auto_login=True, logger=logger):
        View.__init__(self, parent, logger=logger)
        self._auto_login = auto_login
        self.load()

    _login = Login(logger=logger)
    main_menu = MainMenu(logger=logger)
    namespace_filter = NamespaceFilter(logger=logger)
    page_header = Text(locator='//*[contains(@class, "container-fluid")]//h2')
    notifications = Notifications(logger=logger)

    def load(self, force_load=False, force_refresh=False):
        logger.debug('Loading page')
        # if auto login enabled, do login. else do logout
        # TODO: SWSQE-992 this was throwing selenium.common.exceptions.WebDriverException:
        # Message: unknown error: failed to parse value of getElementRegion
        # login function is not working anyway now so disabling it to get rid of that failure
        # if self._auto_login:
        #     if login page displayed, do login
        #    self.login()
        # else:
        #     self.logout()
        # load particular page, only if PAGE_MENU is supplied and is not already displayed
        if self.PAGE_MENU is not None and \
                (self.main_menu.selected != self.PAGE_MENU or (self.PAGE_MENU != MENU.OVERVIEW.text
                 and not self.namespace_filter.is_available) or force_load):
            self.main_menu.select(self.PAGE_MENU)
        if force_refresh:
            self.page_refresh()
        wait_to_spinner_disappear(self.browser)
        wait_displayed(self)

    # TODO: SWSQE-992 login via kiali username is no longer suported,
    # this needs to be updated to use OCP login page
    def login(self, username=None, password=None, force_login=False):
        if force_login:
            if not self.logout():
                self.logger.warning('Existing session logout failed!')
                return False
        if self._login.is_displayed:
            # if username not supplied, take it from configuration
            if username is None:
                username = cfg.kiali.username
                password = cfg.kiali.password
            self._login.login(username=username, password=password)

            # wait till login complete
            def _is_displayed():
                return not self._login.is_displayed
            wait_for(_is_displayed, timeout='3s', delay=0.2, very_quiet=True, silent_failure=True)

        return not self._login.is_displayed

    def logout(self):
        if not self._login.is_displayed:
            self.navbar.user_menu.select(USER_MENU.LOGOUT.text)
        return self._login.is_displayed

    def reload(self):
        logger.debug('Reloading page')
        self.browser.refresh()
        self.load()

    def page_refresh(self):
        logger.debug('Refreshing page')
        self.browser.click(self.refresh)
        wait_to_spinner_disappear(self.browser)
        wait_displayed(self)

    @property
    def navbar(self):
        return self.main_menu.navbar

    @property
    def page_header(self):
        return self.page_header_el.text


class GraphPage(RootPage):
    PAGE_MENU = MENU.GRAPH.text

    namespace = NamespaceFilter()
    duration = ItemDropDown(locator=XP_DROP_DOWN.format('time_range_duration'))
    interval = ItemDropDown(locator=XP_DROP_DOWN.format('time_range_refresh'))
    edge_labels = DropDown(locator=XP_DROP_DOWN.format('graph_filter_edge_labels'))
    type = ItemDropDown(locator=XP_DROP_DOWN.format('graph_filter_view_type'))
    layout = GraphLayout()
    filter = CheckBoxFilter("Display")
    refresh = Button(locator=REFRESH_BUTTON)
    # TODO: implement graph control code


class OverviewPage(RootPage):
    PAGE_MENU = MENU.OVERVIEW.text

    filter = Filter()
    sort = SortDropDown(locator=SORT_DROP_DOWN.format('sort_selector'))
    type = TypeDropDown(locator=XP_DROP_DOWN.format('overview-type'))
    duration = DropDown(locator=XP_DROP_DOWN.format('overvoew-duration'))
    interval = DropDown(locator=XP_DROP_DOWN.format('overview-refresh'))
    refresh = Button(locator=REFRESH_BUTTON)
    content = ListViewOverview()


class ApplicationsPage(RootPage):
    PAGE_MENU = MENU.APPLICATIONS.text

    namespace = NamespaceFilter()
    filter = Filter()
    sort = SortBar()
    refresh = Button(locator=REFRESH_BUTTON)
    content = ListViewApplications()


class WorkloadsPage(RootPage):
    PAGE_MENU = MENU.WORKLOADS.text

    namespace = NamespaceFilter()
    filter = Filter()
    sort = SortBar()
    refresh = Button(locator=REFRESH_BUTTON)
    content = ListViewWorkloads()


class ServicesPage(RootPage):
    PAGE_MENU = MENU.SERVICES.text

    namespace = NamespaceFilter()
    filter = Filter()
    sort = SortBar()
    rate_interval = DropDown(locator=XP_DROP_DOWN.format('rateIntervalDropDown'))
    refresh = Button(locator=REFRESH_BUTTON)
    actions = Actions()
    content = ListViewServices()


class IstioConfigPage(RootPage):
    PAGE_MENU = MENU.ISTIO_CONFIG.text

    namespace = NamespaceFilter()
    filter = Filter()
    sort = SortBar()
    actions = Actions()
    refresh = Button(locator=REFRESH_BUTTON)
    content = ListViewIstioConfig()


class DistributedTracingPage(RootPage):
    PAGE_MENU = MENU.DISTRIBUTED_TRACING.text

    namespace = NamespaceFilter()
    traces = Traces()


class ThreeScaleConfigPage(RootPage):
    PAGE_MENU = MENU.THREESCALE_CONFIG.text

    sort = SortBar()
    actions = Actions()
    refresh = Button(locator=REFRESH_BUTTON)
    content = TableView3ScaleConfig()
