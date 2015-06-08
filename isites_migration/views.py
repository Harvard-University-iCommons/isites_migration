import logging

from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.conf import settings
from django.core.exceptions import PermissionDenied

logger = logging.getLogger(__name__)
