""" Update this doc"""
import re

from widgetastic.widget import Checkbox, TextInput, Widget
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from kiali_qe.components.enums import (
    HelpMenuEnum,
    ApplicationVersionEnum,
    IstioConfigObjectType,
    HealthType,
    IstioConfigValidation
)
from kiali_qe.entities.service import (
    Service,
    ServiceDetails,
    VirtualService,
    DestinationRule,
    SourceWorkload,
)
from kiali_qe.entities.istio_config import IstioConfig, Rule, IstioConfigDetails
from kiali_qe.entities.workload import (
    Workload,
    WorkloadDetails,
    WorkloadPod,
    DestinationService
)
from kiali_qe.entities.applications import Application, ApplicationDetails, AppWorkload
from kiali_qe.entities.overview import Overview
from kiali_qe.utils.date import parse_from_ui
from wait_for import wait_for
from kiali_qe.utils import get_validation


def wait_displayed(obj, timeout='10s'):
    wait_for(
        lambda: obj.is_displayed, timeout=timeout,
        delay=0.2, very_quiet=True, silent_failure=True)


def wait_to_spinner_disappear(browser, timeout='5s', very_quiet=True, silent_failure=True):
    def _is_disappeared(browser):
        return len(browser.elements(locator='//*[contains(@class, " spinner ")]',
                                    parent='//*[contains(@class, "navbar")]')) == 0
    wait_for(
        _is_disappeared, func_args=[browser], timeout=timeout,
        delay=0.2, very_quiet=very_quiet, silent_failure=silent_failure)


class Button(Widget):
    ROOT = '//button'

    def __init__(self, parent, locator=None, logger=None):
        Widget.__init__(self, parent, logger=logger)
        if locator:
            self.locator = locator
        else:
            self.locator = self.ROOT
        wait_displayed(self)

    def __locator__(self):
        return self.locator

    def click(self):
        self.browser.click(locator=self)

    def double_click(self):
        self.browser.double_click(locator=self)

    @property
    def text(self):
        self.browser.text(locator=self)


class ButtonSwitch(Button):
    DEFAULT = '//*[contains(@class, "bootstrap-switch")]'
    TEXT = './/*[contains(@class, "bootstrap-switch-label")]'

    def __init__(self, parent, locator=None, logger=None):
        Button.__init__(self, parent, locator=locator if locator else self.DEFAULT, logger=logger)

    @property
    def is_on(self):
        return 'bootstrap-switch-on' in self.browser.get_attribute('class', self)

    def on(self):
        if not self.is_on:
            self.click()

    def off(self):
        if self.is_on:
            self.click()

    @property
    def text(self):
        return self.browser.text(parent=self, locator=self.TEXT)


class Notifications(Widget):
    ROOT = '//*[contains(@class, "alert-")]'

    def __init__(self, parent, locator=None, logger=None):
        Widget.__init__(self, parent, logger=logger)
        if locator:
            self.locator = locator
        else:
            self.locator = self.ROOT
        wait_displayed(self)

    def __locator__(self):
        return self.locator

    @property
    def _raw_items(self):
        return self.browser.elements(
            parent=self.browser, locator=self.locator, check_visibility=True)

    @property
    def count(self):
        return len(self._raw_items)

    @property
    def items(self):
        _items = []
        for _element in self._raw_items:
            _items.append(Notification(parent=self, element=_element, logger=self.logger))
        return _items

    def get(self, _type=None, text=None):
        for _item in self.items:
            if (_type is not None) and (_type == _item._type):
                if text is not None:
                    if text in _item.text:
                        return _item
                else:
                    return _item
            elif (text is not None) and (text in _item.text):
                return _item
        return None

    def close_all(self):
        for _item in self.items:
            _item.close()

    def close(self, _type=None, text=None):
        _item = self.get(text=text, _type=_type)
        if _item is not None:
            _item.close()

    def contains(self, _type=None, text=None):
        return self.get(_type=_type, text=text) is not None


class Notification(Widget):
    TYPE_SUCCESS = 'success'
    TYPE_INFO = 'info'
    TYPE_WARNING = 'warning'
    TYPE_DANGER = 'danger'

    _TYPE_MAP = {
        'alert-success': TYPE_SUCCESS,
        'alert-info': TYPE_INFO,
        'alert-warning': TYPE_WARNING,
        'alert-danger': TYPE_DANGER,
    }

    def __init__(self, parent, element, logger=None):
        Widget.__init__(self, parent, logger=logger)
        self._element = element

    def __locator__(self):
        return self._element

    def __str__(self):
        return 'type:{}, text:{}'.format(self._type, self.text)

    def __repr__(self):
        return "{}({}, {})".format(
            type(self).__name__, repr(self._type), repr(self.text))

    @property
    def text(self):
        return self.browser.text(self._element)

    def close(self):
        if len(self.browser.elements('')) > 0:
            return self.browser.click('.//button[contains(@class, "close")]', parent=self)

    @property
    def _type(self):
        for _class in self.browser.classes(self):
            if _class in self._TYPE_MAP:
                return self._TYPE_MAP[_class]
        return


class DropDown(Widget):
    ROOT = '//*[contains(@class, "form-group")]/*[contains(@class, "dropdown")]/..'
    SELECT_BUTTON = './/*[contains(@class, "dropdown-toggle")]'
    OPTIONS_LIST = './/*[contains(@class, "dropdown-menu")]//*[contains(@role, "menuitem")]'
    OPTION = ('.//*[contains(@class, "dropdown-menu")]'
              '//*[contains(@role, "menuitem") and text()="{}"]')

    def __init__(self, parent, force_open=False, locator=None, logger=None):
        Widget.__init__(self, parent, logger=logger)
        self._force_open = force_open
        if locator:
            self.locator = locator
        else:
            self.locator = self.ROOT
        wait_displayed(self)

    def __locator__(self):
        return self.locator

    def _close(self):
        els = self.browser.elements(locator=self.SELECT_BUTTON, parent=self)
        if len(els) and els[0].get_attribute('aria-expanded') == 'true':
            self.browser.click(els[0])

    def _open(self):
        el = self.browser.element(locator=self.SELECT_BUTTON, parent=self)
        if el.get_attribute('aria-expanded') == 'false':
            self.browser.click(el)

    @property
    def options(self):
        options = []

        def _update_options():
            if self._force_open:
                self._open()
            for el in self.browser.elements(locator=self.OPTIONS_LIST, parent=self):
                # on filter drop down, title comes in to options list.
                # Here it will be removed
                if self.browser.get_attribute('title', el).startswith('Filter by'):
                    continue
                options.append(self.browser.text(el))
            if self._force_open:
                self._close()

        # sometime options are not displayed, needs to do retry
        for retry in range(1, 3):  # @UnusedVariable
            _update_options()
            if len(options) > 0:
                break
        return options

    def select(self, option):
        self._open()
        try:
            self.browser.click(self.browser.element(self.OPTION.format(option), parent=self))
        except NoSuchElementException:
            for element in self.browser.elements(self.OPTIONS_LIST, parent=self):
                try:
                    if element.text == option:
                        self.browser.click(element)
                # in some of dropdown, when we select options page reloads.
                # reload leads this issue
                except StaleElementReferenceException:
                    pass

    @property
    def selected(self):
        return self.browser.text(self.browser.element(self.SELECT_BUTTON, parent=self))


