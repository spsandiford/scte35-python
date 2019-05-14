import unittest
from datetime import timedelta

from scte35 import exceptions
from scte35 import scte35


class TestHlsCueTag(unittest.TestCase):

    def testSample1(self):
        sample = '#EXT-X-SCTE35:TYPE=0x34,CUE=/DBfAAD6i73N///wBQb+mV9eNwBJAhxDVUVJpvr+m3//AAGHhoEICAAF3oCm+v6bNAIDAilDVUVJAAAAAH+/DBpWTU5VATrI4MzmGxHnv9QAJrlBTzABZTRfGAEAADd/IDU=,ELAPSED=98.098'
        t = scte35.HlsCueTag(sample)
        self.assertIsNotNone(t)
        self.assertIsInstance(t, scte35.HlsCueTag)
        self.assertEqual(t.type,scte35.SegmentationType.PROVIDER_PLACEMENT_OPPORTUNITY_START)
        self.assertEqual(t.elapsed, 98.098)
        s = t.cue
        self.assertEqual(s.pts_adjustment, 4203462093)
        self.assertEqual(s.pts_adjustment_timedelta, timedelta(seconds=46705, microseconds=134367))
        self.assertEqual(s.tier, 0xFFF)
        self.assertEqual(s.splice_command_type, scte35.SpliceCommandType.TIME_SIGNAL)
        c = s.splice_command
        self.assertIsInstance(c, scte35.SpliceCommand)
        self.assertIsInstance(c, scte35.TimeSignal)
        self.assertEqual(c.is_immediate, False)
        self.assertEqual(c.pts_time, 2573164087)
        self.assertEqual(c.timedelta, timedelta(seconds=28590, microseconds=712078))
        descriptors = s.descriptors
        self.assertIsInstance(descriptors, list)
        self.assertEqual(len(descriptors), 2)
        self.assertIsInstance(descriptors[0], scte35.SpliceDescriptor)
        self.assertIsInstance(descriptors[1], scte35.SpliceDescriptor)
        self.assertIsInstance(descriptors[0], scte35.SegmentationDescriptor)
        self.assertIsInstance(descriptors[1], scte35.SegmentationDescriptor)
        d: scte35.SegmentationDescriptor = descriptors[0]
        self.assertEqual(d.segmentation_type, scte35.SegmentationType.PROVIDER_PLACEMENT_OPPORTUNITY_START)
        self.assertEqual(d.segmentation_event_id, 2801467035)
        self.assertEqual(d.segmentation_event_cancel_indicator, False)
        self.assertEqual(d.program_segmentation_flag, True)
        self.assertEqual(d.segmentation_duration_flag, True)
        self.assertEqual(d.delivery_not_restricted_flag, True)
        with self.assertRaises(scte35.FieldNotDefinedException):
            foo = d.web_delivery_allowed_flag
        with self.assertRaises(scte35.FieldNotDefinedException):
            foo = d.no_regional_blackout_flag
        with self.assertRaises(scte35.FieldNotDefinedException):
            foo = d.archive_allowed_flag
        with self.assertRaises(scte35.FieldNotDefinedException):
            foo = d.device_restrictions
        with self.assertRaises(scte35.FieldNotDefinedException):
            foo = d.components
        self.assertEqual(d.segmentation_duration, 25659009)
        self.assertEqual(d.segmentation_duration_timedelta, timedelta(seconds=285, microseconds=100100))
        self.assertEqual(d.segmentation_upid_type, scte35.SegmentationUpidType.TURNER_ID)
        d: scte35.SegmentationDescriptor = descriptors[1]
        self.assertEqual(d.segmentation_type, scte35.SegmentationType.CONTENT_IDENTIFICATION)
        self.assertEqual(d.segmentation_upid_type, scte35.SegmentationUpidType.MANAGED_PRIVATE)

    def testSample2(self):
        sample = '#EXT-X-SCTE35:TYPE=0x35,CUE=/DBaAADRi/7w///wBQb+UBC95wBEAhdDVUVJx+99en+/CAgABpRmx+99ejUAAAIpQ1VFSQAAAAB/vwwaVk1OVQGamy7+vfAR4opzACa5QU8wAGBE4bcBAABtP9Ij'
        t = scte35.HlsCueTag(sample)
        self.assertIsNotNone(t)
        self.assertIsInstance(t, scte35.HlsCueTag)
        self.assertEqual(t.type,scte35.SegmentationType.PROVIDER_PLACEMENT_OPPORTUNITY_END)
        s = t.cue
        self.assertEqual(s.pts_adjustment, 3515612912)
        self.assertEqual(s.pts_adjustment_timedelta, timedelta(seconds=39062, microseconds=365689))
        self.assertEqual(s.tier, 0xFFF)
        self.assertEqual(s.splice_command_type, scte35.SpliceCommandType.TIME_SIGNAL)
        c = s.splice_command
        self.assertIsInstance(c, scte35.SpliceCommand)
        self.assertIsInstance(c, scte35.TimeSignal)
        self.assertEqual(c.is_immediate, False)
        self.assertEqual(c.pts_time, 1343274471)
        self.assertEqual(c.timedelta, timedelta(seconds=14925, microseconds=271900))
        descriptors = s.descriptors
        self.assertIsInstance(descriptors, list)
        self.assertEqual(len(descriptors), 2)
        self.assertIsInstance(descriptors[0], scte35.SpliceDescriptor)
        self.assertIsInstance(descriptors[1], scte35.SpliceDescriptor)
        self.assertIsInstance(descriptors[0], scte35.SegmentationDescriptor)
        self.assertIsInstance(descriptors[1], scte35.SegmentationDescriptor)
        d: scte35.SegmentationDescriptor = descriptors[0]
        self.assertEqual(d.segmentation_type, scte35.SegmentationType.PROVIDER_PLACEMENT_OPPORTUNITY_END)
        self.assertEqual(d.segmentation_event_id, 3354361210)
        self.assertEqual(d.segmentation_event_cancel_indicator, False)
        self.assertEqual(d.program_segmentation_flag, True)
        self.assertEqual(d.segmentation_duration_flag, False)
        self.assertEqual(d.delivery_not_restricted_flag, True)
        with self.assertRaises(scte35.FieldNotDefinedException):
            foo = d.web_delivery_allowed_flag
        with self.assertRaises(scte35.FieldNotDefinedException):
            foo = d.no_regional_blackout_flag
        with self.assertRaises(scte35.FieldNotDefinedException):
            foo = d.archive_allowed_flag
        with self.assertRaises(scte35.FieldNotDefinedException):
            foo = d.device_restrictions
        with self.assertRaises(scte35.FieldNotDefinedException):
            foo = d.components
        with self.assertRaises(scte35.FieldNotDefinedException):
            foo = d.segmentation_duration
        with self.assertRaises(scte35.FieldNotDefinedException):
            foo = d.segmentation_duration_timedelta
        self.assertEqual(d.segmentation_upid_type, scte35.SegmentationUpidType.TURNER_ID)
        d: scte35.SegmentationDescriptor = descriptors[1]
        self.assertEqual(d.segmentation_type, scte35.SegmentationType.CONTENT_IDENTIFICATION)
        self.assertEqual(d.segmentation_upid_type, scte35.SegmentationUpidType.MANAGED_PRIVATE)

    def test_sample_3(self):
        sample = '#EXT-X-SCTE35:TYPE=0x10,CUE=/DBhAAFyoXv5AP/wBQb/5qjG3wBLAhdDVUVJSAAAAH+fCAgAAAAALqOc7hAAAAIXQ1VFSUf///9/nwgIAAAAAC6jnMARAAACF0NVRUlIAABGf58ICAAAAAAuo5zANQAAoDVmCw==,ELAPSED=344.344'
        t = scte35.HlsCueTag(sample)
        self.assertIsNotNone(t)
        self.assertIsInstance(t, scte35.HlsCueTag)
        self.assertEqual(t.type,scte35.SegmentationType.PROGRAM_START)
        s = t.cue
        self.assertEqual(s.pts_adjustment, 6218152953)
        self.assertEqual(s.pts_adjustment_timedelta, timedelta(seconds=69090, microseconds=588367))
        self.assertEqual(s.tier, 0xFFF)
        self.assertEqual(s.splice_command_type, scte35.SpliceCommandType.TIME_SIGNAL)
        c = s.splice_command
        self.assertIsInstance(c, scte35.SpliceCommand)
        self.assertIsInstance(c, scte35.TimeSignal)
        self.assertEqual(c.is_immediate, False)
        self.assertEqual(c.pts_time, 8164787935)
        self.assertEqual(c.timedelta, timedelta(days=1, seconds=4319, microseconds=865944))
        descriptors = s.descriptors
        self.assertIsInstance(descriptors, list)
        self.assertEqual(len(descriptors), 3)
        self.assertIsInstance(descriptors[0], scte35.SpliceDescriptor)
        self.assertIsInstance(descriptors[1], scte35.SpliceDescriptor)
        self.assertIsInstance(descriptors[2], scte35.SpliceDescriptor)
        self.assertIsInstance(descriptors[0], scte35.SegmentationDescriptor)
        self.assertIsInstance(descriptors[1], scte35.SegmentationDescriptor)
        self.assertIsInstance(descriptors[2], scte35.SegmentationDescriptor)
        d: scte35.SegmentationDescriptor = descriptors[0]
        self.assertEqual(d.segmentation_type, scte35.SegmentationType.PROGRAM_START)
        self.assertEqual(d.segmentation_event_id, 1207959552)
        self.assertEqual(d.segmentation_event_cancel_indicator, False)
        self.assertEqual(d.program_segmentation_flag, True)
        self.assertEqual(d.segmentation_duration_flag, False)
        self.assertEqual(d.delivery_not_restricted_flag, False)
        self.assertEqual(d.web_delivery_allowed_flag, True)
        self.assertEqual(d.no_regional_blackout_flag, True)
        self.assertEqual(d.archive_allowed_flag, True)
        self.assertEqual(d.device_restrictions, 3)
        d: scte35.SegmentationDescriptor = descriptors[1]
        self.assertEqual(d.segmentation_type, scte35.SegmentationType.PROGRAM_END)
        self.assertEqual(d.segmentation_event_id, 1207959551)
        d: scte35.SegmentationDescriptor = descriptors[2]
        self.assertEqual(d.segmentation_type, scte35.SegmentationType.PROVIDER_PLACEMENT_OPPORTUNITY_END)
        self.assertEqual(d.segmentation_event_id, 1207959622)

    def testEquivalent(self):
        sample1 = '#EXT-X-SCTE35:TYPE=0x34,CUE=/DBfAAD6i73N///wBQb+mV9eNwBJAhxDVUVJpvr+m3//AAGHhoEICAAF3oCm+v6bNAIDAilDVUVJAAAAAH+/DBpWTU5VATrI4MzmGxHnv9QAJrlBTzABZTRfGAEAADd/IDU=,ELAPSED=98.098'
        sample2 = '#EXT-X-SCTE35:TYPE=0x10,CUE=/DBhAAFyoXv5AP/wBQb/5qjG3wBLAhdDVUVJSAAAAH+fCAgAAAAALqOc7hAAAAIXQ1VFSUf///9/nwgIAAAAAC6jnMARAAACF0NVRUlIAABGf58ICAAAAAAuo5zANQAAoDVmCw==,ELAPSED=344.344'
        h1 = scte35.HlsCueTag(sample1)
        h2 = scte35.HlsCueTag(sample1)
        h3 = scte35.HlsCueTag(sample2)
        self.assertEqual(h1.cue, h1.cue)
        self.assertIs(h1.cue, h1.cue)
        self.assertEqual(h1.cue, h2.cue)
        self.assertEqual(h2.cue, h1.cue)
        self.assertNotEqual(h1.cue, h3.cue)
        self.assertNotEqual(h3.cue, h1.cue)

    def test_segmentation_descriptor_1(self):
        descriptor = scte35.SegmentationDescriptor(1,
                                                   segmentation_event_cancel_indicator=True)
        with self.assertRaises(exceptions.FieldNotDefinedException):
            flag = descriptor.delivery_not_restricted_flag
        with self.assertRaises(exceptions.FieldNotDefinedException):
            flag = descriptor.no_regional_blackout_flag
        descriptor = scte35.SegmentationDescriptor(1,
                                                   segmentation_event_cancel_indicator=False,
                                                   delivery_not_restricted_flag=True)
        with self.assertRaises(exceptions.FieldNotDefinedException):
            flag = descriptor.web_delivery_allowed_flag
        with self.assertRaises(exceptions.FieldNotDefinedException):
            flag = descriptor.no_regional_blackout_flag
        with self.assertRaises(exceptions.FieldNotDefinedException):
            flag = descriptor.archive_allowed_flag
        with self.assertRaises(exceptions.FieldNotDefinedException):
            flag = descriptor.device_restrictions



