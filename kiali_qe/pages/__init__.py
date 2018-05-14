"""update this doc"""
from widgetastic.widget import View, Text
from kiali_qe.components import (
    Button,
    DropDown,
    Filter,
    ListViewIstioMixer,
    ListViewServices,
    MainMenu,
    Pagination,
    SortDropDown,
    CheckBoxFilter)
from kiali_qe.components.enums import MainMenuEnum as MENU
from kiali_qe.utils.log import logger

XP_DROP_DOWN = '//*[contains(@class, "dropdown")]/*[@id="{}"]/../..'
XP_BUTTON_SWITCH = '//*[contains(@class, "bootstrap-switch")]//*[text()="{}"]/../..'


class RootPage(View):
    PAGE_MENU = None

    def __init__(self, parent, logger=logger):
        View.__init__(self, parent, logger=logger)
        self.load()

    main_menu = MainMenu()
    page_header = Text(locator='//*[contains(@class, "container-fluid")]//h2')

    def load(self):
        # load page only if PAGE_MENU is available
        if self.PAGE_MENU is not None and self.main_menu.selected != self.PAGE_MENU:
            self.main_menu.select(self.PAGE_MENU)

    def reload(self):
        self.browser.refresh()
        self.load()

    @property
    def navbar(self):
        return self.main_menu.navbar

    @property
    def page_header(self):
        return self.page_header_el.text


class GraphPage(RootPage):
    PAGE_MENU = MENU.GRAPH.text

    namespace = DropDown(locator=XP_DROP_DOWN.format('namespace-selector'))
    duration = DropDown(locator=XP_DROP_DOWN.format('graph_filter_interval_duration'))
    layout = DropDown(locator=XP_DROP_DOWN.format('graph_filter_layouts'))
    filter = CheckBoxFilter()
    refresh = Button(locator='.//button//*[contains(@class, "fa-refresh")]')
    # TODO: implement graph control code


class ServicesPage(RootPage):
    PAGE_MENU = MENU.SERVICES.text

    filter = Filter()
    sort = SortDropDown(locator=XP_DROP_DOWN.format('sortTypeMenu'))
    rate_interval = DropDown(locator=XP_DROP_DOWN.format('rateIntervalDropDown'))
    content = ListViewServices()
    pagination = Pagination()


class IstioMixerPage(RootPage):
    PAGE_MENU = MENU.ISTIO_MIXER.text

    filter = Filter()
    sort = SortDropDown(locator=XP_DROP_DOWN.format('sortTypeMenu'))
    content = ListViewIstioMixer()
    pagination = Pagination()