class Sort(Widget):
    ROOT = '//button/*[contains(@class, "sort-direction")]/..'
    ORDER_BY_ASC = './/*[contains(@class, "sort-direction") and contains(@class, "-asc")]'
    ORDER_BY_DESC = './/*[contains(@class, "sort-direction") and contains(@class, "-desc")]'

    def __init__(self, parent, locator=None, logger=None):
        Widget.__init__(self, parent, logger=logger)
        if locator:
            self.locator = locator
        else:
            self.locator = self.ROOT

    def __locator__(self):
        return self.locator

    def _order_by(self, ascending):
        if self.is_ascending != ascending:
            self.browser.click(self)

    @property
    def is_ascending(self):
        if len(self.browser.elements(parent=self, locator=self.ORDER_BY_ASC)):
            return True
        return False

    def ascending(self):
        self._order_by(True)

    def descending(self):
        self._order_by(False)


class SortDropDown(Widget):
    ROOT = '//*[contains(@class, "dropdown")]/../button/*[contains(@class, "sort-direction")]/../..'

    def __init__(self, parent, locator=None, logger=None):
        Widget.__init__(self, parent, logger=logger)
        if locator:
            self.locator = locator
        else:
            self.locator = self.ROOT
        self._drop_down = DropDown(
            parent=self, locator=self.locator + '/*[contains(@class, "dropdown")]')
        self._sort = Sort(
            parent=self, locator=self.locator + '/button/*[contains(@class, "sort-direction")]/..')

    def __locator__(self):
        return self.locator

    @property
    def options(self):
        return self._drop_down.options

    def order_by(self, is_ascending):
        if is_ascending:
            self._sort.ascending()
        else:
            self._sort.descending()

    def select(self, option, is_ascending=None):
        self._drop_down.select(option)
        if is_ascending is not None:
            self.order_by(is_ascending)

    @property
    def selected(self):
        return self._drop_down.selected, self._sort.is_ascending


class FilterList(Widget):
    ROOT = '//*[contains(@class, "toolbar-pf-results")]'
    ITEMS = './/*[contains(@class, "list-inline")]//*[contains(@class, "label")]'
    CLEAR = ('.//*[contains(@class, "list-inline")]//*[contains(@class, "label")'
             ' and contains(text(), "{}: {}")]//*[contains(@class, "pficon-close")]')
    CLEAR_ALL = './/a[text()="Clear All Filters"]'

    def __init__(self, parent, locator=None, logger=None):
        Widget.__init__(self, parent, logger=logger)
        if locator:
            self.locator = locator
        else:
            self.locator = self.ROOT

    def __locator__(self):
        return self.locator

    def clear_all(self):
        try:
            self.browser.click(self.browser.element(parent=self, locator=self.CLEAR_ALL))
        except NoSuchElementException:
            pass

    def remove(self, key, value):
        try:
            self.browser.click(
                self.browser.element(parent=self, locator=self.CLEAR.format(key, value)))
        except NoSuchElementException:
            pass

    @property
    def active_filters(self):
        _filters = []
        wait_displayed(self, timeout='5s')
        if not self.is_displayed:
            return _filters
        for el in self.browser.elements(parent=self, locator=self.ITEMS, force_check_safe=True):
            _name, _value = el.text.split('\n')[0].split(':', 1)
            _filters.append({'name': _name.strip(), 'value': _value.strip()})
        return _filters


class Filter(Widget):
    ROOT = '//*[contains(@class, "toolbar-pf-actions")]//*[contains(@class, "toolbar-pf-filter")]'
    FILTER_DROPDOWN = '//*[contains(@class, "dropdown")]'
    VALUE_INPUT = './/input'
    VALUE_DROPDOWN = './/*[contains(@class, "filter-pf-select")]'

    def __init__(self, parent, locator=None, logger=None):
        Widget.__init__(self, parent, logger=logger)
        if locator:
            self.locator = locator
        else:
            self.locator = self.ROOT
        self._filter = DropDown(parent=self, locator=self.locator + self.FILTER_DROPDOWN)
        self._filter_list = FilterList(parent=self.parent)

    def __locator__(self):
        return self.locator

    @property
    def filters(self):
        return self._filter.options

    def filter_options(self, filter_name):
        self.select(filter_name)
        if len(self.browser.elements(parent=self, locator=self.VALUE_DROPDOWN)):
            option_dropdown = DropDown(
                parent=self.parent, locator=self.locator + "/" + self.VALUE_DROPDOWN)
            return option_dropdown.options
        return {}

    def select(self, filter_name):
        self._filter.select(filter_name)

    def apply(self, filter_name, value):
        self.select(filter_name)
        if len(self.browser.elements(parent=self, locator=self.VALUE_INPUT)):
            _input = TextInput(parent=self, locator=self.VALUE_INPUT)
            _input.fill(value + '\n')
        elif len(self.browser.elements(parent=self, locator=self.VALUE_DROPDOWN)):
            _dropdown = DropDown(parent=self, locator=self.VALUE_DROPDOWN)
            _dropdown.select(value)
        else:
            raise NoSuchElementException('There is no "Input" or "Dropdown" component found!')
        # wait to Spinner disappear
        wait_to_spinner_disappear(self.browser)

    def remove(self, filter_name, value):
        self._filter_list.remove(filter_name, value)
        # wait to Spinner disappear
        wait_to_spinner_disappear(self.browser)

    def clear_all(self):
        self._filter_list.clear_all()
        # wait to Spinner disappear
        wait_to_spinner_disappear(self.browser)

    @property
    def active_filters(self):
        return self._filter_list.active_filters


class CheckBoxFilter(Widget):
    ROOT = ('//*[@role="tooltip" and contains(@class, "popover")]'
            '//*[contains(@class, "popover-content")]')
    CB_ITEMS = './/label/input[@type="checkbox"]/..'
    ITEM = './/label/span[normalize-space(text())="{}"]/../input'
    RB_ITEMS = './/label/input[@type="radio"]/..'
    DROP_DOWN = '//*[contains(@class, "dropdown")]/*[@id="{}"]/..'

    def __init__(self, parent, filter_name, locator=None, logger=None):
        Widget.__init__(self, parent, logger=logger)
        if locator:
            self.locator = locator
        else:
            self.locator = self.ROOT
        self._filter_button = Button(
            parent=self.parent,
            locator=('//button[normalize-space(text())="{}"]/'
                     '..//*[contains(@class, "fa-angle-down")]'.format(filter_name)))

    def __locator__(self):
        return self.locator

    def open(self):
        # TODO necessary workaround for remote zalenium webdriver execution
        self.browser.execute_script("window.scrollTo(0,0);")
        if not self.is_displayed:
            self._filter_button.click()

    def close(self):
        if self.is_displayed:
            self._filter_button.click()

            def _is_closed():
                return not self.is_displayed
            wait_for(_is_closed, timeout='3s', delay=0.2, very_quiet=True, silent_failure=True)

    @property
    def layout(self):
        self.open()
        return DropDown(parent=self, locator=self.DROP_DOWN.format('graph_filter_layout'))

    @property
    def items(self):
        self.open()
        try:
            return [
                self.browser.text(el)
                for el in self.browser.elements(parent=self, locator=self.CB_ITEMS)]
        finally:
            self.close()

    @property
    def radio_items(self):
        self.open()
        try:
            return [
                self.browser.text(el)
                for el in self.browser.elements(parent=self, locator=self.RB_ITEMS)]
        finally:
            self.close()

    def _cb_action(self, filter_name, action, value=None):
        self.open()
        try:
            _cb = Checkbox(locator=self.ITEM.format(filter_name), parent=self)
            if action is 'fill':
                _cb.fill(value)
            elif action is 'read':
                return _cb.read()
        finally:
            self.close()

    def check(self, filter_name):
        self._cb_action(filter_name, 'fill', True)

    def uncheck(self, filter_name):
        self._cb_action(filter_name, 'fill', False)

    def is_checked(self, filter_name):
        return self._cb_action(filter_name, 'read')


