from django.urls import path

from offering.views import StoreOfferingDataView

urlpatterns = [
    path("upload/", StoreOfferingDataView.as_view(), name="offering-upload"),
]