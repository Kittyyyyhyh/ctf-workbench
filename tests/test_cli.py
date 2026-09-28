import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ctfcli import cli  # noqa: E402


class TestParseFlatYaml(unittest.TestCase):
    def setUp(self):
        fd, self.path = tempfile.mkstemp(suffix=".yaml")
        os.close(fd)  # Windows locks open handles
        self.f = Path(self.path)

    def tearDown(self):
        self.f.unlink(missing_ok=True)

    def test_basic(self):
        self.f.write_text("name: web1\ntype: web\nremote: 1.2.3.4:9999\n", encoding="utf-8")
        meta = cli.parse_flat_yaml(self.f)
        self.assertEqual(meta["name"], "web1")
        self.assertEqual(meta["remote"], "1.2.3.4:9999")

    def test_comments_and_blanks(self):
        self.f.write_text("# comment\n\nname: p1  # trailing\n", encoding="utf-8")
        meta = cli.parse_flat_yaml(self.f)
        self.assertEqual(meta, {"name": "p1  # trailing"})


class TestUnmangle(unittest.TestCase):
    def setUp(self):
        self._old = cli._MSYS_INFO
        cli._MSYS_INFO = ("D:/Git", "C:/Users/u/AppData/Local/Temp")

    def tearDown(self):
        cli._MSYS_INFO = self._old

    def test_git_root(self):
        self.assertEqual(cli._unmangle("D:/Git/ctf/exploit/x.py"), "/ctf/exploit/x.py")

    def test_temp(self):
        self.assertEqual(cli._unmangle("C:/Users/u/AppData/Local/Temp/svc.log"),
                         "/tmp/svc.log")

    def test_drive_letter(self):
        self.assertEqual(cli._unmangle("C:/nothing"), "/c/nothing")

    def test_posix_untouched(self):
        self.assertEqual(cli._unmangle("/flag.txt"), "/flag.txt")
        self.assertEqual(cli._unmangle("http://127.0.0.1:5000/"), "http://127.0.0.1:5000/")


class TestFindRoot(unittest.TestCase):
    def test_env_root(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "armory").mkdir()
            (Path(d) / "ctfcli").mkdir()
            old = os.environ.get("CTF_ROOT")
            os.environ["CTF_ROOT"] = d
            try:
                self.assertEqual(cli.find_root(), Path(d).resolve())
            finally:
                if old is None:
                    os.environ.pop("CTF_ROOT", None)
                else:
                    os.environ["CTF_ROOT"] = old

    def test_not_a_repo(self):
        old_env = os.environ.pop("CTF_ROOT", None)
        old_cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as d:
            os.chdir(d)  # outside the repo: no armory/+ctfcli/ here or above
            try:
                with self.assertRaises(cli.CtfError):
                    cli.find_root()
            finally:
                os.chdir(old_cwd)
                if old_env is not None:
                    os.environ["CTF_ROOT"] = old_env


class TestMeta(unittest.TestCase):
    def test_container_of(self):
        self.assertEqual(cli.container_of({"container": "ctf-a"}, "a"), "ctf-a")
        self.assertEqual(cli.container_of({}, "b"), "ctf-b")

    def test_notes_template(self):
        t = cli.notes_template("demo", "web")
        self.assertIn("demo", t)
        self.assertIn("web", t)

    def test_type_lists(self):
        self.assertEqual(len(cli.VALID_TYPES), 10)
        self.assertIn("osint", cli.BUILDABLE_TYPES)
        self.assertIn("pentest", cli.BUILDABLE_TYPES)
        self.assertEqual(cli.REQUIRED_IMAGES, {"base", "web", "pwn"})

    def test_expand_deps(self):
        self.assertEqual(cli._expand_deps(["pentest"]), ["base", "web", "pentest"])
        self.assertEqual(cli._expand_deps(["pwn", "base"]), ["base", "pwn"])
        self.assertEqual(cli._expand_deps(["crypto", "web"]), ["base", "crypto", "web"])


if __name__ == "__main__":
    unittest.main()
