#!/usr/bin/env python3
"""
This test script shows that you can kreate komponents from a python script.
The komponents will still be configured by the konfig.strukture.
You can also configure them further in python.
In general it is preferred to kreate all komponents from the strukture.
"""

from kreate.kore import Konfig
from kreate.kore._app import App
import kreate.kube


def kreate_app_script(konfig: Konfig) -> kreate.kube.KustApp:
    app = kreate.kube.KustApp(konfig)
    kreate.kube.Ingress(app, "root")
    kreate.kube.Ingress(app, "api")

    kreate.kube.Egress(app, "db")
    kreate.kube.Egress(app, "redis")
    kreate.kube.Egress(app, "xyz")

    depl=kreate.kube.Deployment(app)
    kreate.kube.Service(app)
    kreate.kube.Service(app, "https")
    pdb = kreate.kube.PodDisruptionBudget(app, name="demo-pdb")
    kreate.kube.Kustomization(app)
    app.kreate_komponent("Secret", "main")
    app.kreate_komponent("ServiceAccount")
    app.kreate_komponent("ServiceMonitor")
    app.kreate_komponent("HorizontalPodAutoscaler")
    app.kreate_komponent("MyUdpService", "main")
    app.kreate_komponent("CronJob", "main")
    app.kreate_komponent("StatefulSet", "main")
    app.kreate_patch(app.depl.main, "HttpProbesPatch")
    app.kreate_patch(depl, "AntiAffinityPatch")
    # Add the next two in alphabetical order, to be predictable
    app.kreate_patch(depl, "MountVolumeFiles", "demo-extra-files")
    app.kreate_patch(depl, "MountVolumeFiles", "demo-files")
    app.kreate_patch(depl, "MountVolumeFiles", "demo-secret-files")

    app.aktivate()

    app.ingress.root.sticky()
    app.ingress.root.whitelist("10.20.30.40")
    app.ingress.root.basic_auth()
    app.ingress.root.label("dummy", "jan")
    app.service.main.headless()
    pdb.yaml.spec.minAvailable = 2
    pdb.label("testje","test")

    return app

class DemoScriptKreator(kreate.kube.KubeKreator):
    def kreate_app(self, konfig : kreate.kube.KubeKonfig) -> kreate.kube.KustApp:
        return kreate_app_script(konfig)

kreator = DemoScriptKreator()
kreate.kube.KubeCli(kreator).run()