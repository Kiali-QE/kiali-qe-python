import random
import re
import time
import math


from kiali_qe.components import (
    BreadCrumb,
    wait_to_spinner_disappear,
    ListViewAbstract
)
from kiali_qe.components.enums import (
    ServicesPageFilter,
    IstioConfigPageFilter,
    WorkloadsPageFilter,
    ApplicationsPageFilter,
    OverviewPageFilter,
    OverviewViewType,
    IstioConfigObjectType as OBJECT_TYPE,
    IstioConfigValidation,
    MainMenuEnum as MENU,
    MetricsSource,
    MetricsHistograms,
    InboundMetricsFilter,
    OutboundMetricsFilter,
    TimeIntervalUIText,
    MetricsTimeInterval,
    GraphRefreshInterval,
    OverviewPageType,
    RoutingWizardType,
    ApplicationsPageSort,
    OverviewPageSort,
    WorkloadsPageSort,
    ServicesPageSort,
    IstioConfigPageSort,
    RoutingWizardTLS,
    RoutingWizardLoadBalancer,
    TrafficType,
    OverviewInjectionLinks,
    OverviewGraphTypeLink,
    OverviewTrafficLinks,
    TailLines,
    TLSMutualValues,
    IstioConfigObjectType,
    AuthPolicyType,
    AuthPolicyActionType,
    LabelOperation,
    VersionLabel,
    AppLabel,
    IstioSidecar,
    OverviewHealth,
    OverviewMTSLStatus,
    MeshWideTLSType
)
from kiali_qe.components.error_codes import (
    KIA0201,
    KIA0301,
    KIA0205,
    KIA0501,
    KIA0401,
    KIA0204,
    KIA0206
)
from kiali_qe.rest.kiali_api import ISTIO_CONFIG_TYPES
from kiali_qe.rest.openshift_api import APP_NAME_REGEX
from kiali_qe.utils import (
    is_equal,
    is_sublist,
    word_in_text,
    get_url,
    get_yaml_path,
    remove_from_list,
    dict_contains
)
from kiali_qe.utils.log import logger
from kiali_qe.utils.command_exec import oc_apply, oc_delete
from time import sleep
from selenium.webdriver.common.keys import Keys
from kiali_qe.pages import (
    ServicesPage,
    IstioConfigPage,
    WorkloadsPage,
    ApplicationsPage,
    OverviewPage,
    DistributedTracingPage,
    GraphPage
)


class AbstractListPageTest(object):
    FILTER_ENUM = None
    SORT_ENUM = None
    SELECT_ITEM = ListViewAbstract.ITEMS + '//a[text()="{}"]'
    SELECT_ITEM_WITH_NAMESPACE = SELECT_ITEM + '/../../td[contains(text(), "{}")]/..//a'

    def __init__(self, kiali_client, openshift_client, page):
        self.kiali_client = kiali_client
        self.openshift_client = openshift_client
        self.page = page

    def _namespaces_ui(self):
        return self.page.namespace.items

    def get_mesh_wide_tls(self):
        return self.page.content.get_mesh_wide_tls()

    def assert_all_items(self, namespaces=[], filters=[], force_clear_all=True,
                         label_operation=LabelOperation.OR):
        """
        Apply supplied filter in to UI, REST, OC and assert content

        Parameters
        ----------
        namespaces: list of namespace names
        filters : list
            A list for filter. filter should be a dict.
            filter = {'name': 'Namespace', 'value': 'bookinfo'}
            Take filter name from pre defined enum
        force_clear_all : boolean
            Default True.
            If this value is True, all existing applied filters will be removed.
            otherwise, will be adjusted with pre filter.
            on both case final outcome will be same.
        """
        raise NotImplementedError('This method should be implemented on sub class')

    def get_additional_filters(self, namespaces, current_filters):
        raise NotImplementedError('This method should be implemented on sub class')

    def open(self, name, namespace=None, force_refresh=False):
        # TODO added wait for unstable performance
        self.browser.send_keys_to_focused_element(Keys.ESCAPE)
        sleep(0.5)
        wait_to_spinner_disappear(self.browser)
        if namespace is not None:
            self.browser.click(self.browser.element(
                self.SELECT_ITEM_WITH_NAMESPACE.format(name, namespace), parent=self))
        else:
            self.browser.click(self.browser.element(self.SELECT_ITEM.format(name), parent=self))

        if force_refresh:
            self.page.page_refresh()
        wait_to_spinner_disappear(self.browser)

    def sidecar_presents(self, sidecar_filter, item_sidecar):
        if item_sidecar:
            return sidecar_filter == IstioSidecar.PRESENT.text
        else:
            return sidecar_filter == IstioSidecar.NOT_PRESENT.text

    def health_equals(self, health_filter, health):
        return health and health_filter == health.text

    def is_in_details_page(self, name, namespace):
        breadcrumb = BreadCrumb(self.page)
        if len(breadcrumb.locations) < 3:
            return False
        menu_location = breadcrumb.locations[0]
        if menu_location != self.page.PAGE_MENU:
            return False
        namespace_location = breadcrumb.locations[1]
        if namespace_location != "Namespace: " + namespace:
            return False
        object_location = breadcrumb.active_location
        if object_location != "{}".format(name):
            return False
        return True

    def apply_namespaces(self, namespaces, force_clear_all=False):
        """
        Apply supplied namespaces in to UI and assert with supplied and applied namespaces

        Parameters
        ----------
        namespaces : list
            A list for namespace names      .
        force_clear_all : boolean
            Default False.
            If this value is True, all existing applied namespaces will be removed.
        """
        logger.debug('Setting namespace filter: {}'.format(namespaces))
        _pre_filters = []
        # clear all filters
        if force_clear_all:
            self.page.namespace.clear_all()
            assert len(self.page.namespace.checked_items) == 0
        else:
            _pre_filters.extend(self.page.namespace.checked_items)

        if not namespaces:
            self.page.namespace.select_all()
        else:
            # apply namespaces
            for _filter in namespaces:
                if _filter not in _pre_filters:
                    self.page.namespace.check(_filter)
                if _filter in _pre_filters:
                    _pre_filters.remove(_filter)
            # remove filters not in list
            for _filter in _pre_filters:
                self.page.namespace.uncheck(_filter)

            self.assert_applied_namespaces(namespaces)

    def apply_filters(self, filters, force_clear_all=True):
        """
        Apply supplied filter in to UI and assert with supplied and applied filters

        Parameters
        ----------
        filters : list
            A list for filter. filter should be a dict.
            filter = {'name': 'Health', 'value': 'Healthy'}
            Take filter name from pre defined enum
        force_clear_all : boolean
            Default False.
            If this value is True, all existing applied filters will be removed.
            otherwise, will be adjusted with pre filter.
            on both case final outcome will be same.
        """
        logger.debug('Setting filters: {}'.format(filters))
        _pre_filters = []
        # clear all filters
        if force_clear_all:
            self.page.filter.clear_all()
            assert len(self.page.filter.active_filters) == 0
        else:
            _pre_filters.extend(self.page.filter.active_filters)

        # apply filter
        for _filter in filters:
            if _filter not in _pre_filters:
                self.page.filter.apply(filter_name=_filter['name'], value=_filter['value'])
            if _filter in _pre_filters:
                _pre_filters.remove(_filter)
        # remove filters not in list
        for _filter in _pre_filters:
            self.page.filter.remove(filter_name=_filter['name'], value=_filter['value'])

        self.assert_applied_filters(filters)
        self.browser.send_keys_to_focused_element(Keys.ESCAPE)
        sleep(0.2)

    def apply_label_operation(self, label_operation):
        assert self.page.filter._label_operation.is_displayed, 'Label Operation is not displayed'
        self.page.filter._label_operation.select(label_operation)

    def assert_filter_options(self):
        # test available options
        options_defined = [item.text for item in self.FILTER_ENUM]
        options_listed = self.page.filter.filters
        logger.debug('Options[defined:{}, defined:{}]'.format(options_defined, options_listed))
        assert is_equal(options_defined, options_listed), \
            'Defined: {}  Listed: {}'.format(options_defined, options_listed)

    def assert_applied_filters(self, filters):
        # validate applied filters
        wait_to_spinner_disappear(self.browser)
        _active_filters = self.page.filter.active_filters
        logger.debug('Filters[applied:{}, active:{}]'.format(filters, _active_filters))
        assert is_equal(filters, _active_filters), \
            'Defined: {}  Listed: {}'.format(filters, _active_filters)

    def assert_applied_namespaces(self, filters):
        # validate applied namespaces
        _active_filters = self.page.namespace.checked_items
        logger.debug('Filters[applied:{}, active:{}]'.format(filters, _active_filters))
        assert is_equal(filters, _active_filters), \
            'Defined: {}  Listed: {}'.format(filters, _active_filters)

    def assert_namespaces(self):
        namespaces_ui = self._namespaces_ui()
        namespaces_rest = self.kiali_client.namespace_list()
        namespaces_oc = self.openshift_client.namespace_list()
        logger.debug('Namespaces UI:{}'.format(namespaces_ui))
        logger.debug('Namespaces REST:{}'.format(namespaces_rest))
        logger.debug('Namespaces OC:{}'.format(namespaces_oc))
        assert is_equal(namespaces_ui, namespaces_rest)
        assert is_sublist(namespaces_rest, namespaces_oc)

    def assert_filter_feature_random(self):
        # clear filters if any
        # TODO: do we need to fail the test if we have filter defined before test?
        logger.debug('Filters before test:{}'.format(self.page.filter.active_filters))
        self.page.filter.clear_all()

        # get namespaces
        namespaces_ui = self._namespaces_ui()
        # apply a namespace filter
        # generate random filters list
        _defined_filters = []
        # random namespace filters
        assert len(namespaces_ui) > 0
        if len(namespaces_ui) > 3:
            _random_namespaces = random.sample(namespaces_ui, 3)
        else:
            _random_namespaces = namespaces_ui
        # add additional filters
        logger.debug('Adding additional filters')
        _defined_filters.extend(self.get_additional_filters(_random_namespaces, _defined_filters))
        logger.debug('Defined filters with additional filters:{}'.format(_defined_filters))

        # apply filters test
        _applied_filters = []
        for _defined_filter in _defined_filters:
            # add it in to applied list
            _applied_filters.append(_defined_filter)
            # apply filter and check the contents
            self.assert_all_items(namespaces=_random_namespaces,
                                  filters=_applied_filters,
                                  force_clear_all=False)

        # remove filters test
        for _defined_filter in _defined_filters:
            # remove it from our list
            _applied_filters.remove(_defined_filter)
            # apply filter and check the contents
            self.assert_all_items(namespaces=_random_namespaces,
                                  filters=_applied_filters,
                                  force_clear_all=False)
            # test remove all
            if len(_applied_filters) == 2:
                self.assert_all_items(namespaces=[], filters=[], force_clear_all=True)
                break

    def sort(self, sort_options=[]):
        """
        Sorts the listed items.

        Parameters
        ----------
        sort_options : array of 2 values
            option: SortEnum item, the sorting option to select
            is_ascending: boolean, sort ascending or descending
        """
        logger.debug('Sorting by: {}'.format(sort_options))
        if len(sort_options) == 2:
            self.page.sort.select(sort_options[0], sort_options[1])

    def assert_sort_options(self):
        # test available options
        options_defined = [item.text for item in self.SORT_ENUM]
        options_listed = self.page.sort.options
        logger.debug('Options[defined:{}, defined:{}]'.format(options_defined, options_listed))
        assert is_equal(options_defined, options_listed), \
            'Defined: {}  Listed: {}'.format(options_defined, options_listed)

    def assert_metrics_options(self, metrics_page, check_grafana=False):
        metrics_page.open()
        self._assert_metrics_settings(metrics_page)
        self._assert_metrics_destination(metrics_page)
        self._assert_metrics_duration(metrics_page)
        self._assert_metrics_interval(metrics_page)
        if check_grafana:
            self._assert_grafana_link(metrics_page)

    def _assert_metrics_settings(self, metrics_page):
        # test available filters
        options_defined = [item.text for item in (
            InboundMetricsFilter if "Inbound" in metrics_page.tab_name
            else OutboundMetricsFilter)]
        for item in MetricsHistograms:
            options_defined.append(item.text)
        options_listed = metrics_page.filter.items
        logger.debug('Filter options[defined:{}, listed:{}]'
                     .format(options_defined, options_listed))
        assert is_sublist(options_defined, options_listed), \
            ('Filter Options mismatch: defined:{}, listed:{}'
             .format(options_defined, options_listed))
        # enable disable each filter, use defined options
        for filter_name in options_defined:
            self._filter_test(metrics_page, filter_name)

    def _filter_test(self, page, filter_name, uncheck=True):
        # TODO 'Quantile 0.nnn' item's text is 2 lines
        if "Quantile" in str(filter_name):
            return
        # test filter checked
        page.filter.check(filter_name)
        assert page.filter.is_checked(filter_name) is True
        if uncheck:
            # test filter unchecked
            page.filter.uncheck(filter_name)
            assert page.filter.is_checked(filter_name) is False

    def _assert_metrics_destination(self, metrics_page):
        self._assert_metrics_options(metrics_page, MetricsSource, 'destination')

    def _assert_metrics_duration(self, metrics_page):
        self._assert_metrics_options(metrics_page, MetricsTimeInterval, 'duration')

    def _assert_metrics_interval(self, metrics_page):
        self._assert_metrics_options(metrics_page, GraphRefreshInterval, 'interval')

    def _assert_metrics_options(self, metrics_page, enum, attr_name):
        options_defined = [item.text for item in enum]
        attr = getattr(metrics_page, attr_name)
        options_listed = attr.options
        logger.debug('Options[defined:{}, listed:{}]'.format(options_defined, options_listed))
        assert is_equal(options_defined, options_listed), \
            ('Options mismatch: defined:{}, listed:{}'.format(options_defined, options_listed))

    def _assert_grafana_link(self, metrics_page):
        _response = self.kiali_client.get_response('getStatus')
        _products = _response['externalServices']
        assert metrics_page.view_in_grafana
        assert get_url(_products, 'Grafana') in metrics_page.view_in_grafana

    def is_host_link(self, link_name):
        self.browser.click(self.browser.element(locator=self.page.content.CONFIG_TAB_OVERVIEW,
                                                parent=self.page.content.CONFIG_TABS_PARENT))
        return len(self.browser.elements(
            './/div[@id="subsets"]//a[contains(text(), "{}")]'.format(
                link_name),
            parent=self.page.content.locator)) > 0

    def assert_breadcrumb_menu(self, name, namespace):
        breadcrumb = self.load_details_page(name, namespace, force_refresh=False, load_only=True)
        menu_location = breadcrumb.locations[0]
        assert menu_location == self.page.PAGE_MENU
        breadcrumb.click_location(menu_location)
        self.assert_applied_namespaces(filters=[namespace])

    def assert_breadcrumb_namespace(self, name, namespace):
        breadcrumb = self.load_details_page(name, namespace, force_refresh=False, load_only=True)
        namespace_location = breadcrumb.locations[1]
        assert namespace_location == "Namespace: " + namespace
        breadcrumb.click_location(namespace_location)
        self.assert_applied_namespaces(filters=[namespace])

    def assert_breadcrumb_object(self, name, namespace):
        breadcrumb = self.load_details_page(name, namespace, force_refresh=False, load_only=True)
        object_location = breadcrumb.active_location
        assert object_location == "{}".format(name)

    def assert_traces_tab(self, traces_tab):
        traces_tab.open()
        self.assert_traces_tab_content(traces_tab)

    def assert_traces_tab_content(self, traces_tab):
        assert not traces_tab.traces.is_oc_login_displayed, "OC Login should not be displayed"
        if not traces_tab.traces.has_no_results:
            assert traces_tab.traces.has_results

    def assert_logs_tab(self, logs_tab, all_pods=[]):
        _filter = "GET"
        logs_tab.open()
        if len(all_pods) == 0:
            assert 'No logs for Workload' in \
                self.browser.text(locator='//h5[contains(@class, "pf-c-title")]', parent=self)
            return
        assert is_equal(all_pods, logs_tab.pods.options)
        assert is_equal([item.text for item in TailLines],
                        logs_tab.tail_lines.options)
        _interval_options = [item.text for item in TimeIntervalUIText]
        _interval_options.append('Custom')
        assert is_equal(_interval_options,
                        logs_tab.duration.options)
        assert is_equal([item.text for item in GraphRefreshInterval],
                        logs_tab.interval.options)
        logs_tab.log_hide.fill(_filter)
        self.browser.click(logs_tab.refresh)
        wait_to_spinner_disappear(self.browser)
        assert _filter not in logs_tab.logs_textarea.text

    def assert_traffic(self, name, traffic_tab, self_object_type, traffic_object_type):
        bound_traffic = traffic_tab.traffic_items()
        for bound_item in bound_traffic:
            if bound_item.object_type == traffic_object_type:
                # skip istio traffic
                if "istio" in bound_item.name:
                    continue
                outbound_traffic = traffic_tab.click_on(
                    object_type=traffic_object_type, name=bound_item.name)
                found = False
                for outbound_item in outbound_traffic:
                    if (outbound_item.name == name
                        and outbound_item.object_type == self_object_type
                            and outbound_item.request_type == bound_item.request_type
                            and outbound_item.bound_traffic_type != bound_item.bound_traffic_type):
                        found = True
                        assert bound_item.status == outbound_item.status, \
                            "Inbound Status {} is not equal to Outbound Status {} for {}".format(
                                bound_item.status, outbound_item.status, name)
                        assert math.isclose(bound_item.rps, outbound_item.rps, abs_tol=2.0), \
                            "Inbound RPS {} is not equal to Outbound RPS {} for {}".format(
                                bound_item.rps,
                                outbound_item.rps,
                                name)
                        assert math.isclose(bound_item.success_rate,
                                            outbound_item.success_rate,
                                            abs_tol=2.0), \
                            "Inbound Rate {} is not equal to Outbound Rate {} for {}".format(
                                bound_item.success_rate, outbound_item.success_rate, name)
                if not found:
                    assert found, "{} {} {} not found in {}".format(name,
                                                                    self_object_type,
                                                                    bound_item.request_type,
                                                                    outbound_traffic)
                # check only the first item
                break

    def assert_graph_overview(self, name, namespace):
        logger.debug('Asserting Graph Overview for: {}, in namespace: {}'.format(
            name, namespace))
        self.load_details_page(name, namespace, force_refresh=False, load_only=True)
        self.page.content.graph_menu.select('Show full graph')
        graph_page = GraphPage(self.browser)
        side_panel = graph_page.side_panel
        assert not side_panel.get_namespace()
        if self.page.PAGE_MENU == MENU.APPLICATIONS.text:
            assert not side_panel.get_workload()
            assert side_panel.get_service()
            if side_panel.get_application():
                assert name == side_panel.get_application()
        elif self.page.PAGE_MENU == MENU.WORKLOADS.text:
            if side_panel.get_workload():
                assert name == side_panel.get_workload()
            assert side_panel.get_service()
            assert side_panel.get_application()
        elif self.page.PAGE_MENU == MENU.SERVICES.text:
            assert not side_panel.get_workload()
            if side_panel.get_service():
                assert name == side_panel.get_service()
            assert side_panel.get_application()
        else:
            assert False, "Graph Overview Page is not recognized"
        assert side_panel.show_traffic()
        assert side_panel.show_traces()
        # assert this on the end of tests
        _traces_tab = side_panel.go_to_traces()
        assert _traces_tab
        self.assert_traces_tab_content(_traces_tab)
        self.browser.execute_script("history.back();")

    def assert_istio_configs(self, object_ui, object_rest, object_oc, namespace):
        assert len(object_rest.istio_configs) == len(object_ui.istio_configs), \
            'UI configs should be equal to REST configs items'
        assert len(object_rest.istio_configs) == len(object_oc.istio_configs), \
            'REST configs should be equal to OC configs items'

        for istio_config_ui in object_ui.istio_configs:
            found = False
            for istio_config_rest in object_rest.istio_configs:
                if istio_config_ui.name == istio_config_rest.name and \
                    istio_config_ui.type == istio_config_rest.object_type and \
                        istio_config_ui.status == istio_config_rest.validation:
                    found = True
                    break
            if not found:
                assert found, 'Config {} not found in REST {}'.format(istio_config_ui,
                                                                      istio_config_rest)
            found = False
            for istio_config_oc in object_oc.istio_configs:
                if istio_config_ui.name == istio_config_oc.name and \
                    istio_config_ui.type == istio_config_oc.object_type and \
                        namespace == istio_config_oc.namespace:
                    found = True
                    break
            if not found:
                assert found, 'Config {} not found in OC {}'.format(istio_config_ui,
                                                                    istio_config_oc)
            config_overview_ui = self.page.content.card_view_istio_config.get_overview(
                    istio_config_ui.name,
                    istio_config_ui.type)
            config_details_oc = self.openshift_client.istio_config_details(
                namespace=namespace,
                object_name=istio_config_ui.name,
                object_type=istio_config_ui.type)
            assert istio_config_ui.status == config_overview_ui.status, \
                'UI Status {} not equal to Overview Status {}'.format(
                    istio_config_ui.status,
                    config_overview_ui.status)
            assert istio_config_ui.status == istio_config_rest.validation, \
                'UI Status {} not equal to REST Status {}'.format(
                    istio_config_ui.status,
                    istio_config_rest.status)
            if istio_config_ui.type == IstioConfigObjectType.PEER_AUTHENTICATION.text:
                assert '\'app\': \'{}\''.format(re.sub(
                    APP_NAME_REGEX,
                    '',
                    object_ui.name)) in config_overview_ui.text
            elif istio_config_ui.type == IstioConfigObjectType.VIRTUAL_SERVICE.text:
                for _host in config_overview_ui.hosts:
                    assert '\'host\': \'{}\''.format(_host) in config_details_oc.text
                for _gateway in config_overview_ui.gateways:
                    assert _gateway.text in config_details_oc.text
            else:
                assert '\'host\': \'{}\''.format(config_overview_ui.host) in config_details_oc.text
                for _rest_dr in object_rest.destination_rules:
                    if _rest_dr.name == istio_config_ui.name:
                        for _ui_subset in config_overview_ui.subsets:
                            found = False
                            for _rest_subset in _rest_dr.subsets:
                                if _ui_subset.name == _rest_subset.name and \
                                    dict_contains(_ui_subset.labels, _rest_subset.labels) and \
                                        _ui_subset.traffic_policy == _rest_subset.traffic_policy:
                                    found = True
                            assert found, 'Subset {} not fund in REST {}'.format(
                                _ui_subset, _rest_subset)


