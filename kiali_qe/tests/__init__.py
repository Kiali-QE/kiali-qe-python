import random
import re

from kiali_qe.components.enums import (
    PaginationPerPage,
    ServicesPageFilter,
    IstioConfigPageFilter,
    WorkloadsPageFilter,
    ApplicationsPageFilter,
    OverviewPageFilter,
    IstioConfigObjectType as OBJECT_TYPE,
    IstioConfigValidation,
    MetricsSource,
    MetricsHistograms,
    MetricsFilter,
    MetricsDuration,
    MetricsRefreshInterval
)
from kiali_qe.utils import is_equal, is_sublist
from kiali_qe.utils.log import logger

from kiali_qe.pages import (
    ServicesPage,
    IstioConfigPage,
    WorkloadsPage,
    ApplicationsPage,
    OverviewPage
)


class AbstractListPageTest(object):
    FILTER_ENUM = None

    def __init__(self, kiali_client, openshift_client, page):
        self.kiali_client = kiali_client
        self.openshift_client = openshift_client
        self.page = page

    def _namespaces_ui(self):
        return self.page.filter.filter_options(filter_name=self.FILTER_ENUM.NAMESPACE.text)

    def assert_all_items(self, filters, force_clear_all=True):
        """
        Apply supplied filter in to UI, REST, OC and assert content

        Parameters
        ----------
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

    def get_additional_filters(self, current_filters):
        raise NotImplementedError('This method should be implemented on sub class')

    def apply_filters(self, filters, force_clear_all=True):
        """
        Apply supplied filter in to UI and assert with supplied and applied filters

        Parameters
        ----------
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

    def assert_filter_options(self):
        # test available options
        options_defined = [item.text for item in self.FILTER_ENUM]
        options_listed = self.page.filter.filters
        logger.debug('Options[defined:{}, defined:{}]'.format(options_defined, options_listed))
        assert is_equal(options_defined, options_listed)

    def assert_applied_filters(self, filters):
        # validate applied filters
        _active_filters = self.page.filter.active_filters
        logger.debug('Filters[applied:{}, active:{}]'.format(filters, _active_filters))
        assert is_equal(filters, _active_filters)

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
        # create filters
        for _selected_namespace in _random_namespaces:
            _defined_filters.append(
                {'name': self.FILTER_ENUM.NAMESPACE.text, 'value': _selected_namespace})
        # add additional filters
        logger.debug('Adding additional filters')
        _defined_filters.extend(self.get_additional_filters(_defined_filters))
        logger.debug('Defined filters with additional filters:{}'.format(_defined_filters))

        # apply filters test
        _applied_filters = []
        for _defined_filter in _defined_filters:
            # add it in to applied list
            _applied_filters.append(_defined_filter)
            # apply filter and check the contents
            self.assert_all_items(filters=_applied_filters, force_clear_all=False)

        # remove filters test
        for _defined_filter in _defined_filters:
            # remove it from our list
            _applied_filters.remove(_defined_filter)
            # apply filter and check the contents
            self.assert_all_items(filters=_applied_filters, force_clear_all=False)
            # test remove all
            if len(_applied_filters) == 2:
                self.assert_all_items(filters=[], force_clear_all=True)
                break

    def assert_pagination_feature(self):
        pagination = self.page.pagination
        # test options
        options_defined = [item.value for item in PaginationPerPage]
        options_listed = pagination.items_per_page_options
        logger.debug('options[defined:{}, listed:{}]'.format(options_defined, options_listed))
        assert is_equal(options_defined, options_listed), \
            ('Options mismatch: defined:{}, listed:{}'.format(options_defined, options_listed))
        # set to minimum value so there is more pages to test
        pagination.set_items_per_page(PaginationPerPage.FIVE.value)
        # test page next, previous, first, last, to page
        total_pages = pagination.total_pages
        logger.debug('Total pages found:{}'.format(total_pages))
        if total_pages > 1:
            # last page
            pagination.move_to_last_page()
            assert pagination.current_page == total_pages
            # first page
            pagination.move_to_first_page()
            assert pagination.current_page == 1
            # next page
            pagination.move_to_next_page()
            assert pagination.current_page == 2
            # previous page
            pagination.move_to_previous_page()
            assert pagination.current_page == 1
            # to page
            pagination.move_to_page(2)
            assert pagination.current_page == 2
            # navigate to all pages
            for to_page in range(1, total_pages + 1):
                pagination.move_to_page(to_page)
                assert pagination.current_page == to_page
        # test items per page and options
        for per_page in options_listed:
            if pagination.total_items > per_page:
                pagination.set_items_per_page(per_page)
                assert len(self.page.content.items) == per_page
                assert pagination.items_per_page == per_page
        # test total items
        total_items_pagin = pagination.total_items
        total_items_page = len(self.page.content.all_items)
        assert total_items_pagin == total_items_page, \
            'Total items mismatch: pagination:{}, page:{}'.format(total_items_pagin,
                                                                  total_items_page)

    def assert_metrics_options(self, metrics_page):
        metrics_page.open()
        self._assert_metrics_settings(metrics_page)
        self._assert_metrics_destination(metrics_page)
        self._assert_metrics_duration(metrics_page)
        self._assert_metrics_interval(metrics_page)

    def _assert_metrics_settings(self, metrics_page):
        # test available filters
        options_defined = [item.text for item in MetricsFilter]
        for item in MetricsHistograms:
            options_defined.append(item.text)
        options_listed = metrics_page.filter.items
        logger.debug('Filter options[defined:{}, listed:{}]'
                     .format(options_defined, options_listed))
        assert is_equal(options_defined, options_listed), \
            ('Filter Options mismatch: defined:{}, listed:{}'
             .format(options_defined, options_listed))
        # enable disable each filter
        for filter_name in options_listed:
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
        self._assert_metrics_options(metrics_page, MetricsDuration, 'duration')

    def _assert_metrics_interval(self, metrics_page):
        self._assert_metrics_options(metrics_page, MetricsRefreshInterval, 'interval')

    def _assert_metrics_options(self, metrics_page, enum, attr_name):
        options_defined = [item.text for item in enum]
        attr = getattr(metrics_page, attr_name)
        options_listed = attr.options
        logger.debug('Options[defined:{}, listed:{}]'.format(options_defined, options_listed))
        assert is_equal(options_defined, options_listed), \
            ('Options mismatch: defined:{}, listed:{}'.format(options_defined, options_listed))


