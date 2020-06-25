""" Update this doc"""
import re

from widgetastic.widget import Checkbox, TextInput, Widget, Text
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from kiali_qe.components.enums import (
    HelpMenuEnum,
    ApplicationVersionEnum,
    IstioConfigObjectType,
    HealthType,
    IstioConfigValidation,
    MeshWideTLSType,
    RoutingWizardTLS,
    TrafficType,
    GraphPageLayout,
    TLSMutualValues,
    ItemIconType,
    MutualTLSMode
)
from kiali_qe.entities import (
    TrafficItem,
    DeploymentStatus,
    AppRequests,
    Requests,
    ConfigurationStatus
)
from kiali_qe.entities.service import (
    Service,
    ServiceDetails,
    VirtualService,
    DestinationRule,
    SourceWorkload,
    VirtualServiceWeight,
    VirtualServiceGateway,
    ServiceHealth
)
from kiali_qe.entities.istio_config import (
    IstioConfig,
    Rule,
    IstioConfigDetails
)
from kiali_qe.entities.three_scale_config import (
    ThreeScaleHandler
)
from kiali_qe.entities.workload import (
    Workload,
    WorkloadDetails,
    WorkloadPod,
    WorkloadHealth
)
from kiali_qe.entities.applications import (
    Application,
    ApplicationDetails,
    AppWorkload,
    ApplicationHealth
)
from kiali_qe.entities.overview import Overview
from kiali_qe.utils.date import parse_from_rest
from time import sleep
from kiali_qe.utils.log import logger
from wait_for import wait_for
from kiali_qe.utils import (
    get_validation,
    to_linear_string,
    get_texts_of_elements
)


def wait_displayed(obj, timeout='10s'):
    wait_for(
        lambda: obj.is_displayed, timeout=timeout,
        delay=0.2, very_quiet=True, silent_failure=False)


def wait_not_displayed(obj, timeout='10s'):
    wait_for(
        lambda: not obj.is_displayed, timeout=timeout,
        delay=0.2, very_quiet=True, silent_failure=False)


def wait_to_spinner_disappear(browser, timeout='10s', very_quiet=True, silent_failure=False):
    def _is_disappeared(browser):
        count = len(browser.elements(locator='//*[@id="loading_kiali_spinner"]', parent='/'))
        logger.debug("Count of spinner elements: {}".format(count))
        return count == 0
    wait_for(
        _is_disappeared, func_args=[browser], timeout=timeout,
        delay=0.2, very_quiet=very_quiet, silent_failure=silent_failure)


POPOVER = './/*[contains(@class, "tippy-popper")]'


class Button(Widget):
    ROOT = '//button'

    def __init__(self, parent, locator=None, logger=None):
        Widget.__init__(self, parent, logger=logger)
        if locator:
            self.locator = locator
        else:
            self.locator = self.ROOT

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
    DEFAULT = '//span[(contains(@class, "pf-c-form__label-text") or ' + \
        'contains(@class, "pf-c-switch__label"))' + \
        ' and normalize-space(text())="{}"]' + \
        '/../..//*[contains(@class, "pf-c-switch__input")]'
    TEXT = '/../..//*[contains(@class, "control-label")]'

    def __init__(self, parent, label=None, locator=None, logger=None):
        Button.__init__(self, parent,
                        locator=locator if locator else self.DEFAULT.format(label),
                        logger=logger)

    @property
    def is_on(self):
        return Checkbox(locator='../input', parent=self).selected

    def on(self):
        if not self.is_on:
            self.click()

    def off(self):
        if self.is_on:
            self.click()

    @property
    def text(self):
        return self.browser.text(parent=self, locator=self.locator + self.TEXT)


class FilterInput(Widget):
    ROOT = '//input[@type="text"]'
    CLEAR_BUTTON = '/following-sibling::button[contains(@class, "pf-m-control")]'

    def __init__(self, parent, locator=None, logger=None):
        Widget.__init__(self, parent, logger=logger)
        if locator:
            self.locator = locator
        else:
            self.locator = self.ROOT
        self._input = TextInput(parent=self, locator=self.locator)
        self._clear_button = Button(parent=self, locator=self.locator + self.CLEAR_BUTTON)

    def __locator__(self):
        return self.locator

    @property
    def is_empty(self):
        return self.text == ''

    @property
    def is_clear_displayed(self):
        return self.browser.is_displayed(self._clear_button)

    def clear(self):
        if not self.is_empty:
            self.browser.click(self._clear_button)
            return True
        return False

    def fill(self, text):
        self._input.fill(text)
        self.browser.send_keys(Keys.ENTER, self._input)

    @property
    def text(self):
        return self._input.value


class Notifications(Widget):
    ROOT = '//*[contains(@class, "pf-c-form__helper-text")]'

    def __init__(self, parent, locator=None, logger=None):
        logger.debug('Loading notifications widget')
        Widget.__init__(self, parent, logger=logger)
        if locator:
            self.locator = locator
        else:
            self.locator = self.ROOT

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
    ROOT = '//*[contains(@class, "pf-c-select__menu")]/div[contains(@class, "pf-c-select")]/../..'
    SELECT_BUTTON = '//*[contains(@class, "pf-c-select__toggle")]'
    OPTIONS_LIST = ('//*[contains(@class, "pf-c-select__menu")]'
                    '//*[not(contains(@class, "disabled"))]//*[contains(@role, "option")]')
    DISABLED_OPTIONS_LIST = ('//*[contains(@class, "pf-c-select__menu")]'
                             '//*[contains(@class, "disabled")]//*[contains(@role, "option")]')
    OPTION = ('//*[contains(@class, "pf-c-select__menu")]'
              '//*[contains(@role, "option") and text()="{}"]')

    def __init__(self, parent, force_open=True, locator=None, logger=None):
        Widget.__init__(self, parent, logger=logger)
        self._force_open = force_open
        if locator:
            self.locator = locator
        else:
            self.locator = self.ROOT

    def __locator__(self):
        return self.locator

    def _close(self):
        els = self.browser.elements(locator=self.locator + self.SELECT_BUTTON, parent=self)
        # TODO check if opened in PF4
        # if len(els) and els[0].get_attribute('aria-expanded') == 'true':
        self.browser.click(els[0])

    def _open(self):
        el = self.browser.element(locator=self.locator + self.SELECT_BUTTON, parent=self)
        # TODO check if opened in PF4
        # if el.get_attribute('aria-expanded') == 'false':
        wait_displayed(el)
        self.browser.click(el)

    def _update_options(self, locator):
        options = []
        if self._force_open:
            self._open()
        for el in self.browser.elements(locator=self.locator + locator, parent=self):
            # on filter drop down, title comes in to options list.
            # Here it will be removed
            if self.browser.get_attribute('title', el).startswith('Filter by'):
                continue
            options.append(self.browser.text(el))
        if self._force_open:
            self._close()
        return options

    @property
    def options(self):
        options = []

        # sometime options are not displayed, needs to do retry
        for retry in range(1, 3):  # @UnusedVariable
            options = self._update_options(self.OPTIONS_LIST)
            if len(options) > 0:
                break
        return options

    @property
    def disabled_options(self):
        options = []

        # sometime options are not displayed, needs to do retry
        for retry in range(1, 3):  # @UnusedVariable
            options = self._update_options(self.DISABLED_OPTIONS_LIST)
            if len(options) > 0:
                break
        return options

    def select(self, option):
        self._open()
        # TODO better approach
        try:
            self.browser.element(locator=self.locator+self.OPTION.format(option)).click()
        except NoSuchElementException:
            try:
                self.browser.element(self.OPTION.format(option), parent=self.locator).click()
            except NoSuchElementException:
                for element in self.browser.elements(self.OPTIONS_LIST, parent=self.locator):
                    try:
                        if element.text == option:
                            element.click()
                    # in some of dropdown, when we select options page reloads.
                    # reload leads this issue
                    except StaleElementReferenceException:
                        pass
        wait_to_spinner_disappear(self.browser)

    @property
    def selected(self):
        return self.browser.text(self.browser.element(self.SELECT_BUTTON, parent=self.locator))


class MenuDropDown(DropDown):
    ROOT = '//*[contains(@class, "pf-l-toolbar")]'
    SELECT_BUTTON = '//*[contains(@class, "pf-c-dropdown__toggle")]'
    OPTIONS_LIST = ('//*[contains(@class, "pf-c-dropdown__menu")]//*[contains(@role, "menuitem")'
                    ' and not(contains(@class, "pf-m-disabled"))]')
    OPTION = ('//*[contains(@class, "pf-c-dropdown__menu")]'
              '//*[contains(@role, "menuitem") and text()="{}"]')
    DISABLED_OPTIONS_LIST = ('/..//*[contains(@class, "pf-c-dropdown__menu")]//*'
                             '[contains(@role, "menuitem") and contains(@class, "pf-m-disabled")]')

    def __init__(self, parent, force_open=True, locator=None, logger=None, select_button=None):
        DropDown.__init__(self, parent=parent,
                          force_open=force_open,
                          locator=locator,
                          logger=logger)
        if select_button or select_button == '':
            self.SELECT_BUTTON = select_button


class ActionsDropDown(DropDown):
    ROOT = '//*[contains(@class, "pf-l-toolbar")]'
    SELECT_BUTTON = '//*[contains(@class, "pf-c-dropdown__toggle")]'
    OPTIONS_LIST = ('//*[contains(@class, "pf-c-dropdown__menu")]//*[contains(@role, "menuitem")]'
                    '//button[not(contains(@class, "pf-m-disabled"))]')
    OPTION = ('//*[contains(@class, "pf-c-dropdown__menu")]'
              '//*[contains(@role, "menuitem")]//*[text()="{}"]')
    DISABLED_OPTIONS_LIST = ('/..//*[contains(@class, "pf-c-dropdown__menu")]//*'
                             '[contains(@role, "menuitem")]'
                             '//button[contains(@class, "pf-m-disabled")]')

    def __init__(self, parent, force_open=True, locator=None, logger=None, select_button=None):
        DropDown.__init__(self, parent=parent,
                          force_open=force_open,
                          locator=locator,
                          logger=logger)
        if select_button or select_button == '':
            self.SELECT_BUTTON = select_button


class ItemDropDown(DropDown):
    ROOT = '//*[contains(@class, "pf-c-select")]'
    SELECT_BUTTON = '//*[contains(@class, "pf-c-select__toggle")]'
    OPTIONS_LIST = '/..//*[contains(@role, "option")]'
    OPTION = ('/..//*[contains(@role, "option") and text()="{}"]')

    def __init__(self, parent, force_open=True, locator=None, logger=None, select_button=None):
        DropDown.__init__(self, parent=parent,
                          force_open=force_open,
                          locator=locator,
                          logger=logger)
        if select_button or select_button == '':
            self.SELECT_BUTTON = select_button


class TypeDropDown(DropDown):
    ROOT = '//*[contains(@class, "pf-c-select")]'
    SELECT_BUTTON = '//*[contains(@class, "pf-c-select__toggle")]'
    OPTIONS_LIST = '/..//li/button[contains(@role, "option")]'
    OPTION = ('//li//button[contains(@role, "option") and contains(text(), "{}")]')

    def __init__(self, parent, force_open=True, locator=None, logger=None, select_button=None):
        DropDown.__init__(self, parent=parent,
                          force_open=force_open,
                          locator=locator,
                          logger=logger)
        if select_button or select_button == '':
            self.SELECT_BUTTON = select_button


class SelectDropDown(DropDown):
    SELECT_BUTTON = '//select[contains(@class, "pf-c-form-control")]'
    OPTIONS_LIST = ('//option')
    OPTION = ('//*[text()="{}"]')

    def __init__(self, parent, force_open=True, locator=None, logger=None, select_button=None):
        DropDown.__init__(self, parent=parent,
                          force_open=force_open,
                          locator=locator,
                          logger=logger)
        if select_button or select_button == '':
            self.SELECT_BUTTON = select_button


class FilterDropDown(DropDown):
    SELECT_BUTTON = ''
    OPTIONS_LIST = ('//option')
    OPTION = ('//*[text()="{}"]')

    def __init__(self, parent, force_open=True, locator=None, logger=None):
        DropDown.__init__(self, parent=parent,
                          force_open=force_open,
                          locator=locator,
                          logger=logger)


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
    ROOT = '//*[contains(@class, "pf-c-select")]/../button/svg/../..'

    def __init__(self, parent, locator=None, logger=None):
        Widget.__init__(self, parent, logger=logger)
        if locator:
            self.locator = locator
        else:
            self.locator = self.ROOT
        self._drop_down = TypeDropDown(
            parent=self, locator=self.locator,
            select_button='//*[contains(@class, "pf-c-select")]')
        self._sort = Sort(
            parent=self,
            locator=self.locator + '/../button/svg/..')

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


class SortBar(Widget):
    ROOT = ('//*[contains(@class, "pf-c-table")]'
            '//button/*[contains(@class, "pf-c-table__sort-indicator")]/../../..')
    BUTTONS = ('//button[contains(@class, "pf-c-button")]'
               '/*[contains(@class, "pf-c-table__sort-indicator")]/..')
    BUTTON = '//button[contains(@class, "pf-c-button") and text()="{}"]'

    def __init__(self, parent, locator=None, logger=None):
        Widget.__init__(self, parent, logger=logger)
        if locator:
            self.locator = locator
        else:
            self.locator = self.ROOT

    def __locator__(self):
        return self.locator

    @property
    def options(self):
        return [el.text for el in self.browser.elements(locator=self.BUTTONS, parent=self.locator)]

    def select(self, option, is_ascending=None):
        button = self.browser.element(parent=self, locator=self.BUTTON.format(option.text))
        self.browser.click(button)
        if is_ascending is not None and not is_ascending:
            # second click orders descending
            self.browser.click(button)


class FilterList(Widget):
    ROOT = './/*[contains(@class, "pf-l-toolbar")]'
    ITEMS = '//ul[contains(@class, "pf-c-chip-group") and contains(@class, "pf-m-toolbar")]/li'
    CLEAR = (ITEMS + '//*[contains(text(), "{}")]/..//*[contains(@aria-label, "close")]')
    CLEAR_ALL = '//a[text()="Clear All Filters"]'

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
                # TODO with value as it can be cut off in page
                self.browser.element(parent=self, locator=self.CLEAR.format(key)))
        except NoSuchElementException:
            pass

    @property
    def active_filters(self):
        _filters = []
        if not self.is_displayed:
            return _filters
        for el in self.browser.elements(parent=self, locator=self.ITEMS, force_check_safe=True):
            _values = el.text.split('\n')
            # in the case of multiple values per key
            i = 1
            while i < len(_values):
                _filters.append({'name': _values[0].strip(), 'value': _values[i].strip()})
                i += 1
        return _filters


