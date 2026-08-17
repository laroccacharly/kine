import hashlib
import subprocess
from pathlib import Path


class UI:
    def __init__(self) -> None:
        self.build_hash_name = ".build-hash"
        self.source_suffixes = {".ts", ".tsx", ".css", ".html"}
        self.skip_dirs = {"node_modules", "dist", "dist-ssr"}
        self.dist_dir.mkdir(parents=True, exist_ok=True)

    @property
    def dir(self) -> Path:
        return Path(__file__).resolve().parents[2] / "ui"

    @property
    def dist_dir(self) -> Path:
        return self.dir / "dist"

    @property
    def build_hash_path(self) -> Path:
        return self.dist_dir / self.build_hash_name

    def assets_exist(self) -> bool:
        return (self.dist_dir / "index.html").is_file()

    def source_files(self) -> list[Path]:
        files: list[Path] = []
        for dirpath, dirnames, filenames in self.dir.walk():
            dirnames[:] = [name for name in dirnames if name not in self.skip_dirs]
            for name in filenames:
                path = dirpath / name
                if path.suffix not in self.source_suffixes:
                    continue
                files.append(path)
        return sorted(files)

    def source_hash(self) -> str:
        digest = hashlib.sha256()
        for path in self.source_files():
            relative = path.relative_to(self.dir).as_posix()
            digest.update(relative.encode())
            digest.update(b"\0")
            digest.update(path.read_bytes())
            digest.update(b"\0")
        return digest.hexdigest()

    def stored_build_hash(self) -> str | None:
        if not self.build_hash_path.is_file():
            return None
        return self.build_hash_path.read_text().strip()

    def build(self) -> None:
        source_hash = self.source_hash()
        if self.assets_exist() and self.stored_build_hash() == source_hash:
            print("ui build up to date, skipping")
            return

        result = subprocess.run(
            ["bun", "run", "build"],
            cwd=self.dir,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(f"ui build failed with exit code {result.returncode}")

        self.build_hash_path.write_text(source_hash)
