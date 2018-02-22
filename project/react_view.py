# -*- coding: utf-8 -*-

from widgetastic.widget import View, Text, TextInput, Select
from widgetastic_patternfly import (Dropdown,
                                    BootstrapSwitch,
                                    BootstrapNav,
                                    Tab,
                                    Button)


class ButtonsView(View):
    defaultButton = Button('Default Button')
    button1 = Button('Default Normal')
    button2 = Button(title='Destructive title')
    button3 = Button(title='noText', classes=[Button.PRIMARY])
