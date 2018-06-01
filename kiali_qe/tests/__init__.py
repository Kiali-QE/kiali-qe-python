from kiali_qe.components.enums import PaginationPerPage, ServicesPageFilter, IstioConfigPageFilter
from kiali_qe.utils import is_equal
from kiali_qe.utils.log import logger
import random

from kiali_qe.pages import ServicesPage, IstioMixerPage


class AbstractListPageTest(object):
    FILTER_ENUM = None

    def __init__(self, kiali_client, openshift_client, page):
        self.kiali_client = kiali_client
        self.openshift_client = openshift_client
        self.page = page

    def _namespaces_ui(self):
        return self.page.filter.filter_options(filter_name=self.FILTER_ENUM.NAMESPACE.text)

    def assert_all_items(self, active_filters):
        raise NotImplementedError('This method should be implemented on sub class')

    def get_additional_filters(self, current_filters):
        raise NotImplementedError('This method should be implemented on sub class')

    def assert_filter_options(self):
        # test available options
        options_defined = [item.text for item in self.FILTER_ENUM]
        options_listed = self.page.filter.filters
        logger.debug('Options[defined:{}, defined:{}]'.format(options_defined, options_listed))
        assert is_equal(options_defined, options_listed)

    def assert_namespaces(self):
        namespaces_ui = self._namespaces_ui()
        namespaces_rest = self.kiali_client.namespace_list()
        namespaces_oc = self.openshift_client.namespace_list()
        logger.debug('Namespaces UI:{}'.format(namespaces_ui))
        logger.debug('Namespaces REST:{}'.format(namespaces_rest))
        logger.debug('Namespaces OC:{}'.format(namespaces_oc))
        assert is_equal(namespaces_ui, namespaces_rest)
        assert is_equal(namespaces_rest, namespaces_oc)

    def assert_filter_feature(self):
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
            # apply filter
            self.page.filter.apply(
                filter_name=_defined_filter['name'], value=_defined_filter['value'])
            # add it in to applied list
            _applied_filters.append(_defined_filter)
            # sleep(3)
            # validate applied filters
            _active_filters = self.page.filter.active_filters
            logger.debug('Filters[applied:{}, active:{}]'.format(_applied_filters, _active_filters))
            assert is_equal(_applied_filters, _active_filters)
            # check the contents
            self.assert_all_items(_active_filters)

        # remove filters test
        for _defined_filter in _defined_filters:
            # remove a filter
            self.page.filter.remove(
                filter_name=_defined_filter['name'], value=_defined_filter['value'])
            # remove it from our list
            _applied_filters.remove(_defined_filter)
            # validate applied filters
            _active_filters = self.page.filter.active_filters
            logger.debug('Filters[applied:{}, active:{}]'.format(_applied_filters, _active_filters))
            assert is_equal(_applied_filters, _active_filters)
            # check the contents
            self.assert_all_items(_active_filters)
            # test remove all
            if len(_applied_filters) == 2:
                self.page.filter.clear_all()
                assert len(self.page.filter.active_filters) == 0
                self.assert_all_items([])
                break

    def assert_pagination_feature(self):
        pagination = self.page.pagination
        # test options
        options_defined = [item.value for item in PaginationPerPage]
        options_listed = pagination.items_per_page_options
        logger.debug('options[defined:{}, listed:{}]'.format(options_defined, options_listed))
        assert is_equal(options_defined, options_listed), \
            ('Options mismatch: defined:{}, listed:{}'.format(options_defined, options_listed))
        # test page next, previous, first, last, to page
        total_pages = pagination.total_pages
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
        assert pagination.total_items == len(self.page.content.all_items)


class ServicesPageTest(AbstractListPageTest):
    FILTER_ENUM = ServicesPageFilter

    def __init__(self, kiali_client, openshift_client, browser, cfg):
        AbstractListPageTest.__init__(
            self, kiali_client=kiali_client,
            openshift_client=openshift_client, page=ServicesPage(browser, cfg))
        self.browser = browser

    def assert_all_items(self, active_filters):
        # get services from ui
        services_ui = self.page.content.all_items
        # get services from rest api
        _ns = self.FILTER_ENUM.NAMESPACE.text
        _namespaces = [_f['value'] for _f in active_filters if _f['name'] == _ns]
        _sn = self.FILTER_ENUM.SERVICE_NAME.text
        _service_names = [_f['value'] for _f in active_filters if _f['name'] == _sn]
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
        assert len(services_rest) == len(services_oc)

        for service_ui in services_ui:
            found = False
            for service_rest in services_rest:
                if service_ui.is_equal(service_rest, advanced_check=False):
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

    def __init__(self, kiali_client, openshift_client, browser, cfg):
        AbstractListPageTest.__init__(
            self, kiali_client=kiali_client,
            openshift_client=openshift_client, page=IstioMixerPage(browser, cfg))
        self.browser = browser

    def assert_all_items(self, active_filters):
        logger.debug('Filters:{}'.format(active_filters))
        # get rules from ui
        config_list_ui = self.page.content.all_items
        logger.debug('Istio config list UI:{}]'.format(config_list_ui))
        # UI changed not in use
        # get rules from rest api
        # _ns = self.FILTER_ENUM.NAMESPACE.text
        # _namespaces = [_f['value'] for _f in active_filters if _f['name'] == _ns]
        # _sn = self.FILTER_ENUM.ISTIO_NAME.text
        # _rule_names = [_f['value'] for _f in active_filters if _f['name'] == _sn]
        config_list_rest = self.kiali_client.istio_config_list(filters=active_filters)
        logger.debug('Istio config list REST:{}]'.format(config_list_ui))
        # compare both result
        assert len(config_list_ui) == len(config_list_ui)
        for config_ui in config_list_ui:
            found = False
            for config_rest in config_list_rest:
                if config_ui.is_equal(config_ui, advanced_check=False):
                    found = True
                    break
            assert found, '{} not found in REST'.format(config_ui)

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