class OverviewPageTest(AbstractListPageTest):
    FILTER_ENUM = OverviewPageFilter

    def _namespaces_ui(self):
        return self.page.filter.filter_options(filter_name=self.FILTER_ENUM.NAME.text)

    def __init__(self, kiali_client, openshift_client, browser):
        AbstractListPageTest.__init__(
            self, kiali_client=kiali_client,
            openshift_client=openshift_client, page=OverviewPage(browser))
        self.browser = browser

    def assert_all_items(self, filters, force_clear_all=True):
        # apply filters
        self.apply_filters(filters=filters, force_clear_all=force_clear_all)

        # get overviews from ui
        overviews_ui = self.page.content.all_items
        # get overviews from rest api
        _ns = self.FILTER_ENUM.NAME.text
        _namespaces = [_f['value'] for _f in filters if _f['name'] == _ns]
        logger.debug('Namespaces:{}'.format(_namespaces))
        overviews_rest = self.kiali_client.overview_list(
            namespaces=_namespaces)

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
                if overview_ui.is_equal(overview_rest, advanced_check=False):
                    found = True
                    break
            assert found, '{} not found in REST'.format(overview_ui)


class ApplicationsPageTest(AbstractListPageTest):
    FILTER_ENUM = ApplicationsPageFilter

    def __init__(self, kiali_client, openshift_client, browser):
        AbstractListPageTest.__init__(
            self, kiali_client=kiali_client,
            openshift_client=openshift_client, page=ApplicationsPage(browser))
        self.browser = browser

    def assert_random_details(self, filters, force_clear_all=True):
        # apply filters
        self.apply_filters(filters=filters, force_clear_all=force_clear_all)
        # get applications from ui
        applications_ui = self.page.content.all_items
        # random applications filters
        assert len(applications_ui) > 0
        if len(applications_ui) > 3:
            _random_applications = random.sample(applications_ui, 3)
        else:
            _random_applications = applications_ui
        # create filters
        for _selected_application in _random_applications:
            self.assert_details(_selected_application.name, _selected_application.namespace)

    def assert_details(self, name, namespace):
        logger.debug('Details: {}, {}'.format(name, namespace))
        # load the page first
        self.page.load(force_load=True)
        # TODO apply pagination feature in get_details
        # apply filters
        self.apply_filters(filters=[
            {'name': ApplicationsPageFilter.NAMESPACE.text, 'value': namespace},
            {'name': ApplicationsPageFilter.APP_NAME.text, 'value': name}])
        # load application details page
        application_details_ui = self.page.content.get_details(name, namespace)
        assert application_details_ui
        assert name == application_details_ui.name
        # get application detals from rest
        application_details_rest = self.kiali_client.application_details(
            namespace=namespace,
            application_name=name)
        assert application_details_rest
        assert name == application_details_rest.name
        # TODO add check for application openshift REST details
        assert application_details_ui.is_equal(application_details_rest,
                                               advanced_check=True), \
            'Application UI {} not equal to REST {}'\
            .format(application_details_ui, application_details_rest)
        for workload_ui in application_details_ui.workloads:
            found = False
            for workload_rest in application_details_rest.workloads:
                if workload_ui.is_equal(workload_rest,
                                        advanced_check=True):
                    found = True
                    break
            if not found:
                assert found, 'Workload {} not found in REST {}'.format(workload_ui, workload_rest)
        assert application_details_ui.services == application_details_rest.services, \
            'UI services {} not equal to REST {}'.format(
                application_details_ui.services,
                application_details_rest.services)

        self.assert_metrics_options(application_details_ui.inbound_metrics)

        self.assert_metrics_options(application_details_ui.outbound_metrics)

    def assert_all_items(self, filters, force_clear_all=True):
        # apply filters
        self.apply_filters(filters=filters, force_clear_all=force_clear_all)

        # get applications from ui
        applications_ui = self.page.content.all_items
        # get applications from rest api
        _ns = self.FILTER_ENUM.NAMESPACE.text
        _namespaces = [_f['value'] for _f in filters if _f['name'] == _ns]
        _sn = self.FILTER_ENUM.APP_NAME.text
        _application_names = [_f['value'] for _f in filters if _f['name'] == _sn]
        logger.debug('Namespaces:{}, Application names:{}'.format(_namespaces, _application_names))
        applications_rest = self.kiali_client.application_list(
            namespaces=_namespaces, application_names=_application_names)
        # TODO get applications from OC client

        # compare all results
        logger.debug('Namespaces:{}, Service names:{}'.format(_namespaces, _application_names))
        logger.debug('Items count[UI:{}, REST:{}]'.format(
            len(applications_ui), len(applications_rest)))
        logger.debug('Applications UI:{}'.format(applications_ui))
        logger.debug('Applications REST:{}'.format(applications_rest))

        assert len(applications_ui) == len(applications_rest)

        for application_ui in applications_ui:
            found = False
            for application_rest in applications_rest:
                if application_ui.is_equal(application_rest, advanced_check=True):
                    found = True
                    break
            if not found:
                assert found, '{} not found in REST'.format(application_ui)