class Filter(Widget):
    ROOT = '//*[contains(@class, "pf-l-toolbar")]//*[contains(@class, "pf-l-toolbar__section")]'
    FILTER_DROPDOWN = '//select[contains(@aria-label, "filter_select_type")]'
    VALUE_INPUT = './/input'
    VALUE_DROPDOWN = '//select[contains(@aria-label, "filter_select_value")]'
    LABEL_OPERATION_DROPDOWN = '//div[contains(@class, "pf-u-mr-md")]' + \
        '//select[contains(@aria-label, "filter_select_value")]'

    def __init__(self, parent, locator=None, logger=None):
        Widget.__init__(self, parent, logger=logger)
        if locator:
            self.locator = locator
        else:
            self.locator = self.ROOT
        self._filter = FilterDropDown(parent=self,
                                      locator=self.locator + self.FILTER_DROPDOWN)
        self._filter_list = FilterList(parent=self.parent)
        self._label_operation = FilterDropDown(
            parent=self,
            locator=self.locator + self.LABEL_OPERATION_DROPDOWN)

    def __locator__(self):
        return self.locator

    @property
    def filters(self):
        return self._filter.options

    def filter_options(self, filter_name):
        self.select(filter_name)
        if len(self.browser.elements(parent=self, locator=self.VALUE_DROPDOWN)):
            option_dropdown = FilterDropDown(
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
            if self.browser.browser_type == 'firefox':
                self.browser.send_keys(Keys.ENTER, _input)
        elif len(self.browser.elements(parent=self, locator=self.VALUE_DROPDOWN)):
            _dropdown = FilterDropDown(parent=self, locator=self.VALUE_DROPDOWN)
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


class Actions(Widget):
    ROOT = '//*[contains(@class, "pf-c-page__main")]' + \
        '//*[contains(@class, "pf-c-page__main-section")]'
    WIZARD_ROOT = '//*[contains(@class, "pf-c-modal-box")]'
    DIALOG_ROOT = '//*[@role="dialog"]'
    ACTIONS_DROPDOWN = '//div[contains(@class, "pf-c-dropdown")]//span[text()="Actions"]/../..'
    RULE_ACTIONS = '//div[contains(@class, "pf-c-dropdown")]//button[@aria-label="Actions"]'
    TLS_DROPDOWN = '//div[contains(@class, "pf-c-form__group")]//select[@id="advanced-tls"]'
    LOAD_BALANCER_TYPE_DROPDOWN = '//div[contains(@class, "pf-c-form__group")]'\
        '//select[@id="trafficPolicy-lb"]'
    INCLUDE_MESH_GATEWAY = '//label[contains(text(), "Include")]/..//input[@type="checkbox"]'
    SHOW_ADVANCED_OPTIONS = '//span[text()="Show Advanced Options"]/..'
    SHOW_CREATE_HANDLER = '//span[text()="Show Create Handler"]/..'
    EXPANDABLE_CONTENT = '//div[@class="pf-c-expandable__content"]'
    CREATE_BUTTON = './/button[text()="Create"]'
    UPDATE_BUTTON = './/button[text()="Update"]'
    SELECT_BUTTON = './/button[text()="SELECT"]'
    REMOVE_RULE = 'Remove Rule'
    ADD_RULE_BUTTON = './/button[text()="Add Rule"]'
    DELETE_ALL_TRAFFIC_ROUTING = 'Delete ALL Traffic Routing'
    CREATE_MATCHING_ROUTING = 'Create Matching Routing'
    UPDATE_MATCHING_ROUTING = 'Update Matching Routing'
    CREATE_WEIGHTED_ROUTING = 'Create Weighted Routing'
    UPDATE_WEIGHTED_ROUTING = 'Update Weighted Routing'
    SUSPEND_TRAFFIC = 'Suspend Traffic'
    UPDATE_SUSPENDED_TRAFFIC = 'Update Suspended Traffic'
    CREATE_3SCALE_RULE = 'Add 3scale API Management Rule'
    DELETE_3SCALE_RULE = 'Delete 3Scale API Management Rule'
    UPDATE_3SCALE_RULE = 'Update 3scale API Management Rule'

    def __init__(self, parent, locator=None, logger=None):
        Widget.__init__(self, parent, logger=logger)
        if locator:
            self.locator = locator
        else:
            self.locator = self.ROOT
        self._actions = ActionsDropDown(parent=self, locator=self.locator + self.ACTIONS_DROPDOWN,
                                        select_button='', force_open=True)
        self._rule_actions = MenuDropDown(parent=self, locator=self.RULE_ACTIONS,
                                          select_button='', force_open=True)
        self._tls = SelectDropDown(parent=self, locator=self.TLS_DROPDOWN, select_button='')
        self._client_certificate = TextInput(parent=self,
                                             locator='//input[@id="clientCertificate"]')
        self._private_key = TextInput(parent=self, locator='//input[@id="privateKey"]')
        self._ca_certificate = TextInput(parent=self, locator='//input[@id="caCertificates"]')
        self._loadbalancer_switch = ButtonSwitch(parent=self, label="Add LoadBalancer")
        self._loadbalancer_type = SelectDropDown(
            parent=self, locator=self.LOAD_BALANCER_TYPE_DROPDOWN,
            select_button='')
        self._gateway_switch = ButtonSwitch(parent=self, label="Add Gateway")
        self._include_mesh_gateway = Checkbox(locator=self.INCLUDE_MESH_GATEWAY, parent=self)

    def __locator__(self):
        return self.locator

    @property
    def is_displayed(self):
        return self.browser.is_displayed(self.WIZARD_ROOT) \
            or self.browser.is_displayed(self.DIALOG_ROOT)

    @property
    def actions(self):
        return self._actions.options

    @property
    def disabled_actions(self):
        return self._actions.disabled_options

    def select(self, action):
        self._actions.select(action)

    def is_delete_disabled(self):
        return self.DELETE_ALL_TRAFFIC_ROUTING in self.disabled_actions

    def is_delete_3scale_disabled(self):
        return self.DELETE_3SCALE_RULE in self.disabled_actions

    def is_create_3scale_disabled(self):
        return self.CREATE_3SCALE_RULE in self.disabled_actions

    def is_create_3scale_enabled(self):
        return self.CREATE_3SCALE_RULE in self.actions

    def is_update_3scale_disabled(self):
        return self.UPDATE_3SCALE_RULE in self.disabled_actions

    def is_update_3scale_enabled(self):
        return self.UPDATE_3SCALE_RULE in self.actions

    def is_create_weighted_disabled(self):
        return self.CREATE_WEIGHTED_ROUTING in self.disabled_actions

    def is_create_matching_disabled(self):
        return self.CREATE_MATCHING_ROUTING in self.disabled_actions

    def is_suspend_disabled(self):
        return self.SUSPEND_TRAFFIC in self.disabled_actions

    def is_create_weighted_enabled(self):
        return self.CREATE_WEIGHTED_ROUTING in self.actions

    def is_create_matching_enabled(self):
        return self.CREATE_MATCHING_ROUTING in self.actions

    def is_suspend_enabled(self):
        return self.SUSPEND_TRAFFIC in self.actions

    def is_update_weighted_enabled(self):
        return self.UPDATE_WEIGHTED_ROUTING in self.actions

    def is_update_matching_enabled(self):
        return self.UPDATE_MATCHING_ROUTING in self.actions

    def is_update_suspended_enabled(self):
        return self.UPDATE_SUSPENDED_TRAFFIC in self.actions

    def delete_all_routing(self):
        if self.is_delete_disabled():
            return False
        else:
            self.select(self.DELETE_ALL_TRAFFIC_ROUTING)
            self.browser.click(self.browser.element(
                parent=self.DIALOG_ROOT,
                locator=('.//button[text()="Delete"]')))
            wait_to_spinner_disappear(self.browser)
            return True

    def create_weighted_routing(self, tls=RoutingWizardTLS.DISABLE,
                                load_balancer=False,
                                load_balancer_type=None,
                                gateway=False,
                                include_mesh_gateway=False,
                                skip_advanced=False):
        if self.is_create_weighted_disabled():
            return False
        else:
            self.select(self.CREATE_WEIGHTED_ROUTING)
            self.advanced_options(tls=tls, load_balancer=load_balancer,
                                  load_balancer_type=load_balancer_type,
                                  gateway=gateway,
                                  include_mesh_gateway=include_mesh_gateway,
                                  skip_advanced=skip_advanced)
            self.browser.click(self.browser.element(
                parent=self.WIZARD_ROOT,
                locator=(self.CREATE_BUTTON)))
            wait_not_displayed(self)
            # wait to Spinner disappear
            wait_to_spinner_disappear(self.browser)
            return True

    def update_weighted_routing(self, tls=RoutingWizardTLS.DISABLE,
                                load_balancer=False,
                                load_balancer_type=None,
                                gateway=False,
                                include_mesh_gateway=False,
                                skip_advanced=False):
        if self.is_update_weighted_enabled():
            self.select(self.UPDATE_WEIGHTED_ROUTING)
            self.advanced_options(tls=tls, load_balancer=load_balancer,
                                  load_balancer_type=load_balancer_type,
                                  gateway=gateway,
                                  include_mesh_gateway=include_mesh_gateway,
                                  skip_advanced=skip_advanced)
            self.browser.click(self.browser.element(
                parent=self.WIZARD_ROOT,
                locator=(self.UPDATE_BUTTON)))
            wait_not_displayed(self)
            # wait to Spinner disappear
            wait_to_spinner_disappear(self.browser)
            return True
        else:
            return False

    def create_matching_routing(self, tls=RoutingWizardTLS.DISABLE,
                                load_balancer=False,
                                load_balancer_type=None,
                                gateway=False,
                                include_mesh_gateway=False,
                                skip_advanced=False):
        if self.is_create_matching_disabled():
            return False
        else:
            self.select(self.CREATE_MATCHING_ROUTING)
            self.advanced_options(tls=tls, load_balancer=load_balancer,
                                  load_balancer_type=load_balancer_type,
                                  gateway=gateway,
                                  include_mesh_gateway=include_mesh_gateway,
                                  skip_advanced=skip_advanced)
            self.browser.click(self.browser.element(
                parent=self.WIZARD_ROOT,
                locator=(self.ADD_RULE_BUTTON)))
            create_button = self.browser.element(
                parent=self.WIZARD_ROOT,
                locator=(self.CREATE_BUTTON))
            wait_displayed(create_button)
            self.browser.click(create_button)
            wait_not_displayed(self)
            # wait to Spinner disappear
            wait_to_spinner_disappear(self.browser)
            return True

    def update_matching_routing(self, tls=RoutingWizardTLS.DISABLE,
                                load_balancer=False,
                                load_balancer_type=None,
                                gateway=False,
                                include_mesh_gateway=False,
                                skip_advanced=False):
        if self.is_update_matching_enabled():
            self.select(self.UPDATE_MATCHING_ROUTING)
            self.advanced_options(tls=tls, load_balancer=load_balancer,
                                  load_balancer_type=load_balancer_type,
                                  gateway=gateway,
                                  include_mesh_gateway=include_mesh_gateway,
                                  skip_advanced=skip_advanced)
            self._rule_actions.select(self.REMOVE_RULE)
            self.browser.click(self.browser.element(
                parent=self.WIZARD_ROOT,
                locator=(self.ADD_RULE_BUTTON)))
            update_button = self.browser.element(
                parent=self.WIZARD_ROOT,
                locator=(self.UPDATE_BUTTON))
            wait_displayed(update_button)
            self.browser.click(update_button)
            wait_not_displayed(self)
            # wait to Spinner disappear
            wait_to_spinner_disappear(self.browser)
            return True
        else:
            return False

    def suspend_traffic(self, tls=RoutingWizardTLS.DISABLE, load_balancer=False,
                        load_balancer_type=None,
                        gateway=False,
                        include_mesh_gateway=False,
                        skip_advanced=False):
        if self.is_suspend_disabled():
            return False
        else:
            self.select(self.SUSPEND_TRAFFIC)
            self.advanced_options(tls=tls, load_balancer=load_balancer,
                                  load_balancer_type=load_balancer_type,
                                  gateway=gateway,
                                  include_mesh_gateway=include_mesh_gateway,
                                  skip_advanced=skip_advanced)
            self.browser.click(self.browser.element(
                parent=self.WIZARD_ROOT,
                locator=(self.CREATE_BUTTON)))
            wait_not_displayed(self)
            # wait to Spinner disappear
            wait_to_spinner_disappear(self.browser)
            return True

    def update_suspended_traffic(self, tls=RoutingWizardTLS.DISABLE,
                                 load_balancer=False,
                                 load_balancer_type=None,
                                 gateway=False,
                                 include_mesh_gateway=False,
                                 skip_advanced=False):
        if self.is_update_suspended_enabled():
            self.select(self.UPDATE_SUSPENDED_TRAFFIC)
            self.advanced_options(tls=tls, load_balancer=load_balancer,
                                  load_balancer_type=load_balancer_type,
                                  gateway=gateway,
                                  include_mesh_gateway=include_mesh_gateway,
                                  skip_advanced=skip_advanced)
            self.browser.click(self.browser.element(
                parent=self.WIZARD_ROOT,
                locator=(self.UPDATE_BUTTON)))
            wait_not_displayed(self)
            # wait to Spinner disappear
            wait_to_spinner_disappear(self.browser)
            return True
        else:
            return False

    def advanced_options(self, tls=RoutingWizardTLS.DISABLE, load_balancer=False,
                         load_balancer_type=None,
                         gateway=False,
                         include_mesh_gateway=False,
                         skip_advanced=False):
        """
        Adds Advanced Options to Wizard.
        """
        if skip_advanced:
            return
        self.browser.click(Button(parent=self.parent, locator=self.SHOW_ADVANCED_OPTIONS))
        wait_displayed(self._tls)
        if tls:
            self._tls.select(tls.text)
            if tls == RoutingWizardTLS.MUTUAL:
                wait_displayed(self._client_certificate)
                self._client_certificate.fill(TLSMutualValues.CLIENT_CERT.text)
                self._private_key.fill(TLSMutualValues.PRIVATE_KEY.text)
                self._ca_certificate.fill(TLSMutualValues.CA_CERT.text)
        if load_balancer and load_balancer_type:
            self._loadbalancer_switch.on()
            if load_balancer_type:
                wait_displayed(self._loadbalancer_type)
                self._loadbalancer_type.select(load_balancer_type.text)
        else:
            self._loadbalancer_switch.off()
        if gateway:
            self._gateway_switch.on()
            wait_displayed(self._include_mesh_gateway)
            self._include_mesh_gateway.fill(include_mesh_gateway)
        else:
            self._gateway_switch.off()

    def create_3scale_rule(self, handler_name):
        if self.is_create_3scale_disabled():
            return False
        else:
            self.select(self.CREATE_3SCALE_RULE)
            self.select_three_scale_handler(handler_name)
            create_button = self.browser.element(
                parent=self.WIZARD_ROOT,
                locator=(self.CREATE_BUTTON))
            wait_displayed(create_button)
            self.browser.click(create_button)
            wait_not_displayed(self)
            # wait to Spinner disappear
            wait_to_spinner_disappear(self.browser)
            return True

    def update_3scale_rule(self, handler_name):
        if self.is_update_3scale_enabled():
            self.select(self.UPDATE_3SCALE_RULE)
            self.select_three_scale_handler(handler_name)
            update_button = self.browser.element(
                parent=self.WIZARD_ROOT,
                locator=(self.UPDATE_BUTTON))
            wait_displayed(update_button)
            self.browser.click(update_button)
            wait_not_displayed(self)
            # wait to Spinner disappear
            wait_to_spinner_disappear(self.browser)
            return True
        else:
            return False

    def delete_3scale_rule(self):
        if self.is_delete_3scale_disabled():
            return False
        else:
            self.select(self.DELETE_3SCALE_RULE)
            self.browser.click(self.browser.element(
                parent=self.DIALOG_ROOT,
                locator=('.//button[text()="Delete"]')))
            wait_to_spinner_disappear(self.browser)
            return True

    def select_three_scale_handler(self, handler_name):
        try:
            wait_to_spinner_disappear(self.browser)
            self.browser.click(Button(
                parent=self.parent,
                locator='//li//*[contains(text(), "{}")]'
                        '/../../..//button[contains(text(), "Select")]'.format(
                                        handler_name)))
        except (NoSuchElementException, StaleElementReferenceException):
            # skip error if button does not exist
            pass


class ConfigActions(Actions):
    ISTIO_RESOURCE = '//div[contains(@class, "pf-c-form__group")]//select[@id="istio-resource"]'
    POLICY = '//div[contains(@class, "pf-c-form__group")]//select[@id="rules-form"]'
    POLICY_ACTION = '//div[contains(@class, "pf-c-form__group")]//select[@id="action-form"]'
    MTLS_MODE = '//div[contains(@class, "pf-c-form__group")]//select[@id="mutualTls"]'
    JWT_FIELD = '//div[contains(@class, "pf-c-form__group")]//select[@id="addNewJwtField"]'
    PORT_MTLS_MODE = '//div[contains(@class, "pf-c-form__group")]' +\
        '//table//select[@name="addPortMtlsMode"]'
    ADD_VALUE = '//div[contains(@class, "pf-c-form__group")]//input[@id="addNewValues"]'
    ADD_PORT = '//div[contains(@class, "pf-c-form__group")]//input[@id="addPortNumber"]'
    ADD_VALUE_BUTTON = '//div[contains(@class, "pf-c-form__group")]' +\
        '//table//button[contains(@class, "pf-m-link")]'
    ADD_RULE_BUTTON = '//div[contains(@class, "pf-c-form__group")]' +\
        '/div/button[contains(@class, "pf-m-link")]'
    CONFIG_CREATE_ROOT = '//*[contains(@class, "pf-c-form")]'
    CREATE_ISTIO_CONFIG = 'Create New Istio Config'
    ADD_SERVER_BUTTON = './/button[text()="Add Server"]'
    ADD_PORT_MTLS_BUTTON = './/button[text()="Add Port MTLS"]'
    ADD_EGRESS_HOST_BUTTON = './/button[text()="Add Egress Host"]'

    def __init__(self, parent, locator=None, logger=None):
        Actions.__init__(self, parent, logger=logger)
        if locator:
            self.locator = locator
        else:
            self.locator = self.ROOT
        self._istio_resource = SelectDropDown(
            parent=self, locator=self.ISTIO_RESOURCE, select_button='')
        self._name = TextInput(parent=self,
                               locator='//input[@id="name"]')
        self._hosts = TextInput(parent=self, locator='//input[@id="addHosts"]')
        self._egress_host = TextInput(parent=self, locator='//input[@id="addEgressHost"]')
        self._workloadselector_switch = ButtonSwitch(parent=self, label="Add Workload Selector")
        self._jwtrules_switch = ButtonSwitch(parent=self, label="Add JWT Rules")
        self._portmtls_switch = ButtonSwitch(parent=self, label="Add Port MTLS")
        self._labels = TextInput(parent=self, locator='//input[@id="gwHosts"]')
        self._policy = SelectDropDown(parent=self, locator=self.POLICY, select_button='')
        self._policy_action = SelectDropDown(parent=self,
                                             locator=self.POLICY_ACTION, select_button='')
        self._mtls_mode = SelectDropDown(parent=self, locator=self.MTLS_MODE, select_button='')
        self._jwt_field = SelectDropDown(parent=self, locator=self.JWT_FIELD, select_button='')
        self._port_mtls_mode = SelectDropDown(parent=self,
                                              locator=self.PORT_MTLS_MODE,
                                              select_button='')
        self._add_value = TextInput(parent=self, locator=self.ADD_VALUE)
        self._add_port = TextInput(parent=self, locator=self.ADD_PORT)

    def create_istio_config_gateway(self, name, hosts):
        wait_to_spinner_disappear(self.browser)
        self.select(self.CREATE_ISTIO_CONFIG)
        self._istio_resource.select(IstioConfigObjectType.GATEWAY.text)
        self._name.fill(name)
        self._hosts.fill(hosts)
        add_server_button = self.browser.element(
            parent=self.CONFIG_CREATE_ROOT,
            locator=(self.ADD_SERVER_BUTTON))
        wait_displayed(add_server_button)
        self.browser.click(add_server_button)
        create_button = self.browser.element(
            parent=self.CONFIG_CREATE_ROOT,
            locator=(self.CREATE_BUTTON))
        wait_displayed(create_button)
        self.browser.click(create_button)
        # wait to Spinner disappear
        wait_to_spinner_disappear(self.browser)
        return True

    def create_istio_config_sidecar(self, name, egress_host, labels=None):
        self.select(self.CREATE_ISTIO_CONFIG)
        self._istio_resource.select(IstioConfigObjectType.SIDECAR.text)
        self._name.fill(name)
        self._egress_host.fill(egress_host)
        self._add_workload_selector(labels)
        add_egress_button = self.browser.element(
            parent=self.CONFIG_CREATE_ROOT,
            locator=(self.ADD_EGRESS_HOST_BUTTON))
        wait_displayed(add_egress_button)
        self.browser.click(add_egress_button)
        create_button = self.browser.element(
            parent=self.CONFIG_CREATE_ROOT,
            locator=(self.CREATE_BUTTON))
        wait_displayed(create_button)
        self.browser.click(create_button)
        # wait to Spinner disappear
        wait_to_spinner_disappear(self.browser)
        return True

    def create_istio_config_authpolicy(self, name, policy, labels=None, policy_action=None):
        self.select(self.CREATE_ISTIO_CONFIG)
        wait_displayed(self._istio_resource)
        self._istio_resource.select(IstioConfigObjectType.AUTHORIZATION_POLICY.text)
        self._name.fill(name)
        self._policy.select(policy)
        self._add_workload_selector(labels)
        if policy_action:
            self._policy_action.select(policy_action)
        create_button = self.browser.element(
            parent=self.CONFIG_CREATE_ROOT,
            locator=(self.CREATE_BUTTON))
        wait_displayed(create_button)
        if create_button.get_attribute("disabled"):
            return False
        self.browser.click(create_button)
        # wait to Spinner disappear
        wait_to_spinner_disappear(self.browser)
        return True

    def create_istio_config_peerauth(self, name, labels=None,
                                     mtls_mode=MutualTLSMode.UNSET, mtls_ports={}):
        self.select(self.CREATE_ISTIO_CONFIG)
        wait_displayed(self._istio_resource)
        self._istio_resource.select(IstioConfigObjectType.PEER_AUTHENTICATION.text)
        self._name.fill(name)
        self._mtls_mode.select(mtls_mode)
        self._add_workload_selector(labels)
        if mtls_ports:
            self._portmtls_switch.on()
            for _key, _value in mtls_ports.items():
                self._add_port.fill(_key)
                self._port_mtls_mode.select(_value)
                add_value_button = self.browser.element(
                    parent=self.CONFIG_CREATE_ROOT,
                    locator=(self.ADD_PORT_MTLS_BUTTON))
                self.browser.click(add_value_button)
        create_button = self.browser.element(
            parent=self.CONFIG_CREATE_ROOT,
            locator=(self.CREATE_BUTTON))
        wait_displayed(create_button)
        if create_button.get_attribute("disabled"):
            return False
        self.browser.click(create_button)
        # wait to Spinner disappear
        wait_to_spinner_disappear(self.browser)
        return True

    def create_istio_config_requestauth(self, name, labels=None, jwt_rules={}):
        self.select(self.CREATE_ISTIO_CONFIG)
        wait_displayed(self._istio_resource)
        self._istio_resource.select(IstioConfigObjectType.REQUEST_AUTHENTICATION.text)
        self._name.fill(name)
        self._add_workload_selector(labels)
        if jwt_rules:
            self._jwtrules_switch.on()
            for _key, _value in jwt_rules.items():
                self._jwt_field.select(_key)
                self._add_value.fill(_value)
                add_value_button = self.browser.element(
                    parent=self.CONFIG_CREATE_ROOT,
                    locator=(self.ADD_VALUE_BUTTON))
                self.browser.click(add_value_button)
            add_rule_button = self.browser.element(
                parent=self.CONFIG_CREATE_ROOT,
                locator=(self.ADD_RULE_BUTTON))
            if add_rule_button.get_attribute("disabled"):
                return False
            self.browser.click(add_rule_button)
        create_button = self.browser.element(
            parent=self.CONFIG_CREATE_ROOT,
            locator=(self.CREATE_BUTTON))
        wait_displayed(create_button)
        if create_button.get_attribute("disabled"):
            return False
        self.browser.click(create_button)
        # wait to Spinner disappear
        wait_to_spinner_disappear(self.browser)
        return True

    def _add_workload_selector(self, labels=None):
        if labels:
            self._workloadselector_switch.on()
            self._labels.fill(labels)


class Traces(Widget):
    ROOT = '//section[contains(@class, "pf-tab-section-3-basic-tabs")]'
    SEARCH_TRACES_BUTTON = './/button[contains(@aria-label, "SearchTraces")]'
    SHOW_HIDE_OPTIONS = '//button[contains(@class, "pf-c-expandable__toggle")]/span[text()="{}"]/..'

    def __init__(self, parent, locator=None, logger=None):
        Widget.__init__(self, parent, logger=logger)
        if locator:
            self.locator = locator
        else:
            self.locator = self.ROOT
        self._search_traces = Button(parent=self, locator=self.SEARCH_TRACES_BUTTON)
        self._show_advanced_options = Button(
            parent=self,
            locator=self.SHOW_HIDE_OPTIONS.format('Show Advanced Options'))
        self._hide_advanced_options = Button(
            parent=self,
            locator=self.SHOW_HIDE_OPTIONS.format('Hide Advanced Options'))
        self._service_drop_down = SelectDropDown(
            parent=self, locator=self.locator)

    @property
    def is_oc_login_displayed(self):
        return len(
            self.browser.elements(
                locator='//button[text()="Log in with OpenShift"]', parent='iframe')) > 0

    @property
    def has_no_results(self):
        return len(
            self.browser.elements(
                locator='//div[contains(@class, "pf-c-empty-state")]', parent=self.ROOT)) > 0

    @property
    def has_results(self):
        return len(
            self.browser.elements(
                locator='//div[contains(@class, "pf-c-chart")]',
                parent=self.ROOT)) > 0

    def search_traces(self, service_name):
        self._service_drop_down.select(service_name)
        if self._show_advanced_options.is_displayed:
            self.browser.click(self._show_advanced_options)
        self.browser.click(self._search_traces)


class CheckBoxFilter(Widget):
    ROOT = ('//*[contains(@class, "pf-c-dropdown__menu")]'
            '//*[contains(@class, "pf-c-dropdown__menu-item")]')
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
            locator=('//button//span[normalize-space(text())="{}"]/..'.format(filter_name)))

    def __locator__(self):
        return self.locator

    def open(self):
        # TODO necessary workaround for remote zalenium webdriver execution
        self.browser.execute_script("window.scrollTo(0,0);")
        if not self.is_displayed:
            wait_displayed(self._filter_button)
            self.browser.click(self._filter_button)
            wait_displayed(self)
        wait_to_spinner_disappear(self.browser)

    def close(self):
        if self.is_displayed:
            self.browser.click(self._filter_button)
            wait_not_displayed(self)

    @property
    def layout(self):
        self.open()
        return DropDown(parent=self, locator=self.DROP_DOWN.format('graph_filter_layout'))

    @property
    def items(self):
        self.open()
        try:
            return self._items
        finally:
            self.close()

    @property
    def _items(self):
        """
        Optimized property, filter should be opened before calling.
        """
        return [
            self.browser.text(el)
            for el in self.browser.elements(parent=self, locator=self.CB_ITEMS)]

    @property
    def radio_items(self):
        self.open()
        try:
            return [
                self.browser.text(el)
                for el in self.browser.elements(parent=self, locator=self.RB_ITEMS)]
        finally:
            self.close()

    def _cb_action(self, filter_name, action, value=None, skipOpen=False):
        if not skipOpen:
            self.open()
        try:
            _cb = Checkbox(locator=self.ITEM.format(filter_name), parent=self)
            if action is 'fill':
                _cb.fill(value)
            elif action is 'read':
                return _cb.read()
        finally:
            if not skipOpen:
                self.close()

    def check(self, filter_name):
        self._cb_action(filter_name, 'fill', True)

    def uncheck(self, filter_name):
        self._cb_action(filter_name, 'fill', False)

    def uncheck_all(self):
        self.open()
        _items = self._items
        for _cb_item in _items:
            self._cb_action(_cb_item, 'fill', False, skipOpen=True)
        self.close()

    def is_checked(self, filter_name, skipOpen=False):
        return self._cb_action(filter_name, 'read', skipOpen=skipOpen)

    @property
    def checked_items(self):
        self.open()
        _items = self._items
        checked_items = []
        for _cb_item in _items:
            if self.is_checked(_cb_item, skipOpen=True):
                checked_items.append(_cb_item)
        self.close()
        return checked_items


