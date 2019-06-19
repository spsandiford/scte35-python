import base64
import re
from abc import ABC, abstractmethod
from datetime import timedelta
from enum import Enum, unique
from typing import List

import bitstring

from scte35.exceptions import *

SPLICE_INFO_SECTION_TABLE_ID = 0xfc
CUEI_IDENTIFIER = 0x43554549  # ASCII "CUEI"


@unique
class SegmentationType(Enum):
    NOT_INDICATED = 0x00
    CONTENT_IDENTIFICATION = 0x01
    PROGRAM_START = 0x10
    PROGRAM_END = 0x11
    PROGRAM_EARLY_TERMINATION = 0x12
    PROGRAM_BREAKAWAY = 0x13
    PROGRAM_RESUMPTION = 0x14
    PROGRAM_RUNOVER_PLANNED = 0x15
    PROGRAM_RUNOVER_UNPLANNED = 0x16
    PROGRAM_OVERLAP_START = 0x17
    PROGRAM_BLACKOUT_OVERRIDE = 0x18
    PROGRAM_START_IN_PROGRESS = 0x19
    CHAPTER_START = 0x20
    CHAPTER_END = 0x21
    BREAK_START = 0x22
    BREAK_END = 0x23
    PROVIDER_ADVERTISEMENT_START = 0x30
    PROVIDER_ADVERTISEMENT_END = 0x31
    DISTRIBUTOR_ADVERTISEMENT_START = 0x32
    DISTRIBUTOR_ADVERTISEMENT_END = 0x33
    PROVIDER_PLACEMENT_OPPORTUNITY_START = 0x34
    PROVIDER_PLACEMENT_OPPORTUNITY_END = 0x35
    DISTRIBUTOR_PLACEMENT_OPPORTUNITY_START = 0x36
    DISTRIBUTOR_PLACEMENT_OPPORTUNITY_END = 0x37
    UNSCHEDULED_EVENT_START = 0x40
    UNSCHEDULED_EVENT_END = 0x41
    NETWORK_START = 0x50
    NETWORK_END = 0x51


@unique
class SpliceCommandType(Enum):
    # The splice_null() command allows a splice_info_table to be sent that can carry descriptors without
    # having to send one of the other defined commands. This command may also be used as a “heartbeat message”
    # for monitoring cue injection equipment integrity and link integrity
    SPLICE_NULL = 0x00

    # The splice_schedule() command is provided to allow a schedule of splice events to be conveyed in advance
    SPLICE_SCHEDULE = 0x04

    # In order to give advance warning of the impending splice (a pre-roll function), the splice_insert()
    # command is sent multiple times before the splice point
    SPLICE_INSERT = 0x05

    # The time_signal() provides a time synchronized data delivery mechanism
    TIME_SIGNAL = 0x06

    # The bandwidth_reservation() command is provided for reserving bandwidth in a multiplex
    BANDWIDTH_RESERVATION = 0x07

    # The private_command() structure provides a means to distribute user-defined commands using the SCTE 35 protocol
    PRIVATE_COMMAND = 0xFF


@unique
class SpliceDescriptorType(Enum):
    AVAIL_DESCRIPTOR = 0x00
    DTMF_DESCRIPTOR = 0x01
    SEGMENTATION_DESCRIPTOR = 0x02
    TIME_DESCRIPTOR = 0x03


@unique
class SegmentationUpidType(Enum):
    NOT_USED = 0x00
    DEPRECATED_USER_DEFINED = 0x01
    DEPRECATED_ISCI = 0x02
    AD_ID = 0x03
    UMID = 0x04
    DEPRECATED_ISAN = 0x05
    ISAN = 0x06
    TRIBUNE_ID = 0x07
    TURNER_ID = 0x08
    ADI = 0x09
    EIDR = 0x0a
    ATSC_CONTENT_ID = 0x0b
    MANAGED_PRIVATE = 0x0c
    MULTIPLE = 0x0d
    ADS_INFORMATION = 0x0e
    URI = 0x0f


class SpliceCommand(ABC):
    @abstractmethod
    def as_dict(self) -> dict:
        pass

    def __ne__(self, other):
        x = self.__eq__(other)
        if x is not NotImplemented:
            return not x
        return NotImplemented

    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))


