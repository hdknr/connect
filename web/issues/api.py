from tastypie.resources import ModelResource
from models import Issue


class IssueResource(ModelResource):

    class Meta:
        queryset = Issue.objects.all()
        resource_name = 'issue'