class GraphLayout(Widget):
    ROOT = ('//*[contains(@class, "pf-l-toolbar")]')

    def __init__(self, parent, locator=None, logger=None):
        Widget.__init__(self, parent, logger=logger)
        if locator:
            self.locator = locator
        else:
            self.locator = self.ROOT
        self._buttons = {}
        self._buttons[GraphPageLayout.DAGRE] = '//button[@id="toolbar_layout_default"]'
        self._buttons[GraphPageLayout.COSE] = '//button[@id="toolbar_layout1"]'
        self._buttons[GraphPageLayout.COLA] = '//button[@id="toolbar_layout2"]'

    def __locator__(self):
        return self.locator

    def check(self, button_type):
        self.browser.click(
            self.browser.element(locator=self._buttons[button_type],
                                 parent=self.locator))

    def _is_active(self, button_locator):
        return 'pf-m-active' in self.browser.element(
            locator=button_locator,
            parent=self.locator).get_attribute("class")

    @property
    def active_items(self):
        active_items = []
        for _key, _value in self._buttons.items():
            if self._is_active(_value):
                active_items.append(_key)
        return active_items


class GraphSidePanel(Widget):
    ROOT = ('.//div[@id="graph-side-panel"]')

    def __init__(self, parent, locator=None, logger=None):
        Widget.__init__(self, parent, logger=logger)
        if locator:
            self.locator = locator
        else:
            self.locator = self.ROOT

    def __locator__(self):
        return self.locator

    def get_namespace(self):
        namespace = self.browser.text_or_default(
            locator='//span[contains(@class, "pf-c-badge") and text()="NS"]/..',
            parent=self.ROOT,
            default=None)
        if namespace:
            namespace = namespace.replace('NS', '')
        return namespace

    def get_workload(self):
        workload = self.browser.text_or_default(
            locator='//span[contains(@class, "pf-c-badge") and text()="W"]/..',
            parent=self.ROOT,
            default=None)
        if workload:
            workload = workload.replace('W', '')
        return workload

    def get_service(self):
        service = self.browser.text_or_default(
            locator='//span[contains(@class, "pf-c-badge") and text()="S"]/..',
            parent=self.ROOT,
            default=None)
        if service:
            service = service.replace('S', '')
        return service

    def get_application(self):
        application = self.browser.text_or_default(
            locator='//span[contains(@class, "pf-c-badge") and text()="A"]/..',
            parent=self.ROOT,
            default=None)
        if application:
            application = application.replace('A', '')
        return application


