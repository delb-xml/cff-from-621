from pathlib import Path
from subprocess import run

from pytest import mark


FIXTURES = Path(__file__).parent.resolve() / "fixtures"


@mark.parametrize("folder", [x for x in FIXTURES.iterdir() if x.is_dir()])
def test_conversion(folder):
    run(["cff-from-621", "--destination", "testresult.cff"], cwd=folder, check=True)
    assert (folder / "CITATION.cff").read_bytes() == (
        folder / "testresult.cff"
    ).read_bytes()
