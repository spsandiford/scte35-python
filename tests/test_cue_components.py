from datetime import timedelta

import pytest

from scte35 import exceptions
from scte35 import scte35


def test_sample_1():
    sample = '#EXT-X-SCTE35:TYPE=0x34,CUE=/DBfAAD6i73N///wBQb+mV9eNwBJAhxDVUVJpvr+m3//AAGHhoEICAAF3oCm+v6bNAIDAilDVUVJAAAAAH+/DBpWTU5VATrI4MzmGxHnv9QAJrlBTzABZTRfGAEAADd/IDU=,ELAPSED=98.098'

    t = scte35.HlsCueTag(sample)
    assert isinstance(t, scte35.HlsCueTag)
    assert t.type == scte35.SegmentationType.PROVIDER_PLACEMENT_OPPORTUNITY_START
    assert t.elapsed == 98.098

    s = t.cue
    assert s.pts_adjustment == 4203462093
    assert s.pts_adjustment_timedelta == timedelta(seconds=46705, microseconds=134367)
    assert s.tier == 0xFFF
    assert s.splice_command_type == scte35.SpliceCommandType.TIME_SIGNAL

    c = s.splice_command
    assert isinstance(c, scte35.SpliceCommand)
    assert isinstance(c, scte35.TimeSignal)
    assert c.is_immediate is False
    assert c.pts_time == 2573164087
    assert c.timedelta == timedelta(seconds=28590, microseconds=712078)

    descriptors = s.descriptors
    assert isinstance(descriptors, list)
    assert len(descriptors) == 2
    assert isinstance(descriptors[0], scte35.SpliceDescriptor)
    assert isinstance(descriptors[1], scte35.SpliceDescriptor)
    assert isinstance(descriptors[0], scte35.SegmentationDescriptor)
    assert isinstance(descriptors[1], scte35.SegmentationDescriptor)

    d: scte35.SegmentationDescriptor = descriptors[0]
    assert d.segmentation_type == scte35.SegmentationType.PROVIDER_PLACEMENT_OPPORTUNITY_START
    assert d.segmentation_event_id == 2801467035
    assert d.segmentation_event_cancel_indicator is False
    assert d.program_segmentation_flag is True
    assert d.segmentation_duration_flag is True
    assert d.delivery_not_restricted_flag is True
    with pytest.raises(scte35.FieldNotDefinedException):
        foo = d.web_delivery_allowed_flag
    with pytest.raises(scte35.FieldNotDefinedException):
        foo = d.no_regional_blackout_flag
    with pytest.raises(scte35.FieldNotDefinedException):
        foo = d.archive_allowed_flag
    with pytest.raises(scte35.FieldNotDefinedException):
        foo = d.device_restrictions
    with pytest.raises(scte35.FieldNotDefinedException):
        foo = d.components
    assert d.segmentation_duration == 25659009
    assert d.segmentation_duration_timedelta == timedelta(seconds=285, microseconds=100100)
    assert d.segmentation_upid_type == scte35.SegmentationUpidType.TURNER_ID

    d: scte35.SegmentationDescriptor = descriptors[1]
    assert d.segmentation_type == scte35.SegmentationType.CONTENT_IDENTIFICATION
    assert d.segmentation_upid_type == scte35.SegmentationUpidType.MANAGED_PRIVATE


def test_sample_2():
    sample = '#EXT-X-SCTE35:TYPE=0x35,CUE=/DBaAADRi/7w///wBQb+UBC95wBEAhdDVUVJx+99en+/CAgABpRmx+99ejUAAAIpQ1VFSQAAAAB/vwwaVk1OVQGamy7+vfAR4opzACa5QU8wAGBE4bcBAABtP9Ij'

    t = scte35.HlsCueTag(sample)
    assert isinstance(t, scte35.HlsCueTag)
    assert t.type == scte35.SegmentationType.PROVIDER_PLACEMENT_OPPORTUNITY_END

    s = t.cue
    assert s.pts_adjustment == 3515612912
    assert s.pts_adjustment_timedelta == timedelta(seconds=39062, microseconds=365689)
    assert s.tier == 0xFFF
    assert s.splice_command_type == scte35.SpliceCommandType.TIME_SIGNAL

    c = s.splice_command
    assert isinstance(c, scte35.SpliceCommand)
    assert isinstance(c, scte35.TimeSignal)
    assert c.is_immediate is False
    assert c.pts_time == 1343274471
    assert c.timedelta == timedelta(seconds=14925, microseconds=271900)

    descriptors = s.descriptors
    assert isinstance(descriptors, list)
    assert len(descriptors) == 2
    assert isinstance(descriptors[0], scte35.SpliceDescriptor)
    assert isinstance(descriptors[1], scte35.SpliceDescriptor)
    assert isinstance(descriptors[0], scte35.SegmentationDescriptor)
    assert isinstance(descriptors[1], scte35.SegmentationDescriptor)

    d: scte35.SegmentationDescriptor = descriptors[0]
    assert d.segmentation_type == scte35.SegmentationType.PROVIDER_PLACEMENT_OPPORTUNITY_END
    assert d.segmentation_event_id == 3354361210
    assert d.segmentation_event_cancel_indicator is False
    assert d.program_segmentation_flag is True
    assert d.segmentation_duration_flag is False
    assert d.delivery_not_restricted_flag is True
    with pytest.raises(scte35.FieldNotDefinedException):
        foo = d.web_delivery_allowed_flag
    with pytest.raises(scte35.FieldNotDefinedException):
        foo = d.no_regional_blackout_flag
    with pytest.raises(scte35.FieldNotDefinedException):
        foo = d.archive_allowed_flag
    with pytest.raises(scte35.FieldNotDefinedException):
        foo = d.device_restrictions
    with pytest.raises(scte35.FieldNotDefinedException):
        foo = d.components
    with pytest.raises(scte35.FieldNotDefinedException):
        foo = d.segmentation_duration
    with pytest.raises(scte35.FieldNotDefinedException):
        foo = d.segmentation_duration_timedelta
    assert d.segmentation_upid_type == scte35.SegmentationUpidType.TURNER_ID

    d: scte35.SegmentationDescriptor = descriptors[1]
    assert d.segmentation_type == scte35.SegmentationType.CONTENT_IDENTIFICATION
    assert d.segmentation_upid_type == scte35.SegmentationUpidType.MANAGED_PRIVATE