class GraphDisplayFilter(CheckBoxFilter):
    ROOT = ('//*[contains(@class, "pf-c-dropdown__menu")]')
    CB_ITEMS = './/label//input[@type="checkbox"]/..'
    RB_ITEMS = './/label//input[@type="radio"]/..'
    ITEM = './/label[normalize-space(text())="{}"]/../input'


class NamespaceFilter(CheckBoxFilter):
    ROOT = ('//*[contains(@class, "pf-c-dropdown__menu")]')
    CB_ITEMS = './/input[@type="checkbox"]/../span'
    ITEM = './/span[normalize-space(text())="{}"]/../input'

    def __init__(self, parent, locator=None, logger=None):
        logger.debug('Loading namespace filter widget')
        Widget.__init__(self, parent, logger=logger)
        if locator:
            self.locator = locator
        else:
            self.locator = self.ROOT
        self._filter_button = Button(
            parent=self.parent,
            locator=('//button[@id="namespace-selector"]'))

    @property
    def is_displayed(self):
        return self.browser.is_displayed(self.ROOT)

    @property
    def is_available(self):
        logger.debug('Checking if available')
        return self.browser.is_displayed(self._filter_button.locator)

    def clear_all(self):
        self.open()
        self.browser.click(Button(
            parent=self.parent,
            locator=('//button/span[normalize-space(text())="Clear all"]')))
        wait_to_spinner_disappear(self.browser)
        self.close()


class About(Widget):
    ROOT = './/*[contains(@class, "pf-c-about-modal-box")]'
    HEADER = './/*[contains(@class, "pf-c-about-modal-box__header")]'
    BODY = './/*[contains(@class, "pf-c-about-modal-box__content")]'
    APP_LOGO = '//*[contains(@class, "pf-c-about-modal-box__brand")]/img'
    VERSION = BODY + '//dl//dt'
    VERSION_VALUE = './following-sibling::dd'
    TRADEMARK = ROOT + '//*[contains(@class, "pf-c-about-modal-box__strapline")]'
    CLOSE = './/*[contains(@class, "pf-c-about-modal-box__close")]//button'

    def __init__(self, parent, logger=None):
        Widget.__init__(self, parent, logger=logger)

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
            _locator = '{}[text()="{}"]'.format(
                self.VERSION, ApplicationVersionEnum.PROMETHEUS.text)
            if len(self.browser.elements(_locator, parent=self, force_check_safe=True)) > 0:
                return True
            else:
                return False
        wait_for(_is_versions_loaded, timout=3, delay=0.2, very_quiet=True)
        for el in self.browser.elements(self.VERSION, parent=self, force_check_safe=True):
            _name = self.browser.text(el)
            _version = self.browser.text(locator=self.VERSION_VALUE, parent=el)
            _versions[_name] = _version
        return _versions

    @property
    def trademark(self):
        return self.browser.text(self.browser.element(self.TRADEMARK, parent=self))


class NavBar(Widget):
    ROOT = '//*[contains(@class, "pf-c-page__header")]'
    TOGGLE_NAVIGATION = './/*[@id="nav-toggle"]'
    NAVBAR_HELP = ('//*[contains(@class, "pf-l-toolbar__group")]'
                   '//*[contains(@class, "pf-c-dropdown")]//span[not(@class)]/../..')
    NAVBAR_USER = ('//*[contains(@class, "pf-l-toolbar__group")]'
                   '//*[contains(@class, "pf-c-dropdown")]//'
                   'span[contains(@class, "pf-c-dropdown__toggle-text")]/../..')
    USER_SELECT_BUTTON = '//*[contains(@class, "pf-c-dropdown__toggle-text")]/..'
    NAVBAR_MASTHEAD = './/*[contains(@class, "pf-l-toolbar__item")]//*[contains(@d, "M512")]'

    def __init__(self, parent, logger=None):
        logger.debug('Loading navbar')
        Widget.__init__(self, parent, logger=logger)
        logger.debug('Loading help menu')
        self.help_menu = MenuDropDown(
            parent=self, locator=self.NAVBAR_HELP,
            logger=logger, force_open=True)
        logger.debug('Loading user menu')
        self.user_menu = MenuDropDown(
            parent=self, locator=self.NAVBAR_USER,
            logger=logger, force_open=True,
            select_button=self.USER_SELECT_BUTTON)

    def about(self):
        logger.debug('Opening about box')
        self.help_menu.select(HelpMenuEnum.ABOUT.text)
        return About(parent=self.parent, logger=self.logger)

    def toggle(self):
        logger.debug('Clicking navigation toggle')
        self.browser.click(self.browser.element(self.TOGGLE_NAVIGATION, parent=self))

    def get_masthead_tooltip(self):
        """
        Returns a Dictionary of broken istio components shown in Masthead tooltip,
        where the key is the component name,
        the value is the status shown in Masthead tooltip.

        If tooltip does not exist, returns empty dict.
        """
        statuses = {}
        try:
            self.browser.move_to_element(locator=self.NAVBAR_MASTHEAD, parent=self.ROOT)
            sleep(0.5)
            masthead_items = self.browser.elements(
                locator=POPOVER + '//ul//div[contains(@class, "pf-m-gutter")]',
                parent='/')
            for _masthead_status in masthead_items:
                _item_key, _item_status = _masthead_status.text.split('\n')
                statuses[_item_key] = _item_status
        except (NoSuchElementException, StaleElementReferenceException):
            # skip errors caused by browser delays, this health will be ignored
            pass
        finally:
            self.browser.send_keys_to_focused_element(Keys.ESCAPE)
            sleep(0.5)
            return statuses


class BreadCrumb(Widget):
    """Represents the Patternfly BreadCrumb.
    """
    ROOT = '//section[contains(@class, "pf-c-page__main-section")]'
    BREADCRUMB_ROOT = './/ol[contains(@class, "breadcrumb")]'
    ELEMENTS = BREADCRUMB_ROOT + "//li"
    LINKS = ELEMENTS + "//a"

    def __init__(self, parent, locator=None, logger=None):
        Widget.__init__(self, parent=parent, logger=logger)
        self._locator = locator or self.ROOT

    def __locator__(self):
        return self._locator

    @property
    def _path_elements(self):
        return self.browser.elements(self.ELEMENTS)

    @property
    def _path_links(self):
        return self.browser.elements(self.LINKS)

    @property
    def locations(self):
        return [self.browser.text(loc) for loc in self._path_elements]

    @property
    def active_location(self):
        return self.locations[-1] if self.locations else None

    def click_location(self, name, handle_alert=False):
        location = next(loc for loc in self._path_links if self.browser.text(loc) == name)
        self.browser.click(location, ignore_ajax=handle_alert)
        if handle_alert:
            self.browser.handle_alert(wait=2.0)
            self.browser.plugin.ensure_page_safe()

    def read(self):
        """Return the active location of the breadcrumb"""
        return self.active_location


class MainMenu(Widget):
    ROOT = ('//*[contains(@class, "pf-c-page__sidebar")]')
    MENU_ITEMS = './/*[contains(@class, "pf-c-nav__link")]/..'
    MENU_ITEM_LINK = './/*[contains(@class, "pf-c-nav__link") and text()="{}"]'
    MENU_ITEM = './/*[contains(@class, "pf-c-nav__link") and text()="{}"]/..'
    MENU_ITEM_ACTIVE = ('.//*[contains(@class, "pf-m-current")'
                        ' and contains(@class, "pf-c-nav__link")]/..')

    def __init__(self, parent, logger=None):
        logger.debug('Loading main menu widget')
        Widget.__init__(self, parent, logger=logger)
        self.navbar = NavBar(parent=self.parent, logger=logger)
        wait_displayed(self)

    def select(self, menu):
        logger.debug('Selecting menu: {}'.format(menu))
        self.browser.click(self.browser.element(self.MENU_ITEM.format(menu), parent=self))

    def get_link(self, menu):
        return self.browser.element(self.MENU_ITEM_LINK.format(menu), parent=self)

    @property
    def selected(self):
        sel_menu = self.browser.text(self.browser.element(self.MENU_ITEM_ACTIVE, parent=self))
        logger.debug('Selected menu: {}'.format(sel_menu))
        return sel_menu

    @property
    def items(self):
        return [
            self.browser.text(el)
            for el
            in self.browser.elements(self.MENU_ITEMS, parent=self)]

    @property
    def is_collapsed(self):
        return 'pf-m-collapsed' in self.browser.get_attribute('class', self.ROOT)

    def collapse(self):
        if not self.is_collapsed:
            self.navbar.toggle()

    def expand(self):
        if self.is_collapsed:
            self.navbar.toggle()


class Login(Widget):
    ROOT = '//*[contains(@class, "pf-c-form")]'
    USERNAME = './/input[@name="pf-login-username-id"]'
    PASSWORD = './/input[@name="pf-login-password-id"]'
    SUBMIT = './/button[@type="submit"]'

    def __init__(self, parent, logger=None):
        logger.debug('Loading login widget')
        Widget.__init__(self, parent, logger=logger)
        self.username = TextInput(parent=self, locator=self.USERNAME)
        self.password = TextInput(parent=self, locator=self.PASSWORD)
        self.submit = Button(parent=self.parent, locator=self.SUBMIT, logger=logger)

    @property
    def is_displayed(self):
        return self.browser.is_displayed(self.ROOT) and \
            self.browser.is_displayed(self.USERNAME)

    def login(self, username, password):
        self.username.fill(username)
        self.password.fill(password)
        self.browser.click(self.submit)


class ViewAbstract(Widget):
    ROOT = '//div[contains(@class, "pf-c-tabs")]'
    MISSING_SIDECAR_TEXT = 'Missing Sidecar'
    NO_SIDECAR_TEXT = 'No Istio sidecar'
    MISSING_TEXT_SIDECAR = './/span[normalize-space(text())="{}"]'.format(MISSING_SIDECAR_TEXT)
    NO_SIDECAR_HEALTH = './/div[contains(text(), "{}")]'.format(NO_SIDECAR_TEXT)
    MISSING_ICON_SIDECAR = './/span//svg'
    INFO_TAB = '//button[@id="pf-tab-0-basic-tabs"]'

    def back_to_service_info(self, parent):
        # TODO find a better way after KIALI-2251
        try:
            self.browser.click('.//a[contains(@href, "/services/")]', parent)
        except NoSuchElementException:
            self.browser.execute_script("history.back();")

    def back_to_info(self):
        tab = self.browser.element(locator=self.INFO_TAB,
                                   parent=self.ROOT)
        try:
            self.browser.click(tab)
        finally:
            self.browser.click(tab)
        wait_to_spinner_disappear(self.browser)

    def _get_date_tooltip(self, element):
        date_text = ''
        try:
            self.browser.move_to_element(locator='.//span', parent=element)
            sleep(1.5)
            date_text = self.browser.element(
                locator=(POPOVER),
                parent='/').text
        except (NoSuchElementException, StaleElementReferenceException):
            # skip errors caused by browser delays, this health will be ignored
            pass
        finally:
            self.browser.send_keys_to_focused_element(Keys.ESCAPE)
            sleep(0.5)
            return date_text

    def click_more_labels(self, parent):
        try:
            elements = self.browser.elements(
                parent=parent,
                locator=('.//a[text()="More labels..."]'))
            for element in elements:
                self.browser.click(element)
        except NoSuchElementException:
            pass

    def _get_labels(self, el):
        _label_dict = {}
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

    def _item_sidecar_text(self, element):
        # TODO sidecar is not shown yet
        return not len(self.browser.elements(
                parent=element, locator=self.MISSING_TEXT_SIDECAR)) > 0

    def _details_sidecar_text(self):
        return not (len(self.browser.elements(
            parent=self.DETAILS_ROOT,
            locator=self.MISSING_TEXT_SIDECAR)) > 0 or
                len(self.browser.elements(
                    parent=self.DETAILS_ROOT,
                    locator=self.NO_SIDECAR_HEALTH)) > 0)

    def _item_sidecar_icon(self, element):
        return not len(self.browser.elements(
                parent=element, locator=self.MISSING_ICON_SIDECAR)) > 0