class TimeSignal(SpliceCommand):
    """
    The time_signal() provides a uniform method of associating a pts_time sample with an arbitrary
    descriptor (or descriptors) as provided by the splice_info_section syntax

    If the time_specified_flag is set to 0, indicating no pts_time in the message, then the command shall
    be interpreted as an immediate command. It must be understood that using it in this manner will cause
    an unspecified amount of accuracy error.
    """

    def __init__(self, immediate: bool = False, pts_time=None):
        self._immediate = immediate
        self._pts_time = pts_time

    @property
    def is_immediate(self) -> bool:
        return self._immediate

    @property
    def pts_time(self) -> int:
        return self._pts_time

    @property
    def timedelta(self) -> timedelta:
        if self._immediate:
            return timedelta(seconds=0)
        else:
            seconds = self._pts_time / 90000.0
            return timedelta(seconds=seconds)

    def __eq__(self, other):
        if isinstance(other, TimeSignal):
            return self.__dict__ == other.__dict__
        return NotImplemented

    def as_dict(self) -> dict:
        d = dict()
        d['time_signal'] = dict()
        d['time_signal']['is_immediate'] = self._immediate
        if not self._immediate:
            d['time_signal']['pts_time'] = self._pts_time
        return d

    @classmethod
    def from_bytes(cls, input_bytes: bitstring.BitStream):
        time_specified_flag = input_bytes.read('bool')
        if time_specified_flag:
            reserved = input_bytes.read('uint:6')
            if reserved != 0x3F:
                raise ReservedBitsException()
            pts_time = input_bytes.read('uint:33')
            return cls(immediate=False, pts_time=pts_time)
        else:
            return cls(immediate=True, pts_time=None)


class SpliceDescriptor(ABC):
    @abstractmethod
    def as_dict(self) -> dict:
        pass

    def __ne__(self, other):
        x = self.__eq__(other)
        if x is not NotImplemented:
            return not x
        return NotImplemented

    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))


class AvailDescriptor(SpliceDescriptor):
    """
    The avail descriptor provides an optional extension to the splice_insert() command that
    allows an authorization identifier to be sent for an avail
    """

    def __init__(self,
                 provider_avail_id: int = 0):
        self._provider_avail_id = provider_avail_id

    @property
    def provider_avail_id(self) -> int:
        """
        This 32-bit number provides information that a receiving device may utilize to alter its
        behavior during or outside of an avail. It may be used in a manner similar to analog cue
        tones. An example would be a network directing an affiliate or a headend to black out a
        sporting event.
        """
        return self._provider_avail_id

    def __eq__(self, other):
        if isinstance(other, AvailDescriptor):
            return self.__dict__ == other.__dict__
        return NotImplemented

    def as_dict(self) -> dict:
        d = dict()
        d['avail_descriptor'] = dict()
        d['avail_descriptor']['provider_avail_id'] = self._provider_avail_id
        return d

    @classmethod
    def from_bytes(cls, input_bytes: bitstring.BitStream):
        descriptor_identifier = input_bytes.read('uint:32')
        if descriptor_identifier != CUEI_IDENTIFIER:
            raise Exception("Avail Descriptor identifier is not CUEI as required")
        provider_avail_id = input_bytes.read('uint:32')
        descriptor = cls(provider_avail_id)
        return descriptor


class DtmfDescriptor(SpliceDescriptor):
    """
     The DTMF descriptor provides an optional extension to the splice_insert() command that allows a
     receiver device to generate a legacy analog DTMF sequence based on a splice_info_section being received.
    """

    def __init__(self,
                 preroll: int = 0,
                 dtmf_string: bytes = None):
        self._preroll = preroll
        self._dtmf_string = dtmf_string

    @property
    def preroll(self) -> int:
        """
         This 8-bit number is the time the DTMF is presented to the analog output of the device in tenths
         of seconds. This gives a preroll range of 0 to 25.5 seconds.
        """
        return self._preroll

    @property
    def dtmf_string(self) -> bytes:
        """
        The DTMF characters the device is to generate
        """
        return self._dtmf_string

    def __eq__(self, other):
        if isinstance(other, DtmfDescriptor):
            return self.__dict__ == other.__dict__
        return NotImplemented

    def as_dict(self) -> dict:
        d = dict()
        d['DTMF_descriptor'] = dict()
        d['DTMF_descriptor']['preroll'] = self._preroll
        d['DTMF_descriptor']['dtmf_string'] = self._dtmf_string
        return d

    @classmethod
    def from_bytes(cls, input_bytes: bitstring.BitStream):
        descriptor_identifier = input_bytes.read('uint:32')
        if descriptor_identifier != CUEI_IDENTIFIER:
            raise Exception("DTMF Descriptor identifier is not CUEI as required")
        preroll = input_bytes.read('uint:8')
        dtmf_count = input_bytes.read('uint:3')
        reserved = input_bytes.read('uint:5')
        if reserved != 0x1F:
            raise ReservedBitsException("DTMF Descriptor")
        dtmf_string = input_bytes.read('bytes:%s' % dtmf_count)
        descriptor = cls(preroll, dtmf_string)
        return descriptor


