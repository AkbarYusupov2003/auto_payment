import re
import json
import datetime
from django.db.models import F
from django.shortcuts import HttpResponse, get_object_or_404
from django.views import View
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from payze import models
from payze import serializers


class TestAPIView(View):

    def get(self, request, *args, **kwargs):
        pass
