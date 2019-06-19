class InvalidTableIdException(Exception):
    """
    Indicate that the table id was not 0xFC as required
    """
    pass


class ReservedBitsException(Exception):
    """
    Indicate that bits reserved by the specification were not set to 1 as required
    """
    pass


class SectionParsingErrorException(Exception):
    pass


class NotAnHLSCueTag(Exception):
    pass


class NotImplementedException(Exception):
    pass


class NoSegmentationDescriptorException(Exception):
    pass


class FieldNotDefinedException(Exception):
    pass


class MissingCueException(Exception):
    pass
