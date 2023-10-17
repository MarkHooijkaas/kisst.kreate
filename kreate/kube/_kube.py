import logging
from ..kore import JinjaApp, Konfig
from ..krypt import KryptKonfig
from . import resource

logger = logging.getLogger(__name__)


class KubeApp(JinjaApp):
    def __init__(self, konfig: Konfig):
        super().__init__(konfig)
        self.namespace = konfig.get_path(
            "app.namespace", f"{self.appname}-{self.env}"
        )

    def register_std_templates(self) -> None:
        super().register_std_templates()

    def register_resource_class(self, cls) -> None:
        package = templates
        super().register_template_class(cls, package=package)

    def register_resource_file(self, kind: str, filename: str = None) -> None:
        package = templates
        cls = resource.Resource
        super().register_template_file(kind, cls, filename=filename, package=package)


class KubeKonfig(KryptKonfig):
    pass
