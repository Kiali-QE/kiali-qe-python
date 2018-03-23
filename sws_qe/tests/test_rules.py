from project.sws_view import RuleListView


def test_rule_list(browser, rest_api):
    view = RuleListView(browser)
    ui_rules = get_ui_rules_set(view.get_all())
    rest_rules = get_rest_rules_set(rest_api.list_rules())
    assert ui_rules == rest_rules, \
        ("Lists of rules mismatch! UI:{}, REST:{}"
         .format(ui_rules, rest_rules))


def get_ui_rules_set(rules):
    """
    Return the set of rules which contains only necessary fields,
    such as 'name' and 'namespace'
    """
    return set((rule.name, rule.namespace, rule.handler, rule.instances) for rule in rules)


def get_rest_rules_set(rules):
    """
    Return the set of rules which contains only necessary fields,
    such as 'name' and 'namespace'
    """
    return set((rule.name, rule.namespace,
                ', '.join(action.handler for action in rule.actions),
                ', '.join(', '.join(instance for instance in action.instances) for action in rule.actions)) for rule in rules)