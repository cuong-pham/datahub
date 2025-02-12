import json
import logging
import pathlib
from typing import Union

from datahub.configuration.common import ConfigModel
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.ingestion.api.common import RecordEnvelope
from datahub.ingestion.api.sink import Sink, SinkReport, WriteCallback
from datahub.metadata.com.linkedin.pegasus2avro.mxe import (
    MetadataChangeEvent,
    MetadataChangeProposal,
)
from datahub.metadata.com.linkedin.pegasus2avro.usage import UsageAggregation

logger = logging.getLogger(__name__)


class FileSinkConfig(ConfigModel):
    filename: str


class FileSink(Sink[FileSinkConfig, SinkReport]):
    def __post_init__(self) -> None:
        fpath = pathlib.Path(self.config.filename)
        self.file = fpath.open("w")
        self.file.write("[\n")
        self.wrote_something = False

    def write_record_async(
        self,
        record_envelope: RecordEnvelope[
            Union[
                MetadataChangeEvent,
                MetadataChangeProposal,
                MetadataChangeProposalWrapper,
                UsageAggregation,
            ]
        ],
        write_callback: WriteCallback,
    ) -> None:
        record = record_envelope.record
        obj = record.to_obj()

        if self.wrote_something:
            self.file.write(",\n")

        json.dump(obj, self.file, indent=4)
        self.wrote_something = True

        self.report.report_record_written(record_envelope)
        write_callback.on_success(record_envelope, {})

    def close(self):
        self.file.write("\n]")
        self.file.close()
