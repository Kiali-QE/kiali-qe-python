# -*- coding: utf-8 -*-
import re
from selenium.webdriver.common.keys import Keys
from wait_for import wait_for
from math import ceil
from widgetastic.exceptions import NoSuchElementException
from widgetastic.widget import (
    Table as VanillaTable,
    TableColumn as VanillaTableColumn,
    TableRow as VanillaTableRow,
    View,
    Widget)
from widgetastic_patternfly import (
    Input)
from widgetastic.xpath import quote


class ReactView(View):
    def wait_displayed(self, timeout='10s'):
        wait_for(lambda: self.is_displayed, timeout=timeout, delay=0.2)


class Menu(View):
    """ Represents Menu on the left side """

    @property
    def services(self):
        return self.browser.element('//a//span[text()="Services"]')

    @property
    def graph(self):
        return self.browser.element('//a//span[text()="Graph"]')


class Search(View):
    """ Represents search_text control """
    search_input = Input(
        locator="//div[contains(@class, 'input-group')]//input[contains(@class, 'form-control')]")

    def simple_search(self, text):
        """ Search text using simple search """
        self.search_input.fill(text)
        self.browser.send_keys(Keys.ENTER, self.search_input)

    @property
    def is_empty(self):
        """ Checks if simple search field is emply """
        return not bool(self.search_input.value)


class TableColumn(VanillaTableColumn):
    def __locator__(self):
        return self.browser.element('./div[{}]'.format(self.position + 1), parent=self.parent)


class TableRow(VanillaTableRow):
    Column = TableColumn


class Table(VanillaTable):
    ROWS = './a'
    ROW_AT_INDEX = './a[{0}]'
    Row = TableRow


class Paginator(Widget):
    """ Represents Paginator control that includes First/Last/Next/Prev buttons
    and a control displaying amount of items on current page vs overall amount.

    It is mainly used in Paginator Pane.
    """
    PAGINATOR_CTL = '//form[contains(@class, "content-view-pf-pagination")]'
    CUR_PAGE_CTL = '//span//span[contains(@class, "pagination-pf-items-current")]'
    TOTAL_PAGE_CTL = '//span//span[contains(@class, "pagination-pf-items-total")]'
    PAGE_BUTTON_CTL = '//a[contains(@title, {})]'

    @property
    def is_displayed(self):
        return self.browser.element(self.PAGINATOR_CTL, parent=self.parent_view).is_displayed()

    def __locator__(self):
        return self._paginator

    @property
    def _paginator(self):
        return self.browser.element(self.PAGINATOR_CTL, parent=self.parent_view)

    def _is_enabled(self, element):
        return 'disabled' not in element.find_element_by_xpath('..').get_attribute('class')

    def _click_button(self, cmd):
        cur_page_btn = self.browser.element(self.PAGE_BUTTON_CTL.format(quote(cmd)),
                                            parent=self._paginator)
        if self._is_enabled(cur_page_btn):
            self.browser.click(cur_page_btn)
        else:
            raise NoSuchElementException('such button {} is absent/grayed out'.format(cmd))

    def next_page(self):
        self._click_button('Next Page')

    def prev_page(self):
        self._click_button('Previous Page')

    def last_page(self):
        self._click_button('Last Page')

    def first_page(self):
        self._click_button('First Page')

    def page_info(self):
        cur_page = self.browser.element(self.CUR_PAGE_CTL, parent=self._paginator)
        curr_text = cur_page.text
        total_page = self.browser.element(self.TOTAL_PAGE_CTL, parent=self._paginator)
        total_text = total_page.text
        return re.search('(\d+)?-?(\d+)\s+of\s+(\d+)', curr_text + ' of ' + total_text).groups()


class PaginationPane(View):
    """ Represents Paginator Pane with the following controls.
    """
    ROOT = '//form[contains(@class, "content-view-pf-pagination")]'
    ITEMS_ON_PAGE_CTL = '//button[@id="pagination-row-dropdown"]'

    paginator = Paginator()

    @property
    def is_displayed(self):
        return self.paginator.is_displayed

    @property
    def exists(self):
        return self.is_displayed

    def _parse_pages(self):
        min_item, max_item, item_amt = self.paginator.page_info()

        item_amt = int(item_amt)
        max_item = int(max_item)
        items_per_page = self.items_per_page

        # obtaining amount of existing pages, there is 1 page by default
        if item_amt == 0:
            page_amt = 1
        else:
            # round up after dividing total item count by per-page
            page_amt = int(ceil(float(item_amt) / float(items_per_page)))

        # calculating current_page_number
        if max_item <= items_per_page:
            cur_page = 1
        else:
            # round up after dividing highest displayed item number by per-page
            cur_page = int(ceil(float(max_item) / float(items_per_page)))

        return cur_page, page_amt

    @property
    def items_per_page(self):
        items_per_page = self.browser.element(self.ITEMS_ON_PAGE_CTL, parent=self.paginator)
        text = items_per_page.text
        return int(re.sub(r'\s+', '', text))

    @property
    def cur_page(self):
        return self._parse_pages()[0]

    @property
    def pages_amount(self):
        return self._parse_pages()[1]

    def next_page(self):
        self.paginator.next_page()

    def prev_page(self):
        self.paginator.prev_page()

    def first_page(self):
        if self.cur_page != 1:
            self.paginator.first_page()

    def last_page(self):
        if self.cur_page != self.pages_amount:
            self.paginator.last_page()

    def pages(self):
        """Generator to iterate over pages, yielding after moving to the next page"""
        if self.exists:
            # start iterating at the first page
            if self.cur_page != 1:
                self.logger.debug('Resetting paginator to first page')
                self.first_page()

            # Adding 1 to pages_amount to include the last page in loop
            for page in range(1, self.pages_amount + 1):
                yield self.cur_page
                if self.cur_page == self.pages_amount:
                    # last or only page, stop looping
                    break
                else:
                    self.logger.debug('Paginator advancing to next page')
                    self.next_page()
        else:
            return

    @property
    def items_amount(self):
        return self.paginator.page_info()[2]

    @property
    def min_item(self):
        return self.paginator.page_info()[0]

    @property
    def max_item(self):
        return self.paginator.page_info()[1]

    def find_row_on_pages(self, table, *args, **kwargs):
        """Find first row matching filters provided by kwargs on the given table widget

        Args:
            table: Table widget object
            args: Filters to be passed to table.row()
            kwargs: Filters to be passed to table.row()
        """
        self.first_page()
        for _ in self.pages():
            try:
                row = table.row(*args, **kwargs)
            except IndexError:
                continue
            if not row:
                continue
            else:
                return row
        else:
            raise NoSuchElementException('Row matching filter {} not found on table {}'
                                         .format(kwargs, table))