class SegmentationDescriptor(SpliceDescriptor):
    """
    The segmentation_descriptor() is an implementation of a splice_descriptor(). It provides an optional
    extension to the time_signal() and splice_insert() commands that allows for segmentation messages to be
    sent in a time/video accurate method
    """

    def __init__(self,
                 segmentation_event_id: int,
                 segmentation_event_cancel_indicator: bool = False,
                 program_segmentation_flag: bool = False,
                 segmentation_duration_flag: bool = False,
                 delivery_not_restricted_flag: bool = False,
                 web_delivery_allowed_flag: bool = False,
                 no_regional_blackout_flag: bool = False,
                 archive_allowed_flag: bool = False,
                 device_restrictions: int = 0):
        self._segmentation_event_id = segmentation_event_id
        self._segmentation_event_cancel_indicator = segmentation_event_cancel_indicator
        self._program_segmentation_flag = program_segmentation_flag
        self._segmentation_duration_flag = segmentation_duration_flag
        self._delivery_not_restricted_flag = delivery_not_restricted_flag
        self._web_delivery_allowed_flag = web_delivery_allowed_flag
        self._no_regional_blackout_flag = no_regional_blackout_flag
        self._archive_allowed_flag = archive_allowed_flag
        self._device_restrictions = device_restrictions
        self._components: List[dict] = list()
        self._segmentation_duration: int = 0
        self._segmentation_upid_type: SegmentationUpidType = None
        self._segmentation_upid_bytes: bitstring.BitStream = None
        self._segmentation_type: SegmentationType = None

    @property
    def segmentation_event_id(self) -> int:
        """
        When a Segment start is signaled, the segmentation_event_id value becomes active. While active
        this value shall not be used to identify other segmentation events. When a Segment end is signaled,
        the segmentation_event_id value shall match the segment start segmentation_event_id value and this
        value then becomes inactive and hence able to be used again for a new segmentation_descriptor()
        occurrence including non-Segment usage such as Content Identification.
        """
        return self._segmentation_event_id

    @property
    def segmentation_event_cancel_indicator(self) -> bool:
        """
        Indicates that a previously sent segmentation event, identified by segmentation_event_id, has been cancelled
        """
        return self._segmentation_event_cancel_indicator

    @property
    def program_segmentation_flag(self) -> bool:
        """
        True indicates that the message refers to a Program Segmentation Point and that the mode is the
        Program Segmentation Mode whereby all PIDs/components of the program are to be segmented

        False indicates that the mode is the Component Segmentation Mode whereby each component that is
        intended to be segmented will be indicated in the components property
        """
        if self._segmentation_event_cancel_indicator:
            raise FieldNotDefinedException()
        else:
            return self._program_segmentation_flag

    @property
    def segmentation_duration_flag(self) -> bool:
        """
        Indicates the presence of a segmentation_duration field
        """
        if self._segmentation_event_cancel_indicator:
            raise FieldNotDefinedException()
        else:
            return self._segmentation_duration_flag

    @property
    def delivery_not_restricted_flag(self) -> bool:
        """
        True indicates there are no restrictions on the content and web_delivery_allowed_flag,
            no_regional_blackout_flag, and archive_allowed_flag are assumed True
        False indicates that the web_delivery_allowed_flag, no_regional_blackout_flag,
            archive_allowed_flag, and device_restrictions are present
        """
        if self._segmentation_event_cancel_indicator:
            raise FieldNotDefinedException()
        else:
            return self._delivery_not_restricted_flag

    @property
    def web_delivery_allowed_flag(self) -> bool:
        """
        True when there are no restrictions with respect to web delivery of this segment
        """
        if self.delivery_not_restricted_flag:
            raise FieldNotDefinedException()
        else:
            return self._web_delivery_allowed_flag

    @property
    def no_regional_blackout_flag(self) -> bool:
        """
        True when there is no regional blackout of this segment
        """
        if self.delivery_not_restricted_flag:
            raise FieldNotDefinedException()
        else:
            return self._no_regional_blackout_flag

    @property
    def archive_allowed_flag(self) -> bool:
        if self.delivery_not_restricted_flag:
            raise FieldNotDefinedException()
        else:
            return self._archive_allowed_flag

    @property
    def device_restrictions(self) -> int:
        if self.delivery_not_restricted_flag:
            raise FieldNotDefinedException()
        else:
            return self._device_restrictions

    @property
    def components(self) -> List[dict]:
        if self.program_segmentation_flag:
            raise FieldNotDefinedException()
        else:
            return self._components

    @property
    def segmentation_duration(self) -> int:
        if self.segmentation_duration_flag:
            return self._segmentation_duration
        else:
            raise FieldNotDefinedException()

    @property
    def segmentation_duration_timedelta(self) -> timedelta:
        return timedelta(seconds=self.segmentation_duration / 90000.0)

    @property
    def segmentation_upid_type(self) -> SegmentationUpidType:
        if self._segmentation_event_cancel_indicator:
            raise FieldNotDefinedException()
        else:
            return self._segmentation_upid_type

    @property
    def segmentation_upid_bytes(self) -> bitstring.BitStream:
        if self._segmentation_event_cancel_indicator:
            raise FieldNotDefinedException()
        else:
            return self._segmentation_upid_bytes

    @property
    def segmentation_type(self) -> SegmentationType:
        if self._segmentation_event_cancel_indicator:
            raise FieldNotDefinedException()
        else:
            return self._segmentation_type

    def __eq__(self, other):
        if isinstance(other, SegmentationDescriptor):
            return self.__dict__ == other.__dict__
        return NotImplemented

    def __str__(self):
        if self.segmentation_event_cancel_indicator:
            return "CANCEL ID:%d" % self.segmentation_event_id
        else:
            retval = "%s ID: %s UPID: (%s %s)" % (
                self.segmentation_type.name,
                self.segmentation_event_id,
                self.segmentation_upid_type.name,
                str(self.segmentation_upid_bytes.tobytes())
            )
            return retval

    def as_dict(self) -> dict:
        d = dict()
        d['segmentation_descriptor'] = dict()
        d['segmentation_descriptor']['segmentation_event_id'] = self._segmentation_event_id
        d['segmentation_descriptor']['segmentation_event_cancel_indicator'] = self._segmentation_event_cancel_indicator
        if not self._segmentation_event_cancel_indicator:
            d['segmentation_descriptor']['program_segmentation_flag'] = self._program_segmentation_flag
            d['segmentation_descriptor']['segmentation_duration_flag'] = self._segmentation_duration_flag
            d['segmentation_descriptor']['delivery_not_restricted_flag'] = self._delivery_not_restricted_flag
            if not self._delivery_not_restricted_flag:
                d['segmentation_descriptor']['web_delivery_allowed_flag'] = self._web_delivery_allowed_flag
                d['segmentation_descriptor']['no_regional_blackout_flag'] = self._no_regional_blackout_flag
                d['segmentation_descriptor']['archive_allowed_flag'] = self._archive_allowed_flag
                d['segmentation_descriptor']['device_restrictions'] = self._device_restrictions
            if not self._program_segmentation_flag:
                d['segmentation_descriptor']['components'] = list()
                for component in self._components:
                    d['segmentation_descriptor']['components'].append(component.copy())
            if self._segmentation_duration_flag:
                d['segmentation_descriptor']['segmentation_duration'] = self._segmentation_duration
            d['segmentation_descriptor']['segmentation_upid'] = dict()
            d['segmentation_descriptor']['segmentation_upid']['type'] = self._segmentation_upid_type.name
            d['segmentation_descriptor']['segmentation_upid']['bytes'] = str(self._segmentation_upid_bytes)
            d['segmentation_descriptor']['segmentation_type'] = self._segmentation_type.name
        return d

    @classmethod
    def from_bytes(cls, input_bytes: bitstring.BitStream):
        descriptor_identifier = input_bytes.read('uint:32')
        if descriptor_identifier != CUEI_IDENTIFIER:
            raise Exception("Segmentation Descriptor identifier is not CUEI as required")
        segmentation_event_id = input_bytes.read('uint:32')
        segmentation_event_cancel_indicator = input_bytes.read('bool')
        reserved = input_bytes.read('uint:7')
        if reserved != 0x7F:
            raise ReservedBitsException("Reserved bits after segmentation_event_cancel_indicator")
        descriptor = cls(segmentation_event_id, segmentation_event_cancel_indicator)
        if not segmentation_event_cancel_indicator:
            descriptor._program_segmentation_flag = input_bytes.read('bool')
            descriptor._segmentation_duration_flag = input_bytes.read('bool')
            descriptor._delivery_not_restricted_flag = input_bytes.read('bool')
            if not descriptor._delivery_not_restricted_flag:
                descriptor._web_delivery_allowed_flag = input_bytes.read('bool')
                descriptor._no_regional_blackout_flag = input_bytes.read('bool')
                descriptor._archive_allowed_flag = input_bytes.read('bool')
                descriptor._device_restrictions = input_bytes.read('uint:2')
            else:
                reserved = input_bytes.read('uint:5')
                if reserved != 0x1F:
                    raise ReservedBitsException("Reserved bits delivery_not_restricted_flag == 1")
            if not descriptor._program_segmentation_flag:
                component_count = input_bytes.read('uint:8')
                if component_count > 0:
                    descriptor._components = list()
                    for i in range(component_count):
                        component = dict()
                        component['tag'] = input_bytes.read('uint:8')
                        reserved = input_bytes.read('uint:7')
                        if reserved != 0x7F:
                            raise ReservedBitsException("Reserved bits in segmentation component")
                        component['pts_offset'] = input_bytes.read('uint:33')
                        descriptor._components.append(component)

            if descriptor._segmentation_duration_flag:
                descriptor._segmentation_duration = input_bytes.read('uint:40')

            descriptor._segmentation_upid_type = SegmentationUpidType(input_bytes.read('uint:8'))
            segmentation_upid_length = input_bytes.read('uint:8')
            descriptor._segmentation_upid_bytes = input_bytes.read(segmentation_upid_length * 8)

            descriptor._segmentation_type = SegmentationType(input_bytes.read('uint:8'))
            descriptor._segment_num = input_bytes.read('uint:8')
            descriptor._segments_expected = input_bytes.read('uint:8')

            if (descriptor._segmentation_type is SegmentationType.PROVIDER_PLACEMENT_OPPORTUNITY_START) or \
                    (descriptor._segmentation_type is SegmentationType.PROVIDER_PLACEMENT_OPPORTUNITY_END):
                try:
                    descriptor._sub_segment_num = input_bytes.read('uint:8')
                    descriptor._sub_segments_expected = input_bytes.read('uint:8')
                except bitstring.ReadError:
                    pass

        return descriptor


