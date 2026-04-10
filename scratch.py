import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))
import json
from custom_components.anova_api.anova_lib.apo.transpiler import *
from custom_components.anova_api.anova_lib.apo.models import *
from custom_components.anova_api.anova_lib.client import AnovaDevice

device = AnovaDevice(device_id="123", type="oven", model="oven_v2")
r = APORecipe(title="Manual Cook", stages=[APOStage(temperature=54.44, sous_vide=True)])
c = APOCook(recipe=r)
print(json.dumps(cook_to_payload(c, device), indent=2))
