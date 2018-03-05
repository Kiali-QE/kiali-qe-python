# -*- coding: utf-8 -*-

from wait_for import wait_for
from widgetastic.widget import View, Text, TextInput, Select
from widgetastic_patternfly import (Dropdown,
                                    BootstrapSwitch,
                                    BootstrapNav,
                                    Tab,
                                    Button)

from widgetastic_sws import Table, Search, ReactView


class GraphView(ReactView):
    defaultButton = Button('Success Button')
    primaryButton = Button(title='noText', classes=[Button.PRIMARY])

class ButtonsView(ReactView):
    defaultButton = Button('Success Button')
    primaryButton = Button(title='noText', classes=[Button.PRIMARY])


class TableView(ReactView):
    search = Search()
    table = Table('//div[contains(@class, "list-group")]')
    
    @property
    def is_displayed(self):
        return self.table.is_displayed
