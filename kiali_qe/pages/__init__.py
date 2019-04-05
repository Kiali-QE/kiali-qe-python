"""update this doc"""
from widgetastic.widget import View, Text
from kiali_qe.components import (
    Button,
    DropDown,
    Filter,
    ListViewIstioConfig,
    ListViewServices,
    ListViewWorkloads,
    ListViewApplications,
    ListViewOverview,
    Login,
    MainMenu,
    Notifications,
    Pagination,
    SortDropDown,
    CheckBoxFilter,
    NamespaceFilter)
from kiali_qe.components.enums import (
    MainMenuEnum as MENU,
    UserMenuEnum as USER_MENU)
from kiali_qe.utils.log import logger
from kiali_qe.utils.conf import env as cfg
from wait_for import wait_for

XP_DROP_DOWN = '//*[contains(@class, "dropdown")]/*[@id="{}"]/..'
XP_BUTTON_SWITCH = '//*[contains(@class, "bootstrap-switch")]//*[text()="{}"]/../..'


class RootPage(View):
    PAGE_MENU = None

    def __init__(self, parent, auto_login=True, logger=logger):
        View.__init__(self, parent, logger=logger)
        self._auto_login = auto_login
        self.load()

    _login = Login()
    main_menu = MainMenu()
    page_header = Text(locator='//*[contains(@class, "container-fluid")]//h2')
    notifications = Notifications()

    def load(self, force_load=False):
        # if auto login enabled, do login. else do logout
        if self._auto_login:
            # if login page displayed, do login
            self.login()
        else:
            self.logout()
        # load particular page, only if PAGE_MENU is supplied
        if self.PAGE_MENU is not None and \
                (self.main_menu.selected != self.PAGE_MENU or force_load):
            self.main_menu.select(self.PAGE_MENU)

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
        self.browser.refresh()
        self.load()

    @property
    def navbar(self):
        return self.main_menu.navbar

    @property
    def page_header(self):
        return self.page_header_el.text


class GraphPage(RootPage):
    PAGE_MENU = MENU.GRAPH.text

    namespace = NamespaceFilter()
    duration = DropDown(locator=XP_DROP_DOWN.format('graph_filter_duration'))
    interval = DropDown(locator=XP_DROP_DOWN.format('graph_refresh_dropdown'))
    edge_labels = DropDown(locator=XP_DROP_DOWN.format('graph_filter_edges'))
    type = DropDown(locator=XP_DROP_DOWN.format('graph_filter_view_type'))
    # TODO Layout
    filter = CheckBoxFilter("Display")
    refresh = Button(locator='.//button//*[contains(@class, "fa-refresh")]')
    # TODO: implement graph control code


class OverviewPage(RootPage):
    PAGE_MENU = MENU.OVERVIEW.text

    filter = Filter()
    sort = SortDropDown(locator=XP_DROP_DOWN.format('sortTypeMenu'))
    type = DropDown(locator=XP_DROP_DOWN.format('overview-type'))
    duration = DropDown(locator=XP_DROP_DOWN.format('overvoew-duration'))
    interval = DropDown(locator=XP_DROP_DOWN.format('overview-refresh'))
    refresh = Button(locator='.//button//*[contains(@class, "fa-refresh")]')
    content = ListViewOverview()


class ApplicationsPage(RootPage):
    PAGE_MENU = MENU.APPLICATIONS.text

    namespace = NamespaceFilter()
    filter = Filter()
    sort = SortDropDown(locator=XP_DROP_DOWN.format('sortTypeMenu'))
    content = ListViewApplications()
    pagination = Pagination()


class WorkloadsPage(RootPage):
    PAGE_MENU = MENU.WORKLOADS.text

    namespace = NamespaceFilter()
    filter = Filter()
    sort = SortDropDown(locator=XP_DROP_DOWN.format('sortTypeMenu'))
    content = ListViewWorkloads()
    pagination = Pagination()


class ServicesPage(RootPage):
    PAGE_MENU = MENU.SERVICES.text

    namespace = NamespaceFilter()
    filter = Filter()
    sort = SortDropDown(locator=XP_DROP_DOWN.format('sortTypeMenu'))
    rate_interval = DropDown(locator=XP_DROP_DOWN.format('rateIntervalDropDown'))
    content = ListViewServices()
    pagination = Pagination()


class IstioConfigPage(RootPage):
    PAGE_MENU = MENU.ISTIO_CONFIG.text

    namespace = NamespaceFilter()
    filter = Filter()
    sort = SortDropDown(locator=XP_DROP_DOWN.format('sortTypeMenu'))
    actions = DropDown(locator=XP_DROP_DOWN.format('actions'))
    content = ListViewIstioConfig()
    pagination = Pagination()