def test_sample_3():
    sample = '#EXT-X-SCTE35:TYPE=0x10,CUE=/DBhAAFyoXv5AP/wBQb/5qjG3wBLAhdDVUVJSAAAAH+fCAgAAAAALqOc7hAAAAIXQ1VFSUf///9/nwgIAAAAAC6jnMARAAACF0NVRUlIAABGf58ICAAAAAAuo5zANQAAoDVmCw==,ELAPSED=344.344'

    t = scte35.HlsCueTag(sample)
    assert isinstance(t, scte35.HlsCueTag)
    assert t.type == scte35.SegmentationType.PROGRAM_START
    assert t.elapsed == 344.344

    s = t.cue
    assert s.pts_adjustment == 6218152953
    assert s.pts_adjustment_timedelta == timedelta(seconds=69090, microseconds=588367)
    assert s.tier == 0xFFF
    assert s.splice_command_type == scte35.SpliceCommandType.TIME_SIGNAL

    c = s.splice_command
    assert isinstance(c, scte35.SpliceCommand)
    assert isinstance(c, scte35.TimeSignal)
    assert c.is_immediate is False
    assert c.pts_time == 8164787935
    assert c.timedelta == timedelta(days=1, seconds=4319, microseconds=865944)

    descriptors = s.descriptors
    assert isinstance(descriptors, list)
    assert len(descriptors) == 3
    assert isinstance(descriptors[0], scte35.SpliceDescriptor)
    assert isinstance(descriptors[1], scte35.SpliceDescriptor)
    assert isinstance(descriptors[2], scte35.SpliceDescriptor)
    assert isinstance(descriptors[0], scte35.SegmentationDescriptor)
    assert isinstance(descriptors[1], scte35.SegmentationDescriptor)
    assert isinstance(descriptors[2], scte35.SegmentationDescriptor)

    d: scte35.SegmentationDescriptor = descriptors[0]
    assert d.segmentation_type == scte35.SegmentationType.PROGRAM_START
    assert d.segmentation_event_id == 1207959552
    assert d.segmentation_event_cancel_indicator is False
    assert d.program_segmentation_flag is True
    assert d.segmentation_duration_flag is False
    assert d.delivery_not_restricted_flag is False
    assert d.web_delivery_allowed_flag is True
    assert d.no_regional_blackout_flag is True
    assert d.archive_allowed_flag is True
    assert d.device_restrictions == 3

    d: scte35.SegmentationDescriptor = descriptors[1]
    assert d.segmentation_type == scte35.SegmentationType.PROGRAM_END
    assert d.segmentation_event_id == 1207959551

    d: scte35.SegmentationDescriptor = descriptors[2]
    assert d.segmentation_type == scte35.SegmentationType.PROVIDER_PLACEMENT_OPPORTUNITY_END
    assert d.segmentation_event_id == 1207959622


def test_equivalent():
    sample1 = '#EXT-X-SCTE35:TYPE=0x34,CUE=/DBfAAD6i73N///wBQb+mV9eNwBJAhxDVUVJpvr+m3//AAGHhoEICAAF3oCm+v6bNAIDAilDVUVJAAAAAH+/DBpWTU5VATrI4MzmGxHnv9QAJrlBTzABZTRfGAEAADd/IDU=,ELAPSED=98.098'
    sample2 = '#EXT-X-SCTE35:TYPE=0x10,CUE=/DBhAAFyoXv5AP/wBQb/5qjG3wBLAhdDVUVJSAAAAH+fCAgAAAAALqOc7hAAAAIXQ1VFSUf///9/nwgIAAAAAC6jnMARAAACF0NVRUlIAABGf58ICAAAAAAuo5zANQAAoDVmCw==,ELAPSED=344.344'
    h1 = scte35.HlsCueTag(sample1)
    h2 = scte35.HlsCueTag(sample1)
    h3 = scte35.HlsCueTag(sample2)
    assert h1.cue == h1.cue
    assert h1.cue is h1.cue
    assert h1.cue == h2.cue
    assert h2.cue == h1.cue
    assert h1.cue != h3.cue
    assert h3.cue != h1.cue


def test_segmentation_descriptor():
    descriptor = scte35.SegmentationDescriptor(1, segmentation_event_cancel_indicator=True)
    with pytest.raises(exceptions.FieldNotDefinedException):
        flag = descriptor.delivery_not_restricted_flag
    with pytest.raises(exceptions.FieldNotDefinedException):
        flag = descriptor.no_regional_blackout_flag
    descriptor = scte35.SegmentationDescriptor(1,
                                               segmentation_event_cancel_indicator=False,
                                               delivery_not_restricted_flag=True)
    with pytest.raises(exceptions.FieldNotDefinedException):
        flag = descriptor.web_delivery_allowed_flag
    with pytest.raises(exceptions.FieldNotDefinedException):
        flag = descriptor.no_regional_blackout_flag
    with pytest.raises(exceptions.FieldNotDefinedException):
        flag = descriptor.archive_allowed_flag
    with pytest.raises(exceptions.FieldNotDefinedException):
        flag = descriptor.device_restrictions
