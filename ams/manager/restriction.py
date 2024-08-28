from django.contrib.auth.decorators import user_passes_test

def is_administrator(user):
    return user.groups.filter(name='Administrators').exists()

# Use the decorator with the custom test function
administrator_required = user_passes_test(is_administrator)

def is_administrator_or_operator(user):
    return user.groups.filter(name__in=['Administrators', 'Operators']).exists()

# Use the decorator with the updated custom test function
administrator_or_operator_required = user_passes_test(is_administrator_or_operator)

def is_approver(user):
    return user.groups.filter(name='Approvers').exists()

# Use the decorator with the custom test function
administrator_required = user_passes_test(is_approver)