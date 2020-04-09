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
import importlib

from plst.indicators.Indicator import Indicator
from plst.Helpers.Vacuum import vacuum
from plst.Helpers.LogEvents import LogEvents
import plst.Helpers.config as config
from ST.celery import app
from celery import task


class EvaluateDistance:
    """
    Suitability layer evaluation
    Attributes:
        user: user id.
        layer: List of layer to be evaluated.
        indicators: List of indicators to be evaluated.
    """

    def __init__(self, study_area, user_id):
        self.user = user_id
        self.study_area = study_area
        self.indicator = Indicator(self.user)
        self.first_layer = None
        if self.study_area != None:
            layers = self.__get_all_layers(self.user,self.study_area)
            self.layers = [layer[0] for layer in layers]
            self.first_layer = self.layers[0]
        self.indicators = ["AmenitiesDistance"]
    """
    run_scenarios method executes all the modules that the user's role
    has access to.
    """

    def run_scenarios(self):
        try:
            LogEvents(
                self.first_layer,
                self.user,
                self.study_area,
                "Start distances",
                "Starting all distances proccesing"
            )
            last = 0
            # Evaluate the scenario(s)
            for layer in self.layers:
                last = layer
                LogEvents(
                    last,
                    self.user,
                    self.study_area,
                    "Distance evaluation",
                    "Start distance evaluation"
                )
                for module in self.indicators:
                    module_r = "plst.indicators."+module+"."+module
                    try:
                        plugin = importlib.import_module(module_r, ".")
                        module = plugin.Module(self.user, layer, self.study_area, dict(
                            first_layer=self.first_layer))
                        module.run()
                    except Exception as e:
                        print("E", e)

                LogEvents(
                    last,
                    self.user,
                    self.study_area,
                    "Distance evaluation",
                    "Distance evaluation finished"
                )

                db = config.get_db()
                vacuum(self.indicator.get_uri(), "mmu_info")
                db.close()
            db = config.get_db()
            vacuum(self.indicator.get_uri(), True)
            db.close()
            LogEvents(
                last,
                self.user,
                self.study_area,
                "All distances finished",
                "All distances have been processed",
            )

        except Exception as e:
            LogEvents(
                self.first_layer,
                self.user,
                self.study_area,
                "Unknown error",
                str(e)
            )

    def __get_all_layers(self,user_id, study_area):
        try:
            db = config.get_db()
            try:
                query = """
                    select distinct layer_id from amenities where user_id={user_id} and study_area={study_area}
                """.format(user_id=user_id, study_area=study_area)
                db.execute(query)
                scenarios = db.fetchall()
                db.close()
                return scenarios
            except Exception as e:
                LogEvents(
                    -1,
                    self.user,
                    study_area,
                    "An error happend while getting the base scenario",
                    str(e) + query
                )

                db.close()
        except Exception as e:
            LogEvents(
                self.first_layer,
                self.user,
                study_area,
                "Unknown error",
                str(e)
            )
            return []
    """
    __get_all_scenarios method finds all the scenarios that were created
    ofr the provided city and country
    """



@app.task
#@task(bind=True,name="evaluate_scenario_task")
def run(study_area, user_id):
    import os
    # import signal
    import time
    my_pid = os.getpid()
    # signal.signal(signal.SIGINT, selfexit)
    print("received: ", study_area, user_id)
    try:
        # evaluate the scenarios
        evaluate = EvaluateDistance(study_area, user_id)
        evaluate.run_scenarios()
    except Exception as e:
        LogEvents(
            -1, 
            user_id, 
            study_area, 
            "There was an error during layer evaluation",
            str(e)
        )


if __name__ == '__main__':
    # sys.argv[1] user_id
    # sys.argv[2] study_area,
    if len(sys.argv) < 3:
        print("Wrong arguments\nExample")
        print(
            "\tEvaluateDistance user_id[1] study_area[1]")
    elif len(sys.argv) <= 2:
        LogEvents(
            -1, 
            sys.argv[1], 
            sys.argv[2], 
            "Evaluate scenarios",
            "You must provide arguments",
        )
    elif len(sys.argv) == 4:
        print("Running")
        run(sys.argv[1], sys.argv[2], sys.argv[3])
