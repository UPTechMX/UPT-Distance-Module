from rest_framework import serializers
from .models import Amenities, Mmu,Modules

class AmenitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenities
        fields = [
            "amenities_id",
            "layer_id",
            "study_area",
            "oskari_code",
            "location",
        ]

class MmuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mmu
        fields = [
            "mmu_id",
            "oskari_code",
            "layer_id",
            "study_area",
            "location",
        ]

class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Modules
        fields = "__all__"