class OverviewPageTest(AbstractListPageTest):
    FILTER_ENUM = OverviewPageFilter
    TYPE_ENUM = OverviewPageType
    SORT_ENUM = OverviewPageSort
    VIEW_ENUM = OverviewViewType
    GRAPH_LINK_TYPES = {TYPE_ENUM.APPS: OverviewGraphTypeLink.APP,
                        TYPE_ENUM.SERVICES: OverviewGraphTypeLink.SERVICE,
                        TYPE_ENUM.WORKLOADS: OverviewGraphTypeLink.WORKLOAD}

    def _namespaces_ui(self):
        return self.page.filter.filter_options(filter_name=self.FILTER_ENUM.NAME.text)

    def __init__(self, kiali_client, openshift_client, browser):
        AbstractListPageTest.__init__(
            self, kiali_client=kiali_client,
            openshift_client=openshift_client, page=OverviewPage(browser))
        self.browser = browser

    def assert_type_options(self):
        # test available type options
        options_defined = [item.text for item in self.TYPE_ENUM]
        options_listed = self.page.type.options
        logger.debug('Options[defined:{}, defined:{}]'.format(options_defined, options_listed))
        assert is_equal(options_defined, options_listed)

    def assert_all_items(self, filters=[],
                         overview_type=TYPE_ENUM.APPS, force_clear_all=True,
                         list_type=VIEW_ENUM.COMPACT,
                         force_refresh=False):

        # apply overview type
        self.page.type.select(overview_type.text)

        # apply filters
        self.apply_filters(filters=filters, force_clear_all=force_clear_all)

        if force_refresh:
            self.page.page_refresh()

        # get overviews from rest api
        _ns = self.FILTER_ENUM.NAME.text
        _namespaces = [_f['value'] for _f in filters if _f['name'] == _ns]
        logger.debug('Namespaces:{}'.format(_namespaces))
        overviews_rest = self._apply_overview_filters(self.kiali_client.overview_list(
            namespaces=_namespaces,
            overview_type=overview_type),
            filters)

        # get overviews from ui
        if list_type == self.VIEW_ENUM.LIST:
            overviews_ui = self.page.content.list_items
        elif list_type == self.VIEW_ENUM.EXPAND:
            overviews_ui = self.page.content.expand_items
        else:
            overviews_ui = self.page.content.compact_items

        # compare all results
        logger.debug('Namespaces:{}'.format(_namespaces))
        logger.debug('Items count[UI:{}, REST:{}]'.format(
            len(overviews_ui), len(overviews_rest)))
        logger.debug('overviews UI:{}'.format(overviews_ui))
        logger.debug('overviews REST:{}'.format(overviews_rest))

        assert len(overviews_ui) == len(overviews_rest)

        for overview_ui in overviews_ui:
            found = False
            for overview_rest in overviews_rest:
                if overview_ui.is_equal(overview_rest, advanced_check=True):
                    found = True
                    assert (overview_ui.healthy +
                            overview_ui.unhealthy +
                            overview_ui.degraded +
                            overview_ui.na +
                            overview_ui.idle) == \
                        (overview_rest.healthy +
                         overview_rest.unhealthy +
                         overview_rest.degraded +
                         overview_rest.na +
                         overview_rest.idle)
                    break
            if not found:
                assert found, '{} not found in REST {}'.format(overview_ui, overviews_rest)

            self._assert_overview_config_status(overview_ui.namespace, overview_ui.config_status)
            assert self.kiali_client.namespace_labels(overview_ui.namespace) == \
                self.openshift_client.namespace_labels(
                overview_ui.namespace)

    def _apply_overview_filters(self, overviews=[], filters=[],
                                skip_health=False,
                                skip_mtls=False):
        _ol = self.FILTER_ENUM.LABEL.text
        _labels = [_f['value'] for _f in filters if _f['name'] == _ol]
        logger.debug('Namespace Labels:{}'.format(_labels))
        _omtls = self.FILTER_ENUM.MTLS_STATUS.text
        _mtls_filters = [_f['value'] for _f in filters if _f['name'] == _omtls]
        logger.debug('mTls Status:{}'.format(_mtls_filters))
        _oh = self.FILTER_ENUM.HEALTH.text
        _healths = [_f['value'] for _f in filters if _f['name'] == _oh]
        logger.debug('Health:{}'.format(_healths))
        items = overviews
        # filter by labels
        if len(_labels) > 0:
            filtered_list = []
            filtered_list.extend(
                [_i for _i in items if dict_contains(
                    _i.labels, _labels)])
            items = set(filtered_list)
        # filter by mtls
        if len(_mtls_filters) > 0 and not skip_mtls:
            filtered_list = []
            for _mtls in _mtls_filters:
                filtered_list.extend([_i for _i in items if
                                      self._tls_equals(_mtls, _i.tls_type)])
            items = set(filtered_list)
        # filter by health
        if len(_healths) > 0 and not skip_health:
            filtered_list = []
            for _health in _healths:
                filtered_list.extend([_i for _i in items if self._health_equals(_health, _i)])
            items = set(filtered_list)
        return items

    def _tls_equals(self, tls_filter, overview_tls):
        if tls_filter == OverviewMTSLStatus.ENABLED.text:
            return overview_tls == MeshWideTLSType.ENABLED
        elif tls_filter == OverviewMTSLStatus.DISABLED.text:
            return overview_tls == MeshWideTLSType.DISABLED
        else:
            return overview_tls == MeshWideTLSType.PARTLY_ENABLED

    def _health_equals(self, health_filter, overview_item):
        if health_filter == OverviewHealth.HEALTHY.text:
            return overview_item.degraded == 0 and overview_item.unhealthy == 0 \
                    and overview_item.healthy > 0
        elif health_filter == OverviewHealth.DEGRADED.text:
            return overview_item.degraded > 0 and overview_item.unhealthy == 0
        else:
            return overview_item.degraded == 0 and overview_item.unhealthy > 0

    def test_disable_enable_delete_auto_injection(self, namespace):
        # load the page first
        self.page.load(force_load=True)
        self.apply_filters(filters=[{"name": OverviewPageFilter.NAME.text, "value": namespace}],
                           force_clear_all=True)

        self.page.page_refresh()
        overviews_ui = self.page.content.list_items

        assert len(overviews_ui) == 1

        overview_ui = overviews_ui[0]

        assert overview_ui.namespace == namespace

        if self.page.content.overview_action_present(namespace,
                                                     OverviewInjectionLinks.
                                                     ENABLE_AUTO_INJECTION.text):
            self.page.content.select_action(
                namespace,
                OverviewInjectionLinks.ENABLE_AUTO_INJECTION.text)
            self.page.page_refresh()
            overviews_ui = self.page.content.list_items
            overview_ui = overviews_ui[0]
            assert 'istio-injection' in overview_ui.labels and \
                overview_ui.labels['istio-injection'] == 'enabled', \
                'istio-injection should be enabled in {}'.format(overview_ui.labels)
            assert not self.page.content.overview_action_present(
                namespace,
                OverviewInjectionLinks.ENABLE_AUTO_INJECTION.text)
            assert self.page.content.overview_action_present(
                namespace,
                OverviewInjectionLinks.DISABLE_AUTO_INJECTION.text)
            assert self.page.content.overview_action_present(
                namespace,
                OverviewInjectionLinks.REMOVE_AUTO_INJECTION.text)
        elif self.page.content.overview_action_present(namespace,
                                                       OverviewInjectionLinks.
                                                       DISABLE_AUTO_INJECTION.text):
            self.page.content.select_action(
                namespace,
                OverviewInjectionLinks.DISABLE_AUTO_INJECTION.text)
            self.page.page_refresh()
            overviews_ui = self.page.content.list_items
            overview_ui = overviews_ui[0]
            assert 'istio-injection' in overview_ui.labels and \
                overview_ui.labels['istio-injection'] == 'disabled', \
                'istio-injection should be disabled in {}'.format(overview_ui.labels)
            assert self.page.content.overview_action_present(
                namespace,
                OverviewInjectionLinks.ENABLE_AUTO_INJECTION.text)
            assert not self.page.content.overview_action_present(
                namespace,
                OverviewInjectionLinks.DISABLE_AUTO_INJECTION.text)
            assert self.page.content.overview_action_present(
                namespace,
                OverviewInjectionLinks.REMOVE_AUTO_INJECTION.text)
            self.page.page_refresh()
            self.page.content.select_action(
                namespace,
                OverviewInjectionLinks.ENABLE_AUTO_INJECTION.text)
        elif self.page.content.overview_action_present(namespace,
                                                       OverviewInjectionLinks.
                                                       REMOVE_AUTO_INJECTION.text):
            self.page.content.select_action(
                namespace,
                OverviewInjectionLinks.REMOVE_AUTO_INJECTION.text)
            self.page.page_refresh()
            overviews_ui = self.page.content.list_items
            overview_ui = overviews_ui[0]
            assert 'istio-injection' not in overview_ui.labels, \
                'istio-injection should not be in {}'.format(overview_ui.labels)
            assert self.page.content.overview_action_present(
                namespace,
                OverviewInjectionLinks.ENABLE_AUTO_INJECTION.text)
            assert not self.page.content.overview_action_present(
                namespace,
                OverviewInjectionLinks.DISABLE_AUTO_INJECTION.text)
            assert not self.page.content.overview_action_present(
                namespace,
                OverviewInjectionLinks.REMOVE_AUTO_INJECTION.text)
            self.page.page_refresh()
            self.page.content.select_action(
                namespace,
                OverviewInjectionLinks.ENABLE_AUTO_INJECTION.text)

    def test_create_update_delete_traffic_policies(self, namespace):
        # load the page first
        self.page.load(force_load=True)
        self.apply_filters(filters=[{"name": OverviewPageFilter.NAME.text, "value": namespace}],
                           force_clear_all=True)

        if self.page.content.overview_action_present(namespace,
                                                     OverviewTrafficLinks.
                                                     DELETE_TRAFFIC_POLICIES.text):
            self.page.page_refresh()
            wait_to_spinner_disappear(self.browser)
            if self.page.content.select_action(
                    namespace, OverviewTrafficLinks.DELETE_TRAFFIC_POLICIES.text):
                wait_to_spinner_disappear(self.browser)
                self.browser.wait_for_element(
                    parent=ListViewAbstract.DIALOG_ROOT,
                    locator=('.//button[text()="Delete"]'))
                self.browser.click(self.browser.element(
                    parent=ListViewAbstract.DIALOG_ROOT,
                    locator=('.//button[text()="Delete"]')))
            wait_to_spinner_disappear(self.browser)
            self.page.page_refresh()
            wait_to_spinner_disappear(self.browser)
            self.page.content.list_items
            assert not self.page.content.overview_action_present(
                namespace,
                OverviewTrafficLinks.DELETE_TRAFFIC_POLICIES.text)
            assert not self.page.content.overview_action_present(
                namespace,
                OverviewTrafficLinks.UPDATE_TRAFFIC_POLICIES.text)
            assert self.page.content.overview_action_present(
                namespace,
                OverviewTrafficLinks.CREATE_TRAFFIC_POLICIES.text)
        elif self.page.content.overview_action_present(namespace,
                                                       OverviewTrafficLinks.
                                                       CREATE_TRAFFIC_POLICIES.text):
            assert self.page.content.select_action(
                namespace, OverviewTrafficLinks.CREATE_TRAFFIC_POLICIES.text)
            wait_to_spinner_disappear(self.browser)
            self.page.page_refresh()
            wait_to_spinner_disappear(self.browser)
            self.page.content.list_items
            assert self.page.content.overview_action_present(
                namespace,
                OverviewTrafficLinks.DELETE_TRAFFIC_POLICIES.text)
            assert self.page.content.overview_action_present(
                namespace,
                OverviewTrafficLinks.UPDATE_TRAFFIC_POLICIES.text)
            assert not self.page.content.overview_action_present(
                namespace,
                OverviewTrafficLinks.CREATE_TRAFFIC_POLICIES.text)
        elif self.page.content.overview_action_present(namespace,
                                                       OverviewTrafficLinks.
                                                       UPDATE_TRAFFIC_POLICIES.text):
            assert self.page.content.select_action(
                namespace, OverviewTrafficLinks.UPDATE_TRAFFIC_POLICIES.text)
            wait_to_spinner_disappear(self.browser)
            self.browser.wait_for_element(
                parent=ListViewAbstract.DIALOG_ROOT,
                locator=('.//button[text()="Update"]'))
            self.browser.click(self.browser.element(
                parent=ListViewAbstract.DIALOG_ROOT,
                locator=('.//button[text()="Update"]')))
            wait_to_spinner_disappear(self.browser)
            self.page.page_refresh()
            wait_to_spinner_disappear(self.browser)
            self.page.content.list_items
            assert self.page.content.overview_action_present(
                namespace,
                OverviewTrafficLinks.DELETE_TRAFFIC_POLICIES.text)
            assert self.page.content.overview_action_present(
                namespace,
                OverviewTrafficLinks.UPDATE_TRAFFIC_POLICIES.text)
            assert not self.page.content.overview_action_present(
                namespace,
                OverviewTrafficLinks.CREATE_TRAFFIC_POLICIES.text)

    def _assert_overview_config_status(self, namespace, config_status):
        expected_status = IstioConfigValidation.NA
        # get configs from rest api
        config_list_rest = self.kiali_client.istio_config_list(
            namespaces=[namespace])
        for config_rest in config_list_rest:
            if hasattr(config_rest, 'validation'):
                if config_rest.validation == IstioConfigValidation.NOT_VALID:
                    expected_status = IstioConfigValidation.NOT_VALID
                elif config_rest.validation == IstioConfigValidation.WARNING:
                    if expected_status != IstioConfigValidation.NOT_VALID:
                        expected_status = IstioConfigValidation.WARNING
                elif config_rest.validation == IstioConfigValidation.VALID:
                    if expected_status == IstioConfigValidation.NA:
                        expected_status = IstioConfigValidation.VALID
        assert expected_status == config_status.validation, \
            'Expected {} but got {} for {} as Config Status'.format(
                expected_status, config_status.validation, namespace)
        if config_status.validation != IstioConfigValidation.NA:
            assert '/console/istio?namespaces={}'.format(
                    namespace) in \
                        config_status.link, 'Wrong config overview link {}'.format(
                            config_status.link)