class WorkloadsPageTest(AbstractListPageTest):
    FILTER_ENUM = WorkloadsPageFilter

    def __init__(self, kiali_client, openshift_client, browser):
        AbstractListPageTest.__init__(
            self, kiali_client=kiali_client,
            openshift_client=openshift_client, page=WorkloadsPage(browser))
        self.browser = browser

    def assert_random_details(self, filters, force_clear_all=True):
        # apply filters
        self.apply_filters(filters=filters, force_clear_all=force_clear_all)
        # get workloads from ui
        workloads_ui = self.page.content.all_items
        # random workloads filters
        assert len(workloads_ui) > 0
        if len(workloads_ui) > 3:
            _random_workloads = random.sample(workloads_ui, 3)
        else:
            _random_workloads = workloads_ui
        # create filters
        for _selected_workload in _random_workloads:
            self.assert_details(_selected_workload.name,
                                _selected_workload.namespace,
                                _selected_workload.workload_type)

    def assert_details(self, name, namespace, workload_type):
        logger.debug('Details: {}, {}'.format(name, namespace))
        # load the page first
        self.page.load(force_load=True)
        # TODO apply pagination feature in get_details
        # apply filters
        self.apply_filters(filters=[
            {'name': WorkloadsPageFilter.NAMESPACE.text, 'value': namespace},
            {'name': WorkloadsPageFilter.WORKLOAD_NAME.text, 'value': name}])
        # load workload details page
        workload_details_ui = self.page.content.get_details(name, namespace)
        assert workload_details_ui
        assert name == workload_details_ui.name
        assert workload_type == workload_details_ui.workload_type, \
            '{} and {} are not equal'.format(workload_type, workload_details_ui.workload_type)
        # get workload detals from rest
        workload_details_rest = self.kiali_client.workload_details(
            namespace=namespace,
            workload_name=name)
        assert workload_details_rest
        assert name == workload_details_rest.name
        # TODO add check for workload openshift REST details
        assert workload_details_ui.is_equal(workload_details_rest,
                                            advanced_check=True), \
            'Workload UI {} not equal to REST {}'\
            .format(workload_details_ui, workload_details_rest)
        if workload_details_ui.pods_number != workload_details_rest.pods_number:
            return False
        if workload_details_ui.services_number != workload_details_rest.services_number:
            return False
        for pod_ui in workload_details_ui.pods:
            found = False
            for pod_rest in workload_details_rest.pods:
                if pod_ui.is_equal(pod_rest,
                                   advanced_check=True):
                    found = True
                    break
            if not found:
                assert found, 'Pod {} not found in REST {}'.format(pod_ui, pod_rest)
        for service_ui in workload_details_ui.services:
            found = False
            for service_rest in workload_details_rest.services:
                if service_ui.is_equal(service_rest,
                                       advanced_check=True):
                    found = True
                    break
            if not found:
                assert found, 'Service {} not found in REST {}'.format(service_ui, service_rest)

        self.assert_metrics_options(workload_details_ui.inbound_metrics)

        self.assert_metrics_options(workload_details_ui.outbound_metrics)

    def assert_all_items(self, filters, force_clear_all=True):
        # apply filters
        self.apply_filters(filters=filters, force_clear_all=force_clear_all)

        # get workloads from ui
        workloads_ui = self.page.content.all_items
        # get workloads from rest api
        _ns = self.FILTER_ENUM.NAMESPACE.text
        _namespaces = [_f['value'] for _f in filters if _f['name'] == _ns]
        _sn = self.FILTER_ENUM.WORKLOAD_NAME.text
        _workload_names = [_f['value'] for _f in filters if _f['name'] == _sn]
        logger.debug('Namespaces:{}, Workload names:{}'.format(_namespaces, _workload_names))
        workloads_rest = self.kiali_client.workload_list(
            namespaces=_namespaces, workload_names=_workload_names)
        # get workloads from OC client
        workloads_oc = self.openshift_client.workload_list(
            namespaces=_namespaces, workload_names=_workload_names)

        # compare all results
        logger.debug('Namespaces:{}, Service names:{}'.format(_namespaces, _workload_names))
        logger.debug('Items count[UI:{}, REST:{}, OC:{}]'.format(
            len(workloads_ui), len(workloads_rest), len(workloads_oc)))
        logger.debug('Workloads UI:{}'.format(workloads_ui))
        logger.debug('Workloads REST:{}'.format(workloads_rest))
        logger.debug('Workloads OC:{}'.format(workloads_oc))

        assert len(workloads_ui) == len(workloads_rest)
        # TODO when workloads are filtered put == here
        assert len(workloads_rest) <= len(workloads_oc)

        for workload_ui in workloads_ui:
            found = False
            for workload_rest in workloads_rest:
                if workload_ui.is_equal(workload_rest, advanced_check=True):
                    found = True
                    break
            if not found:
                assert found, '{} not found in REST'.format(workload_ui)
            found = False
            for workload_oc in workloads_oc:
                if workload_ui.is_equal(workload_oc, advanced_check=False):
                    found = True
                    break
            if not found:
                assert found, '{} not found in OC'.format(workload_ui)


