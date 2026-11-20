import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


FORMATTER = (
    Path(__file__).resolve().parents[1] / "scripts" / "format_ros_test_log.py"
)


class SectionCoverageTests(unittest.TestCase):
    def format_log(self, ticks, events=None):
        events = events or {}
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "raw.log"
            output = Path(directory) / "report.log"
            source.write_text(
                "".join(f"=== TICK {tick} ===\n{events.get(tick, '')}" for tick in ticks),
                encoding="utf-8",
            )
            subprocess.run(
                [sys.executable, FORMATTER, "--input", source, "--output", output],
                check=True,
                capture_output=True,
            )
            return output.read_text(encoding="utf-8")

    def test_incomplete_idle_section_cannot_pass(self):
        report = self.format_log([0, 2, 3])
        self.assertIn("INCOMPLETE (missing tick data)", report)
        self.assertNotIn("PASS (unexpected_events=0)", report)

    def test_complete_idle_section_can_pass(self):
        report = self.format_log(range(4))
        self.assertIn("PASS (unexpected_events=0)", report)

    def test_incomplete_call_section_preserves_event_without_passing(self):
        event = "[START] LLMInteraction mode=call_response\n"
        report = self.format_log([*range(7), *range(8, 12)], {8: event})
        self.assertIn(event, report)
        self.assertIn("INCOMPLETE (missing tick data)", report)
        self.assertNotIn("PASS (llm_call_response+=1)", report)


if __name__ == "__main__":
    unittest.main()