class ApplicationsPageTest(AbstractListPageTest):
    FILTER_ENUM = ApplicationsPageFilter
    SORT_ENUM = ApplicationsPageSort

    def __init__(self, kiali_client, openshift_client, browser):
        AbstractListPageTest.__init__(
            self, kiali_client=kiali_client,
            openshift_client=openshift_client, page=ApplicationsPage(browser))
        self.browser = browser

    def _prepare_load_details_page(self, name, namespace):
        # load the page first
        self.page.load(force_load=True)
        # apply namespace
        self.apply_namespaces(namespaces=[namespace])
        # apply filters
        self.apply_filters(filters=[
            {'name': ApplicationsPageFilter.APP_NAME.text, 'value': name}])

    def load_details_page(self, name, namespace, force_refresh=False, load_only=False):
        logger.debug('Loading details page for application: {}'.format(name))
        if not self.is_in_details_page(name, namespace):
            self._prepare_load_details_page(name, namespace)
            self.open(name, namespace, force_refresh)
            self.browser.wait_for_element(locator='//*[contains(., "Application")]')
        return self.page.content.get_details(load_only)

    def assert_random_details(self, namespaces=[], filters=[], force_refresh=False):
        # get applications from rest api
        _sn = self.FILTER_ENUM.APP_NAME.text
        _application_names = [_f['value'] for _f in filters if _f['name'] == _sn]
        logger.debug('Namespaces:{}, Application names:{}'.format(namespaces, _application_names))
        applications_rest = self._apply_app_filters(self.kiali_client.application_list(
            namespaces=namespaces), filters=filters)

        # random applications filters
        assert len(applications_rest) > 0
        if len(applications_rest) > 3:
            _random_applications = random.sample(applications_rest, 3)
        else:
            _random_applications = applications_rest
        # create filters
        for _idx, _selected_application in enumerate(_random_applications):
            self.assert_details(
                _selected_application.name,
                _selected_application.namespace,
                check_metrics=True if _idx == 0 else False,
                force_refresh=force_refresh)

    def assert_details(self, name, namespace, check_metrics=False, force_refresh=False):
        logger.debug('Asserting details for: {}, in namespace: {}'.format(name, namespace))

        # load application details page
        application_details_ui = self.load_details_page(name, namespace, force_refresh)
        assert application_details_ui
        assert name == application_details_ui.name
        # get application detals from rest
        application_details_rest = self.kiali_client.application_details(
            namespace=namespace,
            application_name=name)
        assert application_details_rest
        assert name == application_details_rest.name
        application_details_oc = self.openshift_client.application_details(
            namespace=namespace,
            application_name=name)
        assert application_details_oc

        assert application_details_ui.is_equal(application_details_rest,
                                               advanced_check=True), \
            'Application UI {} not equal to REST {}'\
            .format(application_details_ui, application_details_rest)
        '''TODO read health tooltip values
        if application_details_ui.application_status:
            assert application_details_ui.application_status.is_healthy() == \
                application_details_ui.health, \
                "Application Details Status {} is not equal to UI Health {} for {}"\
                .format(
                application_details_ui.application_status.is_healthy(),
                application_details_ui.health,
                application_details_ui.name)
        if application_details_oc.application_status:
            assert is_equal(application_details_ui.application_status.deployment_statuses,
                            application_details_oc.application_status.deployment_statuses), \
                    "Application REST Status {} is not equal to OC {} for {}"\
                    .format(
                            application_details_ui.application_status.deployment_statuses,
                            application_details_oc.application_status.deployment_statuses,
                            application_details_ui.name)'''
        assert is_equal([_w.name for _w in application_details_ui.workloads],
                        [_w.name for _w in application_details_rest.workloads])
        assert is_equal([_w.name for _w in application_details_oc.workloads],
                        [_w.name for _w in application_details_rest.workloads])
        for workload_ui in application_details_ui.workloads:
            found = False
            for workload_rest in application_details_rest.workloads:
                if workload_ui.is_equal(workload_rest,
                                        advanced_check=True):
                    found = True
                    break
            if not found:
                assert found, 'Workload {} not found in REST {}'.format(workload_ui, workload_rest)
            found = False
            for workload_oc in application_details_oc.workloads:
                if workload_ui.is_equal(workload_oc,
                                        advanced_check=False):
                    found = True
                    break
            if not found:
                assert found, 'Workload {} not found in OC {}'.format(workload_ui, workload_oc)
        assert application_details_ui.services == application_details_rest.services, \
            'UI services {} not equal to REST {}'.format(
                application_details_ui.services,
                application_details_rest.services)
        assert is_equal(application_details_ui.services, application_details_oc.services), \
            'UI services {} not equal to OC {}'.format(
                application_details_ui.services,
                application_details_oc.services)

        if check_metrics:
            self.assert_metrics_options(application_details_ui.inbound_metrics)

            self.assert_metrics_options(application_details_ui.outbound_metrics)

        self.assert_traces_tab(application_details_ui.traces_tab)

        self.assert_traffic(name, application_details_ui.traffic_tab,
                            self_object_type=TrafficType.APP, traffic_object_type=TrafficType.APP)

    def assert_all_items(self, namespaces=[], filters=[], sort_options=[], force_clear_all=True,
                         label_operation=None):
        # apply namespaces
        self.apply_namespaces(namespaces, force_clear_all=force_clear_all)

        # apply filters
        self.apply_filters(filters=filters, force_clear_all=force_clear_all)

        # apply sorting
        self.sort(sort_options)

        if label_operation:
            self.apply_label_operation(label_operation)

        logger.debug('Namespaces:{}'.format(namespaces))
        # get applications from ui
        applications_ui = self.page.content.all_items
        # get from REST
        applications_rest = self._apply_app_filters(self.kiali_client.application_list(
            namespaces=namespaces),
            filters,
            label_operation)
        # get from OC
        applications_oc = self._apply_app_filters(self.openshift_client.application_list(
            namespaces=namespaces),
            filters,
            label_operation,
            True,
            True)

        # compare all results
        logger.debug('Namespaces:{}'.format(namespaces))
        logger.debug('Items count[UI:{}, REST:{}]'.format(
            len(applications_ui), len(applications_rest)))
        logger.debug('Applications UI:{}'.format(applications_ui))
        logger.debug('Applications REST:{}'.format(applications_rest))
        logger.debug('Applications OC:{}'.format(applications_oc))

        assert len(applications_ui) == len(applications_rest), \
            "UI {} and REST {} applications number not equal".format(applications_ui,
                                                                     applications_rest)
        assert len(applications_rest) <= len(applications_oc)

        for application_ui in applications_ui:
            found = False
            for application_rest in applications_rest:
                if application_ui.is_equal(application_rest, advanced_check=True):
                    found = True
                    if application_ui.application_status:
                        assert application_ui.application_status.is_healthy() == \
                            application_ui.health, \
                            "Application Tooltip Health {} is not equal to UI Health {} for {}"\
                            .format(
                            application_ui.application_status.is_healthy(),
                            application_ui.health,
                            application_ui.name)
                    break
            if not found:
                assert found, '{} not found in REST'.format(application_ui)
            found = False
            for application_oc in applications_oc:
                logger.debug('{} {}'.format(application_oc.name, application_oc.namespace))
                if application_ui.is_equal(application_oc, advanced_check=False):
                    # in OC it contains more labels, skip for jaeger and grafana
                    if application_ui.name != 'jaeger' and application_ui.name != 'grafana':
                        assert application_ui.labels.items() == application_oc.labels.items(), \
                            'Expected {} but got {} labels for application {}'.format(
                                application_oc.labels,
                                application_ui.labels,
                                application_ui.name)
                    found = True
                    if application_oc.application_status and \
                            application_oc.application_status.deployment_statuses:
                        assert is_equal(application_rest.application_status.deployment_statuses,
                                        application_oc.application_status.deployment_statuses), \
                                "Application REST Status {} is not equal to OC {} for {}"\
                                .format(
                                        application_rest.application_status.deployment_statuses,
                                        application_oc.application_status.deployment_statuses,
                                        application_ui.name)
                    break
            if not found:
                assert found, '{} not found in OC'.format(application_ui)

    def _apply_app_filters(self, applications=[], filters=[], label_operation=None,
                           skip_health=False, skip_sidecar=False):
        _an = self.FILTER_ENUM.APP_NAME.text
        _application_names = [_f['value'] for _f in filters if _f['name'] == _an]
        logger.debug('Application names:{}'.format(_application_names))
        _al = self.FILTER_ENUM.LABEL.text
        _labels = [_f['value'] for _f in filters if _f['name'] == _al]
        logger.debug('Application Labels:{}'.format(_labels))
        _ais = self.FILTER_ENUM.ISTIO_SIDECAR.text
        _sidecars = [_f['value'] for _f in filters if _f['name'] == _ais]
        logger.debug('Istio Sidecars:{}'.format(_sidecars))
        _ah = self.FILTER_ENUM.HEALTH.text
        _health = [_f['value'] for _f in filters if _f['name'] == _ah]
        logger.debug('Health:{}'.format(_health))
        # filter by application name
        items = applications
        if len(_application_names) > 0:
            filtered_list = []
            for _name in _application_names:
                filtered_list.extend([_i for _i in items if _name in _i.name])
            items = set(filtered_list)
        # filter by labels
        if len(_labels) > 0:
            filtered_list = []
            filtered_list.extend(
                [_i for _i in items if dict_contains(
                    _i.labels, _labels,
                    (True if label_operation == LabelOperation.AND.text else False))])
            items = set(filtered_list)
        # filter by sidecars
        if len(_sidecars) > 0 and not skip_sidecar:
            filtered_list = []
            for _sidecar in _sidecars:
                filtered_list.extend([_i for _i in items if
                                      self.sidecar_presents(_sidecar, _i.istio_sidecar)])
            items = set(filtered_list)
        # filter by health
        if len(_health) > 0 and not skip_health:
            filtered_list = []
            filtered_list.extend([_i for _i in items if self.health_equals(_health[0], _i.health)])
            items = set(filtered_list)
        return items