class Pagination(Widget):
    ROOT = ('//*[contains(@class, "list-view-pf-pagination")'
            ' and contains(@class, "content-view-pf-pagination")]')
    PER_PAGE_DROPDOWN = './/*[contains(@class, "pagination-pf-pagesize")]'
    TOTAL_ITEMS = './/*[contains(@class, "pagination-pf-items-total")]'
    TOTAL_PAGES = ('.//*[contains(@class, "pagination pagination-pf-forward")]/'
                   '..//*[contains(@class, "pagination-pf-pages")]')
    CURRENT_PAGE = './/input[contains(@class, "pagination-pf-page")]'
    FIRST_PAGE = './/*[@title="First Page"]'
    LAST_PAGE = './/*[@title="Last Page"]'
    NEXT_PAGE = './/*[@title="Next Page"]'
    PREVIOUS_PAGE = './/*[@title="Previous Page"]'

    def __init__(self, parent, locator=None, logger=None):
        Widget.__init__(self, parent, logger=logger)
        if locator:
            self.locator = locator
        else:
            self.locator = self.ROOT
        wait_displayed(self)

    def __locator__(self):
        return self.locator

    def _element(self, locator):
        wait_displayed(self)
        return self.browser.element(parent=self, locator=locator)

    @property
    def _page_input(self):
        wait_displayed(self)
        return TextInput(parent=self, locator=self.CURRENT_PAGE)

    @property
    def current_page(self):
        return int(self._page_input.read())

    def _move_to_page(self, page):
        self.browser.click(self._element(locator=page))
        wait_to_spinner_disappear(self.browser)

    def move_to_first_page(self):
        self._move_to_page(self.FIRST_PAGE)

    def move_to_last_page(self):
        self._move_to_page(self.LAST_PAGE)

    def move_to_next_page(self):
        self._move_to_page(self.NEXT_PAGE)

    def move_to_previous_page(self):
        self._move_to_page(self.PREVIOUS_PAGE)

    def move_to_page(self, page_number):
        self._page_input.fill('{}\n'.format(page_number))
        wait_to_spinner_disappear(self.browser)

    @property
    def total_items(self):
        return int(self.browser.text(self._element(locator=self.TOTAL_ITEMS)))

    @property
    def total_pages(self):
        return int(self.browser.text(self._element(locator=self.TOTAL_PAGES)))

    @property
    def _dropdown_per_page(self):
        wait_displayed(self)
        return DropDown(parent=self, locator=self.PER_PAGE_DROPDOWN)

    @property
    def items_per_page(self):
        return int(self._dropdown_per_page.selected)

    def set_items_per_page(self, items):
        self._dropdown_per_page.select(items)

    @property
    def items_per_page_options(self):
        return [int(i) for i in self._dropdown_per_page.options]


class About(Widget):
    ROOT = '//*[contains(@class, "about-modal-pf")]'
    HEADER = './/*[contains(@class, "modal-header")]'
    BODY = './/*[contains(@class, "modal-body")]'
    APP_LOGO = BODY + '/h1/img'
    VERSION = BODY + '//*[contains(@class, "product-versions-pf")]//li'
    VERSION_NAME = './strong'
    TRADEMARK = BODY + '//*[contains(@class, "trademark-pf")]'
    CLOSE = HEADER + '//*[contains(@class, "close")]'

    def __init__(self, parent, logger=None):
        Widget.__init__(self, parent, logger=logger)
        wait_displayed(self)

    @property
    def application_logo(self):
        return self.browser.element(self.APP_LOGO, parent=self).is_displayed

    def close(self):
        self.browser.click(self.browser.element(self.CLOSE, parent=self))

    @property
    def header(self):
        return self.browser.text(self.browser.element(self.HEADER, parent=self))

    @property
    def versions(self):
        _versions = {}

        # ugly fix to wait until version details loaded
        def _is_versions_loaded():
            _locator = '{}/strong[text()="{}"]'.format(
                self.VERSION, ApplicationVersionEnum.PROMETHEUS.text)
            if len(self.browser.elements(_locator, parent=self, force_check_safe=True)) > 0:
                return True
            else:
                return False
        wait_for(_is_versions_loaded, timout=3, delay=0.2, very_quiet=True)
        for el in self.browser.elements(self.VERSION, parent=self, force_check_safe=True):
            _name = self.browser.text(self.browser.element(self.VERSION_NAME, parent=el))
            _version = self.browser.text(el).split(_name, 1)[1].strip()
            _versions[_name] = _version
        return _versions

    @property
    def trademark(self):
        return self.browser.text(self.browser.element(self.TRADEMARK, parent=self))


class NavBar(Widget):
    ROOT = '//*[contains(@class, "navbar")]'
    TOGGLE_NAVIGATION = './/*[contains(@class, "navbar-toggle")]'
    NAVBAR_RIGHT_MENU = ('//*[contains(@class, "navbar-right")]'
                         '//*[contains(@class, "dropdown")]//*[@id="{}"]/..')

    def __init__(self, parent, logger=None):
        Widget.__init__(self, parent, logger=logger)
        self.help_menu = DropDown(
            parent=self, locator=self.NAVBAR_RIGHT_MENU.format('help'),
            logger=logger, force_open=True)
        self.user_menu = DropDown(
            parent=self, locator=self.NAVBAR_RIGHT_MENU.format('user'),
            logger=logger, force_open=True)

    def about(self):
        self.help_menu.select(HelpMenuEnum.ABOUT.text)
        return About(parent=self.parent, logger=self.logger)

    def toggle(self):
        self.browser.click(self.browser.element(self.TOGGLE_NAVIGATION, parent=self))


