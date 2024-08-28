import logging
from django_auth_ldap.backend import LDAPBackend
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

logger = logging.getLogger(__name__)


class AMSLDAPBackend(LDAPBackend):
    

    def authenticate_ldap_user(self, ldap_user, password):
        print(ldap_user._username)
        user = super().authenticate_ldap_user(ldap_user, password)

        if user:
            logger.info(f"LDAP authentication successful for user: {user}")
            # Group adding mayb handled in signals if needed as well
            if user.is_adminstrator:
                group = Group.objects.get(name="Admins")
                group.user_set.add(user)
            if user.is_operator:
                group = Group.objects.get(name="Operators")
                group.user_set.add(user)
        else:
            logger.warning(f"LDAP authentication failed for user: {ldap_user._username}")

        return user