class WorkloadsPageTest(AbstractListPageTest):
    FILTER_ENUM = WorkloadsPageFilter
    SORT_ENUM = WorkloadsPageSort

    def __init__(self, kiali_client, openshift_client, browser):
        AbstractListPageTest.__init__(
            self, kiali_client=kiali_client,
            openshift_client=openshift_client, page=WorkloadsPage(browser))
        self.browser = browser

    def _prepare_load_details_page(self, name, namespace):
        # load the page first
        self.page.load(force_load=True)
        # apply namespace
        self.apply_namespaces(namespaces=[namespace])
        # apply filters
        self.apply_filters(filters=[
            {'name': WorkloadsPageFilter.WORKLOAD_NAME.text, 'value': name}])

    def load_details_page(self, name, namespace, force_refresh=False, load_only=False):
        logger.debug('Loading details page for workload: {}'.format(name))
        if not self.is_in_details_page(name, namespace):
            self._prepare_load_details_page(name, namespace)
            self.open(name, namespace, force_refresh)
            self.browser.wait_for_element(locator='//*[contains(., "Workload")]')
        return self.page.content.get_details(load_only)

    def assert_random_details(self, namespaces=[], filters=[],
                              force_clear_all=True, force_refresh=False):
        # get workloads from rest api
        logger.debug('Namespaces:{}'.format(namespaces))
        workloads_rest = self._apply_workload_filters(self.kiali_client.workload_list(
            namespaces=namespaces), filters)
        # random workloads filters
        assert len(workloads_rest) > 0
        if len(workloads_rest) > 3:
            _random_workloads = random.sample(workloads_rest, 3)
        else:
            _random_workloads = workloads_rest
        # create filters
        for _idx, _selected_workload in enumerate(_random_workloads):
            self.assert_details(_selected_workload.name,
                                _selected_workload.namespace,
                                _selected_workload.workload_type,
                                check_metrics=True if _idx == 0 else False,
                                force_refresh=force_refresh)

    def assert_details(self, name, namespace, workload_type, check_metrics=False,
                       force_refresh=False):
        logger.debug('Asserting details for: {}, in namespace: {}'.format(name, namespace))

        # load workload details page
        workload_details_ui = self.load_details_page(name, namespace, force_refresh)
        assert workload_details_ui
        assert name == workload_details_ui.name
        # get workload detals from rest
        workload_details_rest = self.kiali_client.workload_details(
            namespace=namespace,
            workload_name=name,
            workload_type=workload_type)
        assert workload_details_rest
        assert name == workload_details_rest.name
        # get workload detals from rest
        workload_details_oc = self.openshift_client.workload_details(
            namespace=namespace,
            workload_name=name,
            workload_type=workload_type)
        assert workload_details_oc
        assert name == workload_details_oc.name

        assert workload_details_ui.is_equal(workload_details_rest,
                                            advanced_check=True), \
            'Workload UI {} not equal to REST {}'\
            .format(workload_details_ui, workload_details_rest)
        assert workload_details_ui.is_equal(workload_details_oc,
                                            advanced_check=False), \
            'Workload UI {} not equal to OC {}'\
            .format(workload_details_ui, workload_details_oc)
        if workload_details_ui.workload_status:
            assert workload_details_ui.workload_status.is_healthy() == \
                workload_details_ui.health, \
                "Workload Details Status {} is not equal to UI Health {} for {}"\
                .format(
                workload_details_ui.workload_status.is_healthy(),
                workload_details_ui.health,
                workload_details_ui.name)
        all_pods = []
        for pod_ui in workload_details_ui.pods:
            all_pods.append(pod_ui.name)
            found = False
            for pod_rest in workload_details_rest.pods:
                if pod_ui.is_equal(pod_rest,
                                   advanced_check=True):
                    found = True
                    break
            if not found:
                assert found, 'Pod {} not found in REST {}'.format(pod_ui, pod_rest)
        for pod_oc in workload_details_oc.pods:
            found = False
            for pod_rest in workload_details_rest.pods:
                if pod_oc.is_equal(pod_rest,
                                   advanced_check=False):
                    found = True
                    break
            if not found:
                assert found, 'OC Pod {} not found in REST {}'.format(pod_oc, pod_rest)
        for service_ui in workload_details_ui.services:
            found = False
            for service_rest in workload_details_rest.services:
                if service_ui == service_rest:
                    found = True
                    break
            if not found:
                assert found, 'Service {} not found in REST {}'.format(service_ui, service_rest)

        self.assert_istio_configs(workload_details_ui,
                                  workload_details_rest,
                                  workload_details_oc,
                                  namespace)

        self.assert_logs_tab(workload_details_ui.logs_tab, all_pods)
        if check_metrics:
            self.assert_metrics_options(workload_details_ui.inbound_metrics, check_grafana=True)

            self.assert_metrics_options(workload_details_ui.outbound_metrics, check_grafana=True)

        self.assert_traces_tab(workload_details_ui.traces_tab)

        self.assert_traffic(name, workload_details_ui.traffic_tab,
                            self_object_type=TrafficType.WORKLOAD,
                            traffic_object_type=TrafficType.WORKLOAD)

    def assert_all_items(self, namespaces=[], filters=[], sort_options=[], force_clear_all=True,
                         label_operation=None):
        # apply namespaces
        self.apply_namespaces(namespaces, force_clear_all=force_clear_all)

        # apply filters
        self.apply_filters(filters=filters, force_clear_all=force_clear_all)

        # apply sorting
        self.sort(sort_options)

        if label_operation:
            self.apply_label_operation(label_operation)

        # get workloads from rest api
        workloads_rest = self._apply_workload_filters(self.kiali_client.workload_list(
            namespaces=namespaces), filters, label_operation)
        # get workloads from OC client
        workloads_oc = self._apply_workload_filters(self.openshift_client.workload_list(
            namespaces=(namespaces if namespaces else self.kiali_client.namespace_list())),
            filters, label_operation,
            skip_sidecar=True,
            skip_health=True)
        # get workloads from ui
        workloads_ui = self.page.content.all_items

        # compare all results
        logger.debug('Namespaces:{}'.format(namespaces))
        logger.debug('Items count[UI:{}, REST:{}, OC:{}]'.format(
            len(workloads_ui), len(workloads_rest), len(workloads_oc)))
        logger.debug('Workloads UI:{}'.format(workloads_ui))
        logger.debug('Workloads REST:{}'.format(workloads_rest))
        logger.debug('Workloads OC:{}'.format(workloads_oc))

        assert len(workloads_ui) == len(workloads_rest), \
            "UI {} and REST {} workloads number not equal".format(workloads_ui, workloads_rest)
        assert len(workloads_rest) <= len(workloads_oc), \
            "REST {} should be less or equal OC {}".format(workloads_rest, workloads_oc)

        for workload_ui in workloads_ui:
            found = False
            for workload_rest in workloads_rest:
                if workload_ui.is_equal(workload_rest, advanced_check=True):
                    found = True
                    if workload_ui.workload_status:
                        assert workload_ui.workload_status.is_healthy() == workload_ui.health, \
                                "Workload Tooltip Health {} is not equal to UI Health {} for {}"\
                                .format(
                                workload_ui.workload_status.is_healthy(),
                                workload_ui.health,
                                workload_ui.name)
                    break
            if not found:
                assert found, '{} not found in REST'.format(workload_ui)
            found = False
            for workload_oc in workloads_oc:
                if workload_ui.is_equal(workload_oc, advanced_check=False) and \
                        workload_ui.labels.items() == workload_oc.labels.items():
                    found = True
                    if workload_oc.workload_status:
                        assert workload_rest.workload_status.workload_status.is_equal(
                            workload_oc.workload_status.workload_status), \
                            "Workload REST Status {} is not equal to OC {} for {}"\
                            .format(
                            workload_rest.workload_status.workload_status,
                            workload_oc.workload_status.workload_status,
                            workload_ui.name)
                    break
            if not found:
                assert found, '{} not found in OC'.format(workload_ui)

    def _apply_workload_filters(self, workloads=[], filters=[], label_operation=None,
                                skip_sidecar=False, skip_health=False):
        _sn = self.FILTER_ENUM.WORKLOAD_NAME.text
        _names = [_f['value'] for _f in filters if _f['name'] == _sn]
        logger.debug('Workload names:{}'.format(_names))
        _wl = self.FILTER_ENUM.LABEL.text
        _labels = [_f['value'] for _f in filters if _f['name'] == _wl]
        logger.debug('Workload Labels:{}'.format(_labels))
        _wt = self.FILTER_ENUM.WORKLOAD_TYPE.text
        _types = [_f['value'] for _f in filters if _f['name'] == _wt]
        logger.debug('Workload Types:{}'.format(_types))
        _wis = self.FILTER_ENUM.ISTIO_SIDECAR.text
        _sidecars = [_f['value'] for _f in filters if _f['name'] == _wis]
        logger.debug('Istio Sidecars:{}'.format(_sidecars))
        _wh = self.FILTER_ENUM.HEALTH.text
        _health = [_f['value'] for _f in filters if _f['name'] == _wh]
        logger.debug('Health:{}'.format(_health))
        _version_label = None
        for _f in filters:
            if _f['name'] == self.FILTER_ENUM.VERSION_LABEL.text:
                _version_label = _f['value']
                break
        logger.debug('Version Label:{}'.format(_version_label))
        _app_label = None
        for _f in filters:
            if _f['name'] == self.FILTER_ENUM.APP_LABEL.text:
                _app_label = _f['value']
                break
        logger.debug('App Label:{}'.format(_app_label))
        items = workloads
        # filter by name
        if len(_names) > 0:
            filtered_list = []
            for _name in _names:
                filtered_list.extend([_i for _i in items if _name in _i.name])
            items = set(filtered_list)
        # filter by labels
        if len(_labels) > 0:
            filtered_list = []
            filtered_list.extend(
                [_i for _i in workloads if dict_contains(
                    _i.labels, _labels,
                    (True if label_operation == LabelOperation.AND.text else False))])
            items = set(filtered_list)
        # filter by types
        if len(_types) > 0:
            filtered_list = []
            for _type in _types:
                filtered_list.extend([_i for _i in items if _type == _i.workload_type])
            items = set(filtered_list)
        # filter by sidecars
        if len(_sidecars) > 0 and not skip_sidecar:
            filtered_list = []
            for _sidecar in _sidecars:
                filtered_list.extend([_i for _i in items if
                                      self.sidecar_presents(_sidecar, _i.istio_sidecar)])
            items = set(filtered_list)
        # filter by version label present
        if _version_label:
            filtered_list = []
            filtered_list.extend([_i for _i in items if
                                  (_version_label == VersionLabel.NOT_PRESENT.text)
                                  ^ dict_contains(
                                      given_list=['version'], original_dict=_i.labels)])
            items = set(filtered_list)
        # filter by app label present
        if _app_label:
            filtered_list = []
            filtered_list.extend([_i for _i in items if
                                  (_app_label == AppLabel.NOT_PRESENT.text)
                                  ^ dict_contains(
                                      given_list=['app'], original_dict=_i.labels)])
            items = set(filtered_list)
        # filter by health
        if len(_health) > 0 and not skip_health:
            filtered_list = []
            filtered_list.extend([_i for _i in items if self.health_equals(_health[0], _i.health)])
            items = set(filtered_list)
        return items

    def test_disable_enable_delete_auto_injection(self, name, namespace):
        logger.debug('Auto Injection test for Workload: {}, {}'.format(name, namespace))
        # load workload details page
        self._prepare_load_details_page(name, namespace)
        self.open(name, namespace)

        if self.page.actions.is_disable_auto_injection_visible():
            self.page.actions.select(OverviewInjectionLinks.DISABLE_AUTO_INJECTION.text)
            self.page.page_refresh()
            assert self.page.content._details_missing_sidecar()
            assert self.page.actions.is_enable_auto_injection_visible()
            assert self.page.actions.is_remove_auto_injection_visible()
            assert not self.page.actions.is_disable_auto_injection_visible()
        elif self.page.actions.is_remove_auto_injection_visible():
            self.page.actions.select(OverviewInjectionLinks.REMOVE_AUTO_INJECTION.text)
            self.page.page_refresh()
            assert self.page.content._details_missing_sidecar()
            assert self.page.actions.is_enable_auto_injection_visible()
            assert not self.page.actions.is_remove_auto_injection_visible()
            assert not self.page.actions.is_disable_auto_injection_visible()
        elif self.page.actions.is_enable_auto_injection_visible():
            self.page.actions.select(OverviewInjectionLinks.ENABLE_AUTO_INJECTION.text)
            self.page.page_refresh()
            assert self.page.content._details_missing_sidecar()
            assert not self.page.actions.is_enable_auto_injection_visible()
            assert self.page.actions.is_remove_auto_injection_visible()
            assert self.page.actions.is_disable_auto_injection_visible()


