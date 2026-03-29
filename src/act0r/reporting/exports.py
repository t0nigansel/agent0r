from __future__ import annotations

import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from act0r.runner import RunResult
from act0r.scenarios.models import LoadedScenario

from .markdown import MarkdownReportGenerator


class RunArtifactExporter:
    def build_json_payload(
        self,
        run_result: RunResult,
        loaded_scenario: LoadedScenario,
    ) -> Dict[str, Any]:
        return {
            "run": run_result.model_dump(mode="json"),
            "scenario": loaded_scenario.model_dump(mode="json"),
        }

    def generate_json(
        self,
        run_result: RunResult,
        loaded_scenario: LoadedScenario,
        output_dir: Path,
    ) -> Path:
        output_path = output_dir.expanduser().resolve()
        output_path.mkdir(parents=True, exist_ok=True)
        json_path = output_path / "{}.json".format(run_result.run_id)
        payload = self.build_json_payload(run_result, loaded_scenario)
        json_path.write_text(
            json.dumps(payload, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        return json_path

    def generate_pdf(
        self,
        run_result: RunResult,
        loaded_scenario: LoadedScenario,
        output_dir: Path,
        *,
        markdown_text: str | None = None,
    ) -> Path:
        output_path = output_dir.expanduser().resolve()
        output_path.mkdir(parents=True, exist_ok=True)
        pdf_path = output_path / "{}.pdf".format(run_result.run_id)

        markdown = markdown_text
        if markdown is None:
            markdown = MarkdownReportGenerator().render(run_result, loaded_scenario)
        pdf_bytes = _render_simple_pdf(markdown)
        pdf_path.write_bytes(pdf_bytes)
        return pdf_path

    def generate_bundle(
        self,
        *,
        run_id: str,
        output_dir: Path,
        artifact_paths: Dict[str, Path],
    ) -> Path:
        output_path = output_dir.expanduser().resolve()
        output_path.mkdir(parents=True, exist_ok=True)
        bundle_path = output_path / "{}.bundle.zip".format(run_id)

        manifest = {
            "run_id": run_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "artifacts": {
                name: path.name for name, path in sorted(artifact_paths.items())
            },
        }

        with zipfile.ZipFile(bundle_path, "w") as archive:
            for name, path in sorted(artifact_paths.items()):
                _writestr_deterministic(
                    archive,
                    arcname=path.name,
                    data=path.read_bytes(),
                )
            _writestr_deterministic(
                archive,
                arcname="manifest.json",
                data=json.dumps(manifest, indent=2, sort_keys=True).encode("utf-8"),
            )

        return bundle_path


def _writestr_deterministic(archive: zipfile.ZipFile, *, arcname: str, data: bytes) -> None:
    info = zipfile.ZipInfo(filename=arcname)
    info.date_time = (1980, 1, 1, 0, 0, 0)
    info.compress_type = zipfile.ZIP_DEFLATED
    archive.writestr(info, data)


def _render_simple_pdf(text: str) -> bytes:
    lines = text.splitlines()
    clipped = [line[:110] for line in lines[:52]]

    operations = ["BT", "/F1 10 Tf", "50 790 Td"]
    for line in clipped:
        operations.append("({}) Tj".format(_escape_pdf_text(line)))
        operations.append("0 -14 Td")
    operations.append("ET")
    stream_data = "\n".join(operations).encode("latin-1", errors="replace")

    objects = [
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n",
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 5 0 R /Resources << /Font << /F1 4 0 R >> >> >>\nendobj\n",
        b"4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n",
        b"5 0 obj\n<< /Length "
        + str(len(stream_data)).encode("ascii")
        + b" >>\nstream\n"
        + stream_data
        + b"\nendstream\nendobj\n",
    ]

    header = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"
    body_parts = [header]
    offsets = [0]

    current_offset = len(header)
    for obj in objects:
        offsets.append(current_offset)
        body_parts.append(obj)
        current_offset += len(obj)

    xref_offset = current_offset
    xref_lines = [b"xref\n", b"0 6\n", b"0000000000 65535 f \n"]
    for offset in offsets[1:]:
        xref_lines.append("{:010d} 00000 n \n".format(offset).encode("ascii"))

    trailer = (
        b"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n"
        + str(xref_offset).encode("ascii")
        + b"\n%%EOF\n"
    )

    return b"".join(body_parts + xref_lines + [trailer])


def _escape_pdf_text(value: str) -> str:
    escaped = value.replace("\\", "\\\\")
    escaped = escaped.replace("(", "\\(").replace(")", "\\)")
    return escaped
