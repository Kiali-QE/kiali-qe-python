# -*- coding: utf-8 -*-
import re
from widgetastic_sws import Table, Search, ReactView, PaginationPane
from entities import Service, Rule


class Menu(ReactView):
    """ Represents Menu on the left side """

    @property
    def services(self):
        return self.browser.element('//a//span[text()="Services"]')

    @property
    def graph(self):
        return self.browser.element('//a//span[text()="Graph"]')

    @property
    def rules(self):
        return self.browser.element('//a//span[text()="Istio Mixer"]')


class ListView(ReactView):
    menu = Menu()
    search = Search()
    paginator = PaginationPane()
    items = Table('//div[contains(@class, "list-group")]')

    def __init__(self, parent, logger=None, **kwargs):
        super(ReactView, self).__init__(parent=parent, logger=logger)
        self.load()

    def simple_search(self, text):
        self.search.simple_search(text)
        self.wait_displayed()

    @property
    def is_displayed(self):
        return self.items.is_displayed


class ServiceListView(ListView):

    def load(self):
        self.menu.services.click()
        self.wait_displayed()

    def get_all(self):
        rows = []
        for _ in self.paginator.pages():
            self.wait_displayed()
            for row in self.items:
                values = row[0].split_text()
                rows.append(Service(name=values[0], namespace=values[1],
                                    replicas=values[3], available_replicas=values[4]))
        return rows


class RuleListView(ListView):

    def load(self):
        self.menu.rules.click()
        self.wait_displayed()

    def get_all(self):
        rows = []
        for _ in self.paginator.pages():
            self.wait_displayed()
            for row in self.items:
                values = row[0].split_text()
                rows.append(Rule(name=values[0], namespace=values[1],
                                 handler=values[2], instances=values[3]))
        return rows
