import pathlib
import tempfile

import numpy as np
import pytest
import tifffile

import iltis.Widgets.MainWindow_Widget
from iltis.Main import Main
from iltis.tests import test_files


def get_test_file_path():

    return pathlib.Path(test_files.__path__[0])


@pytest.fixture
def test_lsm_file():
    """Create a temporary LSM file with random data for testing."""
    # Generate random data, in ZCTYX (inferred from IOtools.read_lsm)
    data = np.random.randint(0, 65535, size=(1, 1, 10, 200, 200), dtype=np.uint16)

    # Create a temporary file
    temp_file = tempfile.NamedTemporaryFile(suffix=".lsm", delete=False)
    temp_file.close()

    # Save the data as a TIFF file (LSM format is not directly supported by tifffile)
    tifffile.imwrite(temp_file.name, data)

    return temp_file.name


@pytest.fixture
def test_pst_file():

    return str(get_test_file_path() / "dbb12D5.pst")


@pytest.fixture
def test_tif_file():

    return str(get_test_file_path() / "dbb12D5.tif")


@pytest.fixture
def test_circle_roi_config_file():
    return str(get_test_file_path() / "roi_test_files" / "circle_roi_files" / "clicks_config.yml")


@pytest.fixture
def test_singleclick_polygon_roi_config_file():
    return str(get_test_file_path() / "roi_test_files" / "singleclick_polygon_files" / "clicks_config.yml")

@pytest.fixture
def test_multiclick_polygon_roi_config_file():
    return str(get_test_file_path() / "roi_test_files" / "multiclick_polygon_files" / "clicks_config.yml")

@pytest.fixture
def iltis_main_object(qtbot, monkeypatch: pytest.MonkeyPatch):

    def closeEvent(self, event):
        self.Options_Control.close()
        event.accept()

    monkeypatch.setattr(
        iltis.Widgets.MainWindow_Widget.MainWindow_Widget, "closeEvent", closeEvent
    )

    main_object = Main(verbose=True)
    qtbot.addWidget(main_object.MainWindow)

    return main_object
