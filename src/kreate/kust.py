import logging
import inspect

from . import core, app
from .app import Komponent, Resource

logger = logging.getLogger(__name__)


class KustApp(app.App):

    def kreate_files(self):
        super().kreate_files()
        self.kust = Kustomization(self)
        self.kust.kreate_file()

    def register_std_templates(self) -> None:
        super().register_std_templates()
        self.register_template_class(Kustomization)
        self.register_template_class(KustConfigMap)
        self.register_template_class(AntiAffinityPatch)
        self.register_template_class(HttpProbesPatch)

    def kreate_from_konfig(self):
        super().kreate_from_konfig()
        for res in self.komponents:
            if isinstance(res, Resource):
                self.kreate_patches(res)

    def kreate_patch(self, res: Resource, kind: str, shortname: str = None, **kwargs):
        templ = self.templates[kind]
        if inspect.isclass(templ):
            return templ(res, "main", **kwargs)
        else:
            return Patch(res, "main", **kwargs)

    def kreate_patches(self, res) -> None:
        for patch in res.konfig.get("patches", {}):
            self.kreate_patch(res, kind=patch, shortname="main")

class Kustomization(Komponent):
    def resources(self):
        # exlcude ConfigMap if it should be generated by kustomize
        return [res for res in self.app.komponents if isinstance(res, Resource) ]

    def konfig_maps(self):
        return [res for res in self.app.komponents if isinstance(res, KustConfigMap)]


    def patches(self):
        return [res for res in self.app.komponents if isinstance(res, Patch)]

    @property
    def filename(self):
        return "kustomization.yaml"


# Note: this is not a resource
class KustConfigMap(Komponent):
    def _init(self):
        self.vars = {}

    def calc_name(self):
        return f"{self.app.name}-{self.shortname}"

    @property
    def filename(self) -> str:
        #logger.debug(f"not kreating file for {self.name}, will be created by kustomize")
        return None

    def calc_name(self):
        return f"{self.app.name}-{self.shortname}"

    def add_var(self, name, value=None):
        if value is None:
            value = self.app.values[name]
        self.vars[name] = value

class Patch(Komponent):
    def __init__(self, target: Resource, shortname: str = None, **kwargs):
        self.target = target
        Komponent.__init__(self, target.app, shortname=shortname, **kwargs)

    def __str__(self):
        return f"<Patch {self.target.kind}.{self.target.shortname}:{self.kind}.{self.shortname}>"

    def _template_vars(self):
        return { **super()._template_vars(),  "target": self.target }

    def _find_konfig(self):
        root_konfig = super()._find_konfig()
        typename = self.kind
        target_konfig = self.target.konfig.get("patches",{})
        if typename in target_konfig and self.shortname in target_konfig[typename]:
            logger.debug(f"using embedded konfig {typename}.{self.shortname} from {self.target.kind}.{self.target.shortname}")
            # The embedded_konfig is first, since the root_konfig will contain all default values
            embedded_konfig = target_konfig[typename][self.shortname]
            return core.DeepChain(embedded_konfig, root_konfig)
        return root_konfig


class HttpProbesPatch(Patch):
    pass
class AntiAffinityPatch(Patch):
    pass
