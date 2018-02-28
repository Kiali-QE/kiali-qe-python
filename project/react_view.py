# -*- coding: utf-8 -*-

from widgetastic.widget import View, Text, TextInput, Select
from widgetastic_patternfly import (Dropdown,
                                    BootstrapSwitch,
                                    BootstrapNav,
                                    Tab,
                                    Button)


class ButtonsView(View):
    defaultButton = Button('Success Button')
    primaryButton = Button(title='noText', classes=[Button.PRIMARY])
