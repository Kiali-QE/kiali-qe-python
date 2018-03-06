# -*- coding: utf-8 -*-
from widgetastic_sws import Table, Search, ReactView


class ServiceListView(ReactView):
    search = Search()
    services = Table('//div[contains(@class, "list-group")]')

    @property
    def is_displayed(self):
        return self.services.is_displayed
