from kiali_qe.components.enums import PaginationPerPage
from kiali_qe.utils.log import logger


def pagination_feature_test(page):
    pagination = page.pagination
    # test options
    options_defined = [item.value for item in PaginationPerPage]
    options_listed = pagination.items_per_page_options
    logger.debug('options[defined:{}, listed:{}]'.format(options_defined, options_listed))
    assert options_defined == options_listed, \
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
            assert len(page.content.items) == per_page and pagination.items_per_page == per_page
    # test total items
    assert pagination.total_items == len(page.content.all_items)


def check_equal(L1, L2):
    return len(L1) == len(L2) and sorted(L1) == sorted(L2)
