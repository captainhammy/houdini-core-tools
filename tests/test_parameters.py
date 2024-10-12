"""Test the houdini_core_tools.parameters module."""

# Standard Library
from contextlib import nullcontext

# Third Party
import pytest

# Houdini Core Tools
import houdini_core_tools.parameters
from houdini_core_tools import exceptions

# Houdini
import hou

pytestmark = pytest.mark.usefixtures("load_module_test_hip_file")


# Tests


@pytest.mark.parametrize(
    "parm_name,context,expected",
    (
        ("cacheinput", pytest.raises(exceptions.ParameterNotAButtonStripError), None),
        ("menu_not_strip", pytest.raises(exceptions.ParameterNotAButtonStripError), None),
        ("strip_normal", nullcontext(), (False, True, False, False)),
        ("strip_toggle", nullcontext(), (True, False, True, True)),
    ),
)
def test_eval_parm_as_strip(obj_test_node, parm_name, context, expected):
    """Test houdini_core_tools.parameters.eval_parm_as_strip()."""
    parm = obj_test_node.parm(f"node/{parm_name}")

    with context:
        assert houdini_core_tools.parameters.eval_parm_as_strip(parm) == expected


@pytest.mark.parametrize(
    "parm_name,expected",
    (
        ("strip_normal", ("bar",)),
        ("strip_toggle", ("foo", "hello", "world")),  # Toggle strip.
    ),
)
def test_eval_parm_strip_as_string(obj_test_node, parm_name, expected):
    """Test houdini_core_tools.parameters.eval_parm_strip_as_string()."""
    parm = obj_test_node.parm(f"node/{parm_name}")

    assert houdini_core_tools.parameters.eval_parm_strip_as_string(parm) == expected


@pytest.mark.parametrize(
    "parm_name,context,expected",
    (
        ("node/color", nullcontext(), hou.Color(0, 0.5, 0.5)),
        ("node/not_color", pytest.raises(exceptions.ParmTupleTypeError, match=".+ color chooser.+"), None),
    ),
)
def test_eval_parm_tuple_as_color(obj_test_node, parm_name, context, expected):
    """Test houdini_core_tools.parameters.eval_parm_tuple_as_color()."""
    parm = obj_test_node.parmTuple(parm_name)

    with context:
        assert houdini_core_tools.parameters.eval_parm_tuple_as_color(parm) == expected


@pytest.mark.parametrize(
    "parm_name,context,expected",
    (
        ("node/vec2", nullcontext(), hou.Vector2(1, 2)),
        ("node/vec3", nullcontext(), hou.Vector3(3, 4, 5)),
        ("node/vec4", nullcontext(), hou.Vector4(6, 7, 8, 9)),
        ("node/not_vec", pytest.raises(exceptions.ParmTupleTypeError, match=".+ vector.+"), None),
    ),
)
def test_eval_parm_tuple_as_vector(obj_test_node, parm_name, context, expected):
    """Test houdini_core_tools.parameters.eval_parm_tuple_as_vector()."""
    parm = obj_test_node.parmTuple(parm_name)

    with context:
        assert houdini_core_tools.parameters.eval_parm_tuple_as_vector(parm) == expected


@pytest.mark.parametrize(
    "parm_name,expected,stop_at_locked",
    (
        ("no_parent/test_parm", None, True),
        ("parent_parm_exists/scale", "scale", True),
        ("parent_is_locked_hda/test_node/scale", "parent_is_locked_hda/scale", True),
        ("ignore_locked_hda_parent/test_node/test_parent_parm", None, True),
        ("find_locked_hda_parent/test_node/test_parent_parm", "test_parent_parm", False),
    ),
)
def test_find_matching_parent_parm(obj_test_node, parm_name, expected, stop_at_locked):
    """Test houdini_core_tools.parameters.find_matching_parent_parm()."""
    parm = obj_test_node.parm(parm_name)

    result = houdini_core_tools.parameters.find_matching_parent_parm(parm, stop_at_locked_hda=stop_at_locked)

    if expected is not None:
        expected = obj_test_node.parm(expected)

    assert result == expected


@pytest.mark.parametrize(
    "varname,expected_parms",
    (
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
    ),
)
def test_find_parameters_using_variable(varname, expected_parms):
    """Test houdini_core_tools.parameters.find_parameters_using_variable()."""
    parms = {hou.parm(name) for name in expected_parms if hou.parm(name) is not None}

    result = houdini_core_tools.parameters.find_parameters_using_variable(varname)

    assert set(result) == parms