class ServicesPageTest(AbstractListPageTest):
    FILTER_ENUM = ServicesPageFilter
    SORT_ENUM = ServicesPageSort

    def __init__(self, kiali_client, openshift_client, browser):
        AbstractListPageTest.__init__(
            self, kiali_client=kiali_client,
            openshift_client=openshift_client, page=ServicesPage(browser))
        self.browser = browser

    def _prepare_load_details_page(self, name, namespace):
        # load the page first
        self.page.load(force_load=True)
        # apply namespace
        self.apply_namespaces(namespaces=[namespace])
        # apply filters
        self.apply_filters(filters=[
            {'name': ServicesPageFilter.SERVICE_NAME.text, 'value': name}])

    def load_details_page(self, name, namespace, force_refresh=False, load_only=False):
        logger.debug('Loading details page for service: {}'.format(name))
        if not self.is_in_details_page(name, namespace):
            self._prepare_load_details_page(name, namespace)
            self.open(name, namespace, force_refresh)
            self.browser.wait_for_element(locator='//*[contains(., "Service")]')
        return self.page.content.get_details(load_only)

    def assert_random_details(self, namespaces=[], filters=[], force_refresh=False):
        # get services from rest api
        services_rest = self._apply_service_filters(self.kiali_client.service_list(
            namespaces=namespaces), filters=filters)
        # random services filters
        assert len(services_rest) > 0
        if len(services_rest) > 2:
            _random_services = random.sample(services_rest, 2)
        else:
            _random_services = services_rest
        # create filters
        for _idx, _selected_service in enumerate(_random_services):
            self.assert_details(_selected_service.name, _selected_service.namespace,
                                check_metrics=True if _idx == 0 else False,
                                force_refresh=force_refresh)

    def assert_details(self, name, namespace, check_metrics=False,
                       force_refresh=False):
        logger.debug('Asserting details for: {}, in namespace: {}'.format(name, namespace))
        # load service details page
        service_details_ui = self.load_details_page(name, namespace, force_refresh)
        assert service_details_ui
        assert name == service_details_ui.name
        # get service details from rest
        service_details_rest = self.kiali_client.service_details(
            namespace=namespace,
            service_name=name)
        assert service_details_rest
        assert name == service_details_rest.name
        service_details_oc = self.openshift_client.service_details(namespace=namespace,
                                                                   service_name=name,
                                                                   skip_workloads=False)
        assert service_details_oc
        assert name == service_details_oc.name

        if namespace != 'istio-system':
            assert service_details_rest.istio_sidecar\
                == service_details_ui.istio_sidecar
        assert service_details_ui.is_equal(service_details_rest,
                                           advanced_check=True), \
            'Service UI {} not equal to REST {}'\
            .format(service_details_ui, service_details_rest)
        assert service_details_ui.is_equal(service_details_oc,
                                           advanced_check=False), \
            'Service UI {} not equal to OC {}'\
            .format(service_details_ui, service_details_oc)
        assert len(service_details_ui.workloads)\
            == len(service_details_rest.workloads)
        assert len(service_details_ui.istio_configs)\
            == len(service_details_rest.istio_configs)
        assert len(service_details_ui.workloads)\
            == len(service_details_oc.workloads)
        assert len(service_details_ui.istio_configs)\
            == len(service_details_oc.istio_configs)

        if service_details_ui.service_status:
            assert service_details_ui.service_status.is_healthy() == \
                service_details_ui.health, \
                "Service Details Status {} is not equal to UI Health {} for {}"\
                .format(
                service_details_ui.service_status.is_healthy(),
                service_details_ui.health,
                service_details_ui.name)

        for workload_ui in service_details_ui.workloads:
            found = False
            for workload_rest in service_details_rest.workloads:
                if workload_ui == workload_rest.name:
                    found = True
                    break
            if not found:
                assert found, 'Workload {} not found in REST {}'.format(workload_ui,
                                                                        workload_rest)
            found = False
            for workload_oc in service_details_oc.workloads:
                if workload_ui == workload_oc.name:
                    found = True
                    break
            if not found:
                assert found, 'Workload {} not found in OC {}'.format(workload_ui,
                                                                      workload_oc)

        self.assert_istio_configs(service_details_ui,
                                  service_details_rest,
                                  service_details_oc,
                                  namespace)

        if check_metrics:
            self.assert_metrics_options(service_details_ui.inbound_metrics, check_grafana=True)

        self.assert_traces_tab(service_details_ui.traces_tab)

        # service traffic is linked to workloads
        self.assert_traffic(name, service_details_ui.traffic_tab,
                            self_object_type=TrafficType.SERVICE,
                            traffic_object_type=TrafficType.SERVICE)

    def get_workload_names_set(self, source_workloads):
        workload_names = []
        for source_workload in source_workloads:
            for workload in source_workload.workloads:
                workload_names.append(workload)
        return set(workload_names)

    def assert_all_items(self, namespaces=[], filters=[], sort_options=[], force_clear_all=True,
                         label_operation=None):
        # apply namespaces
        self.apply_namespaces(namespaces, force_clear_all=force_clear_all)

        # apply filters
        self.apply_filters(filters=filters, force_clear_all=force_clear_all)

        # apply sorting
        self.sort(sort_options)

        if label_operation:
            self.apply_label_operation(label_operation)

        # get services from ui
        services_ui = self.page.content.all_items
        # get services from rest api
        services_rest = self._apply_service_filters(self.kiali_client.service_list(
            namespaces=namespaces), filters=filters)
        # get services from OC client
        services_oc = self._apply_service_filters(self.openshift_client.service_list(
            namespaces=namespaces), filters=filters)

        # compare all results
        logger.debug('Namespaces:{}'.format(namespaces))
        logger.debug('Items count[UI:{}, REST:{}, OC:{}]'.format(
            len(services_ui), len(services_rest), len(services_oc)))
        logger.debug('Services UI:{}'.format(services_ui))
        logger.debug('Services REST:{}'.format(services_rest))
        logger.debug('Services OC:{}'.format(services_oc))

        assert len(services_ui) == len(services_rest), \
            "UI {} and REST {} services number not equal".format(services_ui, services_rest)

        assert len(services_rest) <= len(services_oc)

        for service_ui in services_ui:
            found = False
            for service_rest in services_rest:
                if service_ui.is_equal(service_rest, advanced_check=True):
                    found = True
                    if service_ui.service_status:
                        assert service_ui.service_status.is_healthy() == service_ui.health, \
                                "Service Tooltip Health {} is not equal to UI Health {}".format(
                                service_ui.service_status.is_healthy(),
                                service_ui.health)
                    break
            if not found:
                assert found, '{} not found in REST'.format(service_ui)
            found = False
            for service_oc in services_oc:
                if service_ui.is_equal(service_oc, advanced_check=False):
                    assert service_ui.labels.items() == service_oc.labels.items()
                    found = True
                    break
            if not found:
                assert found, '{} not found in OC'.format(service_ui)
            if service_ui.config_status.validation != IstioConfigValidation.NA:
                assert '/console/namespaces/{}/services/{}'.format(
                    service_ui.namespace,
                    service_ui.name) in \
                        service_ui.config_status.link, 'Wrong service link {}'.format(
                            service_ui.config_status.link)

    def _apply_service_filters(self, services=[], filters=[], label_operation=None):
        _sn = self.FILTER_ENUM.SERVICE_NAME.text
        _service_names = [_f['value'] for _f in filters if _f['name'] == _sn]
        logger.debug('Service names:{}'.format(_service_names))
        _sis = self.FILTER_ENUM.ISTIO_SIDECAR.text
        _sidecars = [_f['value'] for _f in filters if _f['name'] == _sis]
        logger.debug('Istio Sidecars:{}'.format(_sidecars))
        _sl = self.FILTER_ENUM.LABEL.text
        _labels = [_f['value'] for _f in filters if _f['name'] == _sl]
        items = services
        # filter by service name
        if len(_service_names) > 0:
            filtered_list = []
            for _name in _service_names:
                filtered_list.extend([_i for _i in items if _name in _i.name])
            items = set(filtered_list)
        # filter by sidecars
        if len(_sidecars) > 0:
            filtered_list = []
            for _sidecar in _sidecars:
                filtered_list.extend([_i for _i in items if
                                      self.sidecar_presents(_sidecar, _i.istio_sidecar)])
            items = set(filtered_list)
        # filter by labels
        if len(_labels) > 0:
            filtered_list = []
            filtered_list.extend(
                [_i for _i in items if dict_contains(
                    _i.labels, _labels,
                    (True if label_operation == LabelOperation.AND.text else False))])
            items = set(filtered_list)
        return items

    def get_additional_filters(self, namespaces, current_filters):
        logger.debug('Current filters:{}'.format(current_filters))
        # get services of a namespace
        _namespace = namespaces[0]
        logger.debug('Running Services REST query for namespace:{}'.format(_namespace))
        _services = self.kiali_client.service_list(namespaces=[_namespace])
        logger.debug('Query response, Namespace:{}, Services:{}'.format(_namespace, _services))
        # if we have a service, select a service randomly and return it
        if len(_services) > 0:
            _random_service = random.choice(_services)
            return [
                {
                    'name': self.FILTER_ENUM.SERVICE_NAME.text,
                    'value': _random_service.name
                }
            ]
        return []

    def test_routing_create(self, name, namespace, routing_type,
                            peer_auth_mode=None,
                            tls=RoutingWizardTLS.ISTIO_MUTUAL, load_balancer=True,
                            load_balancer_type=RoutingWizardLoadBalancer.ROUND_ROBIN,
                            gateway=True, include_mesh_gateway=True,
                            circuit_braker=False,
                            skip_advanced=False):
        logger.debug('Routing Wizard {} for Service: {}, {}'.format(routing_type, name, namespace))
        # load service details page
        self._prepare_load_details_page(name, namespace)
        self.open(name, namespace)
        self.page.actions.delete_all_routing()
        if routing_type == RoutingWizardType.TRAFFIC_SHIFTING:
            assert self.page.actions.create_weighted_routing(
                tls=tls,
                peer_auth_mode=peer_auth_mode,
                load_balancer=load_balancer,
                load_balancer_type=load_balancer_type, gateway=gateway,
                include_mesh_gateway=include_mesh_gateway,
                circuit_braker=circuit_braker,
                skip_advanced=skip_advanced)
            assert not self.page.actions.is_delete_disabled()
            assert self.page.actions.is_update_weighted_enabled()
            assert self.page.actions.is_create_matching_disabled()
            assert self.page.actions.is_tcp_shifting_disabled()
            assert self.page.actions.is_timeouts_disabled()
            assert self.page.actions.is_suspend_disabled()
        elif routing_type == RoutingWizardType.TCP_TRAFFIC_SHIFTING:
            assert self.page.actions.create_tcp_traffic_shifting(
                tls=tls,
                peer_auth_mode=peer_auth_mode,
                load_balancer=load_balancer,
                load_balancer_type=load_balancer_type, gateway=gateway,
                include_mesh_gateway=include_mesh_gateway,
                skip_advanced=skip_advanced)
            assert not self.page.actions.is_delete_disabled()
            assert self.page.actions.is_tcp_shifting_enabled()
            assert self.page.actions.is_create_weighted_disabled()
            assert self.page.actions.is_create_matching_disabled()
            assert self.page.actions.is_timeouts_disabled()
            assert self.page.actions.is_suspend_disabled()
        elif routing_type == RoutingWizardType.REQUEST_ROUTING:
            assert self.page.actions.create_matching_routing(
                tls=tls,
                peer_auth_mode=peer_auth_mode,
                load_balancer=load_balancer,
                load_balancer_type=load_balancer_type, gateway=gateway,
                include_mesh_gateway=include_mesh_gateway,
                circuit_braker=circuit_braker,
                skip_advanced=skip_advanced)
            assert not self.page.actions.is_delete_disabled()
            assert self.page.actions.is_update_matching_enabled()
            assert self.page.actions.is_create_weighted_disabled()
            assert self.page.actions.is_tcp_shifting_disabled()
            assert self.page.actions.is_timeouts_disabled()
            assert self.page.actions.is_suspend_disabled()
        elif routing_type == RoutingWizardType.FAULT_INJECTION:
            assert self.page.actions.suspend_traffic(
                tls=tls,
                peer_auth_mode=peer_auth_mode,
                load_balancer=load_balancer,
                load_balancer_type=load_balancer_type, gateway=gateway,
                include_mesh_gateway=include_mesh_gateway,
                circuit_braker=circuit_braker,
                skip_advanced=skip_advanced)
            assert not self.page.actions.is_delete_disabled()
            assert self.page.actions.is_create_matching_disabled()
            assert self.page.actions.is_create_weighted_disabled()
            assert self.page.actions.is_tcp_shifting_disabled()
            assert self.page.actions.is_timeouts_disabled()
            assert self.page.actions.is_update_suspended_enabled()
        elif routing_type == RoutingWizardType.REQUEST_TIMEOUTS:
            assert self.page.actions.request_timeouts(
                tls=tls,
                peer_auth_mode=peer_auth_mode,
                load_balancer=load_balancer,
                load_balancer_type=load_balancer_type, gateway=gateway,
                include_mesh_gateway=include_mesh_gateway,
                circuit_braker=circuit_braker,
                skip_advanced=skip_advanced)
            assert not self.page.actions.is_delete_disabled()
            assert self.page.actions.is_create_matching_disabled()
            assert self.page.actions.is_create_weighted_disabled()
            assert self.page.actions.is_tcp_shifting_disabled()
            assert self.page.actions.is_suspend_disabled()
            assert self.page.actions.is_timeouts_enabled()
        # get service details from rest
        service_details_rest = self.kiali_client.service_details(
            namespace=namespace,
            service_name=name)
        assert len(service_details_rest.virtual_services) == 1, 'Service should have 1 VS'
        assert len(service_details_rest.destination_rules) == 1, 'Service should have 1 DR'
        assert service_details_rest.virtual_services[0].name == name
        assert service_details_rest.destination_rules[0].name == name

        if load_balancer_type:
            assert word_in_text(load_balancer_type.text.lower(),
                                service_details_rest.destination_rules[0].traffic_policy,
                                load_balancer)

        if tls:
            assert word_in_text(tls.text.lower(),
                                service_details_rest.destination_rules[0].traffic_policy,
                                tls)
            if tls == RoutingWizardTLS.MUTUAL:
                assert word_in_text('{} {}'.format(TLSMutualValues.CLIENT_CERT.key.lower(),
                                                   TLSMutualValues.CLIENT_CERT.text),
                                    service_details_rest.destination_rules[0].traffic_policy)
                assert word_in_text('{} {}'.format(TLSMutualValues.PRIVATE_KEY.key.lower(),
                                                   TLSMutualValues.PRIVATE_KEY.text),
                                    service_details_rest.destination_rules[0].traffic_policy)
                assert word_in_text('{} {}'.format(TLSMutualValues.CA_CERT.key.lower(),
                                                   TLSMutualValues.CA_CERT.text),
                                    service_details_rest.destination_rules[0].traffic_policy)
        # get virtual service details from rest
        istio_config_details_rest = self.kiali_client.istio_config_details(
            namespace=namespace,
            object_type=OBJECT_TYPE.VIRTUAL_SERVICE.text,
            object_name=service_details_rest.virtual_services[0].name)
        assert word_in_text('\"mesh\"',
                            istio_config_details_rest.text,
                            gateway and include_mesh_gateway)
        # get destination rule details from rest
        istio_config_details_rest = self.kiali_client.istio_config_details(
            namespace=namespace,
            object_type=OBJECT_TYPE.DESTINATION_RULE.text,
            object_name=service_details_rest.destination_rules[0].name)
        assert word_in_text('\"http1MaxPendingRequests\"',
                            istio_config_details_rest.text,
                            circuit_braker)

    def test_routing_update(self, name, namespace, routing_type,
                            peer_auth_mode=None,
                            tls=RoutingWizardTLS.ISTIO_MUTUAL, load_balancer=True,
                            load_balancer_type=RoutingWizardLoadBalancer.ROUND_ROBIN,
                            gateway=True, include_mesh_gateway=True,
                            circuit_braker=False,
                            skip_advanced=False):
        logger.debug('Routing Update Wizard {} for Service: {}, {}'.format(routing_type,
                                                                           name,
                                                                           namespace))
        # load service details page
        self._prepare_load_details_page(name, namespace)
        self.open(name, namespace)
        if routing_type == RoutingWizardType.TRAFFIC_SHIFTING:
            assert self.page.actions.update_weighted_routing(
                tls=tls,
                peer_auth_mode=peer_auth_mode,
                load_balancer=load_balancer,
                load_balancer_type=load_balancer_type, gateway=gateway,
                include_mesh_gateway=include_mesh_gateway,
                circuit_braker=circuit_braker,
                skip_advanced=skip_advanced)
            assert not self.page.actions.is_delete_disabled()
            assert self.page.actions.is_update_weighted_enabled()
            assert self.page.actions.is_create_matching_disabled()
            assert self.page.actions.is_tcp_shifting_disabled()
            assert self.page.actions.is_timeouts_disabled()
            assert self.page.actions.is_suspend_disabled()
        elif routing_type == RoutingWizardType.TCP_TRAFFIC_SHIFTING:
            assert self.page.actions.update_tcp_traffic_shifting(
                tls=tls,
                peer_auth_mode=peer_auth_mode,
                load_balancer=load_balancer,
                load_balancer_type=load_balancer_type, gateway=gateway,
                include_mesh_gateway=include_mesh_gateway,
                skip_advanced=skip_advanced)
            assert not self.page.actions.is_delete_disabled()
            assert self.page.actions.is_create_weighted_disabled()
            assert self.page.actions.is_create_matching_disabled()
            assert self.page.actions.is_tcp_shifting_enabled()
            assert self.page.actions.is_timeouts_disabled()
            assert self.page.actions.is_suspend_disabled()
        elif routing_type == RoutingWizardType.REQUEST_ROUTING:
            assert self.page.actions.update_matching_routing(
                tls=tls,
                peer_auth_mode=peer_auth_mode,
                load_balancer=load_balancer,
                load_balancer_type=load_balancer_type, gateway=gateway,
                include_mesh_gateway=include_mesh_gateway,
                skip_advanced=skip_advanced)
            assert not self.page.actions.is_delete_disabled()
            assert self.page.actions.is_update_matching_enabled()
            assert self.page.actions.is_create_weighted_disabled()
            assert self.page.actions.is_tcp_shifting_disabled()
            assert self.page.actions.is_timeouts_disabled()
            assert self.page.actions.is_suspend_disabled()
        elif routing_type == RoutingWizardType.FAULT_INJECTION:
            assert self.page.actions.update_suspended_traffic(
                tls=tls,
                peer_auth_mode=peer_auth_mode,
                load_balancer=load_balancer,
                load_balancer_type=load_balancer_type, gateway=gateway,
                include_mesh_gateway=include_mesh_gateway,
                circuit_braker=circuit_braker,
                skip_advanced=skip_advanced)
            assert not self.page.actions.is_delete_disabled()
            assert self.page.actions.is_create_matching_disabled()
            assert self.page.actions.is_create_weighted_disabled()
            assert self.page.actions.is_tcp_shifting_disabled()
            assert self.page.actions.is_timeouts_disabled()
            assert self.page.actions.is_update_suspended_enabled()
        elif routing_type == RoutingWizardType.REQUEST_TIMEOUTS:
            assert self.page.actions.update_request_timeouts(
                tls=tls,
                peer_auth_mode=peer_auth_mode,
                load_balancer=load_balancer,
                load_balancer_type=load_balancer_type, gateway=gateway,
                include_mesh_gateway=include_mesh_gateway,
                circuit_braker=circuit_braker,
                skip_advanced=skip_advanced)
            assert not self.page.actions.is_delete_disabled()
            assert self.page.actions.is_create_matching_disabled()
            assert self.page.actions.is_create_weighted_disabled()
            assert self.page.actions.is_tcp_shifting_disabled()
            assert self.page.actions.is_suspend_disabled()
            assert self.page.actions.is_timeouts_enabled()
        # get service details from rest
        service_details_rest = self.kiali_client.service_details(
            namespace=namespace,
            service_name=name)
        assert len(service_details_rest.virtual_services) == 1, 'Service should have 1 VS'
        assert len(service_details_rest.destination_rules) == 1, 'Service should have 1 DR'
        assert service_details_rest.virtual_services[0].name == name
        assert service_details_rest.destination_rules[0].name == name

        if load_balancer_type:
            assert word_in_text(load_balancer_type.text.lower(),
                                service_details_rest.destination_rules[0].traffic_policy,
                                load_balancer)

        if tls and tls.text != RoutingWizardTLS.UNSET.text:
            assert word_in_text(tls.text.lower(),
                                service_details_rest.destination_rules[0].traffic_policy,
                                tls)
        # get virtual service details from rest
        istio_config_details_rest = self.kiali_client.istio_config_details(
            namespace=namespace,
            object_type=OBJECT_TYPE.VIRTUAL_SERVICE.text,
            object_name=service_details_rest.virtual_services[0].name)

        assert word_in_text('\"mesh\"',
                            istio_config_details_rest.text,
                            gateway and include_mesh_gateway)
        # get destination rule details from rest
        istio_config_details_rest = self.kiali_client.istio_config_details(
            namespace=namespace,
            object_type=OBJECT_TYPE.DESTINATION_RULE.text,
            object_name=service_details_rest.destination_rules[0].name)
        assert word_in_text('\"http1MaxPendingRequests\"',
                            istio_config_details_rest.text,
                            circuit_braker)

    def test_routing_delete(self, name, namespace):
        logger.debug('Routing Delete for Service: {}, {}'.format(name, namespace))
        # load service details page
        self._prepare_load_details_page(name, namespace)
        self.open(name, namespace)
        assert self.page.actions.delete_all_routing()
        assert self.page.actions.is_delete_disabled()
        assert self.page.actions.is_create_weighted_enabled()
        assert self.page.actions.is_create_matching_enabled()
        assert self.page.actions.is_tcp_shifting_enabled()
        assert self.page.actions.is_suspend_enabled()
        assert self.page.actions.is_timeouts_enabled()
        # get service details from rest
        service_details_rest = self.kiali_client.service_details(
            namespace=namespace,
            service_name=name)
        assert len(service_details_rest.virtual_services) == 0, 'Service should have no VS'
        assert len(service_details_rest.destination_rules) == 0, 'Service should have no DR'


