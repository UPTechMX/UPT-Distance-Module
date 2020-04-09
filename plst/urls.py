from django.urls import path, include
from django.conf.urls.static import static

from .views import AmenitiesView, MmuView,ModulesView
from .views import TableView,ColumnsView,DistanceEvalView,ExcecutionProgress

urlpatternss = ([
    path('amenities/', AmenitiesView.as_view()),
    path('mmu/', MmuView.as_view()),
    path('indicator/',  ModulesView.as_view()),
    #path('amenities-distance/',  AmenitiesEvalView.as_view()),
    path('layers/',  TableView.as_view()),
    path('layers-columns/',  ColumnsView.as_view()),
    #Calculate distance
    path('distances_evaluation/', DistanceEvalView.as_view()),
    path('distances_evaluation/<int:study_area>/<int:user_id>', DistanceEvalView.as_view()),
    path('distances_status/', ExcecutionProgress.as_view()), 
    
], 'plst')