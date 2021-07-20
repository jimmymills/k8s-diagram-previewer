import os
from enum import Enum

import typer

from .diagram import K8sDiagram

app = typer.Typer()


class ImageFormat(str, Enum):
    JPEG = "jpg"
    PNG = "png"
    GIF = "gif"
    SVG = "svg"


@app.command()
def diagram(
    folder_path: str,
    show: bool = typer.Option(False, help="Show the diagram when finished"),
    image_format: ImageFormat = typer.Option(ImageFormat.PNG, help="Output diagram as png, jpg, svg or pdf."),
    diagram_py: bool = typer.Option(False, help="Save a python script at create_diagram.py that can be edited to add more to the diagram."),
    networking_only: bool = typer.Option(False, help="Only draw diagram edges to display networking, ignore storage links, etc."),
    helm: bool = typer.Option(False, help="Indicates that the path given is a helm chart that needs to be templated."),
    helm_args: str = typer.Option("", help="String of arguments to use with helm template. Ex: '--set ingress.enabled=true'"),
    cluster_context: str = typer.Option("", help="Indicates a cluster to pull current definitions from. YAML of the current state will be stored at the target path."),
):
    """
    Create preview diagram of K8s YAML.
    """
    if helm:
        TMP_PATH = '/tmp/helm_preview_yaml'
        os.popen(f'mkdir -p {TMP_PATH} && helm template {helm_args} {folder_path} > {TMP_PATH}/chart.yaml').read()
        folder_path = TMP_PATH
    elif cluster_context:
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        path = os.path.join(__location__, 'pull_cluster_info.sh')
        os.popen(f'bash {path} {folder_path} {cluster_context}').read()
    K8sDiagram(folder_path, nw_only=networking_only).run(show, image_format.value, diagram_py)


if __name__ == "__main__":
    app()
