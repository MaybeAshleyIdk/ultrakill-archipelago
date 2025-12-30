#!/usr/bin/env python

# Copyright (c) 2025 MaybeAshleyIdk
# SPDX-License-Identifier: GPL-3.0-or-later

import enum
import os
import re
import subprocess
import sys
from collections.abc import Generator, Iterator, Sequence, Set
from contextlib import contextmanager
from enum import Enum
from os import DirEntry
from pathlib import Path, PurePath
from re import Match, Pattern
from subprocess import CompletedProcess
from tempfile import TemporaryDirectory
from typing import final

IGNORED_PATHS: Set[PurePath] = \
	frozenset(
		(
			PurePath("LICENSE.txt"),
			# Too trivial to license:
			PurePath("todo.txt"),
			PurePath("version.txt"),
			# Verbatim copies with attribution found inside:
			PurePath("CODE_OF_CONDUCT.md"),
			PurePath("LICENSES"),
			# Generated:
			PurePath("client-mod") / "packages.lock.json",
			PurePath(".idea"),
		),
	)

COPYRIGHT_LINE_PATTERN: Pattern[str] = \
	re.compile(r"^[\W\s]*Copyright\s*\(\s*c\s*\)\s*\S+(\s+\S+)*[\W\s]*$", re.IGNORECASE)

# No support for full license expressions to make it easier.
SPDX_LICENSE_IDENTIFIER_LINE_PATTERN: Pattern[str] = \
	re.compile(r"^[\W\s]*SPDX-License-Identifier:\s+([A-Za-z0-9.-]+)[\W\s]*$")

EXTERNAL_LICENSE_FILE_SUFFIX: str = ".LICENSE.txt"


@final
@enum.unique
class FileLicenseStatus(Enum):
	OK = enum.auto()
	MISSING = enum.auto()
	INVALID = enum.auto()


def main() -> None:
	script_dir_path: Path = Path(__file__).parent
	try:
		script_dir_path = script_dir_path.relative_to(Path.cwd())
	except ValueError:
		pass

	cloned_repository_path: Path
	with clone_git_repository_head_and_index(repository_path=script_dir_path) as cloned_repository_path:
		git_dir_path: Path = get_git_dir_path(cloned_repository_path)

		is_ok: bool = \
			check_licensing_of_dir_recursively(
				cloned_repository_path,
				does_parent_dir_have_license=False,
				ignored_paths=frozenset(
					(
						git_dir_path,
						*map(lambda ignored_path: cloned_repository_path / ignored_path, IGNORED_PATHS),
					),
				),
				relative_to=cloned_repository_path,
			)

		if is_ok:
			print("No license errors.", file=sys.stderr)
		else:
			sys.exit(1)


def check_licensing_of_dir_recursively(
	dir_path: Path,
	does_parent_dir_have_license: bool,
	ignored_paths: Set[Path],
	relative_to: Path,
) -> bool:
	dir_iter: Iterator[DirEntry]
	with os.scandir(dir_path) as dir_iter:
		is_ok: bool = True

		has_license: bool = does_parent_dir_have_license

		subdir_paths: list[Path] = []

		file_names_with_external_license: set[str] = set()

		file_names_with_license_header: set[str] = set()
		file_names_without_license_header: set[str] = set()

		entry: DirEntry[str]
		for entry in dir_iter:
			entry_name: str = entry.name
			entry_path = Path(entry.path)

			if entry.is_symlink() or any(map(lambda ignored_path: entry_path.samefile(ignored_path), ignored_paths)):
				continue

			if entry.is_dir():
				subdir_paths.append(entry_path)
				continue

			external_license_target_file_name: str | None = \
				if_string_ends_with_then_remove_suffix(entry_name, EXTERNAL_LICENSE_FILE_SUFFIX)
			is_license_file: bool = (external_license_target_file_name is not None) or (entry_name == "LICENSE.txt")

			status: FileLicenseStatus = check_license_status_of_file(entry_path, relative_to)

			if is_license_file and (status == FileLicenseStatus.MISSING):
				status = FileLicenseStatus.INVALID
				print_error(entry_path, relative_to, "License file is missing its license")

			is_ok = is_ok and (status != FileLicenseStatus.INVALID)

			if is_license_file:
				if external_license_target_file_name is not None:
					if status == FileLicenseStatus.OK:
						file_names_with_external_license.add(external_license_target_file_name)
				else:
					# Intentional override of the inherited status.
					has_license = (status == FileLicenseStatus.OK)

				continue

			if status == FileLicenseStatus.OK:
				file_names_with_license_header.add(entry_name)
			else:
				file_names_without_license_header.add(entry_name)

		if not has_license:
			file_names_without_license: set[str] = \
				file_names_without_license_header.difference(file_names_with_external_license)

			is_ok = is_ok and (len(file_names_without_license) == 0)

			file_name_without_license: str
			for file_name_without_license in file_names_without_license:
				print_error(
					dir_path / file_name_without_license,
					relative_to,
					"File is missing a license or an existing license (header or external file) is invalid",
				)

		file_names_with_double_licenses: set[str] = \
			file_names_with_external_license.intersection(file_names_with_license_header)

		is_ok = is_ok and (len(file_names_with_double_licenses) == 0)

		file_name_with_double_licenses: str
		for file_name_with_double_licenses in file_names_with_double_licenses:
			print_error(
				dir_path / file_name_with_double_licenses,
				relative_to,
				"File contains an SPDX license identifier and has an external license file",
			)

		missing_file_names_with_external_license: set[str] = file_names_with_external_license \
			.difference(file_names_with_license_header.union(file_names_without_license_header))

		is_ok = is_ok and (len(missing_file_names_with_external_license) == 0)

		missing_file_name_with_external_license: str
		for missing_file_name_with_external_license in missing_file_names_with_external_license:
			missing_file_path_with_external_license: Path = dir_path / missing_file_name_with_external_license
			try:
				missing_file_path_with_external_license = \
					missing_file_path_with_external_license.relative_to(relative_to)
			except ValueError:
				pass

			print_error(
				dir_path / (missing_file_name_with_external_license + EXTERNAL_LICENSE_FILE_SUFFIX),
				relative_to,
				f"License file targets file \"{missing_file_path_with_external_license}\", which does not exist",
			)

		subdir_path: Path
		for subdir_path in subdir_paths:
			is_subdir_ok: bool = \
				check_licensing_of_dir_recursively(
					subdir_path,
					does_parent_dir_have_license=has_license,
					ignored_paths=ignored_paths,
					relative_to=relative_to,
				)

			is_ok = is_ok and is_subdir_ok

		return is_ok