class ServicesPageTest(AbstractListPageTest):
    FILTER_ENUM = ServicesPageFilter

    def __init__(self, kiali_client, openshift_client, browser):
        AbstractListPageTest.__init__(
            self, kiali_client=kiali_client,
            openshift_client=openshift_client, page=ServicesPage(browser))
        self.browser = browser

    def assert_random_details(self, filters, force_clear_all=True):
        # apply filters
        self.apply_filters(filters=filters, force_clear_all=force_clear_all)
        # get services from ui
        services_ui = self.page.content.all_items
        # random services filters
        assert len(services_ui) > 0
        if len(services_ui) > 3:
            _random_services = random.sample(services_ui, 3)
        else:
            _random_services = services_ui
        # create filters
        for _selected_service in _random_services:
            self.assert_details(_selected_service.name, _selected_service.namespace)

    def assert_details(self, name, namespace):
        logger.debug('Details: {}, {}'.format(name, namespace))
        # load the page first
        self.page.load(force_load=True)
        # TODO apply pagination feature in get_details
        # apply filters
        self.apply_filters(filters=[
            {'name': ServicesPageFilter.NAMESPACE.text, 'value': namespace},
            {'name': ServicesPageFilter.SERVICE_NAME.text, 'value': name}])
        # load service details page
        service_details_ui = self.page.content.get_details(name, namespace)
        assert service_details_ui
        assert name == service_details_ui.name
        # get service detals from rest
        service_details_rest = self.kiali_client.service_details(
            namespace=namespace,
            service_name=name)
        assert service_details_rest
        assert name == service_details_rest.name
        # TODO add check for service openshift REST details
        assert service_details_rest.istio_sidecar\
            == service_details_ui.istio_sidecar
        assert service_details_ui.is_equal(service_details_rest,
                                           advanced_check=True), \
            'Service UI {} not equal to REST {}'\
            .format(service_details_ui, service_details_rest)
        assert service_details_ui.workloads_number\
            == len(service_details_rest.workloads)
        assert service_details_ui.source_workloads_number\
            == len(self.get_workload_names_set(service_details_rest.source_workloads))
        assert service_details_ui.virtual_services_number\
            == len(service_details_rest.virtual_services)
        assert service_details_ui.destination_rules_number\
            == len(service_details_rest.destination_rules)
        assert service_details_ui.workloads_number\
            == len(service_details_rest.workloads)
        assert service_details_ui.source_workloads_number\
            == len(self.get_workload_names_set(service_details_ui.source_workloads))
        assert service_details_ui.virtual_services_number\
            == len(service_details_ui.virtual_services)
        assert service_details_ui.destination_rules_number\
            == len(service_details_ui.destination_rules)
        for workload_ui in service_details_ui.workloads:
            found = False
            for workload_rest in service_details_rest.workloads:
                if workload_ui.is_equal(workload_rest, advanced_check=True):
                    found = True
                    break
            assert found, 'Workload {} not found in REST {}'.format(workload_ui,
                                                                    workload_rest)
        for workload_ui in service_details_ui.source_workloads:
            found = False
            for workload_rest in service_details_rest.source_workloads:
                if workload_ui.is_equal(workload_rest, advanced_check=True):
                    found = True
                    break
            assert found, 'Source Workload {} not found in REST {}'.format(workload_ui,
                                                                           workload_rest)
        for virtual_service_ui in service_details_ui.virtual_services:
            found = False
            for virtual_service_rest in service_details_rest.virtual_services:
                if virtual_service_ui.is_equal(virtual_service_rest, advanced_check=True):
                    found = True
                    break
            assert found, 'VS {} not found in REST {}'.format(virtual_service_ui,
                                                              virtual_service_rest)
        for destination_rule_ui in service_details_ui.destination_rules:
            found = False
            for destination_rule_rest in service_details_rest.destination_rules:
                if destination_rule_ui.is_equal(destination_rule_rest, advanced_check=True):
                    found = True
                    break
            assert found, 'DR {} not found in REST {}'.format(destination_rule_ui,
                                                              destination_rule_rest)

        self.assert_metrics_options(service_details_ui.inbound_metrics)

    def get_workload_names_set(self, source_workloads):
        workload_names = []
        for source_workload in source_workloads:
            for workload in source_workload.workloads:
                workload_names.append(workload)
        return set(workload_names)

    def assert_all_items(self, filters, force_clear_all=True):
        # apply filters
        self.apply_filters(filters=filters, force_clear_all=force_clear_all)

        # get services from ui
        services_ui = self.page.content.all_items
        # get services from rest api
        _ns = self.FILTER_ENUM.NAMESPACE.text
        _namespaces = [_f['value'] for _f in filters if _f['name'] == _ns]
        _sn = self.FILTER_ENUM.SERVICE_NAME.text
        _service_names = [_f['value'] for _f in filters if _f['name'] == _sn]
        logger.debug('Namespaces:{}, Service names:{}'.format(_namespaces, _service_names))
        services_rest = self.kiali_client.service_list(
            namespaces=_namespaces, service_names=_service_names)
        # get services from OC client
        services_oc = self.openshift_client.service_list(
            namespaces=_namespaces, service_names=_service_names)

        # compare all results
        logger.debug('Namespaces:{}, Service names:{}'.format(_namespaces, _service_names))
        logger.debug('Items count[UI:{}, REST:{}, OC:{}]'.format(
            len(services_ui), len(services_rest), len(services_oc)))
        logger.debug('Services UI:{}'.format(services_ui))
        logger.debug('Services REST:{}'.format(services_rest))
        logger.debug('Services OC:{}'.format(services_oc))

        assert len(services_ui) == len(services_rest)
        assert len(services_rest) <= len(services_oc)

        for service_ui in services_ui:
            found = False
            for service_rest in services_rest:
                if service_ui.is_equal(service_rest, advanced_check=True):
                    found = True
                    break
            assert found, '{} not found in REST'.format(service_ui)
            found = False
            for service_oc in services_oc:
                if service_ui.is_equal(service_oc, advanced_check=False):
                    found = True
                    break
            assert found, '{} not found in OC'.format(service_ui)

    def get_additional_filters(self, current_filters):
        logger.debug('Current filters:{}'.format(current_filters))
        # get services of a namespace
        _namespace = current_filters[0]['value']
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