class ListViewAbstract(ViewAbstract):
    ROOT = '//*[contains(@style, "overflow-y")]'
    BODY = '//*[contains(@class, "ReactVirtualized__VirtualGrid__innerScrollContainer")]'
    DIALOG_ROOT = '//*[@role="dialog"]'
    ITEMS = './/tr[contains(@role, "row")]'
    ITEM_COL = './/td'
    ITEM_TEXT = './/*[contains(@class, "virtualitem_definition_link")]'
    DETAILS_ROOT = ('.//section[@id="pf-tab-section-0-basic-tabs"]'
                    '/div[contains(@class, "pf-l-grid")]')
    ISTIO_PROPERTIES = ('.//*[contains(@class, "pf-l-stack__item")]'
                        '/h6[text()="{}"]/..')
    NETWORK_PROPERTIES = ('.//*[contains(@class, "pf-l-stack__item")]'
                          '//h6[text()="{}"]/..')
    PROPERTY_SECTIONS = ('.//*[contains(@class, "pf-l-stack__item")]'
                         '//span[text()="{}"]/../..')
    NAME = 'Name'
    PODS = 'Pods'
    SERVICES = 'Services'
    TYPE = 'Type'
    IP = 'IP'
    SERVICE_IP = 'Service IP'
    PORTS = 'Ports'
    CREATED_AT = 'Created at'
    RULE_3SCALE_HANDLER = '3scale API handler'
    RESOURCE_VERSION = 'Resource Version'
    INBOUND_METRICS = 'Inbound Metrics'
    OUTBOUND_METRICS = 'Outbound Metrics'
    SHOW_ON_GRAPH_TEXT = '(Show on graph)'
    HEALTH_TEXT = "Health"
    CONFIG_TEXT = "Config"
    SUBSETS = 'Subsets'
    OVERVIEW_DETAILS_ROOT = './/div[contains(@class, "row-cards-pf")]'
    CONFIG = 'strong[normalize-space(text()="{}:")]/..//'.format(CONFIG_TEXT)
    CONFIG_TABS_PARENT = './/ul[contains(@class, "pf-c-tabs__list")]'
    CONFIG_TAB_OVERVIEW = './/button[@id="pf-tab-0-basic-tabs"]'
    ACTIVE_TAB_YAML = './/li[contains(@class, "pf-m-current")]//button[@id="pf-tab-1-basic-tabs"]'
    CONFIG_TAB_YAML = './/button[@id="pf-tab-1-basic-tabs"]'
    GRAPH_OVERVIEW_MENU = '//div[contains(@class, "pf-c-card__head")]//'\
        'h3[text()="Graph Overview"]/../..//button'

    def __init__(self, parent, locator=None, logger=None):
        Widget.__init__(self, parent, logger=logger)
        if locator:
            self.locator = locator
        else:
            self.locator = self.ROOT
        self.graph_menu = ActionsDropDown(parent=self,
                                          locator=self.GRAPH_OVERVIEW_MENU,
                                          select_button='',
                                          logger=logger,
                                          force_open=True)

    def __locator__(self):
        return self.locator

    @property
    def is_displayed(self):
        return self.browser.is_displayed(self.ROOT)

    def has_overview_tab(self):
        return len(self.browser.elements(locator=self.CONFIG_TAB_OVERVIEW,
                                         parent=self.CONFIG_TABS_PARENT)) > 0

    def is_yaml_tab_active(self):
        return len(self.browser.elements(locator=self.ACTIVE_TAB_YAML,
                                         parent=self.CONFIG_TABS_PARENT)) > 0

    def display_overview_editor(self):
        logger.debug('Opening overview editor')
        if self.has_overview_tab():
            self.browser.click(self.browser.element(locator=self.CONFIG_TAB_OVERVIEW,
                                                    parent=self.CONFIG_TABS_PARENT))

    def display_yaml_editor(self):
        logger.debug('Opening yaml editor')
        if not self.is_yaml_tab_active():
            self.browser.click(self.browser.element(locator=self.CONFIG_TAB_YAML,
                                                    parent=self.CONFIG_TABS_PARENT))
            self.browser.wait_for_element(locator=self.CONFIG_TEXT, parent=self.CONFIG_DETAILS_ROOT)

    def _item_namespace(self, cell):
        return cell.text.strip().replace('NS', '')

    def _get_service_endpoints(self, element):
        result = []
        _endpoints = self.browser.elements(
            locator='.//div[@id="endpoints"]//span', parent=element)
        for endpoint in _endpoints:
            result.append(endpoint.text)
        return result

    def _get_details_health(self):
        _health_sublocator = '/../..//div[@id="health"]'
        _healthy = len(self.browser.elements(
            parent=self.DETAILS_ROOT,
            locator='.//*[contains(@class, "icon-healthy")]' + _health_sublocator)) > 0
        _not_healthy = len(self.browser.elements(
            parent=self.DETAILS_ROOT,
            locator='.//*[contains(@class, "icon-failure")]' + _health_sublocator)) > 0
        _degraded = len(self.browser.elements(
            parent=self.DETAILS_ROOT,
            locator='.//*[contains(@class, "icon-degraded")]' + _health_sublocator)) > 0
        _idle = len(self.browser.elements(
            parent=self.DETAILS_ROOT,
            locator='.//*[contains(@class, "icon-idle")]' + _health_sublocator)) > 0
        _not_available = len(self.browser.elements(
            parent=self.DETAILS_ROOT,
            locator='.//*[contains(@class, "icon-na")]' + _health_sublocator)) > 0
        _health = None
        if _healthy:
            _health = HealthType.HEALTHY
        elif _not_healthy:
            _health = HealthType.FAILURE
        elif _degraded:
            _health = HealthType.DEGRADED
        elif _idle:
            _health = HealthType.IDLE
        elif _not_available:
            _health = HealthType.NA
        return _health

    def _get_item_health(self, element):
        _healthy = len(self.browser.elements(
            parent=element,
            locator='.//*[contains(@class, "icon-healthy")]')) > 0
        _not_healthy = len(self.browser.elements(
            parent=element,
            locator='.//*[contains(@class, "icon-failure")]')) > 0
        _degraded = len(self.browser.elements(
            parent=element,
            locator='.//*[contains(@class, "icon-degraded")]')) > 0
        _idle = len(self.browser.elements(
            parent=element,
            locator='.//*[contains(@class, "icon-idle")]')) > 0
        _not_available = len(self.browser.elements(
            parent=element,
            locator='.//*[contains(@class, "icon-na")]')) > 0
        _health = None
        if _healthy:
            _health = HealthType.HEALTHY
        elif _not_healthy:
            _health = HealthType.FAILURE
        elif _degraded:
            _health = HealthType.DEGRADED
        elif _idle:
            _health = HealthType.IDLE
        elif _not_available:
            _health = HealthType.NA
        return _health

    def _get_item_config_status(self, element):
        return ConfigurationStatus(
             self._get_item_validation(element),
             self._get_item_config_link(element)
            )

    def _get_item_config_link(self, element):
        try:
            return self.browser.get_attribute(
                'href',
                self.browser.element(
                    locator='.//a',
                    parent=element))
        except (NoSuchElementException):
            return None

    def _get_item_details_icon(self, element):
        _api = len(self.browser.elements(
            parent=element,
            locator='.//img[contains(@title, "{}")]'.format(
                ItemIconType.API_DOCUMENTATION.text))) > 0
        _details = None
        if _api:
            _details = ItemIconType.API_DOCUMENTATION
        return _details

    def _get_workload_health(self, name, element):
        statuses = self._get_health_tooltip(element)
        if len(statuses) > 0:
            return WorkloadHealth(
                workload_status=self._get_deployment_status(statuses, name),
                requests=self._get_apprequests(statuses))
        else:
            return None

    def _get_application_health(self, element):
        statuses = self._get_health_tooltip(element)
        if len(statuses) > 0:
            return ApplicationHealth(
                deployment_statuses=self._get_deployment_statuses(statuses),
                requests=self._get_apprequests(statuses))
        else:
            return None

    def _get_service_health(self, element):
        statuses = self._get_health_tooltip(element)
        if len(statuses) > 0:
            return ServiceHealth(requests=self._get_requests(statuses))
        else:
            return None

    def _get_health_tooltip(self, element):
        statuses = []
        try:
            self.browser.move_to_element(locator='.//*[contains(@class, "icon")]', parent=element)
            sleep(0.5)
            statuses = self._get_request_statuses()
        except (NoSuchElementException, StaleElementReferenceException):
            # skip errors caused by browser delays, this health will be ignored
            pass
        finally:
            self.browser.send_keys_to_focused_element(Keys.ESCAPE)
            sleep(0.5)
            return statuses

    def _get_additional_details_icon(self):
        _api = len(self.browser.elements(
            parent=self.locator,
            locator='.//h6[text()="{}"]'.format(
                ItemIconType.API_DOCUMENTATION.text))) > 0
        _details = None
        if _api:
            _details = ItemIconType.API_DOCUMENTATION
        return _details

    def _get_application_details_health(self):
        statuses = self._get_request_statuses()
        if len(statuses) > 0:
            return ApplicationHealth(
                deployment_statuses=self._get_deployment_statuses(statuses),
                requests=self._get_apprequests(statuses))
        else:
            return None

    def _get_workload_details_health(self, name):
        statuses = self._get_request_statuses()
        if len(statuses) > 0:
            return WorkloadHealth(
                workload_status=self._get_deployment_status(statuses, name),
                requests=self._get_apprequests(statuses))
        else:
            return None

    def _get_service_details_health(self):
        statuses = self._get_request_statuses()
        if len(statuses) > 0:
            return ServiceHealth(requests=self._get_requests(statuses))
        else:
            return None

    def _get_request_statuses(self):
        return self.browser.element(
            locator=('.//*[contains(text(), "Pod Status") or ' +
                     'contains(text(), "Error Rate")]/../..'),
            parent=self.locator).text.split('\n')

    def _get_deployment_status(self, statuses, name=None):
        result = self._get_deployment_statuses(statuses, name)
        if len(result) > 0:
            return result[0]
        else:
            return self._get_deployment_pod_status(statuses, name)

    def _get_deployment_pod_status(self, statuses, name):
        desired_pods = 0
        available_pods = 0
        for _status in statuses:
            if 'desired pod' in _status:
                desired_pods = int(re.search(r'\d+', _status).group())
            if 'available pod' in _status:
                available_pods = int(re.search(r'\d+', _status).group())
        return DeploymentStatus(
            name=name,
            replicas=desired_pods,
            available=available_pods)

    def _get_deployment_statuses(self, statuses, name=None):
        result = []
        for _status in statuses:
            if '/' in _status:
                _label, _value = _status.split(':')
                _replicas, _available = _value.split('/')
                result.append(DeploymentStatus(
                        name=(name if name else _label),
                        replicas=int(_replicas),
                        available=int(_available)))

        return result

    def _get_apprequests(self, statuses):
        _inbound = "Inbound:"
        _outbound = "Outbound:"
        _no_requests = 'No requests'
        _inbound_text = _no_requests
        _outbound_text = _no_requests
        for _request in statuses:
            if _inbound in _request:
                _inbound_text = _request.replace(_inbound, '').replace('%', '').strip()
            if _outbound in _request:
                _outbound_text = _request.replace(_outbound, '').replace('%', '').strip()
        return AppRequests(
                inboundErrorRatio=float(_inbound_text.replace(_no_requests, '-1')) / 100,
                outboundErrorRatio=float(_outbound_text.replace(_no_requests, '-1')) / 100)

    def _get_requests(self, statuses):
        _no_requests = 'No requests'
        _no_istio_sidecar = 'No Istio sidecar'
        _inbound_text = _no_requests
        for _request in statuses:
            if 'Inbound' in _request:
                _inbound_text = _request.split(':')[1].replace('%', '').strip()
        return Requests(
                errorRatio=float(_inbound_text.replace(_no_requests, '-1').
                                 replace(_no_istio_sidecar, '-1')) / 100)

    def _get_item_validation(self, element):
        _valid = len(self.browser.elements(
            parent=element,
            locator='.//*[contains(@style, "color: rgb(62, 134, 53)")]')) > 0
        _not_valid = len(self.browser.elements(
            parent=element,
            locator='.//*[contains(@style, "danger")]')) > 0
        _warning = len(self.browser.elements(
            parent=element,
            locator='.//*[contains(@style, "warning")]')) > 0
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

    def _get_overview_error_messages(self):
        return self._get_subsets_error_messages()

    def _get_subsets_error_messages(self):
        _messages = []
        _subsets_tr = self.browser.elements(
            locator=('.//div[contains(@class, "pf-c-card__body")]//'
                     'h2[@data-pf-content="true" and contains(text(), "{}")]/..//tbody/tr').format(
                        self.SUBSETS),
            parent=self.OVERVIEW_DETAILS_ROOT)
        for subset_tr in _subsets_tr:
            columns = self.browser.elements(self.ITEM_COL, parent=subset_tr)
            validation = self._get_item_validation(columns[0])
            message = ""
            if validation == IstioConfigValidation.WARNING or \
                    validation == IstioConfigValidation.NOT_VALID:
                try:
                    self.browser.move_to_element(
                        locator='.//*[contains(@style, "color")]', parent=columns[0])
                    sleep(0.5)
                    message = self.browser.text(
                        locator=('.//*[contains(@class, "tippy-popper")]'),
                        parent='/').strip()
                except (NoSuchElementException, StaleElementReferenceException):
                    # skip errors caused by browser delays, this health will be ignored
                    pass
                finally:
                    self.browser.send_keys_to_focused_element(Keys.ESCAPE)
                    sleep(0.2)
            if message:
                _messages.append(message)
        return _messages

    def _get_item_label_keys(self, element):
        _label_keys = []
        _labels = self.browser.elements(
            parent=element,
            locator='.//*[contains(@class, "pf-c-badge")]')
        if _labels:
            for _label in _labels:
                _label_keys.append(_label.text)
        return _label_keys

    def _get_item_labels(self, element):
        _label_dict = {}
        _labels = self.browser.elements(
            parent=element,
            locator='.//*[contains(@class, "pf-c-badge")]')
        if _labels:
            for _label in _labels:
                _label_key, _label_value = _label.text.split(':')
                _label_dict[_label_key] = _label_value.strip()
        return _label_dict

    def _get_details_labels(self):
        _label_dict = {}
        try:
            self.browser.click(self.browser.element(
                parent=self.DETAILS_ROOT,
                locator=('.//a[text()="More labels..."]')))
        except NoSuchElementException:
            pass
        _labels = self.browser.elements(
            parent=self.DETAILS_ROOT,
            locator=('//div[@id="labels"]//*[contains(@class, "label-pair")]'))
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

    def _get_labels_tooltip(self, element):
        _label_dict = {}
        try:
            self.browser.move_to_element(
                locator='.//div[contains(@class, "pf-c-card__body")]//div[@id="labels_info"]',
                parent=element)
            sleep(1.5)
            labels_text = self.browser.element(
                locator=(POPOVER),
                parent='/').text
            if labels_text:
                for _label in labels_text.split('\n'):
                    _label_key, _label_value = _label.split(':')
                    _label_dict[_label_key] = _label_value.strip()
        except (NoSuchElementException, StaleElementReferenceException):
            # skip errors caused by browser delays, this labels will be ignored
            pass
        finally:
            self.browser.send_keys_to_focused_element(Keys.ESCAPE)
            sleep(0.5)
            return _label_dict

    def _get_details_selectors(self):
        _selector_dict = {}
        try:
            self.browser.click(self.browser.element(
                parent=self.DETAILS_ROOT,
                locator=('.//a[text()="More selectors..."]')))
        except NoSuchElementException:
            pass
        _selectors = self.browser.elements(
            parent=self.DETAILS_ROOT,
            locator=('//h6[contains(text(), "Selectors")]'
                     '/../../div[@id="selectors"]//*[contains(@class, "label-pair")]'))
        if _selectors:
            for _selector in _selectors:
                _label_key = self.browser.element(
                    parent=_selector,
                    locator='.//*[contains(@class, "label-key")]').text
                _label_value = self.browser.element(
                    parent=_selector,
                    locator='.//*[contains(@class, "label-value")]').text
                _selector_dict[_label_key] = _label_value
        return _selector_dict

    def get_mesh_wide_tls(self):
        self.browser.click(self.parent.refresh)
        wait_to_spinner_disappear(self.browser)
        wait_displayed(self)
        _partial = len(self.browser.elements(
            parent=self.ROOT,
            locator='//*[contains(@class, "pf-l-toolbar")]'
            '//img[contains(@src, "mtls-status-partial")]')) > 0
        _full = len(self.browser.elements(
            parent=self.ROOT,
            locator='//*[contains(@class, "pf-l-toolbar")]'
            '//img[contains(@src, "mtls-status-full")]')) > 0
        if _full:
            return MeshWideTLSType.ENABLED
        elif _partial:
            return MeshWideTLSType.PARTLY_ENABLED
        else:
            return MeshWideTLSType.DISABLED

    def get_namespace_wide_tls(self, element):
        _partial = len(self.browser.elements(
            parent=element,
            locator='.//*[contains(@class, "pf-c-card__body")]'
            '//img[contains(@src, "mtls-status-partial-dark")]')) > 0
        _full = len(self.browser.elements(
            parent=element,
            locator='.//*[contains(@class, "pf-c-card__body")]'
            '//img[contains(@src, "mtls-status-full-dark")]')) > 0
        if _full:
            return MeshWideTLSType.ENABLED
        elif _partial:
            return MeshWideTLSType.PARTLY_ENABLED
        else:
            return MeshWideTLSType.DISABLED

    @property
    def all_items(self):
        self.browser.refresh()
        wait_displayed(self)
        wait_to_spinner_disappear(self.browser)
        return self.items

    def _is_tooltip_visible(self, index, number):
        # TODO better way to find tooltip visiblity
        # now skip the first and after 7th rows
        if index > 0 and index < min(number, 7):
            return True
        return False