class SpliceInfoSection(object):
    """
    The splice information table provides command and control information to the splicer. It notifies
    the splicer of splice events in advance of those events. It is designed to accommodate ad insertion in
    network feeds. In this environment, examples of splice events would include 1) a splice out of a network
    feed into an ad, or 2) the splice out of an ad to return to the network feed. The splice information
    table may be sent multiple times and splice events may be cancelled.

    A splice event indicates the opportunity to splice one or more elementary streams within a program. Each
    splice event is uniquely identified with a splice_event_id. Splice events may be communicated in three
    ways: they may be scheduled ahead of time, a preroll warning may be given, or a command may be given to
    execute the splice event at specified Splice Points
    """

    def __init__(self,
                 pts_adjustment: int,
                 tier: int,
                 splice_command_type: SpliceCommandType):
        self._pts_adjustment: int = pts_adjustment
        self._tier: int = tier
        self._splice_command_type: SpliceCommandType = splice_command_type
        self._splice_command: SpliceCommand = None
        self._descriptors: List[SpliceDescriptor] = list()

    @property
    def pts_adjustment(self) -> int:
        """
         A 33 bit unsigned integer that shall be used by a splicing device as an offset to be added
         to the pts_time field(s) throughout this message to obtain the intended splice time(s). When
         this field has a zero value, then the pts_time field(s) shall be used without an offset.
        """
        return self._pts_adjustment

    @property
    def pts_adjustment_timedelta(self) -> timedelta:
        return timedelta(seconds=self.pts_adjustment / 90000.0)

    @property
    def tier(self) -> int:
        """
        A 12-bit value used by the SCTE 35 message provider to assign messages to authorization tiers. This
        field may take any value between 0x000 and 0xFFF. The value of 0xFFF provides backwards compatibility
        and shall be ignored by downstream equipment
        """
        return self._tier

    @property
    def splice_command_type(self) -> SpliceCommandType:
        return self._splice_command_type

    @property
    def splice_command(self) -> SpliceCommand:
        return self._splice_command

    @property
    def descriptors(self) -> List[SpliceDescriptor]:
        return self._descriptors.copy()

    def __eq__(self, other):
        if isinstance(other, SpliceInfoSection):
            if self._pts_adjustment != other._pts_adjustment:
                return False
            if self._tier != other._tier:
                return False
            if self._splice_command_type != other._splice_command_type:
                return False
            if self._splice_command != other._splice_command:
                return False
            if len(self._descriptors) != len(self._descriptors):
                return False
            for i in range(len(self._descriptors)):
                if self.descriptors[i] != other.descriptors[i]:
                    return False
            return True
        return NotImplemented

    def __ne__(self, other):
        x = self.__eq__(other)
        if x is not NotImplemented:
            return not x
        return NotImplemented

    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))

    def as_dict(self) -> dict:
        """
        Generates a dictionary of the table section suitable for serializing to json
        """
        d = dict()
        d['pts_adjustment'] = self._pts_adjustment
        d['tier'] = self._tier
        d['splice_command'] = self._splice_command.as_dict()
        d['descriptors'] = list()
        for descriptor in self._descriptors:
            d['descriptors'].append(descriptor.as_dict())
        return d

    @classmethod
    def from_bytes(cls, input_bytes):
        input_bitarray = bitstring.BitString(bytes=input_bytes)

        table_id = input_bitarray.read("uint:8")
        if table_id != SPLICE_INFO_SECTION_TABLE_ID:
            raise InvalidTableIdException()

        section_syntax_indicator = input_bitarray.read("bool")
        private = input_bitarray.read("bool")
        reserved = input_bitarray.read('uint:2')
        if reserved != 0x3:
            raise ReservedBitsException()

        section_length = input_bitarray.read('uint:12')
        section_bitarray = input_bitarray.read(section_length * 8)

        protocol_version = section_bitarray.read("uint:8")
        encrypted_packet = section_bitarray.read("bool")
        if encrypted_packet:
            raise Exception("Encrypted table sections are not supported")

        encryption_algorithm = section_bitarray.read("uint:6")
        pts_adjustment = section_bitarray.read("uint:33")
        cw_index = section_bitarray.read("uint:8")
        tier = section_bitarray.read("uint:12")

        splice_command_length = section_bitarray.read("uint:12")
        try:
            splice_command_type = SpliceCommandType(section_bitarray.read('uint:8'))
        except:
            raise

        section = SpliceInfoSection(pts_adjustment, tier, splice_command_type)
        splice_command_bitarray = section_bitarray.read(splice_command_length * 8)
        if splice_command_type is SpliceCommandType.SPLICE_NULL:
            raise NotImplementedException("SPLICE_NULL is not implemented")
        elif splice_command_type is SpliceCommandType.SPLICE_SCHEDULE:
            raise NotImplementedException("SPLICE_SCHEDULE is not implemented")
        elif splice_command_type is SpliceCommandType.SPLICE_INSERT:
            raise NotImplementedException("SPLICE_INSERT is not implemented")
        elif splice_command_type is SpliceCommandType.TIME_SIGNAL:
            section._splice_command = TimeSignal.from_bytes(splice_command_bitarray)
        elif splice_command_type is SpliceCommandType.BANDWIDTH_RESERVATION:
            raise NotImplementedException("BANDWIDTH_RESERVATION is not implemented")
        elif splice_command_type is SpliceCommandType.PRIVATE_COMMAND:
            raise NotImplementedException("PRIVATE_COMMAND is not implemented")

        descriptor_loop_length = section_bitarray.read('uint:16')
        descriptor_loop_bitarray = section_bitarray.read(descriptor_loop_length * 8)

        while descriptor_loop_bitarray.bitpos < descriptor_loop_bitarray.len:
            try:
                splice_descriptor_tag = SpliceDescriptorType(descriptor_loop_bitarray.read('uint:8'))
                descriptor_length = descriptor_loop_bitarray.read('uint:8')
                descriptor_bitarray = descriptor_loop_bitarray.read(descriptor_length * 8)

                if splice_descriptor_tag is SpliceDescriptorType.AVAIL_DESCRIPTOR:
                    section._descriptors.append(AvailDescriptor.from_bytes(descriptor_bitarray))
                elif splice_descriptor_tag is SpliceDescriptorType.DTMF_DESCRIPTOR:
                    section._descriptors.append(DtmfDescriptor.from_bytes(descriptor_bitarray))
                elif splice_descriptor_tag is SpliceDescriptorType.SEGMENTATION_DESCRIPTOR:
                    section._descriptors.append(SegmentationDescriptor.from_bytes(descriptor_bitarray))
                elif splice_descriptor_tag is SpliceDescriptorType.TIME_DESCRIPTOR:
                    raise NotImplementedException("TIME_DESCRIPTOR is not implemented")
            except bitstring.ReadError:
                raise SectionParsingErrorException()

        return section


