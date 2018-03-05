# -*- coding: utf-8 -*-
import atexit
from collections import namedtuple
from datetime import date
import json
from math import ceil
import math
import os
import re
import six
from tempfile import NamedTemporaryFile

from cached_property import cached_property
from jsmin import jsmin
from lxml.html import document_fromstring
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.keys import Keys
from wait_for import TimedOutError, wait_for
from widgetastic.exceptions import NoSuchElementException
from widgetastic.log import logged
from widgetastic.utils import ParametrizedLocator, Parameter, ParametrizedString, attributize_string
from widgetastic.utils import VersionPick, Version
from widgetastic.widget import (
    Table as VanillaTable,
    TableColumn as VanillaTableColumn,
    TableRow as VanillaTableRow,
    Widget,
    View,
    Select,
    TextInput,
    Text,
    Checkbox,
    ParametrizedView,
    FileInput as BaseFileInput,
    ClickableMixin,
    ConditionalSwitchableView,
    do_not_read_this_widget)
from widgetastic.xpath import quote
from widgetastic_patternfly import (
    Accordion as PFAccordion, BootstrapSwitch, BootstrapTreeview,
    BootstrapSelect, Button, Dropdown, Input, VerticalNavigation, Tab)


class ReactView(View):
    def wait_displayed(self, timeout='10s'):
        wait_for(lambda: self.is_displayed, timeout=timeout, delay=0.2)

class Search(View):
    """ Represents search_text control """
    search_input = Input(locator="//div[contains(@class, 'input-group')]//input[contains(@class, 'form-control')]")

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
    
    @property
    def checkbox(self):
        try:
            return self.browser.element('./input[@type="checkbox"]', parent=self)
        except NoSuchElementException:
            return None

    @property
    def checked(self):
        checkbox = self.checkbox
        if checkbox is None:
            return None
        return self.browser.is_selected(checkbox)

    def check(self):
        if not self.checked:
            self.browser.click(self.checkbox)

    def uncheck(self):
        if self.checked:
            self.browser.click(self.checkbox)


class TableRow(VanillaTableRow):
    Column = TableColumn


class Table(VanillaTable):
    SORTED_BY_LOC = '|'.join([
        # Old one
        './thead/tr/th[contains(@class, "sorting_asc") or contains(@class, "sorting_desc")]',
        # New one
        './thead/tr/th[./div/i[contains(@class, "fa-sort-")]]/a',
        './thead/tr/th[contains(@class, "ng-binding ng-scope")]'])
    SORTED_BY_CLASS_LOC = '|'.join([
        # Old one
        './thead/tr/th[contains(@class, "sorting_asc") or contains(@class, "sorting_desc")]',
        # New one
        './thead/tr/th/div/i[contains(@class, "fa-sort-")]'])
    SORT_LINK = './thead/tr/th[{}]'
    ROWS = './a'
    ROW_AT_INDEX = './a[{0}]'
    Row = TableRow

    @property
    def sorted_by(self):
        """Returns the name of column that the table is sorted by. Attributized!"""
        return attributize_string(self.browser.text(self.SORTED_BY_LOC, parent=self))

    @property
    def sort_order(self):
        """Returns the sorting order of the table for current column.

        Returns:
            ``asc`` or ``desc``
        """
        klass = self.browser.get_attribute('class', self.SORTED_BY_CLASS_LOC, parent=self)
        # We get two group matches and one of them will always be None, therefore empty filter
        # for filtering the None out
        try:
            return filter(
                None, re.search(r'sorting_(asc|desc)|fa-sort-(asc|desc)', klass).groups())[0]
        except IndexError:
            raise ValueError(
                'Could not figure out which column is used for sorting now. The class was {!r}'
                .format(klass))
        except AttributeError:
            raise TypeError('SORTED_BY_CLASS_LOC tag did not provide any class. Maybe fix Table?')

    def click_sort(self, column):
        """Clicks the sorting link in the given column. The column gets attributized."""
        self.logger.info('click_sort(%r)', column)
        column = attributize_string(column)
        column_position = self.header_index_mapping[self.attributized_headers[column]]
        self.browser.click(self.SORT_LINK.format(column_position + 1), parent=self)

    def sort_by(self, column, order='asc'):
        """Sort table by column and in given direction.

        Args:
            column: Name of the column, can be normal or attributized.
            order: Sorting order. ``asc`` or ``desc``.
        """
        self.logger.info('sort_by(%r, %r)', column, order)
        column = attributize_string(column)

        # Sort column
        if self.sorted_by != column:
            self.click_sort(column)
        else:
            self.logger.debug('sort_by(%r, %r): column already selected', column, order)

        # Sort order
        if self.sort_order != order:
            self.logger.info('sort_by(%r, %r): changing the sort order', column, order)
            self.click_sort(column)
            self.logger.debug('sort_by(%r, %r): order already selected', column, order)
