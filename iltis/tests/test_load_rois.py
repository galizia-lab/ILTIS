import yaml

from iltis.Main import Main
import pytest

from iltis.Objects.ROIs_Object import myCircleROI, myPolyLineROI
from iltis.tests.test_image_loading import trigger_open_action
import pathlib as pl


def load_rois(iltis_main_object: Main, roi_files: list[str], monkeypatch: pytest.MonkeyPatch):
    """
    Helper function to test loading rois

    Parameters:
        iltis_main_object: iltis main object with data loaded
        roi_files: list of ROI files to be loaded for testing
        monkeypatch: pytest fixture
    """

    for roi_file in roi_files:

        def mock_open_file_dialog(title=None, default_dir=None, extension="*"):
            return [roi_file]

        # Monkey patch the OpenFileDialog method
        monkeypatch.setattr(iltis_main_object.IO, "OpenFileDialog", mock_open_file_dialog)

        iltis_main_object.MainWindow.ReadROIAction.trigger()



def load_roi_files_check(iltis_main_object: Main, test_roi_config_files, monkeypatch):

    roi_files = []
    n_roi_expected = {"circle": 0, "polygon": 0, "polygon-multiclick": 0}
    for test_roi_config_file in test_roi_config_files:
        # Load YML configuration
        with open(test_roi_config_file, "r") as file:
            config = yaml.safe_load(file)

        roi_type = config["type"]
        roi_metadata_all = config["rois"]
        expected_file_stem = config["expected_file_stem"]

        roi_file = pl.Path(test_roi_config_file).parent / f"{expected_file_stem}.roi"
        roi_files.append(roi_file)

        roi_type = "polygon" if roi_type == "polygon-multiclick" else roi_type
        n_roi_expected[roi_type] += len(roi_metadata_all)

    load_rois(iltis_main_object, roi_files, monkeypatch)

    n_roi_found = {"circle": 0, "polygon": 0, "polygon-multiclick": 0}
    for roi in iltis_main_object.ROIs.ROI_list:
        if isinstance(roi, myCircleROI):
            n_roi_found["circle"] += 1
        elif isinstance(roi, myPolyLineROI):
            n_roi_found["polygon"] += 1
        else:
            raise ValueError(f"Found unknown ROI type: {type(roi)}")

    assert n_roi_found == n_roi_expected



def test_loading_circle_rois(iltis_main_object: Main, test_tif_file, test_circle_roi_config_file, monkeypatch):

    trigger_open_action(iltis_main_object, test_tif_file, monkeypatch)

    load_roi_files_check(iltis_main_object, [test_circle_roi_config_file], monkeypatch)


def test_loading_singleclick_polygon_rois(iltis_main_object: Main, test_tif_file, test_singleclick_polygon_roi_config_file, monkeypatch):
    trigger_open_action(iltis_main_object, test_tif_file, monkeypatch)

    load_roi_files_check(iltis_main_object, [test_singleclick_polygon_roi_config_file], monkeypatch)

def test_loading_multiclick_polygon_rois(iltis_main_object: Main, test_tif_file, test_multiclick_polygon_roi_config_file, monkeypatch):
    trigger_open_action(iltis_main_object, test_tif_file, monkeypatch)

    load_roi_files_check(iltis_main_object, [test_multiclick_polygon_roi_config_file], monkeypatch)