class IstioConfigPageTest(AbstractListPageTest):
    FILTER_ENUM = IstioConfigPageFilter
    SORT_ENUM = IstioConfigPageSort

    def __init__(self, kiali_client, openshift_client, browser):
        AbstractListPageTest.__init__(
            self, kiali_client=kiali_client,
            openshift_client=openshift_client, page=IstioConfigPage(browser))
        self.browser = browser

    def _prepare_load_details_page(self, name, namespace, object_type=None):
        # load the page first
        self.page.load(force_load=True)
        # apply namespace
        self.apply_namespaces(namespaces=[namespace])
        # apply filters
        _filters = [{'name': IstioConfigPageFilter.ISTIO_NAME.text, 'value': name}]
        if object_type:
            _filters.append({'name': IstioConfigPageFilter.ISTIO_TYPE.text, 'value': object_type})
        self.apply_filters(filters=_filters)

    def load_details_page(self, name, namespace, object_type=None,
                          force_refresh=False, load_only=False):
        logger.debug('Loading details page for istio config: {}'.format(name))
        if not self.is_in_details_page(name, namespace):
            self._prepare_load_details_page(name, namespace, object_type)
            wait_to_spinner_disappear(self.browser)
            self.open(name, namespace, force_refresh)
            wait_to_spinner_disappear(self.browser)
            self.browser.wait_for_element(locator='//button[contains(., "YAML")]',
                                          parent='//*[contains(@class, "pf-c-page__main-section")]')
            wait_to_spinner_disappear(self.browser)
        return self.page.content.get_details(name, load_only)

    def assert_all_items(self, namespaces=[], filters=[], sort_options=[], force_clear_all=True):
        logger.debug('Asserting all istio config items')
        logger.debug('Filters:{}'.format(filters))

        # apply namespaces
        self.apply_namespaces(namespaces, force_clear_all=force_clear_all)

        # apply filters
        self.apply_filters(filters=filters, force_clear_all=force_clear_all)

        # apply sorting
        self.sort(sort_options)

        _sn = self.FILTER_ENUM.ISTIO_NAME.text
        _istio_names = [_f['value'] for _f in filters if _f['name'] == _sn]

        # get rules from rest api
        config_list_rest = self.kiali_client.istio_config_list(
            namespaces=namespaces, config_names=_istio_names)
        logger.debug('Istio config list REST:{}]'.format(config_list_rest))

        # get rules from ui
        config_list_ui = self.page.content.all_items
        logger.debug('Istio config list UI:{}]'.format(config_list_ui))

        # get configs from OC api
        config_list_oc = self.openshift_client.istio_config_list(
            namespaces=namespaces, config_names=_istio_names)
        logger.debug('Istio config list OC API:{}]'.format(config_list_oc))

        # compare 3 way results
        assert len(config_list_ui) == len(config_list_rest), \
            "UI {} and REST {} config number not equal".format(config_list_ui, config_list_rest)
        assert len(config_list_ui) == len(config_list_oc)
        for config_ui in config_list_ui:
            found = False
            for config_rest in config_list_rest:
                if config_ui.is_equal(config_rest, advanced_check=True):
                    found = True
                    break
            if not found:
                assert found, '{} not found in REST'.format(config_ui)
            found = False
            for config_oc in config_list_oc:
                if config_ui.is_equal(config_oc, advanced_check=False):
                    found = True
                    break
            if not found:
                assert found, '{} not found in OC'.format(config_ui)
            if config_ui.validation != IstioConfigValidation.NA:
                assert '/console/namespaces/{}/istio/{}/{}?list=yaml'.format(
                    config_ui.namespace,
                    ISTIO_CONFIG_TYPES[config_ui.object_type],
                    config_ui.name) in \
                        config_ui.config_link, 'Wrong config link {}'.format(
                            config_ui.config_link)
        logger.debug('Done asserting all istio config items')

    def assert_random_details(self, namespaces=[], filters=[]):
        # get istio config from rest api
        configs_rest = self.kiali_client.istio_config_list(namespaces, filters)

        # random configs filters
        assert len(configs_rest) > 0
        if len(configs_rest) > 3:
            _random_configs = random.sample(configs_rest, 3)
        else:
            _random_configs = configs_rest
        # create filters
        for _selected_config in _random_configs:
            self.assert_details(_selected_config.name,
                                _selected_config.object_type,
                                _selected_config.namespace)

    def assert_details(self, name, object_type,
                       namespace=None, error_messages=[], apply_filters=True):
        logger.debug('Asserting details for: {}, in namespace: {}'.format(name, namespace))

        # load config details page
        config_details_ui = self.load_details_page(name, namespace, object_type,
                                                   force_refresh=False)
        assert config_details_ui
        assert name == config_details_ui.name
        assert config_details_ui.text
        # get config details from rest
        config_details_rest = self.kiali_client.istio_config_details(
            namespace=namespace,
            object_type=object_type,
            object_name=name)
        assert config_details_rest
        assert name == config_details_rest.name
        assert config_details_rest.text
        # get config details from OC
        config_details_oc = self.openshift_client.istio_config_details(
            namespace=namespace,
            object_name=name,
            object_type=object_type)
        assert config_details_oc
        assert name == config_details_oc.name
        for error_message in error_messages:
            assert error_message in config_details_rest.error_messages, \
                'Expected Error messages:{} is not in REST:{}'.format(
                    error_message,
                    config_details_rest.error_messages)
        for error_message in config_details_ui.error_messages:
            assert error_message in config_details_rest.error_messages, \
                'UI Error messages:{} is not in REST:{}'.format(
                    error_message,
                    config_details_rest.error_messages)
        # TODO for Gateways there is no way to check in UI if it is valid or N/A
        assert config_details_ui.is_equal(
            config_details_rest,
            advanced_check=True if
            config_details_rest.validation != IstioConfigValidation.NA
            else False)
        # find key: value pairs from UI in a REST
        for config_ui in re.split(' ',
                                  str(config_details_ui.text).
                                  replace('\'', '').
                                  replace('~', 'null').
                                  replace('selfLink: >- ', 'selfLink: ').
                                  replace(': > ', ': ').
                                  replace('{', '').
                                  replace('}', '').
                                  replace(':" /', ':"/').
                                  replace('"', '').
                                  replace(' ,', ',').
                                  replace(',', '').
                                  replace('[', '').
                                  replace(']', '').
                                  replace('\\', '').
                                  replace(' :', ':').
                                  replace(' .', '.').
                                  replace('...', '').
                                  replace(' \/', '\/')):
            if config_ui.endswith(':'):
                ui_key = config_ui
            elif config_ui.strip() != '-':  # skip this line, it was for formatting
                # the previous one was the key of this value
                found = False
                # make the REST result into the same format as shown in UI
                # to compare only the values
                for config_rest in str(config_details_rest.text).\
                        replace('\\n', '').\
                        replace('\\', '').\
                        replace('{', '').\
                        replace('}', '').\
                        replace('"', '').\
                        replace(',', '').\
                        replace('[', '').\
                        replace(']', '').\
                        split(' '):
                    if config_rest.endswith(':'):
                        rest_key = config_rest
                    else:
                        # the previous one was the key of this value
                        if ui_key == rest_key and config_ui == config_rest:
                            found = True
                            break
                if not found and not self._is_skip_key(ui_key):
                    assert found, '{} {} not found in REST'.format(ui_key, config_ui)
                found = False
                # make the OC result into the same format as shown in UI
                # to compare only the values
                config_oc_list = str(config_details_oc.text).\
                    replace('\n', '').\
                    replace('\'', '').\
                    replace("\\n", '').\
                    replace(' - ', '').\
                    replace('{', '').\
                    replace('}', '').\
                    replace('"', '').\
                    replace(',', '').\
                    replace('[', '').\
                    replace(']', '').\
                    split(' ')
                config_oc_list.append('kind:')
                config_oc_list.append(config_details_oc._type)
                if ui_key == 'apiVersion:' or ui_key == 'selfLink:':
                    continue
                for config_oc in config_oc_list:
                    if config_oc.endswith(':'):
                        oc_key = re.sub('^f:', '', config_oc)
                    else:
                        # the previous one was the key of this value
                        if (ui_key == oc_key and config_ui == config_oc) or config_ui == 'null':
                            found = True
                            break
                if not found and not self._is_skip_key(ui_key):
                    assert found, '{} {} not found in OC'.format(ui_key, config_ui)
        logger.debug('Done asserting details for: {}, in namespace: {}'.format(name, namespace))

    def _is_skip_key(self, key):
        return 'last-applied-configuration' in key \
            or key.startswith('f:') \
            or 'managedFields' in key \
            or 'creationTimestamp' in key \
            or 'selfLink' in key

    def test_gateway_create(self, name, hosts, port_name, port_number, namespaces):
        logger.debug('Creating Gateway: {}, from namespaces: {}'.format(name, namespaces))
        # load the page first
        self.page.load(force_load=True)
        # apply namespace
        self.apply_namespaces(namespaces=namespaces)
        wait_to_spinner_disappear(self.browser)
        self.page.actions.create_istio_config_gateway(name, hosts, port_name, port_number)
        for namespace in namespaces:
            self.assert_details(name, IstioConfigObjectType.GATEWAY.text, namespace)

    def test_sidecar_create(self, name, egress_host, labels, namespaces):
        logger.debug('Creating Sidecar: {}, from namespaces: {}'.format(name, namespaces))
        # load the page first
        self.page.load(force_load=True)
        # apply namespace
        self.apply_namespaces(namespaces=namespaces)
        wait_to_spinner_disappear(self.browser)
        self.page.actions.create_istio_config_sidecar(name, egress_host, labels)
        for namespace in namespaces:
            self.assert_details(name, IstioConfigObjectType.SIDECAR.text, namespace)

    def test_authpolicy_create(self, name, policy, namespaces, labels=None, policy_action=None):
        logger.debug('Creating AuthorizationPolicy: {}, from namespaces: {}'.format(name,
                                                                                    namespaces))
        # load the page first
        self.page.load(force_load=True)
        # apply namespace
        self.apply_namespaces(namespaces=namespaces)
        wait_to_spinner_disappear(self.browser)
        is_created = self.page.actions.create_istio_config_authpolicy(name=name,
                                                                      policy=policy,
                                                                      labels=labels,
                                                                      policy_action=policy_action)
        if policy_action == AuthPolicyActionType.DENY.text:
            # in a case of DENY action the Create button is disabled
            assert not is_created, "Should not create but in fact created AuthPolicy"
        else:
            assert is_created
        if is_created:
            for namespace in namespaces:
                self.assert_details(name, IstioConfigObjectType.AUTHORIZATION_POLICY.text,
                                    namespace)
                config_details_rest = self.kiali_client.istio_config_details(
                    namespace=namespace,
                    object_type=IstioConfigObjectType.AUTHORIZATION_POLICY.text,
                    object_name=name)
                if policy == AuthPolicyType.ALLOW_ALL.text or \
                        policy_action == AuthPolicyActionType.ALLOW.text:
                    assert '\"action\": \"ALLOW\"' in config_details_rest.text

    def test_peerauth_create(self, name, namespaces, expected_created=True,
                             labels=None, mtls_mode=None, mtls_ports={}):
        logger.debug('Creating PeerAuthentication: {}, from namespaces: {}'.format(name,
                                                                                   namespaces))
        # load the page first
        self.page.load(force_load=True)
        # apply namespace
        self.apply_namespaces(namespaces=namespaces)
        wait_to_spinner_disappear(self.browser)
        is_created = self.page.actions.create_istio_config_peerauth(
            name, labels, mtls_mode, mtls_ports)
        assert not expected_created ^ is_created, \
            "Created expected {} but should be {}".format(expected_created,
                                                          is_created)
        if is_created:
            for namespace in namespaces:
                self.assert_details(name, IstioConfigObjectType.PEER_AUTHENTICATION.text,
                                    namespace)
                config_details_rest = self.kiali_client.istio_config_details(
                    namespace=namespace,
                    object_type=IstioConfigObjectType.PEER_AUTHENTICATION.text,
                    object_name=name)
                if mtls_mode:
                    assert '\"mode\": \"{}\"'.format(mtls_mode) in config_details_rest.text
                if labels:
                    assert labels.replace('=', '\": \"') in config_details_rest.text
                if mtls_ports:
                    for _key, _value in mtls_ports.items():
                        assert '\"portLevelMtls\": \"{}\": \"mode\": \"{}\"'.format(_key, _value) \
                            in config_details_rest.text.replace('{', '').replace('}', '')

    def test_requestauth_create(self, name, namespaces, expected_created=True,
                                labels=None, jwt_rules={}):
        logger.debug('Creating RequestAuthentication: {}, from namespaces: {}'.format(
            name,
            namespaces))
        # load the page first
        self.page.load(force_load=True)
        # apply namespace
        self.apply_namespaces(namespaces=namespaces)
        wait_to_spinner_disappear(self.browser)
        is_created = self.page.actions.create_istio_config_requestauth(name, labels, jwt_rules)
        assert not expected_created ^ is_created, \
            "Created expected {} but should be {}".format(expected_created,
                                                          is_created)
        if is_created:
            for namespace in namespaces:
                self.assert_details(name, IstioConfigObjectType.REQUEST_AUTHENTICATION.text,
                                    namespace)
                config_details_rest = self.kiali_client.istio_config_details(
                    namespace=namespace,
                    object_type=IstioConfigObjectType.REQUEST_AUTHENTICATION.text,
                    object_name=name)
                if labels:
                    assert labels.replace('=', '\": \"') in config_details_rest.text
                if jwt_rules:
                    for _key, _value in jwt_rules.items():
                        assert '\"{}\": \"{}\"'.format(_key, _value) in config_details_rest.text

    def delete_istio_config(self, name, object_type, namespace=None):
        logger.debug('Deleting istio config: {}, from namespace: {}'.format(name, namespace))
        self.load_details_page(name, namespace, object_type, force_refresh=False, load_only=True)
        # TODO: wait for all notification boxes to disappear, those are blocking the button
        time.sleep(10)
        self.page.actions.select('Delete')
        self.browser.click(self.browser.element(
            parent=ListViewAbstract.DIALOG_ROOT,
            locator=('.//button[text()="Delete"]')))

    def assert_host_link(self, config_name, namespace, host_name, is_link_expected=True):
        logger.debug('Asserting host link for: {}, in namespace: {}'.format(config_name, namespace))

        # load config details page
        self.load_details_page(config_name, namespace, force_refresh=False, load_only=True)
        assert not is_link_expected ^ self.is_host_link(host_name)

    def click_on_gateway(self, name, namespace):
        self.browser.click(self.browser.element(locator=self.page.content.CONFIG_TAB_OVERVIEW,
                                                parent=self.page.content.CONFIG_TABS_PARENT))
        self.browser.click(
            './/a[contains(@href, "/namespaces/{}/istio/gateways/{}")]'.format(namespace, name),
            parent=self.page.content.locator)

    def get_additional_filters(self, namespaces, current_filters):
        logger.debug('Current filters:{}'.format(current_filters))
        # get rules of a namespace
        _namespace = namespaces[0]
        logger.debug('Running Rules REST query for namespace:{}'.format(_namespace))
        _istio_config_list = self.kiali_client.istio_config_list(
            namespaces=[_namespace])
        logger.debug('Query response, Namespace:{}, Istio config list:{}'.format(
            _namespace, _istio_config_list))
        # if we have a config, select a config randomly and return it
        if len(_istio_config_list) > 0:
            _random_config = random.choice(_istio_config_list)
            return [
                {
                    'name': self.FILTER_ENUM.ISTIO_NAME.text,
                    'value': _random_config.name
                }
            ]
        return []