class MainMenu(Widget):
    ROOT = ('//*[contains(@class, "nav-pf-vertical-with-sub-menus")'
            ' and contains(@class, "nav-pf-persistent-secondary")]')
    MENU_ITEMS = './/*[contains(@class, "list-group-item-value")]'
    MENU_ITEM = './/*[contains(@class, "list-group-item-value") and text()="{}"]'
    MENU_ITEM_ACTIVE = ('.//*[contains(@class, "active") and contains(@class, "list-group-item")]'
                        '//*[contains(@class, "list-group-item-value")]')

    def __init__(self, parent, logger=None):
        Widget.__init__(self, parent, logger=logger)
        self.navbar = NavBar(parent=self.parent, logger=logger)

    def select(self, menu):
        self.browser.click(self.browser.element(self.MENU_ITEM.format(menu), parent=self))

    @property
    def selected(self):
        return self.browser.text(self.browser.element(self.MENU_ITEM_ACTIVE, parent=self))

    @property
    def items(self):
        return [
            self.browser.text(el)
            for el
            in self.browser.elements(self.MENU_ITEMS, parent=self)]

    @property
    def is_collapsed(self):
        return 'collapsed' in self.browser.get_attribute('class', self.ROOT)

    def collapse(self):
        if not self.is_collapsed:
            self.navbar.toggle()

    def expand(self):
        if self.is_collapsed:
            self.navbar.toggle()


class Login(Widget):
    ROOT = '//*[@id="kiali-login"]'
    USERNAME = './/input[@name="username"]'
    PASSWORD = './/input[@name="password"]'
    SUBMIT = './/button[@type="submit"]'

    def __init__(self, parent, logger=None):
        Widget.__init__(self, parent, logger=logger)
        self.username = TextInput(parent=self, locator=self.USERNAME)
        self.password = TextInput(parent=self, locator=self.PASSWORD)
        self.submit = Button(parent=self.parent, locator=self.SUBMIT, logger=logger)

    def login(self, username, password):
        self.username.fill(username)
        self.password.fill(password)
        self.browser.click(self.submit)


class ListViewAbstract(Widget):
    ROOT = '//*[contains(@class, "list-view-pf") and contains(@class, "list-view-pf-view")]'
    ITEMS = './/*[contains(@class, "list-group-item")]//*[contains(@class, "list-view-pf-body")]'
    ITEM_TEXT = './/*[contains(@class, "list-group-item-heading")]'
    SELECT_ITEM = ITEMS + '//*[text()="{}"]'
    SELECT_ITEM_WITH_NAMESPACE = SELECT_ITEM + '/small[text()="{}"]'
    OBJECT_TYPE = './/*[contains(@class, "list-group-item-text")]//td'
    DETAILS_ROOT = './/div[contains(@class, "card-pf")]'
    HEADER = './/div[contains(@class, "card-pf-heading")]//h2'
    ISTIO_PROPERTIES = ('.//*[contains(@class, "card-pf-body")]'
                        '//strong[normalize-space(text())="{}"]/..')
    PROPERTY_SECTIONS = ('.//*[contains(@class, "card-pf-body")]'
                         '//strong[normalize-space(text())="{}"]/../..')
    PODS = 'Pods'
    SERVICES = 'Services'
    TYPE = 'Type'
    IP = 'IP'
    PORTS = 'Ports'
    CREATED_AT = 'Created at'
    RESOURCE_VERSION = 'Resource Version'
    INBOUND_METRICS = 'Inbound Metrics'
    OUTBOUND_METRICS = 'Outbound Metrics'
    MISSING_SIDECAR_TEXT = 'Missing Sidecar'
    MISSING_SIDECAR = './/span[normalize-space(text())="{}"]'.format(MISSING_SIDECAR_TEXT)

    def __init__(self, parent, locator=None, logger=None):
        Widget.__init__(self, parent, logger=logger)
        if locator:
            self.locator = locator
        else:
            self.locator = self.ROOT
        self._pagination = Pagination(parent=self.parent)

    def __locator__(self):
        return self.locator

    def open(self, name, namespace=None):
        # TODO added wait for unstable performance
        wait_to_spinner_disappear(self.browser)
        if namespace is not None:
            self.browser.click(self.browser.element(
                self.SELECT_ITEM_WITH_NAMESPACE.format(name, namespace), parent=self))
        else:
            self.browser.click(self.browser.element(self.SELECT_ITEM.format(name), parent=self))

        wait_to_spinner_disappear(self.browser)
        wait_displayed(self)

    def _item_sidecar(self, element):
        return not len(self.browser.elements(
                parent=element, locator=self.MISSING_SIDECAR)) > 0

    def _details_sidecar(self):
        return not len(self.browser.elements(
            parent=self.DETAILS_ROOT,
            locator=self.MISSING_SIDECAR)) > 0

    def _get_details_health(self):
        _health_sublocator = '/../..//strong[normalize-space(text())="Health"]'
        _healthy = len(self.browser.elements(
            parent=self.DETAILS_ROOT,
            locator='.//*[contains(@class, "pficon-ok")]' + _health_sublocator)) > 0
        _not_healthy = len(self.browser.elements(
            parent=self.DETAILS_ROOT,
            locator='.//*[contains(@class, "pficon-error-circle-o")]' + _health_sublocator)) > 0
        _degraded = len(self.browser.elements(
            parent=self.DETAILS_ROOT,
            locator='.//*[contains(@class, "pficon-warning-triangle-o")]' + _health_sublocator)) > 0
        _not_available = len(self.browser.elements(
            parent=self.DETAILS_ROOT,
            locator='.//*[text()="N/A"]')) > 0
        _health = None
        if _healthy:
            _health = HealthType.HEALTHY
        elif _not_healthy:
            _health = HealthType.FAILURE
        elif _degraded:
            _health = HealthType.DEGRADED
        elif _not_available:
            _health = HealthType.NA
        return _health

    def _get_item_health(self, element):
        wait_displayed(self)
        _healthy = len(self.browser.elements(
            parent=element,
            locator='.//*[contains(@class, "pficon-ok")]')) > 0
        _not_healthy = len(self.browser.elements(
            parent=element,
            locator='.//*[contains(@class, "pficon-error-circle-o")]')) > 0
        _degraded = len(self.browser.elements(
            parent=element,
            locator='.//*[contains(@class, "pficon-warning-triangle-o")]')) > 0
        _not_available = len(self.browser.elements(
            parent=element,
            locator='.//*[text()="N/A"]')) > 0
        _health = None
        if _healthy:
            _health = HealthType.HEALTHY
        elif _not_healthy:
            _health = HealthType.FAILURE
        elif _degraded:
            _health = HealthType.DEGRADED
        elif _not_available:
            _health = HealthType.NA
        return _health

    def _get_item_validation(self, element):
        wait_displayed(self)
        _valid = len(self.browser.elements(
            parent=element,
            locator='.//*[contains(@class, "pficon-ok")]')) > 0
        _not_valid = len(self.browser.elements(
            parent=element,
            locator='.//*[contains(@class, "pficon-error-circle-o")]')) > 0
        _warning = len(self.browser.elements(
            parent=element,
            locator='.//*[contains(@class, "pficon-warning-triangle-o")]')) > 0
        return get_validation(_valid, _not_valid, _warning)

    def _get_details_validation(self):
        _not_valid = len(self.browser.elements(
            parent=self.DETAILS_ROOT,
            locator='.//*[contains(@class, "ace_error")]')) > 0
        _warning = len(self.browser.elements(
            parent=self.DETAILS_ROOT,
            locator='.//*[contains(@class, "ace_warning")]')) > 0
        if _not_valid:
            return IstioConfigValidation.NOT_VALID
        elif _warning:
            return IstioConfigValidation.WARNING
        else:
            return IstioConfigValidation.VALID

    def _get_item_label_keys(self, element):
        _label_keys = []
        wait_displayed(self)
        _labels = self.browser.elements(
            parent=element,
            locator='.//strong[normalize-space(text())="Label Validation :"]\
                /../*[contains(@class, "badge")]')
        if _labels:
            for _label in _labels:
                _label_keys.append(_label.text)
        return _label_keys

    def _get_details_labels(self):
        _label_dict = {}
        wait_displayed(self)
        _labels = self.browser.elements(
            parent=self.DETAILS_ROOT,
            locator='.//strong[contains(text(), "Labels")]\
                /../..//*[contains(@class, "label-pair")]')
        if _labels:
            for _label in _labels:
                _label_key = self.browser.element(
                    parent=_label,
                    locator='.//*[contains(@class, "label-key")]').text
                _label_value = self.browser.element(
                    parent=_label,
                    locator='.//*[contains(@class, "label-value")]').text
                _label_dict[_label_key] = _label_value
        return _label_dict

    @property
    def all_items(self):
        items = []
        self._pagination.move_to_first_page()
        # set per page to maximum size
        # TODO: set to maximum size. right now problem with focus,
        # hence setting it to minimum size
        self._pagination.set_items_per_page(5)
        for _page in range(1, self._pagination.total_pages + 1):
            self._pagination.move_to_page(_page)
            wait_to_spinner_disappear(self.browser)
            items.extend(self.items)
        return items