class ListViewOverview(ListViewAbstract):
    ROOT = '//section[contains(@class, "pf-c-page__main-section")]'
    LINK_ACTIONS = '//div[contains(@class, "pf-c-dropdown")]//button[@aria-label="Actions"]/..'
    ITEMS = './/*[contains(@class, "pf-l-grid__item")]/article[contains(@class, "pf-c-card")]'
    LIST_ITEMS = './/tr[contains(@role, "row")]'
    ITEM_COL = './/td'
    ITEM_TITLE = './/*[contains(@class, "pf-c-title")]'
    ITEM_TEXT = './/*[contains(@class, "pf-c-card__body")]//span/div[contains(text(), "{}")]'
    UNHEALTHY_TEXT = './/*[contains(@class, "icon-failure")]/..'
    HEALTHY_TEXT = './/*[contains(@class, "icon-healthy")]/..'
    DEGRADED_TEXT = './/*[contains(@class, "icon-warning")]/..'
    IDLE_TEXT = './/*[contains(@class, "icon-idle")]/..'
    OVERVIEW_TYPE = '//*[contains(@aria-labelledby, "overview-type")]'

    @property
    def expand_items(self):
        self.browser.click(self.browser.element(
            parent=self.ROOT,
            locator=('//button//*[contains(@d, "M296")]')))
        wait_to_spinner_disappear(self.browser)
        return self.items

    @property
    def compact_items(self):
        self.browser.click(self.browser.element(
            parent=self.ROOT,
            locator=('//button//*[contains(@d, "M149")]')))
        wait_to_spinner_disappear(self.browser)
        return self.items

    @property
    def items(self):
        _items = []
        _overview_type = self.browser.element(
                locator=self.OVERVIEW_TYPE).text
        for el in self.browser.elements(self.ITEMS, parent=self):
            _namespace = self.browser.element(
                locator=self.ITEM_TITLE, parent=el).text.replace('N/A', '')
            _item_numbers = int(re.search(r'\d+', self.browser.text(
                locator=self.ITEM_TEXT.format(_overview_type[0:3]), parent=el)).group())
            _unhealthy = 0
            _healthy = 0
            _degraded = 0
            _idle = 0
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
            if len(self.browser.elements(
                    parent=el, locator=self.IDLE_TEXT)) > 0:
                _idle = int(self.browser.element(
                    locator=self.IDLE_TEXT, parent=el).text)
            # overview object creation
            # TODO links
            _overview = Overview(
                overview_type=_overview_type,
                namespace=_namespace,
                items=_item_numbers,
                config_status=self._get_item_config_status(
                    self.browser.element(
                        locator='.//div[contains(text(), "Istio Config")]/..', parent=el)),
                healthy=_healthy,
                unhealthy=_unhealthy,
                degraded=_degraded,
                idle=_idle,
                na=(_item_numbers - (_healthy + _unhealthy + _degraded + _idle)),
                tls_type=self.get_namespace_wide_tls(el),
                labels=self._get_labels_tooltip(element=el),
                links=[])
            # append this item to the final list
            _items.append(_overview)
        return _items

    @property
    def list_items(self):
        _items = []
        self.browser.click(self.browser.element(
            parent=self.ROOT,
            locator=('//button//*[contains(@d, "M80")]')))
        wait_to_spinner_disappear(self.browser)
        _overview_type = self.browser.element(
                locator=self.OVERVIEW_TYPE).text
        for el in self.browser.elements(self.LIST_ITEMS, parent=self):
            columns = self.browser.elements(self.ITEM_COL, parent=el)
            _namespace = self._item_namespace(columns[1])
            _item_numbers = int(re.search(r'\d+', self.browser.text(
                locator='.//div[contains(text(), "{}")]'.format(_overview_type[0:3]),
                parent=columns[4])).group())
            _unhealthy = 0
            _healthy = 0
            _degraded = 0
            _idle = 0
            # update health
            if len(self.browser.elements(
                    parent=columns[4], locator=self.UNHEALTHY_TEXT)) > 0:
                _unhealthy = int(self.browser.element(
                    locator=self.UNHEALTHY_TEXT, parent=columns[4]).text)
            if len(self.browser.elements(
                    parent=columns[4], locator=self.DEGRADED_TEXT)) > 0:
                _degraded = int(self.browser.element(
                    locator=self.DEGRADED_TEXT, parent=columns[4]).text)
            if len(self.browser.elements(
                    parent=columns[4], locator=self.HEALTHY_TEXT)) > 0:
                _healthy = int(self.browser.element(
                    locator=self.HEALTHY_TEXT, parent=columns[4]).text)
            if len(self.browser.elements(
                    parent=columns[4], locator=self.IDLE_TEXT)) > 0:
                _idle = int(self.browser.element(
                    locator=self.IDLE_TEXT, parent=columns[4]).text)
            # overview object creation
            # TODO links
            _overview = Overview(
                overview_type=_overview_type,
                namespace=_namespace,
                items=_item_numbers,
                config_status=self._get_item_config_status(columns[2]),
                healthy=_healthy,
                unhealthy=_unhealthy,
                degraded=_degraded,
                idle=_idle,
                na=(_item_numbers - (_healthy + _unhealthy + _degraded + _idle)),
                tls_type=self.get_namespace_wide_tls(el),
                labels=self._get_item_labels(columns[3]),
                links=[])
            # append this item to the final list
            _items.append(_overview)
        return _items


class ListViewApplications(ListViewAbstract):

    def get_details(self, load_only=False):
        _breadcrumb = BreadCrumb(self.parent)
        if load_only:
            return _breadcrumb
        self.back_to_info()

        _table_view_workloads = TableViewAppWorkloads(self.parent, self.locator, self.logger)

        _table_view_services = TableViewAppServices(self.parent, self.locator, self.logger)

        _traffic_tab = TrafficView(parent=self.parent, locator=self.locator, logger=self.logger)

        _inbound_metrics = MetricsView(self.parent, self.INBOUND_METRICS)

        _outbound_metrics = MetricsView(self.parent,
                                        self.OUTBOUND_METRICS)

        return ApplicationDetails(name=str(_breadcrumb.active_location),
                                  istio_sidecar=self._details_sidecar_text(),
                                  health=self._get_details_health(),
                                  application_status=self._get_application_details_health(),
                                  workloads=_table_view_workloads.all_items,
                                  services=_table_view_services.all_items,
                                  traffic_tab=_traffic_tab,
                                  inbound_metrics=_inbound_metrics,
                                  outbound_metrics=_outbound_metrics)

    @property
    def items(self):
        _items = []
        _elements = self.browser.elements(self.ITEMS, parent=self)
        for index, el in enumerate(_elements):
            columns = self.browser.elements(self.ITEM_COL, parent=el)
            _name = self.browser.element(
                locator=self.ITEM_TEXT, parent=columns[0]).text.strip()
            _namespace = self._item_namespace(columns[1])

            # application object creation
            _application = Application(
                name=_name, namespace=_namespace,
                istio_sidecar=self._item_sidecar_text(el),
                health=self._get_item_health(element=el),
                application_status=(self._get_application_health(element=columns[3])
                                    if self._is_tooltip_visible(index=index,
                                                                number=len(_elements)) else None),
                labels=self._get_item_labels(element=columns[2]))
            # append this item to the final list
            _items.append(_application)
        return _items


class ListViewWorkloads(ListViewAbstract):

    def get_details(self, load_only=False):
        if load_only:
            return BreadCrumb(self.parent)
        self.back_to_info()
        _name = self.browser.text(
            locator=self.ISTIO_PROPERTIES.format(self.NAME),
            parent=self.DETAILS_ROOT).replace(self.NAME, '').strip()
        _type = self.browser.text(locator=self.ISTIO_PROPERTIES.format(self.TYPE),
                                  parent=self.DETAILS_ROOT).replace(self.TYPE, '').strip()
        _created_at_ui = self.browser.text(locator=self.ISTIO_PROPERTIES.format(self.CREATED_AT),
                                           parent=self.DETAILS_ROOT).replace(
                                            self.CREATED_AT, '').strip()
        _created_at = self._get_date_tooltip(self.browser.element(
            locator=self.ISTIO_PROPERTIES.format(self.CREATED_AT),
            parent=self.DETAILS_ROOT))
        _resource_version = self.browser.text(
            locator=self.ISTIO_PROPERTIES.format(self.RESOURCE_VERSION),
            parent=self.DETAILS_ROOT).replace(self.RESOURCE_VERSION, '').strip()

        _table_view_pods = TableViewWorkloadPods(self.parent, self.locator, self.logger)

        _table_view_services = TableViewServices(self.parent, self.locator, self.logger)

        _traffic_tab = TrafficView(parent=self.parent, locator=self.locator, logger=self.logger)

        _logs_tab = LogsView(parent=self.parent)

        _inbound_metrics = MetricsView(parent=self.parent, tab_name=self.INBOUND_METRICS)

        _outbound_metrics = MetricsView(parent=self.parent,
                                        tab_name=self.OUTBOUND_METRICS)

        return WorkloadDetails(name=str(_name),
                               workload_type=_type,
                               created_at_ui=_created_at_ui,
                               created_at=parse_from_rest(_created_at),
                               resource_version=_resource_version,
                               istio_sidecar=self._details_sidecar_text(),
                               health=self._get_details_health(),
                               workload_status=self._get_workload_details_health(_name),
                               icon=self._get_additional_details_icon(),
                               pods_number=_table_view_pods.number,
                               services_number=_table_view_services.number,
                               pods=_table_view_pods.all_items,
                               services=_table_view_services.all_items,
                               labels=self._get_details_labels(),
                               traffic_tab=_traffic_tab,
                               logs_tab=_logs_tab,
                               inbound_metrics=_inbound_metrics,
                               outbound_metrics=_outbound_metrics)

    @property
    def items(self):
        _items = []
        _elements = self.browser.elements(self.ITEMS, parent=self)
        for index, el in enumerate(_elements):
            # get workload name and namespace
            columns = self.browser.elements(self.ITEM_COL, parent=el)
            _name = self.browser.element(
                locator=self.ITEM_TEXT, parent=columns[0]).text.strip()
            _namespace = self._item_namespace(columns[1])
            _type = columns[2].text.strip()

            # workload object creation
            _workload = Workload(
                name=_name, namespace=_namespace, workload_type=_type,
                istio_sidecar=self._item_sidecar_text(el),
                labels=self._get_item_labels(columns[3]),
                health=self._get_item_health(element=el),
                icon=self._get_item_details_icon(element=el),
                workload_status=(self._get_workload_health(name=_name, element=columns[4])
                                 if self._is_tooltip_visible(index=index,
                                                             number=len(_elements)) else None))
            # append this item to the final list
            _items.append(_workload)
        return _items


class ListViewServices(ListViewAbstract):

    def get_details(self, load_only=False):
        if load_only:
            return BreadCrumb(self.parent)
        self.back_to_info()

        self.browser.click('.//button[contains(text(), "Network")]', parent=self)
        _type = self.browser.text(locator=self.NETWORK_PROPERTIES.format(self.TYPE),
                                  parent=self.DETAILS_ROOT).replace(self.TYPE, '').strip()
        _ip = self.browser.text(locator=self.NETWORK_PROPERTIES.format(self.SERVICE_IP),
                                parent=self.DETAILS_ROOT).replace(self.SERVICE_IP, '').strip()
        _ports = self.browser.text(
            locator=self.PROPERTY_SECTIONS.format(self.PORTS),
            parent=self.DETAILS_ROOT).replace(self.PORTS, '').strip()
        _endpoints = self._get_service_endpoints(self.DETAILS_ROOT)

        self.browser.click('.//button[contains(text(), "Properties")]', parent=self)
        _name = self.browser.text(
            locator=self.NETWORK_PROPERTIES.format(self.NAME),
            parent=self.DETAILS_ROOT).replace(self.NAME, '').strip()
        _created_at_ui = self.browser.text(
            locator=self.NETWORK_PROPERTIES.format(self.CREATED_AT),
            parent=self.DETAILS_ROOT).replace(self.CREATED_AT, '').strip()
        _created_at = self._get_date_tooltip(self.browser.element(
            locator=self.NETWORK_PROPERTIES.format(self.CREATED_AT),
            parent=self.DETAILS_ROOT))
        _resource_version = self.browser.text(
            locator=self.NETWORK_PROPERTIES.format(self.RESOURCE_VERSION),
            parent=self.DETAILS_ROOT).replace(self.RESOURCE_VERSION, '').strip()

        _3scale_api_handler = self.browser.text_or_default(
            locator=self.NETWORK_PROPERTIES.format(self.RULE_3SCALE_HANDLER),
            parent=self.DETAILS_ROOT,
            default='').replace(self.RULE_3SCALE_HANDLER, '').strip()

        _table_view_wl = TableViewWorkloads(self.parent, self.locator, self.logger)

        _traffic_tab = TrafficView(parent=self.parent, locator=self.locator, logger=self.logger)

        _inbound_metrics = MetricsView(parent=self.parent, tab_name=self.INBOUND_METRICS)

        _traces_tab = TracesView(parent=self.parent, locator=self.locator, logger=self.logger)

        return ServiceDetails(name=_name,
                              created_at=parse_from_rest(_created_at),
                              created_at_ui=_created_at_ui,
                              service_type=_type,
                              resource_version=_resource_version,
                              ip=_ip,
                              ports=str(_ports.replace('\n', ' ')),
                              rule_3scale_api_handler=_3scale_api_handler
                              if _3scale_api_handler != '' else None,
                              endpoints=_endpoints,
                              health=self._get_details_health(),
                              service_status=self._get_service_details_health(),
                              istio_sidecar=self._details_sidecar_text(),
                              labels=self._get_details_labels(),
                              selectors=self._get_details_selectors(),
                              workloads_number=_table_view_wl.number,
                              virtual_services_number=self.table_view_vs.number,
                              destination_rules_number=self.table_view_dr.number,
                              workloads=_table_view_wl.all_items,
                              virtual_services=self.table_view_vs.all_items,
                              destination_rules=self.table_view_dr.all_items,
                              traffic_tab=_traffic_tab,
                              inbound_metrics=_inbound_metrics,
                              traces_tab=_traces_tab)

    @property
    def items(self):
        _items = []
        _elements = self.browser.elements(self.ITEMS, parent=self)
        for index, el in enumerate(_elements):
            # get rule name and namespace
            columns = self.browser.elements(self.ITEM_COL, parent=el)
            _name = self.browser.element(
                locator=self.ITEM_TEXT, parent=columns[0]).text.strip()
            _namespace = self._item_namespace(columns[1])

            # create service instance
            _service = Service(
                name=_name,
                namespace=_namespace,
                istio_sidecar=self._item_sidecar_text(el),
                health=self._get_item_health(element=el),
                service_status=(self._get_service_health(element=columns[3])
                                if self._is_tooltip_visible(index=index,
                                                            number=len(_elements)) else None),
                icon=self._get_item_details_icon(element=el),
                config_status=self._get_item_config_status(columns[4]),
                labels=self._get_item_labels(element=columns[2]))
            # append this item to the final list
            _items.append(_service)
        return _items

    @property
    def table_view_dr(self):
        return TableViewDestinationRules(self.parent, self.locator, self.logger)

    @property
    def table_view_vs(self):
        return TableViewVirtualServices(self.parent, self.locator, self.logger)