class DistributedTracingPageTest(AbstractListPageTest):

    def load_page(self, namespaces, force_clear_all):
        self.page.load(force_load=True)
        # apply namespaces
        self.apply_namespaces(namespaces, force_clear_all=force_clear_all)

    def __init__(self, kiali_client, openshift_client, browser):
        AbstractListPageTest.__init__(
            self, kiali_client=kiali_client,
            openshift_client=openshift_client, page=DistributedTracingPage(browser))
        self.browser = browser

    def assert_search_traces(self, service_name, namespaces=[], force_clear_all=True):
        # test Search Traces for provided Namespace and Service
        self.load_page(namespaces, force_clear_all)
        self.page.traces.search_traces(service_name)
        assert not self.page.traces.is_oc_login_displayed, "OC Login should not be displayed"
        if not self.page.traces.has_no_results:
            assert self.page.traces.has_results


class ValidationsTest(object):

    def __init__(self, kiali_client, objects_path, openshift_client, browser=None):
        self.kiali_client = kiali_client
        self.openshift_client = openshift_client
        self.browser = browser
        self.objects_path = objects_path

    def _istio_config_create(self, yaml_file, namespace):
        self._istio_config_delete(yaml_file, namespace=namespace)

        oc_apply(yaml_file=yaml_file,
                 namespace=namespace)

    def _istio_config_delete(self, yaml_file, namespace):
        oc_delete(yaml_file=yaml_file,
                  namespace=namespace)

    def test_istio_objects(self, scenario, namespace=None,
                           config_validation_objects=[],
                           tls_type=None,
                           namespace_tls_objects=[],
                           ignore_common_errors=True):
        """
            All the testing logic goes here.
            It creates the provided scenario yaml into provider namespace.
            And then validates the provided Istio objects if they have the error_messages
        """
        yaml_file = get_yaml_path(self.objects_path, scenario)

        try:
            self._istio_config_create(yaml_file, namespace=namespace)

            for _object in config_validation_objects:
                self._test_validation_errors(object_type=_object.object_type,
                                             object_name=_object.object_name,
                                             namespace=_object.namespace,
                                             error_messages=_object.error_messages,
                                             ignore_common_errors=ignore_common_errors)

            if tls_type:
                self._test_mtls_settings(tls_type,
                                         namespace_tls_objects)
        finally:
            self._istio_config_delete(yaml_file, namespace=namespace)

    def test_service_validation(self, scenario, service_name, namespace,
                                service_validation_objects=[]):
        """
            All the testing logic goes here.
            It creates the provided service scenario yaml into provided namespace.
            And then validates the provided Service objects if they have the error_messages
        """
        yaml_file = get_yaml_path(self.objects_path, scenario)

        try:
            self._istio_config_create(yaml_file, namespace=namespace)

            for _object in service_validation_objects:
                service_details_rest = self.kiali_client.service_details(
                    namespace=namespace,
                    service_name=service_name)
                found = False
                for error_message in service_details_rest.validations:
                    if error_message == _object.error_message:
                        found = True

                assert found, 'Error messages:{} is not in List:{}'.\
                    format(_object.error_message,
                           service_details_rest.validations)
        finally:
            self._istio_config_delete(yaml_file, namespace=namespace)

    def _test_validation_errors(self, object_type, object_name, namespace,
                                error_messages=[], ignore_common_errors=True):
        # get config detals from rest
        config_details_rest = self.kiali_client.istio_config_details(
            namespace=namespace,
            object_type=object_type,
            object_name=object_name)

        rest_error_messages = config_details_rest.error_messages

        if ignore_common_errors:
            remove_from_list(rest_error_messages, KIA0201)
            remove_from_list(rest_error_messages, KIA0301)

        if self.openshift_client.is_auto_mtls():
            # remove errors which are ignored during auto mtls
            remove_from_list(error_messages, KIA0501)
            remove_from_list(error_messages, KIA0204)
            remove_from_list(error_messages, KIA0205)
            remove_from_list(error_messages, KIA0401)
            remove_from_list(error_messages, KIA0206)

        assert len(error_messages) == len(rest_error_messages), \
            'Error messages are different Expected:{}, Got:{}'.\
            format(error_messages,
                   rest_error_messages)

        for error_message in error_messages:
            assert error_message in rest_error_messages, \
                'Error messages:{} is not in List:{}'.\
                format(error_message,
                       rest_error_messages)

    def _test_mtls_settings(self, tls_type, namespace_tls_objects):
        """
            Validates both Mesh-wide mTLS settings in toolbar,
            and namespace wide TLS settings per namespace in Overview page.
        """
        _tests = OverviewPageTest(
                kiali_client=self.kiali_client, openshift_client=self.openshift_client,
                browser=self.browser)
        actual_mtls_type = _tests.get_mesh_wide_tls()
        assert actual_mtls_type == tls_type, \
            'Mesh-wide TLS type expected: {} got: {}'.format(tls_type, actual_mtls_type)
        if namespace_tls_objects:
            overview_items = _tests.page.content.all_items
            for tls_object in namespace_tls_objects:
                for overview_item in overview_items:
                    if overview_item.namespace == tls_object.namespace:
                        assert tls_object.tls_type == overview_item.tls_type, \
                            'Namespace TLS type expected: {} got: {} for {}'.format(
                                tls_object.tls_type,
                                overview_item.tls_type,
                                overview_item.namespace)


class ConfigValidationObject(object):

    def __init__(self, object_type, object_name, namespace=None, error_messages=[]):
        self.namespace = namespace
        self.object_type = object_type
        self.object_name = object_name
        self.error_messages = error_messages


class ServiceValidationObject(object):

    def __init__(self, error_message, severity=None):
        self.error_message = error_message
        self.severity = severity


class NamespaceTLSObject(object):

    def __init__(self, namespace, tls_type):
        self.namespace = namespace
        self.tls_type = tls_type
