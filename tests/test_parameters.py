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


def test__get_names_in_folder(obj_test_node):
    """Test houdini_core_tools.parameters._get_names_in_folder()."""
    node = obj_test_node.node("null")
    parm_template = node.parm("base").parmTemplate()

    result = houdini_core_tools.parameters._get_names_in_folder(parm_template)

    assert result == (
        "stringparm#",
        "vecparm#",
        "collapse_intparm#",
        "simple_intparm#",
        "tab_intparm1#",
        "tab_intparm2#",
        "inner_multi#",
    )


@pytest.mark.parametrize(
    "name, indices, ctx",
    [
        ("foo#_#", (1,), pytest.raises(exceptions.NotEnoughMultiParmIndicesError)),  # Test with not enough indices.
        ("foo#_#", (1, 2), nullcontext()),
        ("foo#_#", (1, 2, 3), nullcontext()),  # Test with more than enough indices.
    ],
)
def test__validate_multiparm_resolve_values(name, indices, ctx):
    """Test houdini_core_tools.parameters._validate_multiparm_resolve_values()."""
    with ctx:
        houdini_core_tools.parameters._validate_multiparm_resolve_values(name, indices)


@pytest.mark.parametrize(
    "name,indices,raw,context,expected",
    (
        ("base", 0, False, pytest.raises(exceptions.MissingMultiParmTokenError), None),
        ("foo#", 0, False, pytest.raises(exceptions.NoMatchingParameterTemplate), None),
        ("vecparm#", 10, False, pytest.raises(exceptions.InvalidMultiParmIndicesError), None),
        ("vecparm#", 0, False, nullcontext(), (1.1, 2.2, 3.3, 4.4)),
        ("vecparm#", 1, False, nullcontext(), (5.5, 6.6, 7.7, 8.8)),
        ("leaf#_#", (0, 0), False, nullcontext(), 1),
        ("leaf#_#", (0, 2), False, nullcontext(), 3),
        ("leaf#_#", (0, 3), False, nullcontext(), 10),
        ("string#", 0, False, nullcontext(), str(hou.intFrame())),
        ("vecparm#", 0, True, nullcontext(), (1.1, 2.2, 3.3, 4.4)),
        ("vecparm#", 1, True, nullcontext(), (5.5, 6.6, 7.7, 8.8)),
        ("leaf#_#", (1, 0), True, pytest.raises(exceptions.InvalidMultiParmIndicesError), None),
        ("leaf#_#", (1, 1), True, nullcontext(), 5),
        ("leaf#_#", (1, 3), True, nullcontext(), 7),
        ("string#", 1, True, nullcontext(), "test_parameters"),
    ),
)
def test_eval_multiparm_instance(obj_test_node, name, indices, raw, context, expected):
    """Test houdini_core_tools.parameters.eval_multiparm_instance()."""
    node = obj_test_node.node("null")

    with context:
        result = houdini_core_tools.parameters.eval_multiparm_instance(node, name, indices, raw_indices=raw)
        assert result == expected


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
        ("node/not_color", pytest.raises(exceptions.ParmTupleTypeError, match=r".+ color chooser.+"), None),
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
        ("node/not_vec", pytest.raises(exceptions.ParmTupleTypeError, match=r".+ vector.+"), None),
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
        ("$BAZ", ()),
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
                "/obj/test_eval_multiparm_instance/null/string1",
                "/stage/rendergallerysource",
                "/tasks/topnet1/taskgraphfile",
                "/tasks/topnet1/checkpointfile",
                "/tasks/topnet1/localscheduler/tempdircustom",
            ),
        ),
        ("$HIPFILE", ("/obj/geo1/font2/text", "/obj/test_unexpanded_string_multiparm_instance/null/string1")),
        (
            "F",  # Test var with no $ to handle auto adding.
            (
                "/obj/geo1/font1/text",
                "/obj/test_eval_multiparm_instance/null/string0",
                "/obj/test_unexpanded_string_multiparm_instance/null/string0",
                "/tasks/topnet1/taskgraphfile",
            ),
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


def test_get_multiparm_siblings(obj_test_node):
    """Test houdini_core_tools.parameters.get_multiparm_siblings()."""
    node = obj_test_node.node("null")
    parm = node.parm("base")

    with pytest.raises(exceptions.ParameterIsNotAMultiParmInstanceError):
        houdini_core_tools.parameters.get_multiparm_siblings(parm)

    parm = node.parm("stringparm0")

    expected = {
        "inner_multi#": node.parm("inner_multi0"),
        "vecparm#": node.parmTuple("vecparm0"),
        "simple_intparm#": node.parm("simple_intparm0"),
        "tab_intparm1#": node.parm("tab_intparm10"),
        "collapse_intparm#": node.parm("collapse_intparm0"),
        "tab_intparm2#": node.parm("tab_intparm20"),
    }

    assert houdini_core_tools.parameters.get_multiparm_siblings(parm) == expected

    parm_tuple = node.parmTuple("vecparm0")

    expected = {
        "inner_multi#": node.parm("inner_multi0"),
        "stringparm#": node.parm("stringparm0"),
        "simple_intparm#": node.parm("simple_intparm0"),
        "tab_intparm1#": node.parm("tab_intparm10"),
        "collapse_intparm#": node.parm("collapse_intparm0"),
        "tab_intparm2#": node.parm("tab_intparm20"),
    }

    assert houdini_core_tools.parameters.get_multiparm_siblings(parm_tuple) == expected


@pytest.mark.parametrize(
    "parm_name,context,expected",
    (
        ("normal", pytest.raises(exceptions.ParameterTemplateIsNotAMultiParmError), None),
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
        ("base", None),
        ("inner0", "inner#"),
        ("vecparm0", "vecparm#"),
        ("leaf1_3", "leaf#_#"),
    ),
)
def test_get_multiparm_template_name(obj_test_node, parm_name, expected):
    """Test houdini_core_tools.parameters.get_multiparm_template_name()."""
    node = obj_test_node.node("null")

    parm_item = node.parm(parm_name)

    if parm_item is None:
        parm_item = node.parmTuple(parm_name)

    assert houdini_core_tools.parameters.get_multiparm_template_name(parm_item) == expected


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


@pytest.mark.parametrize(
    "name,tokens,context,expected",
    (
        ("test#", 3, nullcontext(), "test3"),
        ("#test", 3, nullcontext(), "3test"),
        ("test#", (4,), nullcontext(), "test4"),
        ("test#", [5], nullcontext(), "test5"),
        ("test#_thing", [5], nullcontext(), "test5_thing"),
        ("test#", [5, 6], nullcontext(), "test5"),
        ("test#_#_#", [1, 2, 3], nullcontext(), "test1_2_3"),
        ("test#_#_#", [1, 2, 3, 4], nullcontext(), "test1_2_3"),
        ("test##", [5, 6], nullcontext(), "test56"),
        ("test##", [5, 6, 7], nullcontext(), "test56"),
        ("test#_#", [5], pytest.raises(exceptions.NotEnoughMultiParmIndicesError), None),
    ),
)
def test_resolve_multiparm_tokens(name, tokens, context, expected):
    """Test houdini_core_tools.parameters.resolve_multiparm_tokens()."""
    with context:
        assert houdini_core_tools.parameters.resolve_multiparm_tokens(name, tokens) == expected


@pytest.mark.parametrize(
    "name,indices,raw,context,expected",
    (
        ("base", 0, False, pytest.raises(exceptions.MissingMultiParmTokenError), None),
        ("foo#", 0, False, pytest.raises(exceptions.NoMatchingParameterTemplate), None),
        ("float#", 0, False, pytest.raises(exceptions.ParameterIsNotAStringError), None),
        ("string#", 10, False, pytest.raises(exceptions.InvalidMultiParmIndicesError), None),
        ("string#", 0, False, nullcontext(), "$F"),
        ("string#", 1, False, nullcontext(), "$HIPFILE"),
        ("nested_string#_#", (0, 1), False, nullcontext(), ("$EYE", "$HOME")),
        ("nested_string#_#", (1, 0), False, nullcontext(), ("$JOB", "$TEMP")),
        ("string#", 0, True, nullcontext(), "$F"),
        ("string#", 1, True, nullcontext(), "$HIPFILE"),
        ("nested_string#_#", (0, 1), True, nullcontext(), ("$E", "$C")),
        ("nested_string#_#", (1, 1), True, nullcontext(), ("$JOB", "$TEMP")),
    ),
)
def test_unexpanded_string_multiparm_instance(obj_test_node, name, indices, raw, context, expected):
    """Test houdini_core_tools.parameters.unexpanded_string_multiparm_instance()."""
    node = obj_test_node.node("null")

    with context:
        result = houdini_core_tools.parameters.unexpanded_string_multiparm_instance(
            node, name, indices, raw_indices=raw
        )
        assert result == expected