class HlsCueTag(object):
    """
    Ad cues and other signaling metadata are placed into the HLS M3U8 manifest file using HLS tags and attribute lists.
    The #EXT-X-SCTE35 is the only tag defined by this standard.

    Example:
    #EXT-X-SCTE35:TYPE=0x34,CUE=/DA0AAD6i72m///wBQb+Njmu9gAeAhxDVUVJpu7KTH//AAEMERIICAAF3oCm7spMNAEDjopN5w==,ELAPSED=0.000
    """

    def __init__(self, cue_text: str):
        cue_components = HlsCueTag.tag_components(cue_text)

        if 'CUE' in cue_components.keys():
            self._splice_info_section = SpliceInfoSection.from_bytes(base64.standard_b64decode(cue_components['CUE']))

        if 'DURATION' in cue_components.keys():
            self._duration = cue_components['DURATION']

        if 'ELAPSED' in cue_components.keys():
            self._elapsed = cue_components['ELAPSED']

        if 'ID' in cue_components.keys():
            self._cue_id = cue_components['ID']

        if 'TIME' in cue_components.keys():
            self._cue_time = cue_components['TIME']

        if 'TYPE' in cue_components.keys():
            self._cue_type = SegmentationType(cue_components['TYPE'])

        if 'UPID' in cue_components.keys():
            self._upid = cue_components['UPID']

        if 'BLACKOUT' in cue_components.keys():
            self._blackout = cue_components['BLACKOUT']

        if 'CUE-OUT' in cue_components.keys():
            self._cue_out = cue_components['CUE-OUT']

        if 'CUE-IN' in cue_components.keys():
            self._cue_in = cue_components['CUE-IN']

        if 'SEGNE' in cue_components.keys():
            self._segne = cue_components['SEGNE']

    @staticmethod
    def tag_components(cue_text: str) -> dict:
        """
        Given an HLS cue tag string, return the raw components of the cue as a dictionary.  For tag attribute details,
        see [SCTE 35 2017].  In practice, the quoted-string elements may or may not have quotation marks
        """
        output_components = dict()
        m = re.match(r'^#EXT-X-SCTE35:(.*)$', cue_text)
        if m:
            try:
                cue_params = m.group(1)
            except IndexError:
                raise Exception("Invalid HLS Cue Tag format")
        else:
            raise NotAnHLSCueTag()

        # Attribute Name: CUE
        # Attribute Type: String
        # Attribute Required: Required
        # Description: The SCTE 35 binary message encoded in Base64 as defined in section 7.4 of [RFC 4648]
        #   with W3C recommendations.
        m_cue = re.match(r'.*CUE=\"?((?:[A-Za-z0-9+/]{4})+(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?)\"?.*',
                         cue_params)
        if m_cue:
            try:
                output_components['CUE'] = m_cue.group(1)
            except IndexError:
                raise MissingCueException("An HLS Cue Tag must contain a CUE attribute")
        else:
            raise MissingCueException("An HLS Cue Tag must contain a CUE attribute")

        # Attribute Name: DURATION
        # Attribute Type: Double
        # Attribute Required: Optional
        # Description: The duration of the signaled sequence defined by the CUE. The duration is
        #   expressed in seconds to millisecond accuracy.
        m_duration = re.match(r'.*DURATION=([0-9]+(?:\.[0-9]+)?).*',
                              cue_params)
        if m_duration:
            try:
                output_components['DURATION'] = float(m_duration.group(1))
            except IndexError:
                # Duration is optional
                pass

        # Attribute Name: ELAPSED
        # Attribute Type: Double
        # Attribute Required: Optional
        # Description: Offset from the CUE (typically a start segmentation type) of the
        #   earliest presentation time of the HLS media segment that follows. If an
        #   implementation removes fragments from the manifest file (ex. live application),
        #   the ELAPSED value shall be adjusted by the duration of the media segments removed.
        #   Elapsed is expressed in seconds to millisecond accuracy.
        m_elapsed = re.match(r'.*ELAPSED=([0-9]+(?:\.[0-9]+)?).*',
                             cue_params)
        if m_elapsed:
            try:
                output_components['ELAPSED'] = float(m_elapsed.group(1))
            except IndexError:
                # Elapsed is optional
                pass

        # Attribute Name: ID
        # Attribute Type: String
        # Attribute Required: Optional
        # Description: A unique value identifying the CUE.
        m_id = re.match(r'.*ID=\"([^\"]+)\".*',
                        cue_params)
        if m_id:
            try:
                output_components['ID'] = m_id.group(1)
            except IndexError:
                # ID is optional
                pass

        # Attribute Name: TIME
        # Attribute Type: Double
        # Attribute Required: Optional
        # Description: TIME represents the start time of the signaled sequence.
        #   If present in a stream, the SCTE 35 time descriptor should be utilized
        #   as the time basis.
        m_time = re.match(r'.*TIME=([0-9]+(?:\.[0-9]+)?).*',
                          cue_params)
        if m_time:
            try:
                output_components['TIME'] = float(m_time.group(1))
            except IndexError:
                # Time is optional
                pass

        # Attribute Name: TYPE
        # Attribute Type: Integer
        # Attribute Required: Optional
        # Description: If present, the segmentation type id from the SCTE 35 segmentation descriptor.
        # Try first with hex representation
        m_type = re.match(r'.*TYPE=(0x[0-9A-Fa-f]+).*',
                          cue_params)
        if m_type:
            try:
                output_components['TYPE'] = int(m_type.group(1), 16)
            except IndexError:
                # Time is optional
                pass
        else:
            # Try again with decimal
            m_type = re.match(r'.*TYPE=([0-9]+).*',
                              cue_params)
            if m_type:
                try:
                    output_components['TYPE'] = int(m_type.group(1))
                except IndexError:
                    # Time is optional
                    pass

        # Attribute Name: UPID
        # Attribute Type: String
        # Attribute Required: Optional
        # Description: Quoted string containing the segmentation_upid_type and the
        #   segmentation_upid seperated by a colon.
        # TODO: UPID can be an ascii string representation of the decoded binary, need
        #   to find examples.
        m_upid = re.match(r'.*UPID=\"?(0[xX][0-9A-Fa-f]+:0[xX][0-9A-Fa-f]+)\"?.*',
                          cue_params)
        if m_upid:
            try:
                output_components['UPID'] = m_upid.group(1)
            except IndexError:
                # UPID is optional
                pass

        # Attribute Name: BLACKOUT
        # Attribute Type: String
        # Attribute Required: Optional
        # Description: Enumeration of delivery restriction states as determined by business
        #   logic in the packager. Valid values are: YES, NO (default), MAYBE
        m_blackout = re.match(r'.*BLACKOUT=((?:YES)|(?:NO)|(?:MAYBE)).*',
                              cue_params)
        if m_blackout:
            try:
                output_components['BLACKOUT'] = m_blackout.group(1)
            except IndexError:
                # BLACKOUT is optional
                pass

        # Attribute Name: CUE-OUT
        # Attribute Type: String
        # Attribute Required: Optional
        # Description: Signal to begin ad insertion. Valid values are: YES, NO (default), CONT
        m_cueout = re.match(r'.*CUE-OUT=((?:YES)|(?:NO)|(?:CONT)).*',
                            cue_params)
        if m_cueout:
            try:
                output_components['CUE-OUT'] = m_cueout.group(1)
            except IndexError:
                # CUE-OUT is optional
                pass

        # Attribute Name: CUE-IN
        # Attribute Type: String
        # Attribute Required: Optional
        # Description: Signal to stop replacing content. Valid values are: YES, NO (default).
        m_cuein = re.match(r'.*CUE-IN=((?:YES)|(?:NO)).*',
                           cue_params)
        if m_cuein:
            try:
                output_components['CUE-IN'] = m_cuein.group(1)
            except IndexError:
                # CUE-IN is optional
                pass

        # Attribute Name: SEGNE
        # Attribute Type: String
        # Attribute Required: Optional
        # Description: Values from the seg_num and seg_expected fields, expressed as decimal
        #   integers and delimited with a colon
        m_segne = re.match(r'.*SEGNE=\"?([0-9]+:[0-9]+)\"?.*',
                           cue_params)
        if m_segne:
            try:
                output_components['SEGNE'] = m_segne.group(1)
            except IndexError:
                # SEGNE is optional
                pass

        return output_components

    @property
    def cue(self) -> SpliceInfoSection:
        if hasattr(self, '_splice_info_section'):
            return self._splice_info_section
        else:
            raise FieldNotDefinedException()

    @property
    def duration(self) -> float:
        """
        The duration of the signaled sequence defined by the CUE. The duration is expressed in seconds to
        millisecond accuracy.
        """
        if hasattr(self, '_duration'):
            return self._duration
        else:
            raise FieldNotDefinedException()

    @property
    def elapsed(self) -> float:
        """
        Offset from the CUE (typically a start segmentation type) of the earliest presentation time of
        the HLS media segment that follows. If an implementation removes fragments from the manifest
        file (ex. live application), the ELAPSED value shall be adjusted by the duration of the media
        segments removed. Elapsed is expressed in seconds to millisecond accuracy.
        """
        if hasattr(self, '_elapsed'):
            return self._elapsed
        else:
            raise FieldNotDefinedException()

    @property
    def id(self) -> str:
        """
        A unique value identifying the CUE.
        """
        if hasattr(self, '_cue_id'):
            return self._cue_id
        else:
            raise FieldNotDefinedException()

    @property
    def time(self) -> float:
        """
        TIME represents the start time of the signaled sequence. If present in a stream, the SCTE 35 time
        descriptor should be utilized as the time basis.  TIME shall be the UTC time corresponding to the
        start time of the first inserted HLS media segment. TIME shall be to millisecond accuracy.  To
        calculate the actual temporal position within the content for the CUE, add TIME and ELAPSED.
        """
        if hasattr(self, '_cue_time'):
            return self._cue_time
        else:
            raise FieldNotDefinedException()

    @property
    def type(self) -> SegmentationType:
        """
        The segmentation type id from the SCTE 35 segmentation descriptor.
        """
        if hasattr(self, '_cue_type'):
            return self._cue_type
        else:
            raise FieldNotDefinedException()

    @property
    def upid(self) -> str:
        """
        Quoted string containing the segmentation_upid_type and the segmentation_upid seperated by a
        colon. The segmentation_upid_type is an ascii hex value prefixed with 0x or 0X. The
        segmentation_upid is an ascii hex prefixed with 0x or 0X, or an ascii string representation of
        the decoded binary. If segmentation_upid_type is 0x0D (MID), seperate
        each <segmentation_upid_type:segmentation_upid> pair with a semi-colon.
        """
        if hasattr(self, '_upid'):
            return self._upid
        else:
            raise FieldNotDefinedException()

    @property
    def blackout(self) -> str:
        """
        Enumeration of delivery restriction states as determined by business logic in the packager. Valid
        values are: YES, NO (default), MAYBE. YES indicates content is currently subject to blackout. MAYBE
        indicates content is subject to conditional restrictions and that external authorization is
        required for rights enforcement (i.e., regional blackout and/or device restrictions). NO indicates
        content is not subject to restriction.
        """
        if hasattr(self, '_blackout'):
            return self._blackout
        else:
            raise FieldNotDefinedException()

    @property
    def cue_out(self) -> str:
        """
        Signal to begin ad insertion. Valid values are: YES, NO (default), CONT. CONT signals the "continuation"
        of a break replacement opportunity started with CUE-OUT on a previous tag. Used for partial break
        replacement when a player joins mid-break. When CONT is present, the ELAPSED and DURATION
        attributes should be included.
        """
        if hasattr(self, '_cue_out'):
            return self._cue_out
        else:
            raise FieldNotDefinedException()

    @property
    def cue_in(self) -> str:
        """
        Signal to stop replacing content. Valid values are: YES, NO (default)
        """
        if hasattr(self, '_cue_in'):
            return self._cue_in
        else:
            raise FieldNotDefinedException()

    @property
    def segne(self) -> str:
        """
        Values from the seg_num and seg_expected fields, expressed as decimal integers and delimited with
        a colon. For example, SEGNE="3:3"
        """
        if hasattr(self, '_segne'):
            return self._segne
        else:
            raise FieldNotDefinedException()
