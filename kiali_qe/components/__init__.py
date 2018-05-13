""" Update this doc"""
from widgetastic.widget import Widget, TextInput
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from kiali_qe.components.enums import HelpMenuEnum


class Button(Widget):
    ROOT = '//button'

    def __init__(self, parent, locator=None, logger=None):
        Widget.__init__(self, parent, logger=logger)
        if locator:
            self.locator = locator
        else:
            self.locator = self.ROOT
        self.wait_displayed()

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


class DropDown(Widget):
    ROOT = '//*[contains(@class, "form-group")]/*[contains(@class, "dropdown")]/..'
    SELECT_BUTTON = './/*[contains(@class, "dropdown-toggle")]'
    OPTIONS_LIST = './/*[contains(@class, "dropdown-menu")]//*[contains(@role, "menuitem")]'
    OPTION = ('.//*[contains(@class, "dropdown-menu")]'
              '//*[contains(@role, "menuitem") and text()="{}"]')

    def __init__(self, parent, locator=None, logger=None):
        Widget.__init__(self, parent, logger=logger)
        if locator:
            self.locator = locator
        else:
            self.locator = self.ROOT

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
        for el in self.browser.elements(locator=self.OPTIONS_LIST, parent=self):
            # on filter drop down, title comes in to options list.
            # Here it will be removed
            if self.browser.get_attribute('title', el).startswith('Filter by'):
                continue
            options.append(self.browser.text(el))
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
        if not self.is_displayed:
            return _filters
        for el in self.browser.elements(parent=self, locator=self.ITEMS):
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

    def remove(self, filter_name, value):
        self._filter_list.remove(filter_name, value)

    def clear_all(self):
        self._filter_list.clear_all()

    @property
    def active_filters(self):
        return self._filter_list.active_filters


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
        self.wait_displayed()

    def __locator__(self):
        return self.locator

    @property
    def _page_input(self):
        return TextInput(parent=self, locator=self.CURRENT_PAGE)

    @property
    def current_page(self):
        return int(self._page_input.read())

    def _move_to_page(self, page):
        self.browser.click(self.browser.element(parent=self, locator=page))

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

    @property
    def total_items(self):
        return int(self.browser.text(self.browser.element(parent=self, locator=self.TOTAL_ITEMS)))

    @property
    def total_pages(self):
        return int(self.browser.text(self.browser.element(parent=self, locator=self.TOTAL_PAGES)))

    @property
    def _dropdown_per_page(self):
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
    APP_NAME = BODY + '/h1'
    VERSION = BODY + '//*[contains(@class, "product-versions-pf")]//li'
    VERSION_NAME = './strong'
    TRADEMARK = BODY + '//*[contains(@class, "trademark-pf")]'
    CLOSE = HEADER + '//*[contains(@class, "close")]'

    def __init__(self, parent, logger=None):
        Widget.__init__(self, parent, logger=logger)

    @property
    def application_name(self):
        return self.browser.text(self.browser.element(self.APP_NAME, parent=self))

    def close(self):
        self.browser.click(self.browser.element(self.CLOSE, parent=self))

    @property
    def header(self):
        return self.browser.text(self.browser.element(self.HEADER, parent=self))

    @property
    def versions(self):
        return [
            self.browser.text(el)
            for el
            in self.browser.elements(self.VERSION, parent=self)]

    @property
    def trademark(self):
        return self.browser.text(self.browser.element(self.TRADEMARK, parent=self))


class NavBar(Widget):
    ROOT = '//*[contains(@class, "navbar")]'
    TOGGLE_NAVIGATION = './/*[contains(@class, "navbar-toggle")]'
    NAVBAR_RIGHT_MENU = '//*[contains(@class, "navbar-right")]//*[contains(@class, "dropdown")]'

    def __init__(self, parent, logger=None):
        Widget.__init__(self, parent, logger=logger)
        self.help_menu = DropDown(parent=self, locator=self.NAVBAR_RIGHT_MENU, logger=logger)

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


class ListViewAbstract(Widget):
    ROOT = '//*[contains(@class, "list-view-pf") and contains(@class, "list-view-pf-view")]'
    ITEMS = './/*[contains(@class, "list-group-item")]//*[contains(@class, "list-view-pf-body")]'
    ITEM_TEXT = './/*[contains(@class, "list-group-item-heading")]'
    SELECT_ITEM = ITEMS + '//span[text()="{}"]'
    SELECT_ITEM_WITH_NAMESPACE = SELECT_ITEM + '/small[text()="{}"]'

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
        if namespace is not None:
            self.browser.click(self.browser.element(
                self.SELECT_ITEM_WITH_NAMESPACE.format(name, namespace), parent=self))
        else:
            self.browser.click(self.browser.element(self.SELECT_ITEM.format(name), parent=self))

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
            items.extend(self.items)
        return items


class ListViewServices(ListViewAbstract):

    @property
    def items(self):
        _items = []
        for el in self.browser.elements(self.ITEMS, parent=self):
            # rule dict
            service = {}
            # get rule name and namespace
            name, namespace = self.browser.element(
                locator=self.ITEM_TEXT, parent=el).text.split('\n')
            service['name'] = name.strip()
            service['namespace'] = namespace.strip()
            # update istio sidecar logo
            service['istio_sidecar'] = len(self.browser.elements(
                parent=el, locator='.//img[contains(@class, "IstioLogo")]')) > 0
            # append this item to the final list
            _items.append(service)
        return _items


class ListViewIstioMixer(ListViewAbstract):
    ACTION_HEADER = ('.//*[contains(@class, "list-group-item-text")]'
                     '//strong[normalize-space(text())="{}"]/..')

    @property
    def items(self):
        _items = []
        for el in self.browser.elements(self.ITEMS, parent=self):
            # rule dict
            rule = {}
            action = {}
            # get rule name and namespace
            name, namespace = self.browser.element(
                locator=self.ITEM_TEXT, parent=el).text.split('\n')
            rule['name'] = name.strip()
            rule['namespace'] = namespace.strip()
            # get handler
            handler = self.browser.element(
                locator=self.ACTION_HEADER.format('Handler'),
                parent=el).text.split('Handler:', 1)[1].strip()
            action['handler'] = handler
            # get instances
            instances = self.browser.element(
                locator=self.ACTION_HEADER.format('Instances'),
                parent=el).text.split('Instances:', 1)[1].strip().split(',')
            action['instances'] = instances
            # get Match
            if 'Match:' in el.text:
                match = self.browser.element(
                    locator=self.ACTION_HEADER.format('Match'),
                    parent=el).text.split('Match:', 1)[1].strip()
                action['match'] = match.strip()
            # add action into rule dict
            rule['action'] = action
            # append this item to the final list
            _items.append(rule)
        return _items
