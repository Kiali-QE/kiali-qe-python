# -*- coding: utf-8 -*-
from selenium.webdriver.common.keys import Keys
from wait_for import wait_for
from widgetastic.widget import (
    Table as VanillaTable,
    TableColumn as VanillaTableColumn,
    TableRow as VanillaTableRow,
    View)
from widgetastic_patternfly import Input


class ReactView(View):
    def wait_displayed(self, timeout='10s'):
        wait_for(lambda: self.is_displayed, timeout=timeout, delay=0.2)


class Menu(View):
    """ Represents Menu on the left side """
    @property
    def services(self):
        return self.browser.element('//a//span[text()="Services"]')


class Search(View):
    """ Represents search_text control """
    search_input = Input(locator="//div[contains(@class, 'input-group')]//input[contains(@class, 'form-control')]")

    def simple_search(self, text):
        """ Search text using simple search """
        self.search_input.fill(text)
        self.browser.send_keys(Keys.ENTER, self.search_input)
        self.parent.wait_displayed()

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