def check_license_status_of_file(file_path: Path, relative_to: Path) -> FileLicenseStatus:
	raw_contents: bytes = file_path.read_bytes()

	plaintext_contents: str
	try:
		plaintext_contents = raw_contents.decode(encoding="utf-8", errors="strict")
	except UnicodeDecodeError:
		return FileLicenseStatus.MISSING

	has_copyright: bool = False
	license_id: str = ""

	line: str
	for line in plaintext_contents.splitlines():
		copyright_line_match: Match[str] | None = COPYRIGHT_LINE_PATTERN.match(line)
		spdx_license_identifier_line_match: Match[str] | None = SPDX_LICENSE_IDENTIFIER_LINE_PATTERN.match(line)

		if (copyright_line_match is not None) and (spdx_license_identifier_line_match is not None):
			raise RuntimeError("Both copyright and SPDX license identifier lines match")

		if copyright_line_match is not None:
			# Multiple copyright headers are allowed.
			has_copyright = True
			continue

		if spdx_license_identifier_line_match is not None:
			if license_id != "":
				print_error(file_path, relative_to, "File contains multiple SPDX license identifiers")
				return FileLicenseStatus.INVALID

			license_id = spdx_license_identifier_line_match.group(1)

			continue

	match license_id:
		case "":
			if has_copyright:
				print_error(
					file_path,
					relative_to,
					"File contains a copyright notice, but is missing an SPDX license identifier",
				)
				return FileLicenseStatus.INVALID

			return FileLicenseStatus.MISSING

		case "CC0-1.0":
			if has_copyright:
				print_error(
					file_path,
					relative_to,
					"File is in the public domain, but also contains a copyright header",
				)
				return FileLicenseStatus.INVALID

			return FileLicenseStatus.OK

		case _:
			if not has_copyright:
				print_error(
					file_path,
					relative_to,
					"File contains an SPDX license identifier, but is missing a copyright header",
				)
				return FileLicenseStatus.INVALID

			return FileLicenseStatus.OK


def print_error(file_path: Path, relative_to: Path, message: str) -> None:
	try:
		file_path = file_path.relative_to(relative_to)
	except ValueError:
		pass

	print(f"{file_path}: {message}", file=sys.stderr)


def if_string_ends_with_then_remove_suffix(string: str, suffix: str) -> str | None:
	string_without_suffix: str = string.removesuffix(suffix)

	return string_without_suffix if string_without_suffix != string else None


# region Git