@pytest.mark.parametrize(
    "value,expected",
    (
        ("gaussian", ("/out/mantra1/vm_pfilter",)),
        ("render1", ()),
        ("render", ("/obj/geo1/font1/text", "/out/mantra1/vm_picture")),
        ("renders", ("/obj/geo1/font2/text",)),
    ),
)
def test_find_parameters_with_value(value, expected):
    """Test houdini_core_tools.parameters.find_parameters_with_value()."""
    result = houdini_core_tools.parameters.find_parameters_with_value(value)
    assert result == tuple(hou.parm(value) for value in expected)


@pytest.mark.parametrize(
    "name,expected",
    (
        ("vecparm#", ("base",)),
        ("leaf#_#", ("inner#", "base")),
        ("bottom#_#_#", ("deepest#_#", "inner#", "base")),
    ),
)
def test_get_multiparm_containing_folders(obj_test_node, name, expected):
    """Test houdini_core_tools.parameters.get_multiparm_containing_folders()."""
    node = obj_test_node.node("null")

    ptg = node.parmTemplateGroup()

    expected_folders = tuple(ptg.find(folder_name) for folder_name in expected)

    assert houdini_core_tools.parameters.get_multiparm_containing_folders(name, ptg) == expected_folders


@pytest.mark.parametrize(
    "name,expected",
    (
        ("vecparm#", (0,)),
        ("leaf#_#", (0, 1)),
        ("bottom#_#_#", (0, 1, 2)),
    ),
)
def test_get_multiparm_container_offsets(obj_test_node, name, expected):
    """Test houdini_core_tools.parameters.get_multiparm_container_offsets()."""
    node = obj_test_node.node("null")

    ptg = node.parmTemplateGroup()

    assert houdini_core_tools.parameters.get_multiparm_container_offsets(name, ptg) == expected


@pytest.mark.parametrize(
    "parm_name,context,expected",
    (
        ("normal", pytest.raises(exceptions.ParameterTemplateIsNotAMultiparmError), None),
        ("multi0", nullcontext(), 0),  # Parameter with default of 0, stored in tag.
        ("multi1", nullcontext(), 1),  # Parameter with default of 1, template contains no tags.
        ("multi2", nullcontext(), 2),  # Parameter with default of 2, stored in tag.
    ),
)
def test_get_multiparm_start_offset(obj_test_node, parm_name, context, expected):
    """Test houdini_core_tools.parameters.get_multiparm_start_offset()."""
    parm_template = obj_test_node.parm(f"null/{parm_name}").parmTemplate()

    with context:
        assert houdini_core_tools.parameters.get_multiparm_start_offset(parm_template) == expected


@pytest.mark.parametrize(
    "parm_name,expected",
    (
        ("numobj", True),
        ("objpath1", False),
        ("folder_tabs", False),
        ("folder_collapsible", False),
        ("folder_simple", False),
        ("folder_radio", False),
        ("multi_scroll", True),
        ("multi_tab", True),
    ),
)
def test_is_parm_multiparm(obj_test_node, parm_name, expected):
    """Test houdini_core_tools.parameters.is_parm_multiparm()."""
    parm = obj_test_node.parm(f"object_merge/{parm_name}")
    assert houdini_core_tools.parameters.is_parm_multiparm(parm) == expected

    parm_tuple = obj_test_node.parm(f"object_merge/{parm_name}")
    assert houdini_core_tools.parameters.is_parm_multiparm(parm_tuple) == expected


@pytest.mark.parametrize(
    "parm_name,expected",
    (
        ("tabs", False),
        ("simple", False),
        ("multilist", True),
        ("multiscroll", True),
        ("multitab", True),
    ),
)
def test_is_parm_template_multiparm_folder(obj_test_node, parm_name, expected):
    """Test houdini_core_tools.parameters.is_parm_template_multiparm_folder()."""
    parm_template = obj_test_node.parm(f"null/{parm_name}").parmTemplate()

    assert houdini_core_tools.parameters.is_parm_template_multiparm_folder(parm_template) == expected


@pytest.mark.parametrize(
    "parm_name,expected",
    (
        ("not_color", False),
        ("color", True),
    ),
)
def test_is_parm_tuple_color(obj_test_node, parm_name, expected):
    """Test houdini_core_tools.parameters.is_parm_tuple_color()."""
    parm = obj_test_node.parmTuple(f"node/{parm_name}")

    assert houdini_core_tools.parameters.is_parm_tuple_color(parm) == expected


@pytest.mark.parametrize(
    "parm_name,expected",
    (
        ("not_vec", False),
        ("vec", True),
    ),
)
def test_is_parm_tuple_vector(obj_test_node, parm_name, expected):
    """Test houdini_core_tools.parameters.is_parm_tuple_vector()."""
    parm = obj_test_node.parmTuple(f"node/{parm_name}")

    assert houdini_core_tools.parameters.is_parm_tuple_vector(parm) == expected
