# -*- coding: utf-8 -*-
import sys
import os
import multiprocessing
import threading
import _thread as thread
import time
import gc
from random import randint
import json
import math

from plst.indicators.Indicator import Indicator
from plst.Helpers.Vacuum import vacuum
from plst.Helpers.LogEvents import LogEvents

from django.db import transaction
from plst.models import Mmu,Amenities
from django.db.models import Max, Min


class Module:
    def __init__(self, user,layer_id, study_area, extra_dict_arguments=None):
        self.__user = user
        self.__study_area = study_area
        self.__layer=layer_id


    def run(self):
        
        self.__limits = {"inferior": 0, "superior": 0}
        self.__mmu_limit_offset()  # validated
        self.__amenities_distance_threads()

    def __mmu_limit_offset(self):
        try:
            self.__Indicator = Indicator(self.__user)
            db = self.__Indicator.get_st_calculator_connection()
            try:
                # get the max an min of pk
                query_set=Mmu.objects.filter(
                    study_area=self.__study_area,
                    user_id=self.__user)
                self.__limits["inferior"] = Mmu.objects.filter(
                    study_area=self.__study_area,
                    user_id=self.__user).aggregate(Min('mmu_id'))["mmu_id__min"]
                self.__limits["superior"] = Mmu.objects.filter(
                    study_area=self.__study_area,
                    user_id=self.__user).aggregate(Max('mmu_id'))["mmu_id__max"]
            except Exception as e:
                LogEvents(
                    self.__layer,
                    self.__user,
                    self.__study_area,
                    "squares max min",
                    "unknown error " + str(e)
                    ,True
                )
            db.close()
        except Exception as e:
            LogEvents(
                self.__layer,
                self.__user,
                self.__study_area,
                "squares max min",
                "unknown error " + str(e)
                ,True
            )

    def __amenities_distance_threads(self):
        self.__scenario_t = {}
        self.__scenario_t["limit"] = 0
        self.__scenario_t["offset"] = 0

        inferior = self.__limits["inferior"]
        superior = self.__limits["superior"]
        _threads = {}

        self.max_threads = min(self.__Indicator.get_max_threads(), int(math.ceil(
            (superior - inferior) / self.__Indicator.get_max_rows())))
        num_partitions = self.max_threads
        partition_size = (int)(
            math.ceil((superior - inferior) / self.max_threads))  # 2000

        for h in range(0, num_partitions):
            self.__scenario_t["offset"] = inferior
            self.__scenario_t["limit"] = self.__scenario_t["offset"] + \
                partition_size
            inferior = self.__scenario_t["limit"] + 1
            _threads[h] = threading.Thread(target=self.__ModuleAmenitiesDistance, args=(
                self.__layer,self.__user, self.__scenario_t["offset"], self.__scenario_t["limit"]))

        for process in _threads:
            _threads[process].start()

        for process in _threads:
            if _threads[process].is_alive():
                _threads[process].join()

    def __ModuleAmenitiesDistance(self, layer_id,user_id, offset=0, limit=0):
        try:
            error = True
            count = 0

            while error and count < 3:
                indicator = Indicator(user_id)
                db = indicator.get_st_calculator_connection()
                try:
                    with transaction.atomic():
                        query = """select st_indicator_mmu_amenities_distance({layer},{user},{offset},{limit})""".format(
                            layer=layer_id,user=user_id, offset=offset, limit=limit)
                        LogEvents(
                            self.__layer,
                            user_id,
                            self.__study_area,
                            "mmu amenities distance",
                            "mmu amenities distance  module started: " + query
                        )
                        db.execute(query)
                except Exception as e:
                    # #db.rollback()
                    error = True
                    count += 1
                    LogEvents(
                        self.__layer,
                        user_id,
                        self.__study_area,
                        "mmu amenities distance ",
                        "mmu amenities distance  module failed " + str(count) + ": " + str(e), 
                        True
                    )
                    db.close()
                else:
                    error = False
                    LogEvents(
                        self.__layer,
                        user_id,
                        self.__study_area,
                        "mmu amenities distance ",
                        "mmu amenities distance  module finished"
                    )
                    
                    db.close()
        except Exception as e:
            LogEvents(
                self.__layer,
                user_id,
                self.__study_area,
                "mmu amenities distance ",
                "mmu amenities distance  module finished",
                True
            )
    
    