class ListViewOverview(ListViewAbstract):
    ROOT = '//*[contains(@class, "cards-pf") and contains(@class, "container-cards-pf")]'
    ITEMS = './/*[contains(@class, "row")]//*[contains(@class, "card-pf-accented")]'
    ITEM_TITLE = './/*[contains(@class, "card-pf-title")]'
    ITEM_TEXT = './/*[contains(@class, "card-pf-body")]/a'
    UNHEALTHY_TEXT = './/*[contains(@class, "pficon-error-circle-o")]/..'
    HEALTHY_TEXT = './/*[contains(@class, "pficon-ok")]/..'
    DEGRADED_TEXT = './/*[contains(@class, "pficon-warning-triangle-o")]/..'
    OVERVIEW_TYPE = './/*[@id="overview-type"]'

    @property
    def all_items(self):
        return self.items

    @property
    def items(self):
        _items = []
        _overview_type = self.browser.element(
                locator=self.OVERVIEW_TYPE, parent=self.ROOT).text
        for el in self.browser.elements(self.ITEMS, parent=self):
            _namespace = self.browser.element(
                locator=self.ITEM_TITLE, parent=el).text
            _item_numbers = int(re.search(r'\d+', self.browser.element(
                locator=self.ITEM_TEXT, parent=el).text).group())
            _unhealthy = 0
            _healthy = 0
            _degraded = 0
            # update health
            if len(self.browser.elements(
                    parent=el, locator=self.UNHEALTHY_TEXT)) > 0:
                _unhealthy = int(self.browser.element(
                    locator=self.UNHEALTHY_TEXT, parent=el).text)
            if len(self.browser.elements(
                    parent=el, locator=self.DEGRADED_TEXT)) > 0:
                _degraded = int(self.browser.element(
                    locator=self.DEGRADED_TEXT, parent=el).text)
            if len(self.browser.elements(
                    parent=el, locator=self.HEALTHY_TEXT)) > 0:
                _healthy = int(self.browser.element(
                    locator=self.HEALTHY_TEXT, parent=el).text)
            # overview object creation
            _overview = Overview(
                overview_type=_overview_type,
                namespace=_namespace,
                items=_item_numbers,
                healthy=_healthy,
                unhealthy=_unhealthy,
                degraded=_degraded)
            # append this item to the final list
            _items.append(_overview)
        return _items


class ListViewApplications(ListViewAbstract):

    def get_details(self, name, namespace=None):
        self.open(name, namespace)
        _name = self.browser.text(
            locator=self.HEADER,
            parent=self.DETAILS_ROOT).replace(self.MISSING_SIDECAR_TEXT, '').strip()

        _table_view_workloads = TableViewAppWorkloads(self.parent, self.locator, self.logger)

        _table_view_services = TableViewAppServices(self.parent, self.locator, self.logger)

        _inbound_metrics = MetricsView(self.parent, self.INBOUND_METRICS)

        _outbound_metrics = MetricsView(self.parent,
                                        self.OUTBOUND_METRICS)

        return ApplicationDetails(name=str(_name),
                                  istio_sidecar=self._details_sidecar(),
                                  health=self._get_details_health(),
                                  workloads=_table_view_workloads.all_items,
                                  services=_table_view_services.all_items,
                                  inbound_metrics=_inbound_metrics,
                                  outbound_metrics=_outbound_metrics)

    @property
    def items(self):
        _items = []
        for el in self.browser.elements(self.ITEMS, parent=self):
            # get application name and namespace
            name, namespace = self.browser.element(
                locator=self.ITEM_TEXT, parent=el).text.split('\n')
            _name = name.strip()
            _namespace = namespace.strip()
            # TODO Error Rate
            # application object creation
            _application = Application(
                name=_name, namespace=_namespace,
                istio_sidecar=self._item_sidecar(el),
                health=self._get_item_health(element=el))
            # append this item to the final list
            _items.append(_application)
        return _items


class ListViewWorkloads(ListViewAbstract):

    def get_details(self, name, namespace=None):
        self.open(name, namespace)
        _name = self.browser.text(
            locator=self.HEADER,
            parent=self.DETAILS_ROOT).replace(self.MISSING_SIDECAR_TEXT, '').strip()
        _type = self.browser.text(locator=self.ISTIO_PROPERTIES.format(self.TYPE),
                                  parent=self.DETAILS_ROOT).replace(self.TYPE, '').strip()
        _created_at = self.browser.text(locator=self.ISTIO_PROPERTIES.format(self.CREATED_AT),
                                        parent=self.DETAILS_ROOT).replace(
                                            self.CREATED_AT, '').strip()
        _resource_version = self.browser.text(
            locator=self.ISTIO_PROPERTIES.format(self.RESOURCE_VERSION),
            parent=self.DETAILS_ROOT).replace(self.RESOURCE_VERSION, '').strip()

        _table_view_pods = TableViewWorkloadPods(self.parent, self.locator, self.logger)

        _table_view_services = TableViewServices(self.parent, self.locator, self.logger)

        _table_view_destination_services = TableViewDestinationServices(
            self.parent, self.locator, self.logger)

        _inbound_metrics = MetricsView(self.parent, self.INBOUND_METRICS)

        _outbound_metrics = MetricsView(self.parent,
                                        self.OUTBOUND_METRICS)

        return WorkloadDetails(name=str(_name),
                               workload_type=_type,
                               created_at=parse_from_ui(_created_at),
                               resource_version=_resource_version,
                               istio_sidecar=self._details_sidecar(),
                               health=self._get_details_health(),
                               pods_number=_table_view_pods.number,
                               services_number=_table_view_services.number,
                               destination_services_number=_table_view_destination_services.number,
                               pods=_table_view_pods.all_items,
                               services=_table_view_services.all_items,
                               destination_services=_table_view_destination_services.all_items,
                               labels=self._get_details_labels(),
                               inbound_metrics=_inbound_metrics,
                               outbound_metrics=_outbound_metrics)

    @property
    def items(self):
        _items = []
        for el in self.browser.elements(self.ITEMS, parent=self):
            # get workload name and namespace
            name, namespace, _type = self.browser.element(
                locator=self.ITEM_TEXT, parent=el).text.split('\n')
            _name = name.strip()
            _namespace = namespace.strip()
            _type = _type.strip()
            _label_keys = self._get_item_label_keys(el)
            # workload object creation
            _workload = Workload(
                name=_name, namespace=_namespace, workload_type=_type,
                istio_sidecar=self._item_sidecar(el),
                app_label='app' in _label_keys,
                version_label='version' in _label_keys,
                health=self._get_item_health(element=el))
            # append this item to the final list
            _items.append(_workload)
        return _items