class ListViewIstioConfig(ListViewAbstract):
    ACTION_HEADER = ('.//*[contains(@class, "list-group-item-text")]'
                     '//strong[normalize-space(text())="{}"]/..')
    CONFIG_HEADER = './/div[contains(@class, "row")]//h4'
    CONFIG_TEXT = './/div[contains(@class, "ace_content")]'
    CONFIG_DETAILS_ROOT = './/div[contains(@class, "container-fluid")]'

    def get_details(self, name, load_only=False):
        if load_only:
            return BreadCrumb(self.parent)
        _error_messages = self._get_overview_error_messages()
        self.display_yaml_editor()
        _text = self.browser.text(locator=self.CONFIG_TEXT,
                                  parent=self.CONFIG_DETAILS_ROOT)
        return IstioConfigDetails(name=name, text=_text,
                                  validation=self._get_details_validation(),
                                  error_messages=_error_messages)

    @property
    def items(self):
        _items = []
        for el in self.browser.elements(self.ITEMS, parent=self):
            # get rule name and namespace
            columns = self.browser.elements(self.ITEM_COL, parent=el)
            _name = self.browser.element(
                locator=self.ITEM_TEXT, parent=columns[0]).text.strip()
            _namespace = self._item_namespace(columns[1])
            _object_type = columns[2].text.strip()

            if str(_object_type) == IstioConfigObjectType.RULE.text or \
                    str(_object_type) == IstioConfigObjectType.ADAPTER.text or \
                    str(_object_type) == IstioConfigObjectType.HANDLER.text or \
                    str(_object_type) == IstioConfigObjectType.INSTANCE.text or \
                    str(_object_type) == IstioConfigObjectType.TEMPLATE.text:
                _rule = Rule(name=_name, namespace=_namespace, object_type=_object_type,
                             validation=IstioConfigValidation.NA)
                # append this item to the final list
                _items.append(_rule)
            else:
                _config = IstioConfig(name=_name,
                                      namespace=_namespace,
                                      object_type=_object_type,
                                      validation=self._get_item_validation(el),
                                      config_link=self._get_item_config_link(columns[3]))
                # append this item to the final list
                _items.append(_config)
        return _items


class TableViewAbstract(ViewAbstract):
    SERVICE_DETAILS_ROOT = './/section[contains(@class, "pf-c-page__main-section")]/div'
    OVERVIEW_DETAILS_ROOT = './/div[contains(@class, "pf-l-grid")]'
    OVERVIEW_HEADER = SERVICE_DETAILS_ROOT + \
        '//h6[contains(@class, "pf-c-title") and contains(text(), "{}")]/..'
    OVERVIEW_PROPERTIES = ('.//div[contains(@class, "pf-c-card__body")]//'
                           'h3[@data-pf-content="true" and contains(text(), "{}")]/..')
    HOSTS_PROPERTIES = './/div/h6[contains(text(), "{}")]/..//li'
    SERVICES_TAB = '//*[contains(@class, "pf-c-tabs__item")]//button[contains(text(), "{}")]'
    ROOT = '//[contains(@class, "tab-pane") and contains(@class, "active") and \
        contains(@class, "in")]'
    ROWS = ('//section[@id="{}"]//table[contains(@class, "table")]'
            '//tbody//tr')
    COLUMN = './/td'
    ROW_BY_NAME = \
        '//div[@id="{}"]//table[contains(@class, "table")]//tbody//tr//a[text()="{}"]/../..'
    CREATED_AT = 'Created at'
    RESOURCE_VERSION = 'Resource Version'
    HOST = 'Host'
    HOSTS = 'Hosts'
    NAME = 'Name'
    LABELS = 'Labels'
    TRAFFIC_POLICY = 'Traffic Policy'
    NO_TRAFFIC_POLICY = 'No traffic policy defined.'
    SUBSETS = 'Subsets'
    HTTP_ROUTE = 'HTTP Route'
    NO_SUBSETS = 'No subsets defined.'
    NONE = 'None'

    def __init__(self, parent, locator=None, logger=None):
        Widget.__init__(self, parent, logger=logger)
        if locator:
            self.locator = locator
        else:
            self.locator = self.ROOT

    def __locator__(self):
        return self.locator

    def _get_overview_status(self, element):
        _not_valid = len(self.browser.elements(
            parent=element,
            locator='.//*[contains(@style, "danger")]')) > 0
        _warning = len(self.browser.elements(
            parent=element,
            locator='.//*[contains(@style, "warning")]')) > 0
        if _not_valid:
            return IstioConfigValidation.NOT_VALID
        elif _warning:
            return IstioConfigValidation.WARNING
        else:
            return IstioConfigValidation.VALID

    def _get_item_status(self, element):
        _valid = len(self.browser.elements(
            parent=element,
            locator='.//*[contains(@style, "color: rgb(62, 134, 53)")]')) > 0
        _not_valid = len(self.browser.elements(
            parent=element,
            locator='.//*[contains(@style, "danger")]')) > 0
        _warning = len(self.browser.elements(
            parent=element,
            locator='.//*[contains(@style, "warning")]')) > 0
        return get_validation(_valid, _not_valid, _warning)

    @property
    def all_items(self):
        return self.items


class TableView3ScaleConfig(TableViewAbstract):
    CREATE_3SCALE_HANDLER = 'Create New 3scale Handler'
    TABLE_ROOT = './/table[contains(@class, "pf-c-table")]'
    CONFIG_INPUT = '//input[@id="{}"]'
    CONFIG_DETAILS_ROOT = './/*[contains(@class, "pf-c-form")]'
    CREATE_HANDLER_BUTTON = './/button[text()="Create"]'
    UPDATE_HANDLER_BUTTON = './/button[text()="Save"]'

    def __init__(self, parent, locator=None, logger=None):
        TableViewAbstract.__init__(self, parent, locator=self.CONFIG_DETAILS_ROOT, logger=logger)
        self._handler_name = TextInput(parent=self,
                                       locator=self.CONFIG_INPUT.format('handlerName'))
        self._service_id = TextInput(parent=self,
                                     locator=self.CONFIG_INPUT.format('serviceId'))
        self._system_url = TextInput(parent=self,
                                     locator=self.CONFIG_INPUT.format('systemUrl'))
        self._access_token = TextInput(parent=self,
                                       locator=self.CONFIG_INPUT.format('accessToken'))

    def get_details(self, load_only=False):
        if load_only:
            return BreadCrumb(self.parent)
        _name = self._handler_name.value
        _service_id = self._service_id.value
        _system_url = self._system_url.value
        _access_token = self._access_token.value
        return ThreeScaleHandler(name=_name,
                                 service_id=_service_id,
                                 system_url=_system_url,
                                 access_token=_access_token)

    @property
    def items(self):
        self.browser.click(self.parent.refresh)
        wait_to_spinner_disappear(self.browser)

        _items = []
        for el in self.browser.elements('//tbody//tr', parent=self.TABLE_ROOT):
            # get rule name and namespace
            _columns = self.browser.elements(self.COLUMN, parent=el)
            _name = _columns[0].text.replace('3S', '').strip()
            _service_id = _columns[1].text.replace('ID', '').strip()
            _system_url = _columns[2].text.replace('URL', '').strip()

            _config = ThreeScaleHandler(name=_name,
                                        service_id=_service_id,
                                        system_url=_system_url)
            # append this item to the final list
            _items.append(_config)
        return _items

    def create_3scale_handler(self, name, service_id, system_url, access_token):
        """
        Creates 3scale Handler.
        """
        self.parent.actions.select(self.CREATE_3SCALE_HANDLER)
        wait_to_spinner_disappear(self.browser)
        self._handler_name.fill(name)
        self._service_id.fill(service_id)
        self._system_url.fill(system_url)
        self._access_token.fill(access_token)
        create_button = self.browser.element(
                parent=self.CONFIG_DETAILS_ROOT,
                locator=(self.CREATE_HANDLER_BUTTON))
        wait_displayed(create_button)
        self.browser.click(create_button)

    def update_3scale_handler(self, service_id, system_url, access_token):
        """
        Update 3scale Handler.
        """
        self._service_id.fill(service_id)
        self._system_url.fill(system_url)
        self._access_token.fill(access_token)
        save_button = self.browser.element(
                parent=self.CONFIG_DETAILS_ROOT,
                locator=(self.UPDATE_HANDLER_BUTTON))
        wait_displayed(save_button)
        self.browser.click(save_button)


class TableViewAppWorkloads(TableViewAbstract):
    ROWS = ('//div[contains(@class, "pf-c-data-list__item-content")]'
            '//h3[contains(text(), "Workloads")]/..'
            '/ul[contains(@class, "pf-c-list")]/li')
    COLUMN = './/a'

    @property
    def items(self):

        _items = []
        for el in self.browser.elements(locator=self.ROWS,
                                        parent=self.ROOT):
            _value = self.browser.element(
                locator=self.COLUMN, parent=el).text
            # create Workload instance
            _workload = AppWorkload(
                name=_value,
                istio_sidecar=self._item_sidecar_icon(el))
            # append this item to the final list
            _items.append(_workload)
        return _items


class TableViewAppServices(TableViewAbstract):
    ROWS = ('//div[contains(@class, "pf-c-data-list__item-content")]'
            '//h3[contains(text(), "Services")]/..'
            '/ul[contains(@class, "pf-c-list")]/li/a')

    @property
    def items(self):

        _items = []
        for el in self.browser.elements(locator=self.ROWS,
                                        parent=self.ROOT):
            _items.append(el.text)
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
        wait_to_spinner_disappear(self.browser)
        self.browser.wait_for_element(locator='//section[@id="pf-tab-section-0-service-tabs"]',
                                      parent=self.ROOT)

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
            'pf-tab-section-0-service-tabs'),
                                        parent=self.ROOT):
            _columns = list(self.browser.elements(locator=self.COLUMN, parent=el))

            _name = _columns[0].text.strip()
            _type = _columns[1].text.strip()
            _created_at_ui = _columns[3].text.strip()
            _created_at = self._get_date_tooltip(_columns[3])
            _resource_version = _columns[4].text.strip()

            # workload object creation
            _workload = WorkloadDetails(
                name=_name,
                workload_type=_type,
                labels=self._get_labels(_columns[2]),
                created_at=parse_from_rest(_created_at),
                created_at_ui=_created_at_ui,
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
        wait_to_spinner_disappear(self.browser)
        self.browser.wait_for_element(locator=self.ROWS, parent=self.ROOT)

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
    VS_ROWS = '//section[@id="{}"]//table[contains(@class, "table")]'\
        '//tbody//tr//td//a[text()="{}"]/../..'
    VS_ROUTES = '//section[@id="{}"]//table[contains(@class, "pf-c-table")]'\
        '//tbody//tr'

    def open(self):
        wait_to_spinner_disappear(self.browser)
        tab = self.browser.element(locator=self.SERVICES_TAB.format(self.VS_TEXT),
                                   parent=self.SERVICE_DETAILS_ROOT)
        try:
            self.browser.click(tab)
        finally:
            self.browser.click(tab)
        wait_to_spinner_disappear(self.browser)
        self.browser.wait_for_element(locator='//section[@id="pf-tab-section-1-service-tabs"]',
                                      parent=self.ROOT)

    def get_overview(self, name):
        self.open()

        _row = self.browser.element(locator=self.VS_ROWS.format(
                'pf-tab-section-1-service-tabs', name),
                                        parent=self.ROOT)
        _columns = list(self.browser.elements(locator=self.COLUMN, parent=_row))

        self.browser.click('.//a', parent=_columns[1])
        wait_to_spinner_disappear(self.browser)

        _name = self.browser.text(
            locator=self.OVERVIEW_HEADER.format(self.NAME),
            parent=self.OVERVIEW_DETAILS_ROOT).replace(self.NAME, '').strip()
        _created_at_ui = self.browser.text(locator=self.OVERVIEW_HEADER.format(self.CREATED_AT),
                                           parent=self.OVERVIEW_DETAILS_ROOT).replace(
                                            self.CREATED_AT, '').strip()
        _created_at = self._get_date_tooltip(self.browser.element(
            locator=self.OVERVIEW_HEADER.format(self.CREATED_AT),
            parent=self.OVERVIEW_DETAILS_ROOT))
        _resource_version = self.browser.text(
            locator=self.OVERVIEW_HEADER.format(self.RESOURCE_VERSION),
            parent=self.OVERVIEW_DETAILS_ROOT).replace(self.RESOURCE_VERSION, '').strip()
        _hosts = get_texts_of_elements(self.browser.elements(
            locator=self.HOSTS_PROPERTIES.format(self.HOSTS),
            parent=self.OVERVIEW_DETAILS_ROOT))
        _http_route = self.browser.text_or_default(
            locator=self.OVERVIEW_PROPERTIES.format(self.HTTP_ROUTE),
            parent=self.OVERVIEW_DETAILS_ROOT).replace(self.HTTP_ROUTE, '').strip()
        _gateway_elements = self.browser.elements(
            locator='//div[contains(@class, "pf-c-card__body")]/ul[contains(@class, "details")]/li',
            parent=self.OVERVIEW_DETAILS_ROOT)
        _status = self._get_overview_status(self.OVERVIEW_DETAILS_ROOT)
        _weights = []
        _gateways = []

        for el in self.browser.elements(locator=self.VS_ROUTES.format(
                'pf-tab-section-0-basic-tabs'),
                parent=self.OVERVIEW_DETAILS_ROOT):
            _columns = list(self.browser.elements(locator=self.COLUMN, parent=el))

            _weight_status = _columns[0].text.strip()
            _host = _columns[1].text.strip()
            _subset = _columns[2].text.strip()
            _port = _columns[3].text.strip().replace('-', '')
            _weight = _columns[4].text.strip().replace('-', '')
            if _host == "Host" and _port == "Port":
                continue

            _weights.append(VirtualServiceWeight(host=_host,
                                                 status=_weight_status
                                                 if _weight_status != '' else None,
                                                 subset=_subset if _subset != '-' else None,
                                                 port=int(_port) if _port != '' else None,
                                                 weight=int(_weight) if _weight != '' else None))

        for el in _gateway_elements:
            try:
                _link = self.browser.element(
                    locator='/a', parent=el)
                _gateways.append(
                    VirtualServiceGateway(
                        text=el.text, link=self.browser.get_attribute('href', _link)))
            except NoSuchElementException:
                _gateways.append(VirtualServiceGateway(text=el.text))

        # back to service details
        self.back_to_service_info(parent=self.OVERVIEW_DETAILS_ROOT)

        return VirtualService(
                status=_status,
                name=_name,
                created_at=parse_from_rest(_created_at),
                created_at_ui=_created_at_ui,
                resource_version=_resource_version,
                http_route=to_linear_string(
                    _http_route if _http_route != self.NONE else ''),
                hosts=_hosts,
                weights=_weights,
                gateways=_gateways)

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
            'pf-tab-section-1-service-tabs'),
                                        parent=self.ROOT):
            _columns = list(self.browser.elements(locator=self.COLUMN, parent=el))
            if len(_columns) < 2:
                # empty row
                continue
            _name = _columns[1].text.strip()
            _created_at_ui = _columns[2].text.strip()
            _created_at = self._get_date_tooltip(_columns[2])
            _resource_version = _columns[3].text.strip()
            # create Virtual Service instance
            _virtual_service = VirtualService(
                status=self._get_item_status(_columns[0]),
                name=_name,
                created_at=parse_from_rest(_created_at),
                created_at_ui=_created_at_ui,
                resource_version=_resource_version)
            # append this item to the final list
            _items.append(_virtual_service)
        return _items


