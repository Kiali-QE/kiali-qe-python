# -*- coding: utf-8 -*-
from widgetastic_sws import Table, Search, ReactView, Menu, PaginationPane


class ServiceListView(ReactView):
    menu = Menu()
    search = Search()
    paginator = PaginationPane()
    services = Table('//div[contains(@class, "list-group")]')

    def __init__(self, parent, logger=None, **kwargs):
        super(ReactView, self).__init__(parent=parent, logger=logger)
        self.load()

    def load(self):
        self.menu.services.click()
        self.wait_displayed()

    def simple_search(self, text):
        self.search.simple_search(text)
        self.wait_displayed()

    def get_all(self):
        rows = []
        for _ in self.paginator.pages():
            self.wait_displayed()
            for row in self.services:
                rows.append(row)
        return rows

    @property
    def is_displayed(self):
        return self.services.is_displayed