class ListViewServices(ListViewAbstract):

    def get_details(self, name, namespace=None):
        self.open(name, namespace)
        _name = self.browser.text(
            locator=self.HEADER,
            parent=self.DETAILS_ROOT).replace(self.MISSING_SIDECAR_TEXT, '').strip()
        _type = self.browser.text(locator=self.ISTIO_PROPERTIES.format(self.TYPE),
                                  parent=self.DETAILS_ROOT).replace(self.TYPE, '').strip()
        _ip = self.browser.text(locator=self.ISTIO_PROPERTIES.format(self.IP),
                                parent=self.DETAILS_ROOT).replace(self.IP, '').strip()
        _created_at = self.browser.text(
            locator=self.ISTIO_PROPERTIES.format(self.CREATED_AT),
            parent=self.DETAILS_ROOT).replace(self.CREATED_AT, '').strip()
        _resource_version = self.browser.text(
            locator=self.ISTIO_PROPERTIES.format(self.RESOURCE_VERSION),
            parent=self.DETAILS_ROOT).replace(self.RESOURCE_VERSION, '').strip()
        _ports = self.browser.text(
            locator=self.PROPERTY_SECTIONS.format(self.PORTS),
            parent=self.DETAILS_ROOT).replace(self.PORTS, '').strip()

        _table_view_wl = TableViewWorkloads(self.parent, self.locator, self.logger)

        _table_view_swl = TableViewSourceWorkloads(self.parent, self.locator, self.logger)

        _table_view_vs = TableViewVirtualServices(self.parent, self.locator, self.logger)

        _table_view_dr = TableViewDestinationRules(self.parent, self.locator, self.logger)

        _inbound_metrics = MetricsView(self.parent, self.INBOUND_METRICS)

        return ServiceDetails(name=_name,
                              created_at=parse_from_ui(_created_at),
                              service_type=_type,
                              resource_version=_resource_version,
                              ip=_ip,
                              ports=str(_ports.replace('\n', ' ')),
                              health=self._get_details_health(),
                              istio_sidecar=self._details_sidecar(),
                              labels=self._get_details_labels(),
                              workloads_number=_table_view_wl.number,
                              source_workloads_number=_table_view_swl.number,
                              virtual_services_number=_table_view_vs.number,
                              destination_rules_number=_table_view_dr.number,
                              workloads=_table_view_wl.all_items,
                              source_workloads=_table_view_swl.all_items,
                              virtual_services=_table_view_vs.all_items,
                              destination_rules=_table_view_dr.all_items,
                              inbound_metrics=_inbound_metrics)

    @property
    def items(self):
        _items = []
        for el in self.browser.elements(self.ITEMS, parent=self):
            # get rule name and namespace
            name, namespace = self.browser.element(
                locator=self.ITEM_TEXT, parent=el).text.split('\n')
            _name = name.strip()
            _namespace = namespace.strip()

            # create service instance
            _service = Service(
                name=_name,
                namespace=_namespace,
                istio_sidecar=self._item_sidecar(el),
                health=self._get_item_health(element=el))
            # append this item to the final list
            _items.append(_service)
        return _items


class ListViewIstioConfig(ListViewAbstract):
    ACTION_HEADER = ('.//*[contains(@class, "list-group-item-text")]'
                     '//strong[normalize-space(text())="{}"]/..')
    CONFIG_HEADER = './/div[contains(@class, "row")]//h1'
    CONFIG_TEXT = './/div[contains(@class, "ace_content")]'
    CONFIG_DETAILS_ROOT = './/div[contains(@class, "container-cards-pf")]'

    def get_details(self, name, namespace=None):
        self.open(name, namespace)
        _type, _name = self.browser.text(locator=self.CONFIG_HEADER,
                                         parent=self.CONFIG_DETAILS_ROOT).split(': ')
        _text = self.browser.text(locator=self.CONFIG_TEXT,
                                  parent=self.CONFIG_DETAILS_ROOT)
        return IstioConfigDetails(name=_name, _type=_type, text=_text,
                                  validation=self._get_details_validation())

    @property
    def items(self):
        _items = []
        for el in self.browser.elements(self.ITEMS, parent=self):
            # get rule name and namespace
            name, namespace = self.browser.element(
                locator=self.ITEM_TEXT, parent=el).text.split('\n')
            _name = name.strip()
            _namespace = namespace.strip()
            # disable handler and other features. UI changed
            # _actions = []
            # _match = None
            # get handler
            # _handler = self.browser.element(
            #     locator=self.ACTION_HEADER.format('Handler'),
            #     parent=el).text.split('Handler:', 1)[1].strip()
            # # get instances
            # _instances = self.browser.element(
            #     locator=self.ACTION_HEADER.format('Instances'),
            #     parent=el).text.split('Instances:', 1)[1].strip().split(',')
            # _actions.append(Action(handler=_handler, instances=_instances))
            # # get Match
            # if 'Match:' in el.text:
            #     match = self.browser.element(
            #         locator=self.ACTION_HEADER.format('Match'),
            #         parent=el).text.split('Match:', 1)[1].strip()
            #     _match = match.strip()

            # create istio config instance
            _object_type = self.browser.text(
                self.browser.element(locator=self.OBJECT_TYPE, parent=el))
            if str(_object_type) == IstioConfigObjectType.RULE.text or \
                    '{}: '.format(IstioConfigObjectType.ADAPTER.text) in str(_object_type) or \
                    '{}: '.format(IstioConfigObjectType.TEMPLATE.text) in str(_object_type):
                _rule = Rule(name=_name, namespace=_namespace, object_type=_object_type)
                # append this item to the final list
                _items.append(_rule)
            else:
                _config = IstioConfig(name=_name,
                                      namespace=_namespace,
                                      object_type=_object_type,
                                      validation=self._get_item_validation(el))
                # append this item to the final list
                _items.append(_config)
        return _items


