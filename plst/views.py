# Required to upload files
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import generics
from .serializers import AmenitiesSerializer, MmuSerializer
from .models import Amenities, Mmu, execution_progress
from django.db import connection
# require to upload files
from .serializers import ModuleSerializer
# use scenario evaluation with celery
from .indicators.EvaluateScenario import run
import json
import shutil
import os
import urllib.parse


class AmenitiesView(generics.ListCreateAPIView):
    """
    Provides a get method handler.
    """
    queryset = Amenities.objects.all()
    filter_fields = ('scenario', 'study_area')
    serializer_class = AmenitiesSerializer

    def post(self, request, *args, **kwargs):
        print(request.data["data"])
        try:
            Amenities.objects.bulk_create(
                [Amenities(
                    oskari_code=data["oskari_code"], user_id=data["user_id"], layer_id=data["layer_id"], study_area=data[
                        "study_area"], fclass=data["fclass"], location=data["location"]
                ) for data in request.data["data"]
                ], ignore_conflicts=True
            )
        except Exception as identifier:
            return Response(dict(status="", message="Error when inserting data "+str(identifier)), status=status.HTTP_400_BAD_REQUEST)
        return Response(dict(status="", message="All data created"), status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        try:
            Amenities.objects.filter(
                scenario=request.GET.get("study_area")).delete()
        except Exception as identifier:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_200_OK)


class MmuView(generics.ListCreateAPIView):
    """
    Provides a get method handler.
    """
    queryset = Mmu.objects.all()
    filter_fields = ('scenario', 'study_area')
    serializer_class = MmuSerializer

    def post(self, request, *args, **kwargs):
        print(request.data["data"])
        try:
            Mmu.objects.bulk_create(
                [Mmu(
                    oskari_code=data["oskari_code"], study_area=data["study_area"], layer_id=data[
                        "layer_id"], user_id=data["user_id"], location=data["location"]
                ) for data in request.data["data"]], ignore_conflicts=True
            )
        except Exception as identifier:
            return Response(dict(status="", message="Error when importing data: "+str(identifier)), status=status.HTTP_400_BAD_REQUEST)

        return Response(dict(status="", message="All data imported"), status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        query_set = Mmu.objects.filter(scenario=request.GET.get(
            "scenario")).values("mmu_id", "oskari_code")
        return Response(query_set)

    def delete(self, request, *args, **kwargs):
        try:
            Mmu.objects.filter(scenario=int(
                request.data["study_area"])).delete()
        except Exception as identifier:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_200_OK)


class DistanceEvalView(APIView):
    def post(self, request, *args, **kwargs):
        study_area = int(request.data["study_area"])
        user_id = int(request.data["user_id"])
        execution_progress.objects.filter(
            study_area=study_area).filter(user_id=user_id).delete()
        resultado = run.delay(study_area, user_id)
        return Response(dict(id=1, event="Evaluating distances", value="", created_on=None, study_area=study_area, user_id=user_id))

    def get(self, request, *args, **kwargs):
        try:
            user_id = int(urllib.parse.unquote(
                request.query_params.get('user_id')))
            study_area = int(urllib.parse.unquote(
                request.query_params.get('study_area')))
            projection = int(urllib.parse.unquote(
                request.query_params.get('projection')))
            all_buffers = self.__getAmentityBuffers(
                user_id, study_area, projection)
            return Response(all_buffers)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, *args, **kwargs):
        try:
            study_area = int(kwargs["study_area"])
            user_id = int(kwargs["user_id"])
            Amenities.objects.filter(study_area=study_area,user_id=user_id).delete()
            Mmu.objects.filter(study_area=study_area,user_id=user_id).delete()
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            return Response(dict(error=str(e)),status=status.HTTP_400_BAD_REQUEST)

    def __getAmentityBuffers(self, user_id, study_area, projection):
        buffers = []
        try:
            query = """
                select 
                    layer_id,
                    study_area,
                    user_id,
                    name,
                    concat('EPSG:', {projection}::text) as projection,
                    json_build_object(
                            'type',
                            'FeatureCollection',
                            'crs',
                            json_build_object(
                                'type', 
                                'name', 
                                'properties', 
                                json_build_object(
                                    'name', 
                                    concat('EPSG:', {projection}::text)
                                )
                            ), 
                            'features', 
                            json_agg(
                                json_build_object(
                                    'type', 
                                    'Feature',
                                    'geometry', 
                                    ST_AsGeoJSON (st_setsrid(st_transform(location,3857),0))::json, 
                                    'properties', 
                                    json_build_object(
                                        'id',
                                        mmu.mmu_id,
                                        'type', 
                                        replace(st_geometrytype (location), 'ST_', ''), 
                                        'value', 
                                        value
                                    )
                                )
                            )
                        )::text as geojson
                from mmu
                inner join mmu_info on mmu_info.mmu_id = mmu.mmu_id
                where user_id={user_id} and study_area={study_area}
                group by layer_id, study_area, user_id,projection, name
                """.format(user_id=user_id, study_area=study_area, projection=projection)
            cursor = connection.cursor()
            cursor.execute(query)
            buffers = [dict(layer_id=row[0], study_area=row[1], user_id=row[2], name=row[3]+" distances "+str(
                row[0])+str(row[2]), projection=row[4], geojson="{\"0\":"+row[5]+"}") for row in cursor.fetchall()]
        except Exception as e:
            return buffers
        else:
            return buffers


class ExcecutionProgress(APIView):
    def get(self, request, *args, **kwargs):
        user_id = urllib.parse.unquote(request.query_params.get('user_id'))
        study_area = urllib.parse.unquote(
            request.query_params.get('study_area'))
        results = execution_progress.objects.filter(user_id=user_id, study_area=study_area).values(
            "id", "layer_id", "event", "value", "created_on").order_by("-id")
        return Response(results, status=status.HTTP_200_OK)


class ModulesView(APIView):
    parser_class = (FileUploadParser,)

    def post(self, request, *args, **kwargs):

        file_serializer = ModuleSerializer(data=request.data)

        if file_serializer.is_valid():
            file_serializer.save()
            return Response(file_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TableView(APIView):
    def get(self, request, *args, **kwargs):
        import urllib.parse
        from django.apps import apps
        table_list = ["mmu", "amenities"]
        return Response(table_list)


class ColumnsView(APIView):
    def get(self, request, *args, **kwargs):
        import urllib.parse
        from django.apps import apps
        table = urllib.parse.unquote(request.query_params.get('table'))
        model = apps.get_model('plst', table)
        first_query = model._meta.fields

        columns = [f.name for f in first_query]
        if 'id' in columns:
            columns.remove('id')
        if 'buffer' in columns:
            columns.remove('buffer')
        if 'created' in columns:
            columns.remove('created')
        if 'updated' in columns:
            columns.remove('updated')
        if 'oskari_code' in columns:
            columns.remove('oskari_code')
        if 'study_area' in columns:
            columns.remove('study_area')
        if 'layer_id' in columns:
            columns.remove('layer_id')
        if 'user_id' in columns:
            columns.remove('user_id')
        if table.find("_info") < 0 and (table+'_id') in columns:
            columns.remove(table+'_id')
        return Response(columns)
