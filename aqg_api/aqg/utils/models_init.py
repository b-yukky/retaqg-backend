from ..models import Model

def init_models(models: dict, deactivate:bool=False):
    
    for model_name, activated in models.items():
        try:
            model = Model.objects.get(name=model_name)
            model.active = activated
            model.save()
        except Model.DoesNotExist:
            Model.objects.create(name=model_name, active=activated)
            
    default_model = Model.objects.get(name=list(models.keys())[0]).name
    
    if deactivate:
        return {key:False for key,_ in models.items()}, default_model
    else:
        return models, default_model

