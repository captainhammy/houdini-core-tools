"""Test the houdini_core_tools.parameters module."""

# Third Party
import pytest

# Houdini Core Tools
import houdini_core_tools.parameters

# Houdini
import hou

pytestmark = pytest.mark.usefixtures("load_module_test_hip_file")


# TESTS


class Test_find_matching_parent_parm:
    """Test houdini_core_tools.parameters.find_matching_parent_parm()."""

    def test_no_parent(self, obj_test_node):
        """Test when there is no parent parm."""
        parm = obj_test_node.parm("test_parm")

        result = houdini_core_tools.parameters.find_matching_parent_parm(parm)

        assert result is None

    def test_parent_parm_exists(self, obj_test_node):
        """Test when there is no parent parm."""
        parm = obj_test_node.parm("scale")

        result = houdini_core_tools.parameters.find_matching_parent_parm(parm)

        assert result == obj_test_node.parent().parm("scale")

    def test_parent_is_locked_hda(self, obj_test_node):
        """Test when there is no parent parm."""
        parm = obj_test_node.node("test_node").parm("scale")

        result = houdini_core_tools.parameters.find_matching_parent_parm(parm)

        assert result == obj_test_node.parm("scale")

    def test_ignore_locked_hda_parent(self, obj_test_node):
        """Test when there is no parent parm."""
        parm = obj_test_node.node("test_node").parm("test_parent_parm")

        result = houdini_core_tools.parameters.find_matching_parent_parm(parm)

        assert result is None

    def test_find_locked_hda_parent(self, obj_test_node):
        """Test when there is no parent parm."""
        parm = obj_test_node.node("test_node").parm("test_parent_parm")

        result = houdini_core_tools.parameters.find_matching_parent_parm(parm, stop_at_locked_hda=False)

        assert result == obj_test_node.parent().parm("test_parent_parm")


@pytest.mark.parametrize(
    ("varname", "expected_parms"),
    [
        ("$BAR", ()),
        (
            "$HIP",
            (
                "/obj/geo1/font1/text",
                "/obj/geo1/font3/text",
                "/out/mantra1/vm_picture",
                "/out/mantra1/soho_diskfile",
                "/out/mantra1/vm_dcmfilename",
                "/out/mantra1/vm_dsmfilename",
                "/out/mantra1/vm_tmpsharedstorage",
                "/stage/rendergallerysource",
                "/tasks/topnet1/taskgraphfile",
                "/tasks/topnet1/checkpointfile",
                "/tasks/topnet1/localscheduler/pdg_workingdir",
            ),
        ),
        (
            "HIP",
            (
                "/obj/geo1/font1/text",
                "/obj/geo1/font3/text",
                "/out/mantra1/vm_picture",
                "/out/mantra1/soho_diskfile",
                "/out/mantra1/vm_dcmfilename",
                "/out/mantra1/vm_dsmfilename",
                "/out/mantra1/vm_tmpsharedstorage",
                "/stage/rendergallerysource",
                "/tasks/topnet1/taskgraphfile",
                "/tasks/topnet1/checkpointfile",
                "/tasks/topnet1/localscheduler/pdg_workingdir",
            ),
        ),
        (
            "${HIP}",
            (
                "/obj/geo1/font1/text",
                "/obj/geo1/font3/text",
                "/out/mantra1/vm_picture",
                "/out/mantra1/soho_diskfile",
                "/out/mantra1/vm_dcmfilename",
                "/out/mantra1/vm_dsmfilename",
                "/out/mantra1/vm_tmpsharedstorage",
                "/stage/rendergallerysource",
                "/tasks/topnet1/taskgraphfile",
                "/tasks/topnet1/checkpointfile",
                "/tasks/topnet1/localscheduler/pdg_workingdir",
            ),
        ),
        (
            "$HIPNAME",
            (
                "/out/mantra1/vm_picture",
                "/stage/rendergallerysource",
                "/tasks/topnet1/taskgraphfile",
                "/tasks/topnet1/checkpointfile",
                "/tasks/topnet1/localscheduler/tempdircustom",
            ),
        ),
        ("$HIPFILE", ("/obj/geo1/font2/text",)),
        (
            "F",  # Test var with no $ to handle auto adding.
            ("/obj/geo1/font1/text", "/tasks/topnet1/taskgraphfile"),
        ),
        ("$F4", ("/out/mantra1/vm_picture",)),
    ],
)
def test_find_parameters_using_variable(varname, expected_parms):
    """Test houdini_core_tools.parameters.find_parameters_using_variable()."""
    parms = {hou.parm(name) for name in expected_parms if hou.parm(name) is not None}

    result = houdini_core_tools.parameters.find_parameters_using_variable(varname)

    assert set(result) == parms


def test_find_parameters_with_value():
    """Test houdini_core_tools.parameters.find_parameters_with_value()."""
    result = houdini_core_tools.parameters.find_parameters_with_value("gaussian")
    assert result == (hou.parm("/out/mantra1/vm_pfilter"),)

    result = houdini_core_tools.parameters.find_parameters_with_value("render1")
    assert result == ()

    result = houdini_core_tools.parameters.find_parameters_with_value("render")
    assert result == (
        hou.parm("/obj/geo1/font1/text"),
        hou.parm("/out/mantra1/vm_picture"),
    )

    result = houdini_core_tools.parameters.find_parameters_with_value("renders")
    assert result == (hou.parm("/obj/geo1/font2/text"),)
