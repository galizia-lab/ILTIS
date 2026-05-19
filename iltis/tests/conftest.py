import pathlib
import tempfile

import numpy as np
import pytest
import tifffile
from qtpy.QtCore import QPointF
from qtpy import QtCore

import iltis.Widgets.MainWindow_Widget
from iltis.Main import Main
from iltis.tests import test_files


class MockMouseEvent:
    """Mock mouse event compatible with both PyQt5 and PyQt6.
    
    This class provides a Qt5/Qt6 compatible mock for simulating mouse
    events in tests without relying on the QMouseEvent constructor,
    which has different signatures between Qt5 and Qt6.
    
    The mock is designed to work with pyqtgraph's sigMouseClicked signal
    and the ILTIS ROI creation code, which expects specific event attributes.
    """

    def __init__(self, scene_pos: QPointF):
        self._scene_pos = scene_pos
        self.currentItem = None

    def pos(self):
        """Return position as QPointF (float) - used by pyqtgraph's mapToView."""
        return self._scene_pos

    def posF(self):
        """Return position as QPointF (float)."""
        return self._scene_pos

    def scenePos(self):
        """Return scene position as QPointF."""
        return self._scene_pos

    def button(self):
        """Return the button that triggered the event.
        
        Returns 1 for left button, which is the value expected by
        the ILTIS ROI creation code (evt.button() == 1).
        """
        return 1

    def buttons(self):
        """Return the current button state."""
        return QtCore.Qt.LeftButton

    def modifiers(self):
        """Return the keyboard modifier state."""
        return QtCore.Qt.NoModifier

    def type(self):
        """Return the event type."""
        return QtCore.QEvent.MouseButtonPress

    def accept(self):
        """Accept the event."""
        pass

    def ignore(self):
        """Ignore the event."""
        pass


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
