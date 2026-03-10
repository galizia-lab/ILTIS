# -*- coding: utf-8 -*-
"""
Test module for creating and saving ROI files.
"""

import pathlib as pl

import pytest
import yaml
from PyQt5.QtCore import QPointF
from qtpy import QtCore
from qtpy.QtGui import QMouseEvent
from qtpy.QtTest import QSignalSpy

from iltis.Main import Main
from iltis.Widgets.Frame_Visualizer_Widget import Frame_Visualizer_Widget
from iltis.tests.test_image_loading import trigger_open_action
from iltis.Widgets.Options_Control_Widget import StringChoiceWidget



def set_roi_type(iltis_main_object: Main,
        roi_type: str):

    # Find the StringChoiceWidget for ROI type
    roi_type_widget = None
    for widget in iltis_main_object.MainWindow.roi_type_widget.children():
        if isinstance(widget, StringChoiceWidget):
            if widget.dict_name == "ROI" and widget.param_name == "type":
                roi_type_widget = widget
                break

    if roi_type_widget is None:
        raise ValueError("StringChoiceWidget for ROI type not found")

    # Set the ROI type
    index = roi_type_widget.choices.index(roi_type)
    roi_type_widget.setCurrentIndex(index)


def simulate_click_frame_visualizer(frame_visualizer: Frame_Visualizer_Widget, click_pos):

    # Create a mock mouse event
    pos = frame_visualizer.ViewBox.mapViewToScene(QPointF(*click_pos))
    press_evt = QMouseEvent(
        QtCore.QEvent.MouseButtonPress,
        pos.toPoint(),
        QtCore.Qt.LeftButton,
        QtCore.Qt.LeftButton,
        QtCore.Qt.NoModifier,
    )
    press_evt.currentItem = frame_visualizer.ViewBox

    # Simulate the mouse click
    frame_visualizer.scene().sigMouseClicked.emit(press_evt)

def create_rois_singleclick(
        iltis_main_object: Main,
        roi_metadata: dict,
):
    """
        Helper function to test the creation ROI files for single-click ROIs.

        Args:
            iltis_main_object: An instance of the ILTIS main object with data loaded.
            roi_metadata: contains info about creating ROIs

        """

    # Simulate clicks for ROI creation
    frame_visualizer = iltis_main_object.MainWindow.Data_Display.Frame_Visualizer

    for click in roi_metadata["clicks"]:
        simulate_click_frame_visualizer(frame_visualizer, click)


def create_rois_multiclick(
        iltis_main_object: Main,
        roi_metadata: dict,
):
    """
        Helper function to test the creation ROI files for multi-click ROIs.

        Args:
            iltis_main_object: An instance of the ILTIS main object with data loaded.
            roi_metadata: contains info about creating ROIs

        """

    create_rois_singleclick(iltis_main_object, roi_metadata)

    roi_object = iltis_main_object.ROIs
    roi_object.ROI_clicked(roi_object.multi_click_rois[0][1])


def save_rois(
    iltis_main_object: Main,
    output_dir: pl.Path,
    output_stem: str,
    monkeypatch: pytest.MonkeyPatch,
):

    output_file_path = output_dir / f"{output_stem}.roi"
    output_file_str = str(output_file_path)

    # Monkeypatch SaveFileDialog to save files to a temporary directory
    def mock_save_file_dialog(title=None, default_dir=None, extension="*"):
        return output_file_str

    monkeypatch.setattr(iltis_main_object.IO, "SaveFileDialog", mock_save_file_dialog)

    # Save the ROI file
    iltis_main_object.MainWindow.WriteROIAction.trigger()

    return output_file_str