class TableViewAbstract(Widget):
    SERVICE_DETAILS_ROOT = './/div[contains(@class, "card-pf")]'
    SERVICES_TAB = '//div[@id="service-tabs"]//li//a[contains(text(), "{}")]/..'
    ROOT = '//[contains(@class, "tab-pane") and contains(@class, "active") and \
        contains(@class, "in")]'
    ROWS = '//div[@id="{}"]//table[contains(@class, "table")]//tbody//tr'
    COLUMN = './/td'

    def __init__(self, parent, locator=None, logger=None):
        Widget.__init__(self, parent, logger=logger)
        if locator:
            self.locator = locator
        else:
            self.locator = self.ROOT

    def __locator__(self):
        return self.locator

    def _get_item_status(self, element):
        wait_displayed(self)
        _valid = len(self.browser.elements(
            parent=element,
            locator='.//*[contains(@class, "pficon-ok")]')) > 0
        _not_valid = len(self.browser.elements(
            parent=element,
            locator='.//*[contains(@class, "pficon-error-circle-o")]')) > 0
        _warning = len(self.browser.elements(
            parent=element,
            locator='.//*[contains(@class, "pficon-warning-triangle-o")]')) > 0
        return get_validation(_valid, _not_valid, _warning)

    def _get_labels(self, el):
        _label_dict = {}
        wait_displayed(self)
        _labels = self.browser.elements(
            parent=el,
            locator='.//*[contains(@class, "label-pair")]')
        if _labels:
            for _label in _labels:
                _label_key = self.browser.element(
                    parent=_label,
                    locator='.//*[contains(@class, "label-key")]').text
                _label_value = self.browser.element(
                    parent=_label,
                    locator='.//*[contains(@class, "label-value")]').text
                _label_dict[_label_key] = _label_value
        return _label_dict

    @property
    def all_items(self):
        return self.items


class TableViewAppWorkloads(TableViewAbstract):
    ROWS = '//div[contains(@class, "card-pf-body")]\
    //div[contains(@class, "row")]\
    //div[contains(@class, "list-view-pf-main-info")]'
    COLUMN = './/div[contains(@class, "list-view-pf-description")]'

    @property
    def items(self):

        _items = []
        for el in self.browser.elements(locator=self.ROWS,
                                        parent=self.ROOT):
            _values = self.browser.element(
                locator=self.COLUMN, parent=el).text.split('\n')
            # create Workload instance
            # TODO add istio sidecar when KIALI-1200 IS DONE
            if _values[0] == 'WORKLOAD':
                _workload = AppWorkload(
                    name=_values[1] if len(_values) >= 2 else '')
            # append this item to the final list
            _items.append(_workload)
        return _items


class TableViewAppServices(TableViewAbstract):
    ROWS = '//div[contains(@class, "card-pf-body")]\
    //div[contains(@class, "row")]\
    //div[contains(@class, "list-view-pf-main-info")]'
    COLUMN = './/div[contains(@class, "list-view-pf-description")]'

    @property
    def items(self):

        _items = []
        for el in self.browser.elements(locator=self.ROWS,
                                        parent=self.ROOT):
            _values = self.browser.element(
                locator=self.COLUMN, parent=el).text.split('\n')
            # create Service instance
            if _values[0] == 'SERVICE':
                # append this item to the final list
                _items.append(_values[1])
        return _items


class TableViewWorkloads(TableViewAbstract):
    WLD_TEXT = 'Workloads'

    def open(self):
        tab = self.browser.element(locator=self.SERVICES_TAB.format(self.WLD_TEXT),
                                   parent=self.SERVICE_DETAILS_ROOT)
        try:
            self.browser.click(tab)
        finally:
            self.browser.click(tab)
        wait_displayed(self)

    @property
    def number(self):
        _wl_text = self.browser.text(locator=self.SERVICES_TAB.format(self.WLD_TEXT),
                                     parent=self.SERVICE_DETAILS_ROOT)
        return int(re.search(r'\d+', _wl_text).group())

    @property
    def items(self):
        self.open()

        _items = []
        for el in self.browser.elements(locator=self.ROWS.format(
            'service-tabs-pane-workloads'),
                                        parent=self.ROOT):
            _columns = list(self.browser.elements(locator=self.COLUMN, parent=el))

            _name = _columns[0].text.strip()
            _type = _columns[1].text.strip()
            # TODO labels
            _created_at = _columns[3].text.strip()
            _resource_version = _columns[4].text.strip()

            # workload object creation
            _workload = WorkloadDetails(
                name=_name,
                workload_type=_type,
                labels=self._get_labels(_columns[2]),
                created_at=parse_from_ui(_created_at),
                resource_version=_resource_version)
            # append this item to the final list
            _items.append(_workload)
        return _items


class TableViewSourceWorkloads(TableViewAbstract):
    WLD_TEXT = 'Source Workloads'
    ROWS = '//div[contains(@class, "card-pf")]\
    //div[contains(@class, "row-cards-pf")]\
    //div[contains(@class, "card-pf-body")]'
    DEST = './/div[contains(@class, "progress-description")]'
    COLUMN = './/li'

    def open(self):
        tab = self.browser.element(locator=self.SERVICES_TAB.format(self.WLD_TEXT),
                                   parent=self.SERVICE_DETAILS_ROOT)
        try:
            self.browser.click(tab)
        finally:
            self.browser.click(tab)
        wait_displayed(self)

    @property
    def number(self):
        _wl_text = self.browser.text(locator=self.SERVICES_TAB.format(self.WLD_TEXT),
                                     parent=self.SERVICE_DETAILS_ROOT)
        return int(re.search(r'\d+', _wl_text).group())

    @property
    def items(self):
        self.open()

        _items = []
        for el in self.browser.elements(locator=self.ROWS.format(
            'service-tabs-pane-sources'),
                                        parent=self.ROOT):
            _to = self.browser.element(locator=self.DEST, parent=el).text.replace('To:', '').strip()
            _columns = list(self.browser.elements(locator=self.COLUMN, parent=el))
            _workloads = []
            for _column in _columns:
                _workloads.append(_column.text.strip())
            # source workload object creation
            _workload = SourceWorkload(
                to=_to,
                workloads=_workloads)
            # append this item to the final list
            _items.append(_workload)
        return _items


class TableViewVirtualServices(TableViewAbstract):
    VS_TEXT = 'Virtual Services'

    def open(self):
        tab = self.browser.element(locator=self.SERVICES_TAB.format(self.VS_TEXT),
                                   parent=self.SERVICE_DETAILS_ROOT)
        try:
            self.browser.click(tab)
        finally:
            self.browser.click(tab)
        wait_displayed(self)

    @property
    def number(self):
        _vs_text = self.browser.text(locator=self.SERVICES_TAB.format(self.VS_TEXT),
                                     parent=self.SERVICE_DETAILS_ROOT)
        return int(re.search(r'\d+', _vs_text).group())

    @property
    def items(self):
        self.open()

        _items = []
        for el in self.browser.elements(locator=self.ROWS.format(
            'service-tabs-pane-virtualservices'),
                                        parent=self.ROOT):
            _columns = list(self.browser.elements(locator=self.COLUMN, parent=el))

            _name = _columns[1].text.strip()
            _created_at = _columns[2].text.strip()
            _resource_version = _columns[3].text.strip()
            # create Virtual Service instance
            _virtual_service = VirtualService(
                status=self._get_item_status(_columns[0]),
                name=_name,
                created_at=parse_from_ui(_created_at),
                resource_version=_resource_version)
            # append this item to the final list
            _items.append(_virtual_service)
        return _items