class TableViewDestinationRules(TableViewAbstract):
    DR_ROWS = '//section[@id="{}"]//table[contains(@class, "table")]'\
        '//tbody//tr//td//a[text()="{}"]/../..'
    DR_TEXT = 'Destination Rules'

    def open(self):
        wait_to_spinner_disappear(self.browser)
        tab = self.browser.element(locator=self.SERVICES_TAB.format(self.DR_TEXT),
                                   parent=self.SERVICE_DETAILS_ROOT)
        try:
            self.browser.click(tab)
        finally:
            self.browser.click(tab)
        wait_to_spinner_disappear(self.browser)
        self.browser.wait_for_element(locator='//section[@id="pf-tab-section-2-service-tabs"]',
                                      parent=self.ROOT)

    def get_overview(self, name):
        self.open()

        _row = self.browser.element(locator=self.DR_ROWS.format(
                'pf-tab-section-2-service-tabs', name),
                                        parent=self.ROOT)
        _columns = list(self.browser.elements(locator=self.COLUMN, parent=_row))

        self.browser.click('.//a', parent=_columns[1])
        wait_to_spinner_disappear(self.browser)

        _name = self.browser.text(
            locator=self.OVERVIEW_HEADER.format(self.NAME),
            parent=self.OVERVIEW_DETAILS_ROOT).replace(self.NAME, '').strip()
        _created_at_ui = self.browser.text(locator=self.OVERVIEW_PROPERTIES.format(self.CREATED_AT),
                                           parent=self.OVERVIEW_DETAILS_ROOT).replace(
                                            self.CREATED_AT, '').strip()
        _created_at = self._get_date_tooltip(self.browser.element(
            locator=self.OVERVIEW_PROPERTIES.format(self.CREATED_AT),
            parent=self.OVERVIEW_DETAILS_ROOT))
        _resource_version = self.browser.text(
            locator=self.OVERVIEW_PROPERTIES.format(self.RESOURCE_VERSION),
            parent=self.OVERVIEW_DETAILS_ROOT).replace(self.RESOURCE_VERSION, '').strip()
        _host = self.browser.text(
            locator=self.OVERVIEW_PROPERTIES.format(self.HOST),
            parent=self.OVERVIEW_DETAILS_ROOT).replace(self.HOST, '').strip()
        _traffic_policy = self.browser.text_or_default(
            locator='//div[@id="traffic_policy"]',
            parent=self.OVERVIEW_DETAILS_ROOT).\
            replace(self.NO_TRAFFIC_POLICY, self.NONE).strip()
        _subsets = self.browser.text_or_default(
            locator=('.//div[contains(@class, "pf-c-card__body")]//'
                     'h2[@data-pf-content="true" and contains(text(), "{}")]/..//tbody').format(
                        self.SUBSETS),
            parent=self.OVERVIEW_DETAILS_ROOT).\
            replace(self.NO_SUBSETS, self.NONE).\
            replace(' :', '').strip()
        _status = self._get_overview_status(self.OVERVIEW_DETAILS_ROOT)

        # back to service details
        self.back_to_service_info(parent=self.OVERVIEW_DETAILS_ROOT)

        return DestinationRule(
                status=_status,
                name=_name,
                host=_host,
                created_at=parse_from_rest(_created_at),
                created_at_ui=_created_at_ui,
                resource_version=_resource_version,
                traffic_policy=to_linear_string(
                    _traffic_policy if _traffic_policy != self.NONE else ''),
                subsets=to_linear_string(_subsets if _subsets != self.NONE else ''))

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
                'pf-tab-section-2-service-tabs'),
                                        parent=self.ROOT):
            _columns = list(self.browser.elements(locator=self.COLUMN, parent=el))
            if len(_columns) < 2:
                # empty row
                continue
            _name = _columns[1].text.strip()
            _traffic_policy = _columns[2].text.strip()
            _subsets = _columns[3].text.strip()
            _host = _columns[4].text.strip()
            _created_at_ui = _columns[5].text.strip()
            _created_at = self._get_date_tooltip(_columns[5])
            _resource_version = _columns[6].text.strip()
            # create Destination Rule instance
            _destination_rule = DestinationRule(
                status=self._get_item_status(_columns[0]),
                name=_name,
                host=_host,
                created_at=parse_from_rest(_created_at),
                created_at_ui=_created_at_ui,
                resource_version=_resource_version,
                traffic_policy=to_linear_string(
                    _traffic_policy if _traffic_policy != self.NONE else ''),
                subsets=to_linear_string(_subsets if _subsets != self.NONE else ''))
            # append this item to the final list
            _items.append(_destination_rule)
        return _items


class TableViewWorkloadPods(TableViewAbstract):
    POD_TEXT = 'Pods'
    SECTION_ID = 'pf-tab-section-0-service-tabs'
    PODS_SECTION_ROOT = '//section[@id="{}"]'.format(SECTION_ID)
    TABLE_ROOT = '//table[contains(@class, "pf-c-table")]'

    def open(self):
        tab = self.browser.element(locator=self.SERVICES_TAB.format(self.POD_TEXT),
                                   parent=self.SERVICE_DETAILS_ROOT)
        try:
            self.browser.click(tab)
        finally:
            self.browser.click(tab)
        wait_to_spinner_disappear(self.browser)
        self.browser.wait_for_element(locator=self.TABLE_ROOT, parent=self.PODS_SECTION_ROOT)

    @property
    def number(self):
        _vs_text = self.browser.text(locator=self.SERVICES_TAB.format(self.POD_TEXT),
                                     parent=self.SERVICE_DETAILS_ROOT)
        return int(re.search(r'\d+', _vs_text).group())

    @property
    def items(self):
        self.open()
        self.click_more_labels(parent=self.ROOT)

        _items = []
        for el in self.browser.elements(locator=self.ROWS.format(
            self.SECTION_ID),
                                        parent=self.ROOT):
            _columns = list(self.browser.elements(locator=self.COLUMN, parent=el))
            if len(_columns) < 2:
                # empty row
                continue
            _name = _columns[1].text.strip()
            _created_at_ui = _columns[2].text.strip()
            _created_at = self._get_date_tooltip(_columns[2])
            _created_by = _columns[3].text.strip()
            _istio_init_containers = _columns[5].text.strip()
            _istio_containers = _columns[6].text.strip()
            _phase = _columns[7].text.strip()

            _items.append(WorkloadPod(
                        name=str(_name),
                        created_at=parse_from_rest(_created_at),
                        created_at_ui=_created_at_ui,
                        created_by=_created_by,
                        labels=self._get_labels(_columns[4]),
                        istio_init_containers=_istio_init_containers,
                        istio_containers=_istio_containers,
                        status=self._get_item_status(el),
                        phase=_phase))
        return _items


class TableViewServices(TableViewAbstract):
    SERVICES_TEXT = 'Services'
    SECTION_ID = 'pf-tab-section-1-service-tabs'
    PODS_SECTION_ROOT = '//section[@id="{}"]'.format(SECTION_ID)
    TABLE_ROOT = '//table[contains(@class, "pf-c-table")]'

    def open(self):
        tab = self.browser.element(locator=self.SERVICES_TAB.format(self.SERVICES_TEXT),
                                   parent=self.SERVICE_DETAILS_ROOT)
        try:
            self.browser.click(tab)
        finally:
            self.browser.click(tab)
        wait_to_spinner_disappear(self.browser)
        self.browser.wait_for_element(locator=self.TABLE_ROOT, parent=self.PODS_SECTION_ROOT)

    @property
    def number(self):
        _vs_text = self.browser.text(locator=self.SERVICES_TAB.format(self.SERVICES_TEXT),
                                     parent=self.SERVICE_DETAILS_ROOT)
        return int(re.search(r'\d+', _vs_text).group())

    @property
    def items(self):
        self.open()
        self.click_more_labels(parent=self.ROOT)

        _items = []
        for el in self.browser.elements(locator=self.ROWS.format(
            self.SECTION_ID),
                                        parent=self.ROOT):
            _columns = list(self.browser.elements(locator=self.COLUMN, parent=el))
            if len(_columns) < 2:
                # empty row
                continue
            _name = _columns[0].text.strip()
            _created_at_ui = _columns[1].text.strip()
            _created_at = self._get_date_tooltip(_columns[1])
            _type = _columns[2].text.strip()
            _resource_version = _columns[4].text.strip()
            _ip = _columns[5].text.strip()
            _ports = _columns[6].text.strip()

            _items.append(ServiceDetails(
                        name=_name,
                        created_at=parse_from_rest(_created_at),
                        created_at_ui=_created_at_ui,
                        service_type=str(_type),
                        labels=self._get_labels(_columns[3]),
                        resource_version=str(_resource_version),
                        ip=str(_ip),
                        ports=str(_ports.replace('\n', ' '))))
        return _items


class TabViewAbstract(ViewAbstract):
    """
        Abstract base class for all Tabs besides the Info tab.
        After opening the tab and reading the data, it it can back to Info tab.
    """

    def __init__(self, parent, tab_name=None, locator=None, logger=None):
        Widget.__init__(self, parent, logger=logger)
        self.tab_name = tab_name
        if locator:
            self.locator = locator
        else:
            self.locator = self.ROOT

    def __locator__(self):
        return self.locator

    def _get_item_health(self, element):
        _healthy = len(self.browser.elements(
            parent=element,
            locator='.//*[contains(@d, "M504")]')) > 0
        _not_healthy = len(self.browser.elements(
            parent=element,
            locator='.//*[contains(@d, "M512")]')) > 0
        _degraded = len(self.browser.elements(
            parent=element,
            locator='.//*[contains(@d, "M569")]')) > 0
        _not_available = len(self.browser.elements(
            parent=element,
            locator='.//*[contains(@d, "M520")]')) > 0
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


class TrafficView(TabViewAbstract):
    TRAFFIC_TAB = '//button[text()="Traffic"]'
    TRAFFIC_ROOT = '//section[@id="pf-tab-section-1-basic-tabs"]'
    ROWS = ('//table[contains(@class, "pf-c-table")]'
            '//span[contains(text(), "{}")]/../../tbody/tr')
    COLUMN = './/td'

    def open(self):
        tab = self.browser.element(locator=self.TRAFFIC_TAB,
                                   parent=self.ROOT)
        try:
            self.browser.click(tab)
        finally:
            self.browser.click(tab)
        wait_to_spinner_disappear(self.browser)
        self.browser.wait_for_element(locator=self.ROWS.format("Inbound"), parent=self.TRAFFIC_ROOT)

    def inbound_items(self):
        return self._bound_items(inbound=True)

    def outbound_items(self):
        return self._bound_items(inbound=False)

    def _bound_items(self, inbound=True):
        self.open()

        _items = []
        for el in self.browser.elements(
            locator=self.ROWS.format("Inbound" if inbound else "Outbound"),
                parent=self.TRAFFIC_ROOT):
            if "Not enough" in el.text:
                break
            _columns = list(self.browser.elements(locator=self.COLUMN, parent=el))

            _name = _columns[1].text.strip()
            _request_type = _columns[2].text.strip()
            _traffic = _columns[3].text.strip().replace('N/A', '0.0')

            # Traffic Item object creation
            _item = TrafficItem(
                status=self._get_item_health(_columns[0]),
                name=_name,
                object_type=self._get_type(_columns[1]),
                request_type=_request_type,
                rps=float(re.sub('rps.*', '', _traffic).strip()),
                success_rate=float(re.sub('\\%.*', '', re.sub('.*\\|', '', _traffic)).strip()))
            # append this item to the final list
            _items.append(_item)
        return _items

    def click_on(self, object_type, name, inbound=True):
        self.open()

        for el in self.browser.elements(
            locator=self.ROWS.format("Inbound" if inbound else "Outbound"),
                parent=self.TRAFFIC_ROOT):
            if "Not enough" in el.text:
                continue
            _columns = list(self.browser.elements(locator=self.COLUMN, parent=el))

            if name == _columns[1].text.strip() and self._get_type(_columns[1]) == object_type:
                self.browser.click(self.browser.element(parent=_columns[1], locator='.//a'))
                return self._bound_items(not inbound)
        return []

    def _get_type(self, element):
        _appliction = len(self.browser.elements(
            parent=element,
            locator='.//*[contains(@d, "M950")]')) > 0
        _workload = len(self.browser.elements(
            parent=element,
            locator='.//*[contains(@d, "M348")]')) > 0
        _service = len(self.browser.elements(
            parent=element,
            locator='.//*[contains(@d, "M1316")]')) > 0
        if _appliction:
            return TrafficType.APP
        elif _workload:
            return TrafficType.WORKLOAD
        elif _service:
            return TrafficType.SERVICE
        else:
            return TrafficType.UNKNOWN


class LogsView(TabViewAbstract):
    LOGS_TAB = '//button[contains(text(), "Logs")]'
    DROP_DOWN = '//*[contains(@class, "pf-c-select")]/*[contains(@aria-labelledby, "{}")]/..'

    pods = DropDown(locator=DROP_DOWN.format('wpl_pods'))
    tail_lines = DropDown(locator=DROP_DOWN.format('wpl_tailLines'))
    interval = DropDown(locator=DROP_DOWN.format('metrics_filter_interval_duration'))
    refresh = Button(locator='//button[@id="refresh_button"]')
    pod_textarea = Text(locator='//h5[not(contains(text(), "Istio proxy (sidecar)"))]/../textarea')
    proxy_textarea = Text(locator='//h5[contains(text(), "Istio proxy (sidecar)")]/../textarea')

    def open(self):
        tab = self.browser.element(locator=self.LOGS_TAB,
                                   parent=self.ROOT)
        try:
            self.browser.click(tab)
        except (NoSuchElementException, StaleElementReferenceException):
            try:
                self.browser.click(tab)
            except StaleElementReferenceException:
                pass
        wait_to_spinner_disappear(self.browser)
        self.logs_switch = ButtonSwitch(parent=self, label="Side by Side")
        self.log_hide = FilterInput(parent=self, locator='//input[@id="log_hide"]')


class MetricsView(TabViewAbstract):
    METRICS_TAB = '//ul[contains(@class, "pf-c-tabs__list")]//li//button[contains(text(), "{}")]'
    DROP_DOWN = '//*[contains(@class, "pf-c-select")]/*[contains(@aria-labelledby, "{}")]/..'

    filter = CheckBoxFilter(filter_name="Metrics Settings")
    destination = DropDown(locator=DROP_DOWN.format('metrics_filter_reporter'))
    duration = DropDown(locator=DROP_DOWN.format('metrics_filter_interval_duration'))
    interval = DropDown(locator=DROP_DOWN.format('metrics-refresh'))
    refresh = Button(locator='.//button[@id="metrics-refresh_btn"]')

    def open(self):
        tab = self.browser.element(locator=self.METRICS_TAB.format(self.tab_name),
                                   parent=self.ROOT)
        try:
            self.browser.click(tab)
        except (NoSuchElementException, StaleElementReferenceException):
            try:
                self.browser.click(tab)
            except StaleElementReferenceException:
                pass
        wait_to_spinner_disappear(self.browser)
        wait_displayed(self.destination)
        try:
            self.view_in_grafana = self.browser.get_attribute(
                'href', self.browser.element(
                    locator='//a[contains(text(), "View in Grafana")]',
                    parent=self.ROOT))
        except (NoSuchElementException):
            self.view_in_grafana = None
            pass


class TracesView(TabViewAbstract):
    TRACES_TAB = '//button[contains(text(), "Traces")]'
    traces = Traces()

    def open(self):
        tab = self.browser.element(locator=self.TRACES_TAB,
                                   parent=self.ROOT)
        try:
            self.browser.click(tab)
        finally:
            self.browser.click(tab)
        wait_to_spinner_disappear(self.browser)
