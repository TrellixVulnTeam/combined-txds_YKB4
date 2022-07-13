# import pytest as pt
from logic.parsers.anoeds_parser import Parser
from logic.powerflow import PowerFlow
from models.threephase.resistive_load import ResistiveLoad
import os
import numpy as np

CURR_DIR = os.path.realpath(os.path.dirname(__file__))

# Check that disconnected swing buses just return the nominal voltage.
def test_powerflowrunner_just_swing():
    glm_file_path = os.path.join("data", "just_swing", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlow(glm_full_file_path)
    v_estimate = test_runner.execute()
    expected_v = np.array([2.40000000e+03,
                           0.00000000e+00,
                           -1.20000000e+03,
                           -2.07846097e+03,
                           -1.20000000e+03,
                           2.07846097e+03], dtype=float)
    assert np.allclose(v_estimate[:6], expected_v, rtol=1e-5)

# Check that the stamps of resistive loads look correct
def test_powerflowrunner_just_load_stamp():
    glm_file_path = os.path.join("data", "just_load_stamp", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    parser = Parser(glm_full_file_path)
    simulation_state = parser.parse()
    simulation_state.reset_linear_stamp_collection()
    model_has_resistive_loads = False
    for load in simulation_state.loads:
        if isinstance(load, ResistiveLoad):
            model_has_resistive_loads = True
            load.collect_Y_stamps(simulation_state)
    if not model_has_resistive_loads:
        # Only run the test when resistive loads are implemented
        return
    PowerFlowRunner.stamp_linear(simulation_state)
    expected_Y = np.matrix([[ 0.3125    ,  0.        ,  0.        ,  0.        ,  0.        ,0.        ],
        [ 0.        , 0.15135066,  0.        ,  0.        ,  0.        ,0.        ],
        [ 0.        ,  0.        ,  0.3125    ,  0.        ,  0.        ,0.        ],
        [ 0.        ,  0.        ,  0.        , 0.15135066,  0.        ,0.        ],
        [ 0.        ,  0.        ,  0.        ,  0.        ,  0.3125    ,0.        ],
        [ 0.        ,  0.        ,  0.        ,  0.        ,  0.        ,0.15135066]], dtype=float)
    assert np.allclose(simulation_state.lin_Y.todense(), expected_Y, rtol=1e-5)

# Check that the stamps of infinite sources look correct
def test_powerflowrunner_just_swing_stamp():
    glm_file_path = os.path.join("data", "just_swing", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    parser = Parser(glm_full_file_path)
    simulation_state = parser.parse()
    simulation_state.reset_linear_stamp_collection()
    for infinite_source in simulation_state.infinite_sources:
        infinite_source.collect_Y_stamps(simulation_state)
        infinite_source.collect_J_stamps(simulation_state)
    PowerFlowRunner.stamp_linear(simulation_state)
    expected_Y = np.array([[0., 0., 0., 0., 0., 0., 1., 0., 0., 0., 0., 0.],
        [0., 0., 0., 0., 0., 0., 0., 1., 0., 0., 0., 0.],
        [0., 0., 0., 0., 0., 0., 0., 0., 1., 0., 0., 0.],
        [0., 0., 0., 0., 0., 0., 0., 0., 0., 1., 0., 0.],
        [0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1., 0.],
        [0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1.],
        [1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
        [0., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
        [0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
        [0., 0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 0.],
        [0., 0., 0., 0., 1., 0., 0., 0., 0., 0., 0., 0.],
        [0., 0., 0., 0., 0., 1., 0., 0., 0., 0., 0., 0.]], dtype=float)
    expected_J = np.array([[    0.        ],
        [    0.        ],
        [    0.        ],
        [    0.        ],
        [    0.        ],
        [    0.        ],
        [ 2400.        ],
        [    0.        ],
        [-1200.        ],
        [-2078.46096908],
        [-1200.        ],
        [ 2078.46096908]], dtype=float)
    assert np.allclose(simulation_state.lin_Y.todense(), expected_Y, rtol=1e-5)
    assert np.allclose(simulation_state.lin_J.todense(), expected_J, rtol=1e-5)

# Check that the stamps of swing buses plus resistive loads look correct
def test_powerflowrunner_swing_and_load_stamp():
    glm_file_path = os.path.join("data", "swing_and_load_stamp", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    parser = Parser(glm_full_file_path)
    simulation_state = parser.parse()
    simulation_state.reset_linear_stamp_collection()
    model_has_resistive_loads = False
    for load in simulation_state.loads:
        if isinstance(load, ResistiveLoad):
            model_has_resistive_loads = True
            load.collect_Y_stamps(simulation_state)
    if not model_has_resistive_loads:
        # Only run the test when resistive loads are implemented
        return
    for infinite_source in simulation_state.infinite_sources:
        infinite_source.collect_Y_stamps(simulation_state)
        infinite_source.collect_J_stamps(simulation_state)
    PowerFlowRunner.stamp_linear(simulation_state)
    # Columns: Voltage variables at swing | Voltage variables at load | Current variables
    # Rows: KCLs at swing ; KCLs at load; extra equations for infinite sources at swing bus
    expected_Y = np.array([
        [ 0.        ,  0.        ,  0.        ,  0.        ,  0.        ,0.        ,  0.        ,  0.        ,  0.        ,  0.        ,0.        ,  0.        ,  1.        ,  0.        ,  0.        ,0.        ,  0.        ,  0.        ],
        [ 0.        ,  0.        ,  0.        ,  0.        ,  0.        ,0.        ,  0.        ,  0.        ,  0.        ,  0.        ,0.        ,  0.        ,  0.        ,  1.        ,  0.        ,0.        ,  0.        ,  0.        ],
        [ 0.        ,  0.        ,  0.        ,  0.        ,  0.        ,0.        ,  0.        ,  0.        ,  0.        ,  0.        ,0.        ,  0.        ,  0.        ,  0.        ,  1.        ,0.        ,  0.        ,  0.        ],
        [ 0.        ,  0.        ,  0.        ,  0.        ,  0.        ,0.        ,  0.        ,  0.        ,  0.        ,  0.        ,0.        ,  0.        ,  0.        ,  0.        ,  0.        ,1.        ,  0.        ,  0.        ],
        [ 0.        ,  0.        ,  0.        ,  0.        ,  0.        ,0.        ,  0.        ,  0.        ,  0.        ,  0.        ,0.        ,  0.        ,  0.        ,  0.        ,  0.        ,0.        ,  1.        ,  0.        ],
        [ 0.        ,  0.        ,  0.        ,  0.        ,  0.        ,0.        ,  0.        ,  0.        ,  0.        ,  0.        ,0.        ,  0.        ,  0.        ,  0.        ,  0.        ,0.        ,  0.        ,  1.        ],
        [ 0.        ,  0.        ,  0.        ,  0.        ,  0.        ,0.        ,  0.3125    ,  0.        ,  0.        ,  0.        ,0.        ,  0.        ,  0.        ,  0.        ,  0.        ,0.        ,  0.        ,  0.        ],
        [ 0.        ,  0.        ,  0.        ,  0.        ,  0.        ,0.        ,  0.        , 0.15135066,  0.        ,  0.        ,0.        ,  0.        ,  0.        ,  0.        ,  0.        ,0.        ,  0.        ,  0.        ],
        [ 0.        ,  0.        ,  0.        ,  0.        ,  0.        ,0.        ,  0.        ,  0.        ,  0.3125    ,  0.        ,0.        ,  0.        ,  0.        ,  0.        ,  0.        ,0.        ,  0.        ,  0.        ],
        [ 0.        ,  0.        ,  0.        ,  0.        ,  0.        ,0.        ,  0.        ,  0.        ,  0.        , 0.15135066,0.        ,  0.        ,  0.        ,  0.        ,  0.        ,0.        ,  0.        ,  0.        ],
        [ 0.        ,  0.        ,  0.        ,  0.        ,  0.        ,0.        ,  0.        ,  0.        ,  0.        ,  0.        ,0.3125    ,  0.        ,  0.        ,  0.        ,  0.        ,0.        ,  0.        ,  0.        ],
        [ 0.        ,  0.        ,  0.        ,  0.        ,  0.        ,0.        ,  0.        ,  0.        ,  0.        ,  0.        ,0.        , 0.15135066,  0.        ,  0.        ,  0.        ,0.        ,  0.        ,  0.        ],
        [ 1.        ,  0.        ,  0.        ,  0.        ,  0.        ,0.        ,  0.        ,  0.        ,  0.        ,  0.        ,0.        ,  0.        ,  0.        ,  0.        ,  0.        ,0.        ,  0.        ,  0.        ],
        [ 0.        ,  1.        ,  0.        ,  0.        ,  0.        ,0.        ,  0.        ,  0.        ,  0.        ,  0.        ,0.        ,  0.        ,  0.        ,  0.        ,  0.        ,0.        ,  0.        ,  0.        ],
        [ 0.        ,  0.        ,  1.        ,  0.        ,  0.        ,0.        ,  0.        ,  0.        ,  0.        ,  0.        ,0.        ,  0.        ,  0.        ,  0.        ,  0.        ,0.        ,  0.        ,  0.        ],
        [ 0.        ,  0.        ,  0.        ,  1.        ,  0.        ,0.        ,  0.        ,  0.        ,  0.        ,  0.        ,0.        ,  0.        ,  0.        ,  0.        ,  0.        ,0.        ,  0.        ,  0.        ],
        [ 0.        ,  0.        ,  0.        ,  0.        ,  1.        ,0.        ,  0.        ,  0.        ,  0.        ,  0.        ,0.        ,  0.        ,  0.        ,  0.        ,  0.        ,0.        ,  0.        ,  0.        ],
        [ 0.        ,  0.        ,  0.        ,  0.        ,  0.        ,1.        ,  0.        ,  0.        ,  0.        ,  0.        ,0.        ,  0.        ,  0.        ,  0.        ,  0.        ,0.        ,  0.        ,  0.        ]], dtype=float)
    expected_J = np.array([[    0.        ],
        [    0.        ],
        [    0.        ],
        [    0.        ],
        [    0.        ],
        [    0.        ],
        [    0.        ],
        [    0.        ],
        [    0.        ],
        [    0.        ],
        [    0.        ],
        [    0.        ],
        [ 2400.        ],
        [    0.        ],
        [-1200.        ],
        [-2078.46096908],
        [-1200.        ],
        [ 2078.46096908]], dtype=float)
    assert np.allclose(simulation_state.lin_Y.todense(), expected_Y, rtol=1e-5)
    assert np.allclose(simulation_state.lin_J.todense(), expected_J, rtol=1e-5)

def test_powerflowrunner_swing_and_line_to_resistive_stamp():
    glm_file_path = os.path.join("data", "swing_and_line_to_resistive_stamp", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate, simulation_state = test_runner.run(return_state=True)
    model_has_resistive_loads = any((isinstance(load, ResistiveLoad) for load in simulation_state.loads))
    if not model_has_resistive_loads:
        # Only run the test when resistive loads are implemented
        return

    # Columns: Voltage variables at swing | Voltage variables at load | Current variables
    # Rows: KCLs at swing ; KCLs at load; extra equations for infinite sources at swing bus
    expected_Y = np.array([[1.28442388, 2.66353529, -0.6239444, -0.91412373, -0.22517843, -0.59401059, -1.28442388, -2.66353637, 0.6239444, 0.91412407, 0.22517843, 0.59401072, 1., 0., 0., 0., 0., 0.],
        [-2.66353529, 1.28442388, 0.91412373, -0.6239444, 0.59401059, -0.22517843, 2.66353637, -1.28442388, -0.91412407, 0.6239444, -0.59401072, 0.22517843, 0., 1., 0., 0., 0., 0.],
        [-0.6239444, -0.91412373, 1.43662299, 2.7601376, -0.38234995, -0.72506359, 0.6239444, 0.91412407, -1.43662299, -2.76013873, 0.38234995, 0.72506381, 0., 0., 1., 0., 0., 0.],
        [0.91412373, -0.6239444, -2.7601376, 1.43662299, 0.72506359, -0.38234995, -0.91412407, 0.6239444, 2.76013873, -1.43662299, -0.72506381, 0.38234995, 0., 0., 0., 1., 0., 0.],
        [-0.22517843, -0.59401059, -0.38234995, -0.72506359, 1.15420534, 2.57087262, 0.22517843, 0.59401072, 0.38234995, 0.72506381, -1.15420534, -2.57087365, 0., 0., 0., 0., 1., 0.],
        [0.59401059, -0.22517843, 0.72506359, -0.38234995, -2.57087262, 1.15420534, -0.59401072, 0.22517843, -0.72506381, 0.38234995, 2.57087365, -1.15420534, 0., 0., 0., 0., 0., 1.],
        [-1.28442388, -2.66353637, 0.6239444, 0.91412407, 0.22517843, 0.59401072, 1.28575721, 2.66353529, -0.6239444, -0.91412373, -0.22517843, -0.59401059, 0., 0., 0., 0., 0., 0.],
        [2.66353637, -1.28442388, -0.91412407, 0.6239444, -0.59401072, 0.22517843, -2.66353529, 1.28575721, 0.91412373, -0.6239444, 0.59401059, -0.22517843, 0., 0., 0., 0., 0., 0.],
        [0.6239444, 0.91412407, -1.43662299, -2.76013873, 0.38234995, 0.72506381, -0.6239444, -0.91412373, 1.43795633, 2.7601376, -0.38234995, -0.72506359, 0., 0., 0., 0., 0., 0.],
        [-0.91412407, 0.6239444, 2.76013873, -1.43662299, -0.72506381, 0.38234995, 0.91412373, -0.6239444, -2.7601376, 1.43795633, 0.72506359, -0.38234995, 0., 0., 0., 0., 0., 0.],
        [0.22517843, 0.59401072, 0.38234995, 0.72506381, -1.15420534, -2.57087365, -0.22517843, -0.59401059, -0.38234995, -0.72506359, 1.15553867, 2.57087262, 0., 0., 0., 0., 0., 0.],
        [-0.59401072, 0.22517843, -0.72506381, 0.38234995, 2.57087365, -1.15420534, 0.59401059, -0.22517843, 0.72506359, -0.38234995, -2.57087262, 1.15553867, 0., 0., 0., 0., 0., 0.],
        [1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
        [0., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
        [0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
        [0., 0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
        [0., 0., 0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
        [0., 0., 0., 0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.]], dtype=float)
    expected_J = np.array([
        [    0.        ],
        [    0.        ],
        [    0.        ],
        [    0.        ],
        [    0.        ],
        [    0.        ],
        [    0.        ],
        [    0.        ],
        [    0.        ],
        [    0.        ],
        [    0.        ],
        [    0.        ],
        [ 2400.        ],
        [    0.        ],
        [-1200.        ],
        [-2078.46096908],
        [-1200.        ],
        [ 2078.46096908]], dtype=float)
    Y = (simulation_state.lin_Y + simulation_state.nonlin_Y).todense()
    assert Y.shape == expected_Y.shape
    for i in range(Y.shape[0]):
        assert np.allclose(np.array(Y[i]), expected_Y[i], rtol=1e-4)
    assert np.allclose((simulation_state.lin_J + simulation_state.nonlin_J).todense(), expected_J, rtol=1e-4)
    
def test_powerflowrunner_swing_and_line_to_pq():
    glm_file_path = os.path.join("data", "swing_and_line_to_pq", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate = test_runner.execute()
    
    # Voltages at node 1, voltages at node 2
    expected_v = np.array([
         2400.        ,
            0.        ,
        -1200.        ,
        -2078.46096908,
        -1200.        ,
         2078.46096908,
         2167.809212  ,
         -129.459975  ,
        -1233.209355  ,
        -1873.096501  ,
         -973.394008  ,
         1981.430136], dtype=float)
    assert np.allclose(v_estimate[:12], expected_v[:12], rtol=1e-8, atol=1e-8)

def test_powerflowrunner_swing_and_long_line_to_pq():
    glm_file_path = os.path.join("data", "swing_and_long_line_to_pq", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate = test_runner.execute()
    
    # Voltages at node 1, voltages at node 2
    expected_v = np.array([
        2400.000000,
        0.000000,
        -1200.000000,
        -2078.460969,
        -1200.000000,
        2078.460969,
        1481.787249,
        -285.484828,
        -829.767885,
        -704.110354,
        -129.228599,
        1266.560786], dtype=float)
    assert np.allclose(v_estimate[:12], expected_v[:12], rtol=1e-8, atol=1e-8)

def test_powerflowrunner_swing_and_long_ul_to_pq():
    glm_file_path = os.path.join("data", "swing_and_long_ul_to_pq", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate = test_runner.execute()
    
    # Voltages at node 1, voltages at node 2
    expected_v = np.array([
        2400.000000,
        0.000000,
        -1200.000000,
        -2078.460969,
        -1200.000000,
        2078.460969,
        2159.677659,
        -118.040650,
        -1182.065031,
        -1811.315391,
        -977.612628,
        1929.356042
    ], dtype=float)
    assert np.allclose(v_estimate[:12], expected_v[:12], rtol=1e-8, atol=1e-8)
    
def test_powerflowrunner_swing_and_underground_lines_to_pq():
    glm_file_path = os.path.join("data", "swing_and_underground_lines_to_pq", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate = test_runner.execute()
    
    # Voltages at node 1, voltages at node 2
    expected_v = np.array([
        2400.000000,
        0.000000,
        -1200.000000,
        -2078.460969,
        -1200.000000,
        2078.460969,
        2309.597715,
        -39.346883,
        -1188.874258,
        -1980.496852,
        -1120.723457,
        2019.843736,
        2219.195430,
        -78.693767,
        -1177.748516,
        -1882.532735,
        -1041.446914,
        1961.226502,
        2128.793145,
        -118.040650,
        -1166.622775,
        -1784.568618,
        -962.170371,
        1902.609268,
        2038.390861,
        -157.387534,
        -1155.497033,
        -1686.604501,
        -882.893828,
        1843.992035,
        1947.988576,
        -196.734417,
        -1144.371291,
        -1588.640384,
        -803.617285,
        1785.374801
    ], dtype=float)
    assert np.allclose(v_estimate[:36], expected_v[:36], rtol=1e-7, atol=1e-7)

def test_powerflowrunner_swing_2lines_load():
    glm_file_path = os.path.join("data", "swing_2lines_load", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate = test_runner.execute()
    expected_v = np.array([
        7199.558000,
        0.000000,
        -3599.779000,
        -6235.000000,
        -3599.779000,
        6235.000000,
        7129.179318,
        -41.923931,
        -3612.334859,
        -6168.662777,
        -3526.732960,
        6208.670790,
        7058.800636,
        -83.847862,
        -3624.890719,
        -6102.325553,
        -3453.686920,
        6182.341580,
        6970.827284,
        -136.252776,
        -3640.585543,
        -6019.404024,
        -3362.379369,
        6149.430068
    ], dtype=float)
    assert np.allclose(v_estimate[:24], expected_v[:24], rtol=1e-6, atol=1e-6)

def test_powerflowrunner_ieee_four_bus_resistive():
    glm_file_path = os.path.join("data", "ieee_four_bus_resistive", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate, simulation_state = test_runner.run(return_state=True)
    model_has_resistive_loads = any((isinstance(load, ResistiveLoad) for load in simulation_state.loads))
    if not model_has_resistive_loads:
        # Only run the test when resistive loads are implemented
        return
    expected_v = np.array([
        7199.56,
        0.00,
        -3599.78,
        -6235.00,
        -3599.78,
        6235.00,
        7199.39,
        -0.26,
        -3599.93,
        -6234.80,
        -3599.49,
        6235.04,
        2401.63,
        -0.64,
        -1201.37,
        -2079.57,
        -1200.27,
        2080.21
    ], dtype=float)
    assert np.allclose(v_estimate[:18], expected_v[:18], rtol=1e-1)
    
def test_powerflowrunner_balanced_stepdown_grY_grY():
    glm_file_path = os.path.join("data", "balanced_stepdown_grY_grY", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate = test_runner.execute()
    expected_v = np.array([
        7199.558000,
        0.000000,
        -3599.779000,
        -6235.000000,
        -3599.779000,
        6235.000000,
        7106.422287,
        -42.067600,
        -3606.903032,
        -6161.628479,
        -3520.343705,
        6189.706477,
        2242.742683,
        -144.807987,
        -1251.271366,
        -1892.203540,
        -1002.844346,
        2020.691679,
        1893.763615,
        -302.435080,
        -1277.965079,
        -1617.280802,
        -705.200678,
        1850.977065
    ], dtype=float)
    assert np.allclose(v_estimate[:24], expected_v[:24], rtol=1e-7, atol=1e-7)

def test_powerflowrunner_ieee_four_bus():
    glm_file_path = os.path.join("data", "ieee_four_bus", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate = test_runner.execute()
    expected_v = np.array([
        7199.558000,
        0.000000,
        -3599.779000,
        -6235.000000,
        -3599.779000,
        6235.000000,
        7106.422287,
        -42.067600,
        -3606.903032,
        -6161.628479,
        -3520.343705,
        6189.706477,
        2242.742683,
        -144.807987,
        -1251.271366,
        -1892.203540,
        -1002.844346,
        2020.691679,
        1893.763615,
        -302.435080,
        -1277.965079,
        -1617.280802,
        -705.200678,
        1850.977065
    ], dtype=float)
    assert np.allclose(v_estimate[:24], expected_v[:24], rtol=1e-7, atol=1e-7)
    
def test_powerflowrunner_ieee_four_bus_higher_transformer_impedance():
    glm_file_path = os.path.join("data", "ieee_four_bus_higher_transformer_impedance", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate = test_runner.execute()
    expected_v = np.array([
        7199.558000,
        0.000000,
        -3599.779000,
        -6235.000000,
        -3599.779000,
        6235.000000,
        7080.865336,
        -47.086731,
        -3609.013913,
        -6158.078310,
        -3513.606680,
        6175.443283,
        1992.960195,
        -183.902648,
        -1185.758929,
        -1710.711509,
        -860.294668,
        1848.877763,
        1548.219353,
        -360.336403,
        -1220.362104,
        -1422.486308,
        -537.407399,
        1625.719030
    ], dtype=float)
    assert np.allclose(v_estimate[:24], expected_v[:24], rtol=1e-7, atol=1e-7)
    
def test_powerflowrunner_ieee_four_bus_transformer_shunt_impedance():
    glm_file_path = os.path.join("data", "ieee_four_bus_transformer_shunt_impedance", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate = test_runner.execute()
    expected_v = np.array([
        7199.558000,
        0.000000,
        -3599.779000,
        -6235.000000,
        -3599.779000,
        6235.000000,
        7106.422287,
        -42.067600,
        -3606.903032,
        -6161.628479,
        -3520.343705,
        6189.706477,
        2242.742683,
        -144.807987,
        -1251.271366,
        -1892.203540,
        -1002.844346,
        2020.691679,
        1893.763615,
        -302.435080,
        -1277.965079,
        -1617.280802,
        -705.200678,
        1850.977065
    ], dtype=float)
    assert np.allclose(v_estimate[:24], expected_v[:24], rtol=1e-7, atol=1e-7)

# This is known to not be as close as desired, but it is in agreement with Amrit's code.
def test_powerflowrunner_ieee_four_bus_long_lines():
    glm_file_path = os.path.join("data", "ieee_four_bus_long_lines", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate = test_runner.execute()
    expected_v = np.array([
        7199.558000,
        0.000000,
        -3599.779000,
        -6235.000000,
        -3599.779000,
        6235.000000,
        6668.356234,
        -186.590938,
        -3662.041811,
        -5961.269772,
        -3288.195936,
        5997.013899,
        2042.215385,
        -207.724889,
        -1261.767465,
        -1819.182589,
        -906.780392,
        1942.733479,
        1445.092247,
        -417.471493,
        -1331.757002,
        -1511.482836,
        -556.530319,
        1675.213647
    ], dtype=float)
    assert np.allclose(v_estimate[:24], expected_v[:24], rtol=1e-4, atol=1e-11)

def test_powerflowrunner_connected_transformer():
    glm_file_path = os.path.join("data", "connected_transformer", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate = test_runner.execute()
    expected_v = np.array([
        7200.000000,
        0.000000,
        -3600.000000,
        -6235.382907,
        -3600.000000,
        6235.382907,
        2307.901173,
        -119.219539,
        -1257.197736,
        -1939.091276,
        -1050.703437,
        2058.310815
    ], dtype=float)
    assert np.allclose(v_estimate[:12], expected_v[:12], rtol=1e-8, atol=1e-8)

def test_powerflowrunner_just_two_transformers():
    glm_file_path = os.path.join("data", "just_two_transformers", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate = test_runner.execute()
    expected_v = np.array([
        7200.000000,
        0.000000,
        -3600.000000,
        -6235.382907,
        -3600.000000,
        6235.382907,
        2296.390489,
        -119.219539,
        -1251.442394,
        -1929.122731,
        -1044.948095,
        2048.342270,
        6567.302594,
        -714.744064,
        -3902.637814,
        -5330.078849,
        -2664.664781,
        6044.822913
    ], dtype=float)
    assert np.allclose(v_estimate[:18], expected_v[:18], rtol=1e-8, atol=1e-8)

def test_powerflowrunner_two_transformers():
    glm_file_path = os.path.join("data", "two_transformers", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate = test_runner.execute()
    expected_v = np.array([
        7200.000000,
        0.000000,
        -3600.000000,
        -6235.382907,
        -3600.000000,
        6235.382907,
        2274.258070,
        -123.228147,
        -1241.297185,
        -1912.673556,
        -1029.335407,
        2028.738078,
        2070.748189,
        -244.244753,
        -1300.253660,
        -1701.342391,
        -797.465641,
        1907.264129,
        5824.574052,
        -1101.535349,
        -4018.543039,
        -4597.977395,
        -1876.011796,
        5563.162167
    ], dtype=float)
    assert np.allclose(v_estimate[:24], expected_v[:24], rtol=1e-8, atol=1e-8)

def test_powerflowrunner_three_transformers_with_lines():
    glm_file_path = os.path.join("data", "three_transformers_with_lines", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate = test_runner.execute()
    expected_v = np.array([
        7200.000000,
        0.000000,
        -3600.000000,
        -6235.382907,
        -3600.000000,
        6235.382907,
        2239.272578,
        -124.254013,
        -1227.692967,
        -1890.221059,
        -1006.386752,
        1994.867780,
        1989.662450,
        -248.037406,
        -1272.730345,
        -1660.554932,
        -750.896079,
        1808.958923,
        5476.639373,
        -1115.979326,
        -3895.259304,
        -4408.409548,
        -1667.624257,
        5166.953388,
        5393.369274,
        -1157.273545,
        -3910.283802,
        -4331.792781,
        -1582.392405,
        5104.934074,
        1636.579409,
        -510.321210,
        -1331.203843,
        -1255.182172,
        -333.311564,
        1617.749324
    ], dtype=float)
    assert np.allclose(v_estimate[:36], expected_v[:36], rtol=1e-8, atol=1e-8)

def test_powerflowrunner_three_transformers():
    glm_file_path = os.path.join("data", "three_transformers", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate = test_runner.execute()
    expected_v = np.array([
        7200.000000,
        0.000000,
        -3600.000000,
        -6235.382907,
        -3600.000000,
        6235.382907,
        2401.077177,
        -1.192195,
        -1201.571060,
        -2078.797734,
        -1199.506117,
        2079.989929,
        4801.590227,
        -3.178012,
        -2403.547353,
        -4156.710109,
        -2398.042875,
        4159.888121,
        1600.543435,
        -2.847047,
        -802.737333,
        -1384.687751,
        -797.806103,
        1387.534798
    ], dtype=float)
    assert np.allclose(v_estimate[:24], expected_v[:24], rtol=1e-8, atol=1e-8)
    
def test_powerflowrunner_kersting_example_4_1():
    glm_file_path = os.path.join("data", "kersting_example_4_1", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-13})
    v_estimate, simulation_state = test_runner.run(return_state=True)
    expected_v = np.array([
        7199.558000,
        0.000000,
        -3599.779000,
        -6235.000000,
        -3599.779000,
        6235.000000,
        7130.382343,
        -38.873965,
        -3613.920169,
        -6166.804123,
        -3528.624337,
        6213.353304
    ])
    assert np.allclose(v_estimate[:12], expected_v[:12], rtol=1e-7, atol=1e-7)

def test_powerflowrunner_kersting_example_4_2():
    glm_file_path = os.path.join("data", "kersting_example_4_2", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-13})
    v_estimate, simulation_state = test_runner.run(return_state=True)
    expected_v = np.array([
        7199.558000,
        0.000000,
        -3599.779000,
        -6235.000000,
        -3599.779000,
        6235.000000,
        7129.241844,
        -13.956357,
        -3580.596805,
        -6174.425925,
        -3547.070648,
        6190.201114
    ])
    assert np.allclose(v_estimate[:12], expected_v[:12], rtol=1e-7, atol=1e-7)

def test_powerflowrunner_underground_lines_and_transformers():
    glm_file_path = os.path.join("data", "underground_lines_and_transformers", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate, simulation_state = test_runner.run(return_state=True)
    expected_v = np.array([
        2400.000000,
        0.000000,
        -1200.000000,
        -2078.460969,
        -1200.000000,
        2078.460969,
        2174.081956,
        -60.902588,
        -1139.784166,
        -1852.358910,
        -1034.297790,
        1913.261497,
        6032.255040,
        -596.518325,
        -3532.727543,
        -4925.826944,
        -2499.527497,
        5522.345269,
        5956.888635,
        -616.835467,
        -3512.639502,
        -4850.399152,
        -2444.249133,
        5467.234619,
        1825.504066,
        -343.873016,
        -1210.554800,
        -1408.996388,
        -614.949266,
        1752.869404,
        1599.586022,
        -404.775603,
        -1150.338966,
        -1182.894329,
        -449.247056,
        1587.669932
    ], dtype=float)
    assert np.allclose(v_estimate[:36], expected_v[:36], rtol=1e-6, atol=1e-6)

def test_powerflowrunner_ieee_four_bus_underground_spaced():
    glm_file_path = os.path.join("data", "ieee_four_bus_underground_spaced", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate, simulation_state = test_runner.run(return_state=True)
    expected_v = np.array([
        7199.558000,
        0.000000,
        -3599.779000,
        -6235.000000,
        -3599.779000,
        6235.000000,
        7172.955032,
        -12.280743,
        -3597.112950,
        -6205.820782,
        -3575.842080,
        6218.101524,
        2290.680068,
        -126.733830,
        -1255.094749,
        -1920.420171,
        -1035.585314,
        2047.154004,
        2190.998873,
        -172.749713,
        -1245.105073,
        -1811.085782,
        -945.893791,
        1983.835497
    ], dtype=float)
    assert np.allclose(v_estimate[:18], expected_v[:18], rtol=1e-6, atol=1e-6)

def test_powerflowrunner_ieee_four_bus_underground():
    glm_file_path = os.path.join("data", "ieee_four_bus_underground", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate, simulation_state = test_runner.run(return_state=True)
    expected_v = np.array([
        7199.558000,
        0.000000,
        -3599.779000,
        -6235.000000,
        -3599.779000,
        6235.000000,
        7172.955032,
        -12.280743,
        -3597.112950,
        -6205.820782,
        -3575.842080,
        6218.101524,
        2290.680068,
        -126.733830,
        -1255.094749,
        -1920.420171,
        -1035.585314,
        2047.154005,
        2190.998873,
        -172.749713,
        -1245.105073,
        -1811.085781,
        -945.893791,
        1983.835498
    ], dtype=float)
    assert np.allclose(v_estimate[:24], expected_v[:24], rtol=1e-7, atol=1e-7)
    
def test_powerflowrunner_ieee_four_bus_underground_step_up():
    glm_file_path = os.path.join("data", "ieee_four_bus_underground_step_up", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate, simulation_state = test_runner.run(return_state=True)
    expected_v = np.array([
        2401.777000,
        0.000000,
        -1200.889000,
        -2080.000000,
        -1200.889000,
        2080.000000,
        2309.151299,
        -49.139274,
        -1197.131990,
        -1975.214170,
        -1112.020293,
        2024.353446,
        6921.118981,
        -148.333012,
        -3589.021088,
        -5919.698718,
        -3332.100841,
        6068.031735,
        6896.398987,
        -161.447327,
        -3588.018415,
        -5891.733422,
        -3308.383515,
        6053.180755
    ], dtype=float)
    assert np.allclose(v_estimate[:24], expected_v[:24], rtol=1e-7, atol=1e-7)

def test_powerflowrunner_ieee_four_bus_underground_long_lines():
    glm_file_path = os.path.join("data", "ieee_four_bus_underground_long_lines", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate, simulation_state = test_runner.run(return_state=True)
    expected_v = np.array([
        7199.558000,
        0.000000,
        -3599.779000,
        -6235.000000,
        -3599.779000,
        6235.000000,
        7089.869661,
        -48.954675,
        -3587.330820,
        -6115.529773,
        -3502.538836,
        6164.484448,
        2258.832889,
        -140.676188,
        -1251.245595,
        -1885.868525,
        -1007.587288,
        2026.544717,
        2135.532386,
        -195.706067,
        -1237.252614,
        -1751.572216,
        -898.279760,
        1947.278286
    ], dtype=float)
    assert np.allclose(v_estimate[:24], expected_v[:24], rtol=1e-6, atol=1e-6)

def test_powerflowrunner_ieee_four_bus_switch():
    glm_file_path = os.path.join("data", "ieee_four_bus_switch", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate = test_runner.execute()
    expected_v = np.array([
        7199.558000,
        0.000000,
        -3599.779000,
        -6235.000000,
        -3599.779000,
        6235.000000,
        7126.409318,
        -39.482195,
        -3609.893079,
        -6166.230282,
        -3526.071228,
        6205.759921,
        2281.499622,
        -133.094021,
        -1259.992399,
        -1914.461013,
        -1024.788331,
        2047.035826,
        2281.482751,
        -133.034484,
        -1259.932576,
        -1914.476141,
        -1024.831436,
        2046.991573
    ], dtype=float)
    assert np.allclose(v_estimate[:24], expected_v[:24], rtol=1e-7, atol=1e-7)

def test_powerflowrunner_ieee_four_bus_fuse():
    glm_file_path = os.path.join("data", "ieee_four_bus_fuse", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate = test_runner.execute()
    expected_v = np.array([
        7199.558000,
        0.000000,
        -3599.779000,
        -6235.000000,
        -3599.779000,
        6235.000000,
        7126.409318,
        -39.482195,
        -3609.893079,
        -6166.230282,
        -3526.071228,
        6205.759921,
        2281.499622,
        -133.094021,
        -1259.992399,
        -1914.461013,
        -1024.788331,
        2047.035826,
        2281.482751,
        -133.034484,
        -1259.932576,
        -1914.476141,
        -1024.831436,
        2046.991573
    ], dtype=float)
    assert np.allclose(v_estimate[:24], expected_v[:24], rtol=1e-7, atol=1e-7)

def test_powerflowrunner_ieee_four_bus_cap():
    glm_file_path = os.path.join("data", "ieee_four_bus_cap", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate = test_runner.execute()
    expected_v = np.array([
        7199.558000,
        0.000000,
        -3599.779000,
        -6235.000000,
        -3599.779000,
        6235.000000,
        7106.422287,
        -42.067600,
        -3606.903032,
        -6161.628479,
        -3520.343705,
        6189.706477,
        2242.742683,
        -144.807987,
        -1251.271366,
        -1892.203540,
        -1002.844346,
        2020.691679,
        1893.763615,
        -302.435080,
        -1277.965079,
        -1617.280802,
        -705.200678,
        1850.977065
    ], dtype=float)
    assert np.allclose(v_estimate[:24], expected_v[:24], rtol=1e-7, atol=1e-7)

def test_powerflowrunner_ieee_four_bus_unbalanced_pq_load():
    glm_file_path = os.path.join("data", "ieee_four_bus_unbalanced_pq_load", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate = test_runner.execute()
    expected_v = np.array([
        7199.558000,
        0.000000,
        -3599.779000,
        -6235.000000,
        -3599.779000,
        6235.000000,
        7173.191420,
        -11.570974,
        -3601.439533,
        -6210.615924,
        -3574.944688,
        6222.889390,
        2356.580806,
        -42.759078,
        -1217.089634,
        -2020.616179,
        -1140.578125,
        2063.713774,
        2257.785357,
        -86.115461,
        -1223.311644,
        -1929.249164,
        -1047.524077,
        2018.335376
    ], dtype=float)
    assert np.allclose(v_estimate[:24], expected_v[:24], rtol=1e-7, atol=1e-7)

def test_powerflowrunner_load_within_meter():
    glm_file_path = os.path.join("data", "load_within_meter", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate = test_runner.execute()
    expected_v = np.array([
        7199.558000,
        0.000000,
        -3599.779000,
        -6235.000000,
        -3599.779000,
        6235.000000,
        7106.422287,
        -42.067600,
        -3606.903032,
        -6161.628479,
        -3520.343705,
        6189.706477,
        2242.742683,
        -144.807987,
        -1251.271366,
        -1892.203540,
        -1002.844346,
        2020.691679,
        1893.763615,
        -302.435080,
        -1277.965079,
        -1617.280802,
        -705.200678,
        1850.977065,
        1893.763615,
        -302.435080,
        -1277.965079,
        -1617.280802,
        -705.200678,
        1850.977065
    ], dtype=float)
    assert np.allclose(v_estimate[:24], expected_v[:24], rtol=1e-7, atol=1e-7)

def test_powerflowrunner_transformer_to_meter():
    glm_file_path = os.path.join("data", "transformer_to_meter", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate = test_runner.execute()
    expected_v = np.array([
        7199.558000,
        0.000000,
        -3599.779000,
        -6235.000000,
        -3599.779000,
        6235.000000,
        7106.422287,
        -42.067600,
        -3606.903032,
        -6161.628479,
        -3520.343705,
        6189.706477,
        2242.742683,
        -144.807987,
        -1251.271366,
        -1892.203540,
        -1002.844346,
        2020.691679,
        1893.763615,
        -302.435080,
        -1277.965079,
        -1617.280802,
        -705.200678,
        1850.977065
    ], dtype=float)
    assert np.allclose(v_estimate[:24], expected_v[:24], rtol=1e-7, atol=1e-7)

def test_powerflowrunner_regulator_node_load():
    glm_file_path = os.path.join("data", "regulator_node_load", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate, simulation_state = test_runner.run(return_state=True)
    expected_v = np.array([
        2401.777100,
        0.000000,
        -1200.888600,
        -2080.000000,
        -1200.888600,
        2080.000000,
        2551.887725,
        0.000261,
        -1260.931282,
        -2183.998989,
        -1283.449719,
        2222.996472,
        2555.056809,
        0.395674,
        -1258.339662,
        -2178.549073,
        -1270.796020,
        2220.907824,
        2555.849080,
        0.494527,
        -1257.691757,
        -2177.186593,
        -1267.632595,
        2220.385662
    ], dtype=float)
    assert np.allclose(v_estimate[:24], expected_v[:24], atol=1e-6, rtol=1e-6)

def test_powerflowrunner_regulatorB_node_load():
    glm_file_path = os.path.join("data", "regulatorB_node_load", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate, simulation_state = test_runner.run(return_state=True)
    expected_v = np.array([
        2401.777100,
        0.000000,
        -1200.888600,
        -2080.000000,
        -1200.888600,
        2080.000000,
        2561.895122,
        0.000260,
        -1264.091439,
        -2189.472536,
        -1289.544569,
        2233.553066,
        2534.299786,
        18.840223,
        -1133.952479,
        -2103.385857,
        -1258.435472,
        1954.540239,
        2527.400952,
        23.550213,
        -1101.417739,
        -2081.864187,
        -1250.658198,
        1884.787032,
    ], dtype=float)
    assert np.allclose(v_estimate[:24], expected_v[:24], atol=1e-6, rtol=1e-6)

def test_powerflowrunner_ieee_thirteen_bus_pq_top_right():
    glm_file_path = os.path.join("data", "ieee_thirteen_bus_pq_top_right", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate, simulation_state = test_runner.run(return_state=True)
    expected_v = np.array([
        2530.112678,
        -13.609827,
        -1263.866463,
        -2162.289985,
        -1256.518525,
        2206.969617,
        2551.881331,
        0.004815,
        -1260.925636,
        -2183.996674,
        -1283.450527,
        2222.990498,
        2537.135365,
        -11.050963,
        -1264.496605,
        -2167.288150,
        -1259.653691,
        2212.053750,
        2401.777100,
        0.000000,
        -1200.888600,
        -2080.000000,
        -1200.888600,
        2080.000000,
        285.493565,
        -4.676781,
        -145.207385,
        -243.973164,
        -140.577891,
        251.394710,
        2537.933201,
        -10.954905,
        -1263.837409,
        -2165.924034,
        -1256.473486,
        2211.520676
    ], dtype=float)
    assert np.allclose(v_estimate[:36], expected_v[:36], rtol=1e-7, atol=1e-7)

def test_powerflowrunner_two_regulators():
    glm_file_path = os.path.join("data", "two_regulators", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate, simulation_state = test_runner.run(return_state=True)
    expected_v = np.array([
        2401.777100,
        0.000000,
        -1200.888600,
        -2080.000000,
        -1200.888600,
        2080.000000,
        2401.776629,
        0.000277,
        -1200.886766,
        -2079.998938,
        -1200.888628,
        2079.996230,
        2405.188993,
        0.359629,
        -1198.079747,
        -2074.324519,
        -1187.354883,
        2077.715301,
        2405.188522,
        0.359907,
        -1198.077913,
        -2074.323457,
        -1187.354911,
        2077.711531
    ], dtype=float)
    assert np.allclose(v_estimate[:24], expected_v[:24], rtol=1e-6, atol=1e-6)

def test_powerflowrunner_regulator_lower_impedance_transformer_load():
    glm_file_path = os.path.join("data", "regulator_lower_impedance_transformer_load", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate, simulation_state = test_runner.run(return_state=True)
    # Lower series impedance of the xfmr
    expected_v = np.array([
        2401.777100,
        0.000000,
        -1200.888600,
        -2080.000000,
        -1200.888600,
        2080.000000,
        2401.776628,
        0.000278,
        -1200.886770,
        -2079.998941,
        -1200.888611,
        2079.996243,
        92.448879,
        -0.001424,
        -46.227489,
        -80.057274,
        -46.212328,
        80.061723
    ])

    assert np.allclose(v_estimate[:18], expected_v[:18], rtol=1e-6, atol=1e-6)

def test_powerflowrunner_regulator_higher_impedance_transformer_load():
    glm_file_path = os.path.join("data", "regulator_higher_impedance_transformer_load", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate, simulation_state = test_runner.run(return_state=True)
    # Higher impedance
    expected_v = np.array([
        2401.777100,
        0.000000,
        -1200.888600,
        -2080.000000,
        -1200.888600,
        2080.000000,
        2401.776627,
        0.000281,
        -1200.886714,
        -2079.998962,
        -1200.888764,
        2079.996118,
        92.018848,
        -0.509496,
        -47.090983,
        -77.598759,
        -41.610269,
        79.093291
    ])

    assert np.allclose(v_estimate[:18], expected_v[:18], rtol=1e-6, atol=1e-6)

def test_powerflowrunner_regulator_ol():
    glm_file_path = os.path.join("data", "regulator_ol", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate = test_runner.execute()
    expected_v = np.array([
        2401.777100,
        0.000000,
        -1200.888600,
        -2080.000000,
        -1200.888600,
        2080.000000,
        2401.776629,
        0.000277,
        -1200.886766,
        -2079.998938,
        -1200.888628,
        2079.996230,
        2405.188986,
        0.359626,
        -1198.079751,
        -2074.324526,
        -1187.354905,
        2077.715294
    ], dtype=float)
    assert np.allclose(v_estimate[:18], expected_v[:18], rtol=1e-6, atol=1e-6)

def test_powerflowrunner_regulator_overhead_line_transformer_load():
    glm_file_path = os.path.join("data", "regulator_overhead_line_transformer_load", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate, simulation_state = test_runner.run(return_state=True)
    # Overhead
    expected_v = np.array([
        2401.777100,
        0.000000,
        -1200.888600,
        -2080.000000,
        -1200.888600,
        2080.000000,
        2401.776629,
        0.000277,
        -1200.886765,
        -2079.998938,
        -1200.888628,
        2079.996230,
        2405.189448,
        0.359038,
        -1198.079083,
        -2074.324765,
        -1187.353933,
        2077.713449,
        92.580248,
        0.012388,
        -46.119420,
        -79.838843,
        -45.691310,
        79.973788
    ])

    assert np.allclose(v_estimate[:24], expected_v[:24], rtol=1e-6, atol=1e-6)
    
def test_powerflowrunner_regulator_overhead_lines():
    glm_file_path = os.path.join("data", "regulator_overhead_lines", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate, simulation_state = test_runner.run(return_state=True)
    expected_v = np.array([
        2401.777100,
        0.000000,
        -1200.888600,
        -2080.000000,
        -1200.888600,
        2080.000000,
        2401.776631,
        0.000275,
        -1200.886745,
        -2079.998928,
        -1200.888697,
        2079.996174,
        2405.241199,
        0.266838,
        -1198.047236,
        -2074.361348,
        -1187.221368,
        2077.409612,
        2408.705766,
        0.533400,
        -1195.207726,
        -2068.723768,
        -1173.554039,
        2074.823051,
        2412.170333,
        0.799963,
        -1192.368216,
        -2063.086188,
        -1159.886710,
        2072.236489,
        2415.634900,
        1.066525,
        -1189.528707,
        -2057.448608,
        -1146.219381,
        2069.649928,
        2419.099467,
        1.333088,
        -1186.689197,
        -2051.811028,
        -1132.552052,
        2067.063367
    ])

    assert np.allclose(v_estimate[:42], expected_v[:42], rtol=1e-6, atol=1e-6)
    
def test_powerflowrunner_gc_12_47_1_only_overhead_lines():
    glm_file_path = os.path.join("data", "gc_12_47_1_only_overhead_lines", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate, simulation_state = test_runner.run(return_state=True)
    expected_v_file_path = os.path.join("data", "gc_12_47_1_only_overhead_lines", "expected_output.txt")
    expected_v_full_file_path = os.path.join(CURR_DIR, expected_v_file_path)
    expected_v = np.loadtxt(expected_v_full_file_path)
    assert np.allclose(v_estimate[:186], expected_v[:186], rtol=1e-6, atol=1e-6)

def test_powerflowrunner_regulator_overhead_line_underground_line():
    glm_file_path = os.path.join("data", "regulator_overhead_line_underground_line", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate, simulation_state = test_runner.run(return_state=True)
    expected_v = np.array([
        2401.777100,
        0.000000,
        -1200.888600,
        -2080.000000,
        -1200.888600,
        2080.000000,
        2401.776629,
        0.000277,
        -1200.886764,
        -2079.998938,
        -1200.888630,
        2079.996224,
        2405.196916,
        0.355429,
        -1198.071941,
        -2074.325479,
        -1187.334063,
        2077.700919,
        2404.838447,
        -0.379325,
        -1197.778668,
        -2072.800374,
        -1184.239291,
        2075.079133
    ])

    assert np.allclose(v_estimate[:24], expected_v[:24], rtol=1e-4, atol=1e-1)

def test_powerflowrunner_regulator_ul():
    glm_file_path = os.path.join("data", "regulator_ul", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate = test_runner.execute()
    expected_v = np.array([
        2401.777100,
        0.000000,
        -1200.888600,
        -2080.000000,
        -1200.888600,
        2080.000000,
        2401.776628,
        0.000278,
        -1200.886769,
        -2079.998941,
        -1200.888613,
        2079.996238,
        2401.420077,
        -0.733144,
        -1200.591660,
        -2078.477605,
        -1197.792792,
        2077.396864
    ], dtype=float)
    assert np.allclose(v_estimate[:18], expected_v[:18], rtol=1e-4, atol=1e-1)

def test_powerflowrunner_regulator_ul_xfmr():
    glm_file_path = os.path.join("data", "regulator_ul_xfmr", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate = test_runner.execute()
    expected_v = np.array([
        2401.777100,
        0.000000,
        -1200.888600,
        -2080.000000,
        -1200.888600,
        2080.000000,
        2401.776628,
        0.000278,
        -1200.886769,
        -2079.998941,
        -1200.888613,
        2079.996238,
        2401.420077,
        -0.733145,
        -1200.591660,
        -2078.477605,
        -1197.792792,
        2077.396864,
        62386.891191,
        -19.047917,
        -31190.373322,
        -53997.109269,
        -31117.645823,
        53969.037055
    ], dtype=float)
    assert np.allclose(v_estimate[:24], expected_v[:24], rtol=1e-4, atol=1e-1)

def test_powerflowrunner_regulator_ul_xfmr_ul():
    glm_file_path = os.path.join("data", "regulator_ul_xfmr_ul", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate = test_runner.execute()
    expected_v = np.array([
        2401.777100,
        0.000000,
        -1200.888600,
        -2080.000000,
        -1200.888600,
        2080.000000,
        2401.776628,
        0.000278,
        -1200.886769,
        -2079.998941,
        -1200.888613,
        2079.996238,
        2401.420076,
        -0.733146,
        -1200.591660,
        -2078.477605,
        -1197.792787,
        2077.396855,
        62386.891169,
        -19.047950,
        -31190.373318,
        -53997.109260,
        -31117.645705,
        53969.036824,
        62386.877444,
        -19.076182,
        -31190.361959,
        -53997.050700,
        -31117.526539,
        53968.936767
    ], dtype=float)
    assert np.allclose(v_estimate[:30], expected_v[:30], rtol=1e-4, atol=1e-1)

def test_powerflowrunner_gc_12_47_1_pared_down_no_regulator():
    glm_file_path = os.path.join("data", "gc_12_47_1_pared_down_no_regulator", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate, simulation_state = test_runner.run(return_state=True)
    expected_v = np.array([
        276.922391,
        -0.056781,
        -138.509431,
        -239.773729,
        -138.408503,
        239.834182,
        7199.434875,
        -0.639372,
        -3600.279635,
        -6234.178443,
        -3599.154835,
        6234.832172,
        7194.778063,
        -0.835743,
        -3598.079946,
        -6229.943215,
        -3596.582731,
        6230.860004,
        7197.357018,
        -1.554187,
        -3600.027471,
        -6231.876784,
        -3597.289563,
        6233.476837,
        7200.000000,
        0.000000,
        -3600.000000,
        -6235.000000,
        -3600.000000,
        6235.000000
    ])
    assert np.allclose(v_estimate[:30], expected_v[:30], rtol=1e-4, atol=1e-2)

def test_powerflowrunner_gc_12_47_1_somewhat_pared_down_no_regulator():
    glm_file_path = os.path.join("data", "gc_12_47_1_somewhat_pared_down_no_regulator", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate, simulation_state = test_runner.run(return_state=True)
    expected_v = np.array([
        276.591613,
        -0.206985,
        -138.473418,
        -239.405045,
        -138.107659,
        239.620803,
        7199.433852,
        -0.639829,
        -3600.279520,
        -6234.177286,
        -3599.153905,
        6234.831498,
        7197.162323,
        -1.638448,
        -3600.002513,
        -6231.661794,
        -3597.116047,
        6233.349020,
        7195.540530,
        -2.351428,
        -3599.804740,
        -6229.865819,
        -3595.661087,
        6232.290583,
        7194.604545,
        -2.762910,
        -3599.690600,
        -6228.829308,
        -3594.821386,
        6231.679727,
        7194.170064,
        -3.083036,
        -3599.754297,
        -6228.284041,
        -3594.321135,
        6231.463643,
        7192.282064,
        -3.913047,
        -3599.524061,
        -6226.193268,
        -3592.627352,
        6230.231470,
        7190.848235,
        -4.543393,
        -3599.349210,
        -6224.605445,
        -3591.341021,
        6229.295704,
        7186.185765,
        -4.737481,
        -3597.144474,
        -6220.366289,
        -3588.767997,
        6225.317275,
        7188.767401,
        -5.458178,
        -3599.095458,
        -6222.301128,
        -3589.474240,
        6227.937680,
        7198.851553,
        -0.895822,
        -3600.208510,
        -6233.532448,
        -3598.631507,
        6234.451470,
        7200.000000,
        0.000000,
        -3600.000000,
        -6235.000000,
        -3600.000000,
        6235.000000
    ])
    assert np.allclose(v_estimate[:72], expected_v[:72], rtol=1e-4, atol=1e-1)

def test_powerflowrunner_gc_12_47_1_no_reg():
    glm_file_path = os.path.join("data", "gc_12_47_1_no_reg", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate, simulation_state = test_runner.run(return_state=True)
    expected_v = np.array([
        275.779525,
        -0.554492,
        -138.366001,
        -238.510494,
        -137.387453,
        239.085928,
        275.779918,
        -0.554602,
        -138.366298,
        -238.510788,
        -137.387560,
        239.086326,
        275.777913,
        -0.563516,
        -138.373137,
        -238.504571,
        -137.378795,
        239.089066,
        7199.995281,
        0.019758,
        -3599.980169,
        -6235.005799,
        -3600.014838,
        6234.985835,
        7193.156842,
        -2.976276,
        -3599.136797,
        -6227.437801,
        -3593.888810,
        6230.517066,
        7188.274433,
        -5.115340,
        -3598.534659,
        -6222.034512,
        -3589.515038,
        6227.326519,
        7185.456649,
        -6.349858,
        -3598.187147,
        -6218.916113,
        -3586.990803,
        6225.485159,
        7184.148142,
        -7.311401,
        -3598.376682,
        -6217.275149,
        -3585.486418,
        6224.833009,
        7178.464317,
        -9.801579,
        -3597.675707,
        -6210.984945,
        -3580.394720,
        6221.118754,
        7174.147774,
        -11.692728,
        -3597.143355,
        -6206.207892,
        -3576.527863,
        6218.297988,
        7165.049014,
        -13.998702,
        -3594.539510,
        -6196.975556,
        -3569.835024,
        6211.504822,
        7165.090874,
        -13.764240,
        -3594.354102,
        -6197.129409,
        -3570.059931,
        6211.423270,
        7165.101070,
        -13.767099,
        -3594.361820,
        -6197.137044,
        -3570.062709,
        6211.433626,
        7167.327956,
        -14.644218,
        -3596.270190,
        -6198.678875,
        -3570.450300,
        6213.822914,
        7167.327956,
        -14.644218,
        -3596.270190,
        -6198.678875,
        -3570.450300,
        6213.822914,
        7167.326384,
        -14.637632,
        -3596.263580,
        -6198.680808,
        -3570.455246,
        6213.818192,
        7167.382651,
        -14.620257,
        -3596.276937,
        -6198.739404,
        -3570.499295,
        6213.858656,
        7167.384224,
        -14.626843,
        -3596.283547,
        -6198.737471,
        -3570.494349,
        6213.863378,
        7167.689354,
        -14.493168,
        -3596.321185,
        -6199.075150,
        -3570.767685,
        6214.062778,
        7167.690927,
        -14.499754,
        -3596.327796,
        -6199.073217,
        -3570.762739,
        6214.067500,
        7167.689354,
        -14.493168,
        -3596.321185,
        -6199.075150,
        -3570.767685,
        6214.062778,
        7167.636698,
        -14.516236,
        -3596.314690,
        -6199.016878,
        -3570.720516,
        6214.028368,
        7167.638271,
        -14.522823,
        -3596.321300,
        -6199.014944,
        -3570.715570,
        6214.033089,
        7167.878701,
        -14.417488,
        -3596.350953,
        -6199.281024,
        -3570.930951,
        6214.190206,
        7167.883419,
        -14.437246,
        -3596.370784,
        -6199.275224,
        -3570.916113,
        6214.204370,
        7167.327956,
        -14.644218,
        -3596.270190,
        -6198.678875,
        -3570.450300,
        6213.822914,
        7167.327956,
        -14.644218,
        -3596.270190,
        -6198.678875,
        -3570.450300,
        6213.822914,
        7185.456649,
        -6.349858,
        -3598.187147,
        -6218.916113,
        -3586.990803,
        6225.485159,
        7167.327956,
        -14.644218,
        -3596.270190,
        -6198.678875,
        -3570.450300,
        6213.822914,
        7198.242271,
        -0.748265,
        -3599.763974,
        -6233.065768,
        -3598.444451,
        6233.840281,
        7200.000000,
        0.000000,
        -3600.000000,
        -6235.000000,
        -3600.000000,
        6235.000000
    ])
    assert np.allclose(v_estimate[:186], expected_v[:186], rtol=1e-4, atol=1e-1)
    
def test_powerflowrunner_gc_12_47_1_xfmr_as_reg():
    glm_file_path = os.path.join("data", "gc_12_47_1_xfmr_as_reg", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate, simulation_state = test_runner.run(return_state=True)
    expected_v = np.array([
        275.713531,
        -0.629036,
        -138.398535,
        -238.414605,
        -137.288859,
        239.066251,
        275.713923,
        -0.629146,
        -138.398832,
        -238.414899,
        -137.288966,
        239.066650,
        275.711916,
        -0.638062,
        -138.405671,
        -238.408679,
        -137.280199,
        239.069387,
        7198.293176,
        -1.922965,
        -3600.837380,
        -6232.522525,
        -3597.454330,
        6234.488840,
        7191.452292,
        -4.917870,
        -3599.991710,
        -6224.952940,
        -3591.328058,
        6230.017308,
        7186.568139,
        -7.056128,
        -3599.387931,
        -6219.548518,
        -3586.954112,
        6226.824789,
        7183.749347,
        -8.290180,
        -3599.039472,
        -6216.429464,
        -3584.429778,
        6224.982291,
        7182.440268,
        -9.251598,
        -3599.228599,
        -6214.788051,
        -3582.925211,
        6224.329571,
        7176.754411,
        -11.740837,
        -3598.525714,
        -6208.496528,
        -3577.833309,
        6220.613020,
        7172.436326,
        -13.631273,
        -3597.991912,
        -6203.718473,
        -3573.966300,
        6217.790511,
        7163.334771,
        -15.935343,
        -3595.384880,
        -6194.484638,
        -3567.273717,
        6210.993867,
        7163.376705,
        -15.700836,
        -3595.199471,
        -6194.638579,
        -3567.498700,
        6210.912356,
        7163.386902,
        -15.703699,
        -3595.207192,
        -6194.646213,
        -3567.501476,
        6210.922716,
        7165.614080,
        -16.581628,
        -3597.116452,
        -6196.187886,
        -3567.888506,
        6213.312686,
        7165.614080,
        -16.581628,
        -3597.116452,
        -6196.187886,
        -3567.888506,
        6213.312686,
        7165.612509,
        -16.575040,
        -3597.109841,
        -6196.189822,
        -3567.893455,
        6213.307965,
        7165.668795,
        -16.557676,
        -3597.123217,
        -6196.248428,
        -3567.937503,
        6213.348451,
        7165.670366,
        -16.564264,
        -3597.129829,
        -6196.246493,
        -3567.932555,
        6213.353172,
        7165.975606,
        -16.430639,
        -3597.167569,
        -6196.584243,
        -3568.205902,
        6213.552696,
        7165.977177,
        -16.437228,
        -3597.174181,
        -6196.582307,
        -3568.200953,
        6213.557417,
        7165.975606,
        -16.430639,
        -3597.167569,
        -6196.584243,
        -3568.205902,
        6213.552696,
        7165.922931,
        -16.453699,
        -3597.161056,
        -6196.525958,
        -3568.158731,
        6213.518264,
        7165.924502,
        -16.460287,
        -3597.167668,
        -6196.524022,
        -3568.153782,
        6213.522985,
        7166.165018,
        -16.354992,
        -3597.197402,
        -6196.790157,
        -3568.369172,
        6213.680199,
        7166.169732,
        -16.374756,
        -3597.217236,
        -6196.784351,
        -3568.354326,
        6213.694363,
        7165.614080,
        -16.581628,
        -3597.116452,
        -6196.187886,
        -3567.888506,
        6213.312686,
        7165.614080,
        -16.581628,
        -3597.116452,
        -6196.187886,
        -3567.888506,
        6213.312686,
        7183.749347,
        -8.290180,
        -3599.039472,
        -6216.429464,
        -3584.429778,
        6224.982291,
        7165.614080,
        -16.581628,
        -3597.116452,
        -6196.187886,
        -3567.888506,
        6213.312686,
        7196.539538,
        -2.690699,
        -3600.620596,
        -6230.582087,
        -3595.883881,
        6233.342578,
        7200.000000,
        0.000000,
        -3600.000000,
        -6235.000000,
        -3600.000000,
        6235.000000
    ])
    assert np.allclose(v_estimate[:186], expected_v[:186], rtol=1e-4, atol=1e-1)

def test_powerflowrunner_gc_12_47_1_further_simplified():
    glm_file_path = os.path.join("data", "gc_12_47_1_further_simplified", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate, simulation_state = test_runner.run(return_state=True)
    expected_v = np.array([
        276.943849,
        -0.031994,
        -138.498363,
        -239.805181,
        -138.441039,
        239.840296,
        7199.991866,
        0.004977,
        -3599.991502,
        -6234.995326,
        -3600.000205,
        6234.990373,
        7195.335431,
        -0.191794,
        -3597.792374,
        -6230.760228,
        -3597.427941,
        6231.018749,
        7197.914252,
        -0.909952,
        -3599.739569,
        -6232.693824,
        -3598.134955,
        6233.635314,
        7200.000000,
        0.000000,
        -3600.000000,
        -6235.000000,
        -3600.000000,
        6235.000000
    ])
    assert np.allclose(v_estimate[:30], expected_v[:30], rtol=1e-4, atol=1e-1)

def test_powerflowrunner_gc_12_47_1_simplified():
    glm_file_path = os.path.join("data", "gc_12_47_1_simplified", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate, simulation_state = test_runner.run(return_state=True)
    expected_v = np.array([
        276.941328,
        -0.032544,
        -138.497564,
        -239.802671,
        -138.439264,
        239.838368,
        7199.991866,
        0.004977,
        -3599.991502,
        -6234.995326,
        -3600.000205,
        6234.990373,
        7195.269954,
        -0.206101,
        -3597.771621,
        -6230.695029,
        -3597.381846,
        6230.968666,
        7197.850375,
        -0.930826,
        -3599.725424,
        -6232.626727,
        -3598.083945,
        6233.589968,
        7197.848797,
        -0.924270,
        -3599.718838,
        -6232.628639,
        -3598.088861,
        6233.585256,
        7197.912652,
        -0.903401,
        -3599.732976,
        -6232.695715,
        -3598.139856,
        6233.630586,
        7197.914231,
        -0.909956,
        -3599.739561,
        -6232.693803,
        -3598.134941,
        6233.635297,
        7200.000000,
        0.000000,
        -3600.000000,
        -6235.000000,
        -3600.000000,
        6235.000000,
    ])
    assert np.allclose(v_estimate[:48], expected_v[:48], rtol=1e-4, atol=1e-1)

def test_powerflowrunner_gc_12_47_1_subset():
    glm_file_path = os.path.join("data", "gc_12_47_1_subset", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate, simulation_state = test_runner.run(return_state=True)
    expected_v = np.array([
        276.610623,
        -0.182749,
        -138.461589,
        -239.434052,
        -138.138458,
        239.625053,
        7199.991859,
        0.004987,
        -3599.991489,
        -6234.995325,
        -3600.000210,
        6234.990361,
        7197.720574,
        -0.993762,
        -3599.714727,
        -6232.479982,
        -3597.962361,
        6233.508168,
        7196.098955,
        -1.706834,
        -3599.517129,
        -6230.684113,
        -3596.507407,
        6232.449933,
        7195.163070,
        -2.118369,
        -3599.403089,
        -6229.647664,
        -3595.667710,
        6231.839194,
        7194.728647,
        -2.438512,
        -3599.466831,
        -6229.102440,
        -3595.167474,
        6231.623170,
        7192.840849,
        -3.268631,
        -3599.236798,
        -6227.011791,
        -3593.473699,
        6230.391232,
        7191.407174,
        -3.899058,
        -3599.062101,
        -6225.424063,
        -3592.187373,
        6229.455646,
        7186.679520,
        -4.107836,
        -3596.837113,
        -6221.119770,
        -3589.568067,
        6225.427594,
        7189.262619,
        -4.834823,
        -3598.794381,
        -6223.052731,
        -3590.269569,
        6228.052469,
        7189.261042,
        -4.828259,
        -3598.787788,
        -6223.054649,
        -3590.274493,
        6228.047755,
        7189.324986,
        -4.807399,
        -3598.801980,
        -6223.121799,
        -3590.325525,
        6228.093168,
        7189.326563,
        -4.813963,
        -3598.808573,
        -6223.119881,
        -3590.320601,
        6228.097882,
        7195.163070,
        -2.118369,
        -3599.403089,
        -6229.647664,
        -3595.667710,
        6231.839194,
        7199.409622,
        -0.251039,
        -3599.920542,
        -6234.350525,
        -3599.477815,
        6234.610406,
        7200.000000,
        0.000000,
        -3600.000000,
        -6235.000000,
        -3600.000000,
        6235.000000
    ])
    assert np.allclose(v_estimate[:96], expected_v[:96], rtol=1e-4, atol=1e-1)

# def test_powerflowrunner_gc_12_no_shunt_impedances():
#     glm_file_path = os.path.join("data", "gc-12.47-1_no_shunt_impedances", "node.glm")
#     glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
#     test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
#     v_estimate, simulation_state = test_runner.run(return_state=True)
#     expected_v = np.array([])
#     assert np.allclose(v_estimate[:216], expected_v[:216], rtol=1e-3, atol=1e-3)

def test_powerflowrunner_gc_12_47_1_no_cap():
    glm_file_path = os.path.join("data", "gc_12_47_1_no_cap", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate, simulation_state = test_runner.run(return_state=True)
    expected_v = np.array([
        275.778761,
        -0.554674,
        -138.365776,
        -238.509726,
        -137.386905,
        239.085353,
        275.779153,
        -0.554784,
        -138.366073,
        -238.510020,
        -137.387012,
        239.085752,
        275.777148,
        -0.563698,
        -138.372912,
        -238.503804,
        -137.378248,
        239.088491,
        7199.975523,
        0.015040,
        -3599.974370,
        -6234.985969,
        -3600.000673,
        6234.970997,
        7193.137063,
        -2.980998,
        -3599.130990,
        -6227.417950,
        -3593.874631,
        6230.502210,
        7188.254639,
        -5.120065,
        -3598.528846,
        -6222.014646,
        -3589.500849,
        6227.311652,
        7185.436846,
        -6.354585,
        -3598.181331,
        -6218.896238,
        -3586.976608,
        6225.470285,
        7184.128335,
        -7.316129,
        -3598.370866,
        -6217.255269,
        -3585.472220,
        6224.818132,
        7178.444492,
        -9.806310,
        -3597.669884,
        -6210.965048,
        -3580.380509,
        6221.103863,
        7174.127937,
        -11.697462,
        -3597.137528,
        -6206.187982,
        -3576.513644,
        6218.283087,
        7165.029149,
        -14.003436,
        -3594.533668,
        -6196.955622,
        -3569.820791,
        6211.489897,
        7165.071010,
        -13.768973,
        -3594.348261,
        -6197.109475,
        -3570.045699,
        6211.408345,
        7165.081206,
        -13.771832,
        -3594.355978,
        -6197.117111,
        -3570.048477,
        6211.418701,
        7167.308098,
        -14.648956,
        -3596.264355,
        -6198.658945,
        -3570.436067,
        6213.807996,
        7167.308098,
        -14.648956,
        -3596.264355,
        -6198.658945,
        -3570.436067,
        6213.807996,
        7167.306525,
        -14.642370,
        -3596.257745,
        -6198.660878,
        -3570.441013,
        6213.803274,
        7167.362793,
        -14.624994,
        -3596.271102,
        -6198.719474,
        -3570.485062,
        6213.843738,
        7167.364365,
        -14.631581,
        -3596.277712,
        -6198.717541,
        -3570.480116,
        6213.848460,
        7167.669497,
        -14.497906,
        -3596.315351,
        -6199.055221,
        -3570.753453,
        6214.047861,
        7167.671070,
        -14.504492,
        -3596.321961,
        -6199.053288,
        -3570.748507,
        6214.052582,
        7167.669497,
        -14.497906,
        -3596.315351,
        -6199.055221,
        -3570.753453,
        6214.047861,
        7167.616841,
        -14.520974,
        -3596.308855,
        -6198.996948,
        -3570.706283,
        6214.013451,
        7167.618413,
        -14.527560,
        -3596.315466,
        -6198.995015,
        -3570.701337,
        6214.018172,
        7167.858844,
        -14.422225,
        -3596.345119,
        -6199.261095,
        -3570.916719,
        6214.175289,
        7167.863562,
        -14.441983,
        -3596.364950,
        -6199.255296,
        -3570.901881,
        6214.189454,
        7167.308098,
        -14.648956,
        -3596.264355,
        -6198.658945,
        -3570.436067,
        6213.807996,
        7167.308098,
        -14.648956,
        -3596.264355,
        -6198.658945,
        -3570.436067,
        6213.807996,
        7185.436846,
        -6.354585,
        -3598.181331,
        -6218.896238,
        -3586.976608,
        6225.470285,
        7167.308098,
        -14.648956,
        -3596.264355,
        -6198.658945,
        -3570.436067,
        6213.807996,
        7198.222507,
        -0.752984,
        -3599.758172,
        -6233.045932,
        -3598.430283,
        6233.825438,
        7200.000000,
        0.000000,
        -3600.000000,
        -6235.000000,
        -3600.000000,
        6235.000000
    ])
    assert np.allclose(v_estimate[:186], expected_v[:186], rtol=1e-4, atol=1e-1)

def test_powerflowrunner_gc_12_47_1():
    glm_file_path = os.path.join("data", "gc_12_47_1", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate, simulation_state = test_runner.run(return_state=True)
    expected_v_file_path = os.path.join("data", "gc_12_47_1", "gld_expected_output.txt")
    expected_v_full_file_path = os.path.join(CURR_DIR, expected_v_file_path)
    expected_v = np.loadtxt(expected_v_full_file_path)
    assert np.allclose(v_estimate[:186], expected_v[:186], rtol=1e-4, atol=1e-1)

def test_powerflowrunner_center_tap_xfmr():
    glm_file_path = os.path.join("data", "center_tap_xfmr", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate, simulation_state = test_runner.run(return_state=True)
    expected_v = np.array([
        7216.880000,
        0.000000,
        -3608.440000,
        -6250.000000,
        -3608.440000,
        6250.000000,
        7216.880000,
        0.000000,
        -3608.440000,
        -6250.000000,
        -3608.440035,
        6249.999962,
        7216.902459,
        -0.006015,
        -3608.417541,
        -6250.006015,
        -3608.375479,
        6249.976360,
        -58.6474,
        102.067,
        -58.6474,
        102.067,
        -58.6214,
        101.947,
        -58.6214,
        101.947,
        -58.5953,
        101.826,
        -58.5953,
        101.826,
        -58.5693,
        101.705,
        -58.5693,
        101.705
    ])
    assert np.allclose(v_estimate[:34], expected_v[:34], rtol=1e-4, atol=1e-1)

def test_powerflowrunner_regulator_center_tap_xfmr():
    glm_file_path = os.path.join("data", "regulator_center_tap_xfmr", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate, simulation_state = test_runner.run(return_state=True)
    expected_v = np.array([
        7216.880000,
        0.000000,
        -3608.440000,
        -6250.000000,
        -3608.440000,
        6250.000000,
        7216.880000,
        -0.000000,
        -3608.440000,
        -6250.000000,
        -3608.439997,
        6249.999927,
        7216.880000,
        0.000000,
        -3608.440000,
        -6250.000000,
        -3608.440032,
        6249.999889,
        7216.902410,
        -0.006016,
        -3608.417590,
        -6250.006016,
        -3608.375623,
        6249.976295,
        -58.6513,
        102.07,
        -58.6513,
        102.07,
        -58.6254,
        101.95,
        -58.6254,
        101.95
    ])
    assert np.allclose(v_estimate[:32], expected_v[:32], rtol=1e-4, atol=1e-1)
    
def test_powerflowrunner_triplex_load_class():
    glm_file_path = os.path.join("data", "triplex_load_class", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate, simulation_state = test_runner.run(return_state=True)
    expected_v = np.array([
        7216.880000,
        0.000000,
        -3608.440000,
        -6250.000000,
        -3608.440000,
        6250.000000,
        7216.880000,
        -0.000000,
        -3608.440000,
        -6250.000000,
        -3608.439998,
        6249.999964,
        7216.880000,
        -0.000000,
        -3608.440000,
        -6250.000000,
        -3608.440016,
        6249.999945,
        7216.891155,
        -0.002974,
        -3608.428845,
        -6250.002974,
        -3608.407948,
        6249.988262,
        -59.1807,
        102.534,
        -59.4739,
        103.471,
        -59.0964,
        102.347,
        -59.5323,
        103.538
    ])
    assert np.allclose(v_estimate[:32], expected_v[:32], rtol=1e-4, atol=1e-1)

def test_powerflowrunner_basic_triplex_network():
    glm_file_path = os.path.join("data", "basic_triplex_network", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate, simulation_state = test_runner.run(return_state=True)
    expected_v = np.array([
        7216.880000,
        0.000000,
        -3608.440000,
        -6250.000000,
        -3608.440000,
        6250.000000,
        7216.880000,
        -0.000000,
        -3608.440000,
        -6250.000000,
        -3608.439998,
        6249.999961,
        7216.880000,
        -0.000000,
        -3608.440000,
        -6250.000000,
        -3608.440017,
        6249.999941,
        7216.891891,
        -0.003095,
        -3608.428109,
        -6250.003095,
        -3608.405814,
        6249.987708,
        -59.1194,
        102.45,
        -59.4373,
        103.445,
        -56.0874,
        95.8343,
        -61.5221,
        105.81
    ])
    assert np.allclose(v_estimate[:32], expected_v[:32], rtol=1e-4, atol=1e-1)

def test_powerflowrunner_r1_12_47_1():
    glm_file_path = os.path.join("data", "r1_12_47_1", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-6})
    v_estimate, simulation_state = test_runner.run(return_state=True)
    expected_v_file_path = os.path.join("data", "r1_12_47_1", "gld_expected_output.txt")
    expected_v_full_file_path = os.path.join(CURR_DIR, expected_v_file_path)
    expected_v = np.loadtxt(expected_v_full_file_path)
    assert np.allclose(v_estimate[:6800], expected_v[:6800], rtol=1e-4, atol=1e-1)

# Requires support for delta connected transformers (not yet supported)
def test_powerflowrunner_ieee_four_bus_delta_delta_transformer():
    glm_file_path = os.path.join("data", "ieee_four_bus_delta_delta_transformer", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate = test_runner.execute()
    expected_v = np.array([
        7199.558000,
        0.000000,
        -3599.779000,
        -6235.000000,
        -3599.779000,
        6235.000000,
        7106.277773,
        -42.075713,
        -3607.171149,
        -6161.519929,
        -3521.244627,
        6189.669412,
        2245.404924,
        -143.257842,
        -1248.933296,
        -1890.408631,
        -996.471628,
        2033.666474,
        1895.884360,
        -300.915338,
        -1276.631641,
        -1615.079159,
        -702.203709,
        1863.812979
    ], dtype=float)
    assert np.allclose(v_estimate[:24], expected_v[:24], rtol=1e-6, atol=1e-6)

def test_powerflowrunner_ieee_thirteen_bus_Y_Y_pq_loads_top_half():
    glm_file_path = os.path.join("data", "ieee_thirteen_bus_Y_Y_pq_loads_top_half", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate, simulation_state = test_runner.run(return_state=True)
    expected_v = np.array([
        2527.413813,
        21.026001,
        -1268.879030,
        -2088.712286,
        -1256.924681,
        2234.586792,
        2551.881259,
        0.004726,
        -1260.909210,
        -2183.990082,
        -1283.450566,
        2222.990594,
        2534.381281,
        23.653699,
        -1269.684238,
        -2093.853157,
        -1260.044125,
        2239.635343,
        2401.777100,
        0.000000,
        -1200.888600,
        -2080.000000,
        -1200.888600,
        2080.000000,
        285.218224,
        -0.771645,
        -145.671425,
        -235.353183,
        -140.684165,
        254.591193,
        -1257.783878,
        -2064.856440,
        -1259.765544,
        2247.968781,
        -1254.204220,
        -2056.141749,
        -1259.681042,
        2250.473607,
        2535.178957,
        23.769788,
        -1269.012592,
        -2092.435081,
        -1256.890030,
        2239.114466
    ], dtype=float)
    assert np.allclose(v_estimate[:44], expected_v[:44], rtol=1e-6, atol=1e-6)

# Requires support for delta-connected loads, (not yet supported)
def test_powerflowrunner_ieee_thirteen_bus_core():
    glm_file_path = os.path.join("data", "ieee_13_core", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate, simulation_state = test_runner.run(return_state=True)
    expected_v = np.array([
        2551.872178,
        0.009692,
        -1260.914633,
        -2183.989885,
        -1283.450224,
        2222.976678,
        2522.264067,
        -22.808067,
        -1271.713885,
        -2137.041419,
        -1221.895080,
        2203.573395,
        2514.862040,
        -28.512507,
        -1274.413697,
        -2125.304302,
        -1206.506294,
        2198.722574,
        2401.777100,
        0.000000,
        -1200.888600,
        -2080.000000,
        -1200.888600,
        2080.000000,
        2490.217532,
        -45.869289,
        -1284.571692,
        -2094.193728,
        -1169.990388,
        2185.943230
    ], dtype=float)
    assert np.allclose(v_estimate[:30], expected_v[:30], rtol=1e-5, atol=1e-5)

# Requires support for delta loads (not yet supported)
def test_powerflowrunner_ieee_thirteen_bus_pq_loads_top_half():
    glm_file_path = os.path.join("data", "ieee_thirteen_bus_pq_loads_top_half", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate, simulation_state = test_runner.run(return_state=True)
    expected_v = np.array([
        2527.687894,
        4.211254,
        -1274.057147,
        -2116.020375,
        -1248.896569,
        2210.436074,
        2551.881291,
        0.004772,
        -1260.914623,
        -2183.989494,
        -1283.453478,
        2222.986561,
        2534.66223,
        6.812269,
        -1274.822183,
        -2121.087845,
        -1252.062088,
        2215.531639,
        2401.7771,
        0,
        -1200.8886,
        -2080,
        -1200.8886,
        2080,
        285.229227,
        -2.668878,
        -146.300047,
        -238.563007,
        -139.707831,
        251.779222,
        -1269.230772,
        -2100.167368,
        -1251.682983,
        2212.982423,
        -1269.354083,
        -2096.182817,
        -1251.528341,
        2208.994121,
        2535.470654,
        6.916907,
        -1274.142133,
        -2119.695189,
        -1248.875136,
        2214.99793
    ], dtype=float)
    assert np.allclose(v_estimate[:44], expected_v[:44], rtol=1e-6, atol=1e-6)

# Requires support for delta loads (not yet supported)
def test_powerflowrunner_ieee_thirteen_bus_pq():
    glm_file_path = os.path.join("data", "ieee_13_pq_loads", "node.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate, simulation_state = test_runner.run(return_state=True)
    expected_v = np.array([
        2407.799947,
        -146.086205,
        -1289.592686,
        -2092.236160,
        -1094.392832,
        2086.873323,
        2551.822886,
        0.041211,
        -1260.877945,
        -2183.977170,
        -1283.460616,
        2222.921820,
        2415.302999,
        -143.751381,
        -1290.313926,
        -2097.256911,
        -1097.595409,
        2092.496088,
        2401.777100,
        0.000000,
        -1200.888600,
        -2080.000000,
        -1200.888600,
        2080.000000,
        2298.244587,
        -294.322508,
        -1305.505431,
        -2072.527484,
        -941.181913,
        1971.576267,
        2292.279676,
        -297.437603,
        -933.395523,
        1955.796218,
        270.876777,
        -19.735288,
        -148.030026,
        -235.797550,
        -121.644192,
        237.105897,
        -1284.271006,
        -2076.091569,
        -1097.444394,
        2089.732588,
        -1284.230560,
        -2071.967906,
        -1097.452643,
        2085.603750,
        2279.413447,
        -288.535397,
        2298.244414,
        -294.322424,
        -1305.505281,
        -2072.527363,
        -941.181880,
        1971.576093,
        2278.613714,
        -298.334481,
        -1309.988345,
        -2072.712391,
        -940.787032,
        1961.661167,
        2298.235778,
        -294.295354,
        -1305.494402,
        -2072.534569,
        -941.195915,
        1971.563762,
        -923.177945,
        1941.010818,
        2386.700105,
        -181.385380,
        -1293.526138,
        -2090.093030,
        -1055.898256,
        2061.674605
    ], dtype=float)
    assert np.allclose(v_estimate[:76], expected_v[:76], rtol=1e-3, atol=1e-3)

def test_powerflowrunner_ieee_thirteen_bus_overhead():
    glm_file_path = os.path.join("data", "ieee_13_node_overhead_nr", "test_IEEE_13_NR_overhead.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate = test_runner.execute()
    expected_v = np.array([
        
    ], dtype=float)
    assert np.allclose(v_estimate[:18], expected_v[:18], rtol=1e-3)

# Requires resistive loads, current loads, and IP loads
def test_powerflowrunner_ieee_thirteen_bus():
    glm_file_path = os.path.join("data", "ieee_13_node_nr", "test_IEEE_13_NR.glm")
    glm_full_file_path = os.path.join(CURR_DIR, glm_file_path)
    test_runner = PowerFlowRunner(glm_full_file_path, {'max_iterations':50, 'tolerance': 1e-10})
    v_estimate, simulation_state = test_runner.run(return_state=True)
    expected_v = np.array([
        2442.766782,
        -108.916789,
        -1314.775436,
        -2123.156359,
        -1137.361833,
        2159.061304,
        2551.838732,
        0.026586,
        -1260.900822,
        -2183.973852,
        -1283.445032,
        2222.941672,
        2450.159062,
        -106.480827,
        -1315.483449,
        -2128.069895,
        -1140.432894,
        2164.524602,
        2401.777100,
        0.000000,
        -1200.888600,
        -2080.000000,
        -1200.888600,
        2080.000000,
        2368.071362,
        -219.430952,
        -1352.200812,
        -2135.101781,
        -1029.628252,
        2117.238224,
        2363.393048,
        -219.797727,
        -1023.361479,
        2115.173477,
        275.057129,
        -15.517488,
        -150.938282,
        -239.458838,
        -126.758858,
        245.578067,
        -1310.510972,
        -2105.222586,
        -1139.239687,
        2159.781233,
        -1311.080781,
        -2099.946317,
        -1138.627939,
        2154.503202,
        2354.092425,
        -214.377082,
        2368.071183,
        -219.430874,
        -1352.200657,
        -2135.101659,
        -1029.628215,
        2117.238035,
        2351.548001,
        -228.228718,
        -1361.834443,
        -2135.753512,
        -1028.161791,
        2112.874103,
        2368.063607,
        -219.416279,
        -1352.199784,
        -2135.096820,
        -1029.633379,
        2117.226532,
        -1015.480115,
        2113.920787,
        2430.265602,
        -134.701751,
        -1324.106564,
        -2128.854086,
        -1110.249873,
        2152.154125
    ], dtype=float)
    assert np.allclose(v_estimate[:82], expected_v[:82], rtol=1e-3, atol=1e-3)


if __name__ == "__main__":
    test_powerflowrunner_gc_12_47_1()