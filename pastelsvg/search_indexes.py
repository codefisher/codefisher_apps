from haystack import indexes
from codefisher_apps.pastelsvg.models import Icon

class PostIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(model_attr='description', document=True)
    pub_date = indexes.DateTimeField(model_attr='date_modified')
    title = indexes.CharField(model_attr='title', boost=2)
    category = indexes.CharField(model_attr='category', boost=1.5)

    def get_model(self):
        return Icon
        
    def index_queryset(self, using=None):
        return self.get_model().objects.all()