class IstioConfigPageTest(AbstractListPageTest):
    FILTER_ENUM = IstioConfigPageFilter

    def __init__(self, kiali_client, openshift_client, browser):
        AbstractListPageTest.__init__(
            self, kiali_client=kiali_client,
            openshift_client=openshift_client, page=IstioConfigPage(browser))
        self.browser = browser

    def assert_all_items(self, filters, force_clear_all=True):
        logger.debug('Filters:{}'.format(filters))
        # load the page first
        self.page.load(force_load=True)
        # apply filters
        self.apply_filters(filters=filters, force_clear_all=force_clear_all)

        # get rules from ui
        config_list_ui = self.page.content.all_items
        logger.debug('Istio config list UI:{}]'.format(config_list_ui))

        # get rules from rest api
        config_list_rest = self.kiali_client.istio_config_list(filters=filters)
        logger.debug('Istio config list REST:{}]'.format(config_list_rest))

        # compare both results
        assert len(config_list_ui) == len(config_list_rest)
        for config_ui in config_list_ui:
            found = False
            for config_rest in config_list_rest:
                if config_ui.is_equal(config_rest, advanced_check=True):
                    found = True
                    break
            if not found:
                assert found, '{} not found in REST'.format(config_ui)

    def assert_random_details(self, filters, force_clear_all=True):
        # apply filters
        self.apply_filters(filters=filters, force_clear_all=force_clear_all)
        # get configs from ui
        configs_ui = self.page.content.all_items
        # random configs filters
        assert len(configs_ui) > 0
        if len(configs_ui) > 3:
            _random_configs = random.sample(configs_ui, 3)
        else:
            _random_configs = configs_ui
        # create filters
        for _selected_config in _random_configs:
            if _selected_config.object_type != OBJECT_TYPE.RULE.text:
                self.assert_details(_selected_config.name, _selected_config.namespace)

    def assert_details(self, name, namespace=None):
        logger.debug('Details: {}, {}'.format(name, namespace))
        # load the page first
        self.page.load(force_load=True)
        # TODO apply pagination feature in get_details
        # apply filters
        self.apply_filters(filters=[
            {'name': IstioConfigPageFilter.NAMESPACE.text, 'value': namespace},
            {'name': IstioConfigPageFilter.ISTIO_NAME.text, 'value': name}])
        # load config details page
        config_details_ui = self.page.content.get_details(name, namespace)
        assert config_details_ui
        assert name == config_details_ui.name
        assert config_details_ui.text
        # get config detals from rest
        config_details_rest = self.kiali_client.istio_config_details(
            namespace=namespace,
            object_type=config_details_ui._type,
            object_name=name)
        assert config_details_rest
        assert name == config_details_rest.name
        assert config_details_rest.text
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
                                  replace('"', '').
                                  replace(',', '').
                                  replace('[', '').
                                  replace(']', '').
                                  replace('\\', '')):
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
                if not found:
                    assert found, '{} {} not found in REST'.format(ui_key, config_ui)

    def get_additional_filters(self, current_filters):
        logger.debug('Current filters:{}'.format(current_filters))
        # get rules of a namespace
        _namespace = current_filters[0]['value']
        logger.debug('Running Rules REST query for namespace:{}'.format(_namespace))
        _istio_config_list = self.kiali_client.istio_config_list(
            filters=[{'name': self.FILTER_ENUM.NAMESPACE.text, 'value': _namespace}])
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