def check_compare_roi_output(expected_dir: pl.Path, expected_stem: str, output_dir: pl.Path, output_stem: str):

    # Compare saved ROI file to expected ROI file
    expected_roi_file_path = expected_dir / f"{expected_stem}.roi"

    output_file_path = output_dir / f"{output_stem}.roi"

    # Read both files and compare
    with open(output_file_path, "r") as saved_file:
        saved_content = saved_file.read()

    with open(expected_roi_file_path, "r") as expected_file:
        expected_content = expected_file.read()

    assert (
            saved_content == expected_content
    ), "Saved ROI file does not match expected ROI file"

    # Check if the mask file was also saved
    mask_file_str = output_dir / f"{output_file_path.stem}_mask.tif"
    assert pl.Path(mask_file_str).exists(), "Mask file was not saved"

    # Compare saved mask file to expected mask file
    expected_mask_file_path = (
            expected_dir / f"{expected_stem}_mask.tif"
    )

    # Read both mask files and compare
    import numpy as np
    import tifffile

    saved_mask = tifffile.imread(mask_file_str)
    expected_mask = tifffile.imread(expected_mask_file_path)

    assert np.array_equal(
        saved_mask, expected_mask
    ), "Saved mask file does not match expected mask file"


def create_roi_and_save_check(
    iltis_main_object: Main,
    yml_file_path_str: str,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: pl.Path,
):
    """
    Helper function to test the creation and saving of ROI files.

    Args:
        iltis_main_object: An instance of the ILTIS main object with data loaded.
        yml_file_path: Path to a YML file containing ROI configuration.
        monkeypatch: pytest fixture for monkeypatching.
        tmp_path: pytest fixture for temporary directory.

    YML file format:
        - type: string (e.g., 'circle', 'polygon', 'polygon-multiclick')
        - rois: list of roi_metadata, each a dict with a list of x, y coordinates for the key "clicks"
        - expected_file_stem: stem of the expected ROI file
    """

    assert (
        iltis_main_object.MainWindow.Data_Display.interaction_enabled
    ), "Interaction has not been enabled for the Data Display Widget"

    # Load YML configuration
    with open(yml_file_path_str, "r") as file:
        config = yaml.safe_load(file)

    roi_type = config["type"]
    roi_metadata_all = config["rois"]
    expected_file_stem = config["expected_file_stem"]

    set_roi_type(iltis_main_object, roi_type)

    for _roi_label, roi_metadata in roi_metadata_all.items():
        print(roi_metadata, type(roi_metadata))
        if roi_type in ("circle", "polygon"):
            create_rois_singleclick(iltis_main_object, roi_metadata)
        elif roi_type in ("polygon-multiclick"):
            create_rois_multiclick(iltis_main_object, roi_metadata)
        else:
            raise ValueError(f"Unknown roi type {roi_type}")

    yml_file_path = pl.Path(yml_file_path_str)
    output_stem = f"{expected_file_stem}_output"
    output_dir_path = tmp_path
    save_rois(
        iltis_main_object, output_dir_path, output_stem, monkeypatch)


    check_compare_roi_output(yml_file_path.parent, expected_file_stem, output_dir_path, output_stem)

    return True


def test_roi_creation_saving_circle(
    iltis_main_object: Main,
    test_tif_file: str,
    test_circle_roi_config_file: str,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: pl.Path,
):
    """
    test creation and saving of circular rois
    """

    trigger_open_action(iltis_main_object, test_tif_file, monkeypatch)

    create_roi_and_save_check(
        iltis_main_object, test_circle_roi_config_file, monkeypatch, tmp_path
    )


def test_roi_creation_saving_singleclick_polygon(
    iltis_main_object: Main,
    test_tif_file: str,
    test_singleclick_polygon_roi_config_file: str,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: pl.Path,
):
    """
    test creation and saving of singleclick polygon rois
    """

    trigger_open_action(iltis_main_object, test_tif_file, monkeypatch)

    create_roi_and_save_check(
        iltis_main_object, test_singleclick_polygon_roi_config_file, monkeypatch, tmp_path
    )

def test_roi_creation_saving_multiclick_polygon(
    iltis_main_object: Main,
    test_tif_file: str,
    test_multiclick_polygon_roi_config_file: str,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: pl.Path,
):
    """
    test creation and saving of multiclick polygon rois
    """

    trigger_open_action(iltis_main_object, test_tif_file, monkeypatch)

    create_roi_and_save_check(
        iltis_main_object, test_multiclick_polygon_roi_config_file, monkeypatch, tmp_path
    )
