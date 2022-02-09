import click
import sys
import subprocess
import re

from PyQt5.QtWidgets import QApplication
from cand_viewer.app import ClassifierApp


@click.command(context_settings=dict(show_default=True))
@click.argument("imgdir", type=click.Path(exists=True))
@click.option("--sort_snr", is_flag=True, help="Sort by S/N ratio")
@click.option("--sort_rank", is_flag=True, help="Sort by rank")
@click.option("-o", "--outfile", type=click.Path(exists=False), default="results.csv", help="Output file")
@click.option("-h", "--history_file", type=click.Path(exists=True), default=None, help="History file")
def main(
    imgdir, outfile="results.csv", history_file=None, sort_snr=False, sort_rank=False
):
    """3-way Classifier building with PyQt5."""
    image_paths = get_image_paths(imgdir)
    if sort_snr:
        image_paths.sort(
            key=lambda x: float(re.search("snr_(.+?)_rank", x).group(1)), reverse=True
        )

    if sort_rank:
        image_paths.sort(
            key=lambda x: float(re.search("rank_(.+?).png", x).group(1)), reverse=True
        )

    app = QApplication(sys.argv)
    classifier = ClassifierApp(image_paths, outfile, history_file)
    try:
        app.exec()
    except Exception as err:
        classifier.export()
        sys.stdout.write(f"{err}\n")


def get_image_paths(imgdir):
    cmd = f'find {imgdir} -name "*snr*.png"'
    output = subprocess.check_output(cmd, shell=True)
    image_paths = output.decode().split("\n")[:-1]
    image_paths.sort()
    return image_paths


if __name__ == "__main__":
    main()