class TableViewDestinationRules(TableViewAbstract):
    DR_TEXT = 'Destination Rules'

    def open(self):
        tab = self.browser.element(locator=self.SERVICES_TAB.format(self.DR_TEXT),
                                   parent=self.SERVICE_DETAILS_ROOT)
        try:
            self.browser.click(tab)
        finally:
            self.browser.click(tab)
        wait_displayed(self)

    @property
    def number(self):
        _dr_text = self.browser.text(locator=self.SERVICES_TAB.format(self.DR_TEXT),
                                     parent=self.SERVICE_DETAILS_ROOT)
        return int(re.search(r'\d+', _dr_text).group())

    @property
    def items(self):
        self.open()

        _items = []
        for el in self.browser.elements(locator=self.ROWS.format(
                'service-tabs-pane-destinationrules'),
                                        parent=self.ROOT):
            _columns = list(self.browser.elements(locator=self.COLUMN, parent=el))

            _name = _columns[1].text.strip()
            _host = _columns[4].text.strip()
            _created_at = _columns[5].text.strip()
            _resource_version = _columns[6].text.strip()
            # TODO: fetch traffic policy and subset information from GUI
            # create Virtual Service instance
            _destination_rule = DestinationRule(
                status=self._get_item_status(_columns[0]),
                name=_name,
                host=_host,
                created_at=parse_from_ui(_created_at),
                resource_version=_resource_version)
            # append this item to the final list
            _items.append(_destination_rule)
        return _items


class TableViewWorkloadPods(TableViewAbstract):
    POD_TEXT = 'Pods'

    def open(self):
        tab = self.browser.element(locator=self.SERVICES_TAB.format(self.POD_TEXT),
                                   parent=self.SERVICE_DETAILS_ROOT)
        try:
            self.browser.click(tab)
        finally:
            self.browser.click(tab)
        wait_displayed(self)

    @property
    def number(self):
        _vs_text = self.browser.text(locator=self.SERVICES_TAB.format(self.POD_TEXT),
                                     parent=self.SERVICE_DETAILS_ROOT)
        return int(re.search(r'\d+', _vs_text).group())

    @property
    def items(self):
        self.open()

        _items = []
        for el in self.browser.elements(locator=self.ROWS.format(
            'service-tabs-pane-pods'),
                                        parent=self.ROOT):
            _columns = list(self.browser.elements(locator=self.COLUMN, parent=el))

            _name = _columns[1].text.strip()
            _created_at = _columns[2].text.strip()
            _created_by = _columns[3].text.strip()
            _istio_init_containers = _columns[5].text.strip()
            _istio_containers = _columns[6].text.strip()
            # TODO: fetch status information from GUI
            _items.append(WorkloadPod(
                        name=str(_name),
                        created_at=_created_at,
                        created_by=_created_by,
                        labels=self._get_labels(_columns[4]),
                        istio_init_containers=_istio_init_containers,
                        istio_containers=_istio_containers))
        return _items


class TableViewServices(TableViewAbstract):
    SERVICES_TEXT = 'Services'

    def open(self):
        tab = self.browser.element(locator=self.SERVICES_TAB.format(self.SERVICES_TEXT),
                                   parent=self.SERVICE_DETAILS_ROOT)
        try:
            self.browser.click(tab)
        finally:
            self.browser.click(tab)
        wait_displayed(self)

    @property
    def number(self):
        _vs_text = self.browser.text(locator=self.SERVICES_TAB.format(self.SERVICES_TEXT),
                                     parent=self.SERVICE_DETAILS_ROOT)
        return int(re.search(r'\d+', _vs_text).group())

    @property
    def items(self):
        self.open()

        _items = []
        for el in self.browser.elements(locator=self.ROWS.format(
            'service-tabs-pane-services'),
                                        parent=self.ROOT):
            _columns = list(self.browser.elements(locator=self.COLUMN, parent=el))

            _name = _columns[0].text.strip()
            _created_at = _columns[1].text.strip()
            _type = _columns[2].text.strip()
            _resource_version = _columns[4].text.strip()
            _ip = _columns[5].text.strip()
            _ports = _columns[6].text.strip()

            _items.append(ServiceDetails(
                        name=_name,
                        created_at=parse_from_ui(_created_at),
                        service_type=str(_type),
                        labels=self._get_labels(_columns[3]),
                        resource_version=str(_resource_version),
                        ip=str(_ip),
                        ports=str(_ports.replace('\n', ' '))))
        return _items


class TableViewDestinationServices(TableViewAbstract):
    DESTS_TEXT = 'Destination Services'
    ROWS = '//div[contains(@class, "card-pf")]\
    //div[contains(@class, "row-cards-pf")]\
    //div[contains(@class, "card-pf-body")]'
    DEST = './/div[contains(@class, "progress-description")]'
    COLUMN = './/li'

    def open(self):
        tab = self.browser.element(locator=self.SERVICES_TAB.format(self.DESTS_TEXT),
                                   parent=self.SERVICE_DETAILS_ROOT)
        try:
            self.browser.click(tab)
        finally:
            self.browser.click(tab)
        wait_displayed(self)

    @property
    def number(self):
        _wl_text = self.browser.text(locator=self.SERVICES_TAB.format(self.DESTS_TEXT),
                                     parent=self.SERVICE_DETAILS_ROOT)
        return int(re.search(r'\d+', _wl_text).group())

    @property
    def items(self):
        self.open()

        _items = []
        for el in self.browser.elements(locator=self.ROWS.format(
            'service-tabs-pane-destinationServices'),
                                        parent=self.ROOT):
            _from = self.browser.element(
                locator=self.DEST,
                parent=el).text.replace('From:', '').strip()
            _columns = list(self.browser.elements(locator=self.COLUMN, parent=el))
            for _column in _columns:
                # destination service object creation
                _service = DestinationService(
                    _from=_from,
                    name=_column.text.strip())
                # append this item to the final list
                _items.append(_service)
        return _items


class MetricsView(Widget):
    METRICS_TAB = '//ul[contains(@class, "nav-tabs-pf")]//li//a//div[contains(text(), "{}")]/..'
    ROOT = '//div[@id="basic-tabs"]'
    DROP_DOWN = '//*[contains(@class, "dropdown")]/*[@id="{}"]/..'

    filter = CheckBoxFilter(filter_name="Metrics Settings")
    destination = DropDown(locator=DROP_DOWN.format('metrics_filter_reporter'))
    duration = DropDown(locator=DROP_DOWN.format('metrics_filter_interval_duration'))
    interval = DropDown(locator=DROP_DOWN.format('metrics-refresh'))
    refresh = Button(locator='.//button//*[contains(@class, "fa-refresh")]')

    def __init__(self, parent, tab_name, locator=None, logger=None):
        Widget.__init__(self, parent, logger=logger)
        self.tab_name = tab_name
        if locator:
            self.locator = locator
        else:
            self.locator = self.ROOT

    def __locator__(self):
        return self.locator

    def open(self):
        tab = self.browser.element(locator=self.METRICS_TAB.format(self.tab_name),
                                   parent=self.ROOT)
        try:
            self.browser.click(tab)
        finally:
            self.browser.click(tab)
        wait_displayed(self)
