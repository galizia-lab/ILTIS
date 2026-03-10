# -*- coding: utf-8 -*-
"""
Test file for testing the OpenAction in Main.MainWindow using pytest-qt.
"""

import os

import pytest


def trigger_open_action(iltis_main_object, input_file, monkeypatch: pytest.MonkeyPatch):
    """Test the OpenAction in MainWindow using pytest-qt."""

    # Verify the file exists
    assert os.path.exists(input_file), f"Input file {input_file} does not exist"

    # Simulate opening the file using the OpenAction
    # The OpenAction is connected to iltis_app.IO.init_data
    # We need to mock the file dialog to return the input_file
    def mock_open_file_dialog(title=None, default_dir=None, extension="*"):
        return [input_file]

    # Monkey patch the OpenFileDialog method
    monkeypatch.setattr(iltis_main_object.IO, "OpenFileDialog", mock_open_file_dialog)

    # Trigger the OpenAction
    iltis_main_object.MainWindow.OpenAction.trigger()

    # Verify that data was loaded
    assert iltis_main_object.Data is not None, "Data was not loaded"
    assert iltis_main_object.Data.raw is not None, "Raw data was not loaded"


def test_loading_lsm(iltis_main_object, test_lsm_file, monkeypatch: pytest.MonkeyPatch):
    """Test the OpenAction in MainWindow using pytest-qt for an LSM File"""

    trigger_open_action(iltis_main_object, test_lsm_file, monkeypatch)


def test_loading_tif(iltis_main_object, test_tif_file, monkeypatch: pytest.MonkeyPatch):
    """Test the OpenAction in MainWindow using pytest-qt for a TIF File"""

    trigger_open_action(iltis_main_object, test_tif_file, monkeypatch)


def test_loading_pst(iltis_main_object, test_pst_file, monkeypatch: pytest.MonkeyPatch):
    """Test the OpenAction in MainWindow using pytest-qt for a pst File"""

    trigger_open_action(iltis_main_object, test_pst_file, monkeypatch)