@contextmanager
def clone_git_repository_head_and_index(repository_path: Path) -> Generator[Path]:
	branch_name_or_commit_name: str
	is_branch: bool
	branch_name_or_commit_name, is_branch = get_git_head(repository_path)

	clone_branch_options: Sequence[str]
	if is_branch:
		clone_branch_options = (f"--branch={branch_name_or_commit_name}", "--depth=1", "--single-branch")
	else:
		clone_branch_options = ()

	git_diff_process: CompletedProcess = \
		subprocess.run(
			args=(
				"git", "-c", "diff.noPrefix=false", "--no-pager",
				"diff", "--cached", "--patch-with-raw", "-z", "--no-color", "--full-index", "--binary",
			),
			stdout=subprocess.PIPE,
			stderr=sys.stderr,
			cwd=repository_path,
		)
	if git_diff_process.returncode != 0:
		sys.exit(git_diff_process.returncode)

	with TemporaryDirectory() as tmp_dir_path_str:
		tmp_dir_path = Path(tmp_dir_path_str)

		exit_status: int = \
			subprocess.call(
				args=(
					"git", "--no-pager",
					# The option --no-hardlinks is required because the temporary directory may be on different file system.
					"clone", "--no-local", "--no-hardlinks", "--quiet", *clone_branch_options, "--no-tags",
					"--", str(repository_path), str(tmp_dir_path),
				),
				stdout=sys.stderr,
				stderr=sys.stderr,
			)
		if exit_status != 0:
			sys.exit(exit_status)

		if not is_branch:
			exit_status = \
				subprocess.call(
					args=("git", "--no-pager", "switch", "--detach", "--quiet", branch_name_or_commit_name),
					stdout=sys.stderr,
					stderr=sys.stderr,
					cwd=tmp_dir_path,
				)
			if exit_status != 0:
				sys.exit(exit_status)

		git_apply_process: CompletedProcess = \
			subprocess.run(
				args=("git", "--no-pager", "apply", "--index", "--quiet", "--allow-empty"),
				input=git_diff_process.stdout,
				stdout=sys.stderr,
				stderr=sys.stderr,
				cwd=tmp_dir_path,
			)
		if git_apply_process.returncode != 0:
			sys.exit(git_apply_process.returncode)

		yield tmp_dir_path


def get_git_head(repository_path: Path) -> tuple[str, bool]:
	"""
	Returns either the currently checked out branch name and `True` or, if no branch is currently checked out,
	the currently checked out commit name and `False`.
	"""

	# <https://git.kernel.org/pub/scm/git/git.git/tree/contrib/completion/git-prompt.sh?h=v2.52.0#n538>
	git_dir_path: Path
	ref_format: str
	head_commit_name: str
	git_dir_path, ref_format, head_commit_name = get_git_dir_path_and_ref_format_and_head_commit_name(repository_path)

	head_ref_file: Path = git_dir_path / "HEAD"

	tmp: str = ""
	if head_ref_file.is_symlink():
		tmp = read_git_head_symbolic_ref(repository_path)
	else:
		match ref_format:
			case "files":
				tmp = head_ref_file.read_text(encoding="utf-8").splitlines()[0]

				if tmp.startswith("ref: "):
					tmp = tmp[5:]
				else:
					tmp = ""

			case _:
				tmp = read_git_head_symbolic_ref(repository_path)

		if tmp == "":
			return head_commit_name, False

	tmp = tmp.removeprefix("refs/heads/")

	return tmp, True


def get_git_dir_path_and_ref_format_and_head_commit_name(repository_path: Path) -> tuple[Path, str, str]:
	process: CompletedProcess = \
		subprocess.run(
			args=("git", "--no-pager", "rev-parse", "--git-dir", "--show-ref-format", "HEAD"),
			stdout=subprocess.PIPE,
			stderr=sys.stderr,
			cwd=repository_path,
			encoding="utf-8",
		)

	if process.returncode != 0:
		sys.exit(process.returncode)

	tmp: str = process.stdout
	tmp = tmp.rstrip()

	n: int = tmp.rindex("\n")

	head_commit_name: str = tmp[n + 1:]

	tmp = tmp[:n]
	n = tmp.rindex("\n")

	ref_format: str = tmp[n + 1:]
	git_dir_path = PurePath(tmp[:n])

	return (repository_path / git_dir_path), ref_format, head_commit_name


def get_git_dir_path(repository_path: Path) -> Path:
	process: CompletedProcess = \
		subprocess.run(
			args=("git", "--no-pager", "rev-parse", "--git-dir"),
			stdout=subprocess.PIPE,
			stderr=sys.stderr,
			cwd=repository_path,
			encoding="utf-8",
		)

	if process.returncode != 0:
		sys.exit(process.returncode)

	git_dir_path_str: str = process.stdout
	git_dir_path_str = git_dir_path_str.removesuffix("\n")
	return repository_path / PurePath(git_dir_path_str)


def read_git_head_symbolic_ref(repository_path: Path) -> str:
	process: CompletedProcess = \
		subprocess.run(
			args=("git", "--no-pager", "symbolic-ref", "HEAD"),
			stdout=subprocess.PIPE,
			stderr=sys.stderr,
			cwd=repository_path,
			encoding="utf-8",
		)

	if process.returncode != 0:
		sys.exit(process.returncode)

	return process.stdout.strip()


# endregion


if __name__ == "__main__":
	main()
