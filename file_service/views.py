import logging

from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required


logger = logging.getLogger(__name__)
