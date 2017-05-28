############
# Standard #
############
import logging

###############
# Third Party #
###############
import pytest
import numpy as np
from bluesky             import Msg, RunEngine
from bluesky.plans       import run_wrapper

##########
# Module #
##########
from pswalker.plans import measure_average, measure_centroid, walk_to_pixel
from .utils import collector

logger = logging.getLogger(__name__)


def test_measure_average(RE, one_bounce_system):
    logger.debug("test_measure_average")
    #Load motor and yag
    _, mot, det = one_bounce_system

    #Fake event storage 
    centroids = []
    readbacks = []
    col_c = collector('centroid_x', centroids)
    col_r = collector('alpha',    readbacks)
    #Run plan
    RE(run_wrapper(measure_average([det, mot],
                                   ['centroid_x','alpha'],
                                   delay=0.1, num=5)),
       subs={'event':[col_c, col_r]})
    #Check events
    assert centroids == [250.,250.,250.,250.,250.]
    assert readbacks == [0.,0.,0.,0.,0.]

    #Clear from last test
    centroids.clear()
    readbacks.clear()
    #Run with array of delays
    RE(run_wrapper(measure_average([det, mot],
                                   ['centroid_x','alpha'],
                                   delay=[0.1], num=2)),
       subs={'event':[col_c, col_r]})
    #Check events
    assert centroids == [250., 250.]
    assert readbacks == [0., 0.]

    #Invalid delay settings
    with pytest.raises(ValueError):
        RE(run_wrapper(measure_average([det, mot],
                                       ['centroid_x','alpha'],
                                       delay=[0.1], num=3)))


def test_measure_centroid(RE, one_bounce_system):
    logger.debug("test_measure_centroid")
    #Load motor and yag
    _, mot, det = one_bounce_system
    #Fake event storage 
    centroids = []
    col_c = collector('centroid_x', centroids)
    #Run plan
    # assert 0
    RE(run_wrapper(measure_centroid(det, average=5, target_field='centroid_x')),
       subs={'event':[col_c]})
    #Check events
    assert centroids == [250.,250.,250.,250.,250.]


def test_walk_to_pixel(RE, one_bounce_system):
    logger.debug("test_walk_to_pixel")
    _, mot, det = one_bounce_system
    #Walk to the pixel using dumb first step
    plan = run_wrapper(walk_to_pixel(det, mot, 200, 0, first_step=1e-6,
                                     tolerance=10, average=None,
                                     target_fields=['centroid_x', 'alpha'],
                                     max_steps=3))
    RE(plan)
    assert np.isclose(det.read()['centroid_x']['value'], 200, atol=10)
    #Walk to pixel using intial guess at gradient
    plan = run_wrapper(walk_to_pixel(det, mot, 200, 0, gradient=200,
                                     tolerance=10, average=None,
                                     target_fields=['centroid_x', 'alpha'],
                                     max_steps=3))
    RE(plan)
    assert np.isclose(det.read()['centroid_x']['value'], 200, atol=10)
