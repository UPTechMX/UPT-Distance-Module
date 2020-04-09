# -*- coding: utf-8 -*-
import sys
import os
import gc
import logging
# sys.path.insert(1,"..")
import plst.Helpers.logging_config
import plst.Helpers.config 

from plst.models import execution_progress
from django.db import IntegrityError, transaction

class LogEvents:
    """
    Suitability log execution monitoring
    Attributes:
        event: actual process
        value: event raised
        layer: Layer under excecution.
    """

    def __init__(self, layer_id, user_id, study_area, event,value, type=False):
        self.__logger = logging.getLogger(__name__)
        if type:
            self.__logger.error(dict(layer=layer_id,user=user_id,event=event,value=value))
        else:
            self.__logger.debug(dict(layer=layer_id,user=user_id,event=event,value=value))
        if layer_id > 0:
            self.__log(layer_id, user_id, study_area, event,value)
    
    @transaction.atomic
    def __log(self, layer_id, user_id, study_area, event,value):
        try:
            p = execution_progress(event=event, value=value, layer_id=layer_id,user_id=user_id,study_area=study_area)
            with transaction.atomic():
                p.save()
        except IntegrityError as e:
            self.__logger.error(dict(layer=layer_id,user=user_id,event=event,value=value, error=e))
