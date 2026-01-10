#!/usr/bin/env python

# Copyright (c) 2026 MaybeAshleyIdk
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import enum
import hashlib
import http.client
import io
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
from abc import ABC, abstractmethod
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from enum import Enum, StrEnum
from io import BufferedRandom, BufferedReader, TextIOBase, TextIOWrapper
from os import DirEntry
from pathlib import Path, PurePath
from re import Match
from subprocess import CompletedProcess
from tarfile import TarFile, TarInfo
from tempfile import SpooledTemporaryFile, TemporaryDirectory
from types import SimpleNamespace
from typing import Any, ClassVar, Mapping, Never, final, override
from venv import EnvBuilder

if sys.version_info < (3, 12, 0):
	print(f"{sys.argv[0]}: Python 3.12 required", file=sys.stderr)
	sys.exit(1)

# When changing the Archipelago version, remember to update the SHA-256 checksum as well.
ARCHIPELAGO_VERSION: str = "0.6.5"

ARCHIPELAGO_SOURCE_ARCHIVE_SHA256_CHECKSUM: bytes = \
	bytes.fromhex("2149257cb2e43e2e6c56a2eb72a6cb302a40c0cdb60cde4d1b9d98cc7c24b2d3")

ARCHIPELAGO_SOURCE_ARCHIVE_URL: str = \
	f"https://github.com/ArchipelagoMW/Archipelago/archive/refs/tags/{ARCHIPELAGO_VERSION}.tar.gz"

APWORLD_NAME: str = "ultrakill"


class Environment:
	script_dir_path: Path = Path(__file__).parent

	base_build_dir_path: Path = script_dir_path / ".build"
	build_dir_path: Path = base_build_dir_path / f"archipelago-{ARCHIPELAGO_VERSION}"

	archipelago_source_archive_file_path: Path = build_dir_path / "source.tar.gz"
	archipelago_source_dir_path: Path = build_dir_path / "source"

	archipelago_venv_dir_path: Path = build_dir_path / "venv"
	archipelago_venv_exec_cmd_file_path: Path = build_dir_path / "venv_exec_cmd.txt"

	source_dir_path: Path = script_dir_path / "src"

	slot_data_schema_file_path: Path = script_dir_path / ".." / "shared" / "slot_data_schema.cfg"
	slot_data_class_source_file_path: Path = source_dir_path / "slot_data.py"

	version_file_path: Path = script_dir_path / ".." / "version.txt"
	version_python_file_path: Path = source_dir_path / "version.py"

	manifest_file_path: Path = build_dir_path / "manifest.json"

	base_apworlds_output_dir_path: Path = script_dir_path / "output"
	apworld_output_file_path: Path = (base_apworlds_output_dir_path /
	                                  f"archipelago-{ARCHIPELAGO_VERSION}" /
	                                  f"{APWORLD_NAME}.apworld")


class Target(ABC):
	_name: str
	_dependencies: Sequence[Target]

	def __init__(self, name: str, dependencies: Sequence[Target]) -> None:
		self._name = name
		self._dependencies = (*dependencies,)

	@final
	@property
	def name(self) -> str:
		return self._name

	@final
	def build(self, environment: Environment) -> None:
		self._build0(environment, ignore_cache=True)

	@abstractmethod
	def _is_up_to_date(self, environment: Environment) -> bool:
		raise NotImplementedError()

	@abstractmethod
	def _build(self, environment: Environment) -> None:
		raise NotImplementedError()

	@abstractmethod
	def clean(self, environment: Environment) -> None:
		raise NotImplementedError()

	@final
	def _build0(self, environment: Environment, ignore_cache: bool) -> None:
		for dependency in self._dependencies:
			dependency._build0(environment, ignore_cache=False)

		if ignore_cache or not self._is_up_to_date(environment):
			self._build(environment)
			print(f"> {self._name}: Done", file=sys.stderr)


# region target: archipelago source archive


class ArchipelagoSourceArchiveTarget(Target):

	def __init__(self) -> None:
		super().__init__(
			name="archipelago_source_archive",
			dependencies=(),
		)

	@override
	def _is_up_to_date(self, environment: Environment) -> bool:
		sha256_checksum: bytes
		try:
			archipelago_source_archive_file: BufferedReader
			with open(environment.archipelago_source_archive_file_path, mode="rb") as archipelago_source_archive_file:
				sha256_checksum = hashlib.file_digest(archipelago_source_archive_file, "sha256").digest()
		except FileNotFoundError:
			return False

		return sha256_checksum == ARCHIPELAGO_SOURCE_ARCHIVE_SHA256_CHECKSUM

	@override
	def _build(self, environment: Environment) -> None:
		environment.archipelago_source_archive_file_path.parent.mkdir(parents=True, exist_ok=True)

		archipelago_source_archive_file: BufferedRandom
		with open(environment.archipelago_source_archive_file_path, mode="w+b") as archipelago_source_archive_file:
			response: http.client.HTTPResponse
			with urllib.request.urlopen(url=ARCHIPELAGO_SOURCE_ARCHIVE_URL) as response:
				# <https://youtrack.jetbrains.com/issue/PY-81830>
				# noinspection PyTypeChecker
				shutil.copyfileobj(response, archipelago_source_archive_file, length=io.DEFAULT_BUFFER_SIZE)

			archipelago_source_archive_file.seek(0)

			sha256_checksum: bytes = hashlib.file_digest(archipelago_source_archive_file, "sha256").digest()
			if sha256_checksum != ARCHIPELAGO_SOURCE_ARCHIVE_SHA256_CHECKSUM:
				terminal_width: int = shutil.get_terminal_size()[0]

				separator_exclamation_marks_count: int = max(0, terminal_width - 9)
				separator_exclamation_marks_count_half: int = separator_exclamation_marks_count // 2

				separator: str = (("!" * separator_exclamation_marks_count_half) +
				                  " WARNING " +
				                  ("!" * (separator_exclamation_marks_count - separator_exclamation_marks_count_half)))
				print(
					f"{separator}\n\n"
					"The downloaded Archipelago source code archive's SHA-256 checksum is not what is expected!\n"
					f"Actual:   {sha256_checksum.hex()}\n"
					f"Expected: {ARCHIPELAGO_SOURCE_ARCHIVE_SHA256_CHECKSUM.hex()}\n"
					"\n"
					"This may be due to various reasons:\n"
					"\n"
					"* The Archipelago target version was changed, but the expected SHA-256 checksum was not updated "
					"(most likely)\n"
					"\n"
					"* The Archipelago source archive failed to properly download and got corrupted, "
					"possibly due to a spotty internet connection.\n"
					"  Please make sure that there is a stable internet connection and then try again by executing "
					f"the command `{sys.argv[0]} {self.name}`\n"
					"\n"
					f"* The Archipelago team intentionally re-released version {ARCHIPELAGO_VERSION} or "
					"the Archipelago GitHub repository was hijacked by bad actors that try to share malware. "
					"(both unlikely)\n"
					"  In either cases, please get in contact with the Archipelago team to get clarifications as to "
					"what happened\n"
					f"\n{separator}",
					file=sys.stderr,
				)

				sys.exit(1)

	@override
	def clean(self, environment: Environment) -> None:
		try:
			os.remove(environment.archipelago_source_archive_file_path)
		except FileNotFoundError:
			pass

		remove_empty_tree(environment.base_build_dir_path)


archipelago_source_archive_target = ArchipelagoSourceArchiveTarget()


# endregion
# region target: archipelago source directory


class ArchipelagoSourceDirectoryTarget(Target):

	def __init__(self) -> None:
		super().__init__(
			name="archipelago_source_directory",
			dependencies=(archipelago_source_archive_target,),
		)

	@override
	def _is_up_to_date(self, environment: Environment) -> bool:
		return is_dir_not_empty(environment.archipelago_source_dir_path)

	@override
	def _build(self, environment: Environment) -> None:
		try:
			shutil.rmtree(environment.archipelago_source_dir_path)
		except FileNotFoundError:
			pass

		environment.archipelago_source_dir_path.mkdir(parents=True, exist_ok=True)

		archipelago_source_archive: TarFile
		with tarfile.open(environment.archipelago_source_archive_file_path, mode="r:gz") as archipelago_source_archive:
			archipelago_source_archive.extractall(
				path=environment.archipelago_source_dir_path,
				filter=ArchipelagoSourceDirectoryTarget._filter_archipelago_source_archive_member,
			)

	@override
	def clean(self, environment: Environment) -> None:
		try:
			shutil.rmtree(environment.archipelago_source_dir_path)
		except FileNotFoundError:
			pass

		remove_empty_tree(environment.base_build_dir_path)

	@staticmethod
	def _filter_archipelago_source_archive_member(member: TarInfo, _path: str) -> TarInfo | None:
		# All files in the archive are wrapped inside a directory.
		name: str = member.name.removeprefix(f"Archipelago-{ARCHIPELAGO_VERSION}").removeprefix("/")

		if name == "":
			return None

		if name.removeprefix(".run").removeprefix("/") != name:
			return None

		worlds_name: str = name.removeprefix("worlds/")
		if worlds_name != name:
			is_world: bool = ("/" in worlds_name) or member.isdir()

			is_generic: bool = worlds_name.removeprefix("generic").removeprefix("/") != worlds_name

			apquest_name: str = worlds_name.removeprefix("apquest").removeprefix("/")
			is_apquest: bool = apquest_name != worlds_name
			is_apquest_test: bool = is_apquest and (apquest_name.removeprefix("test").removeprefix("/") != apquest_name)

			if (is_world and not is_generic and not is_apquest) or is_apquest_test:
				return None

		if name.removeprefix("test/webhost").removeprefix("/") != name:
			return None

		return member.replace(name=name)


archipelago_source_directory_target = ArchipelagoSourceDirectoryTarget()


# endregion
# region target: archipelago virtual environment


class ArchipelagoVirtualEnvironmentTarget(Target):

	def __init__(self) -> None:
		super().__init__(
			name="archipelago_virtual_environment",
			dependencies=(archipelago_source_directory_target,),
		)

	@override
	def _is_up_to_date(self, environment: Environment) -> bool:
		return is_dir_not_empty(environment.archipelago_venv_dir_path)

	@override
	def _build(self, environment: Environment) -> None:
		env_exec_cmd: str = \
			ArchipelagoEnvBuilder(requirements_file_path=environment.archipelago_source_dir_path / "requirements.txt") \
				.create_and_get_env_exec_cmd(env_dir=environment.archipelago_venv_dir_path)

		environment.archipelago_venv_exec_cmd_file_path.parent.mkdir(parents=True, exist_ok=True)
		environment.archipelago_venv_exec_cmd_file_path.write_text(f"{env_exec_cmd}\n", encoding="utf-8")

	@override
	def clean(self, environment: Environment) -> None:
		try:
			os.remove(environment.archipelago_venv_exec_cmd_file_path)
		except FileNotFoundError:
			pass

		try:
			shutil.rmtree(environment.archipelago_venv_dir_path)
		except FileNotFoundError:
			pass

		remove_empty_tree(environment.base_build_dir_path)


archipelago_virtual_environment_target = ArchipelagoVirtualEnvironmentTarget()


class ArchipelagoEnvBuilder(EnvBuilder):
	_requirements_file_path: Path
	_env_exec_cmd: str = ""

	def __init__(self, requirements_file_path: Path) -> None:
		super().__init__(
			system_site_packages=False,
			clear=True,
			symlinks=os.name != "nt",
			upgrade=False,
			with_pip=True,
			prompt=None,
			upgrade_deps=False,
		)

		self._requirements_file_path = requirements_file_path

	def create_and_get_env_exec_cmd(self, env_dir: Path) -> str:
		self.create(env_dir)

		env_exec_cmd: str = self._env_exec_cmd

		if len(env_exec_cmd) == 0:
			raise ValueError("The property `env_exec_cmd` is empty")

		return env_exec_cmd

	@override
	def post_setup(self, context: SimpleNamespace) -> None:
		env_exec_cmd: Any = context.env_exec_cmd
		env_dir: Any = context.env_dir

		if not isinstance(env_exec_cmd, str): raise TypeError("The property `env_exec_cmd` is not a string")
		if not isinstance(env_dir, str): raise TypeError("The property `env_dir` is not a string")

		self._env_exec_cmd = env_exec_cmd
		self._install_requirements(env_dir, env_exec_cmd)

	def _install_requirements(self, env_dir: str, env_exec_cmd: str) -> None:
		print(
			"Installing the Archipelago requirements...\n" + ("=" * shutil.get_terminal_size()[0]),
			file=sys.stderr,
		)

		ArchipelagoEnvBuilder._venv_pip_install(
			env_dir=env_dir,
			env_exec_cmd=env_exec_cmd,
			args=("--upgrade", "pip"),
		)

		with tempfile.NamedTemporaryFile(
			mode="w+",
			encoding="utf-8",
			newline="\n",
			suffix=".txt",
		) as additional_requirements_file:
			additional_requirements_file.write("setuptools>=75,<81\n")  # See `ModuleUpdate.py`
			additional_requirements_file.write("pytest>=9.0.1,<10\n")  # See `ci-requirements.txt`
			additional_requirements_file.seek(0)

			args: list[str] = []

			requirements_file_path_str: str
			for requirements_file_path_str in (additional_requirements_file.name, str(self._requirements_file_path)):
				args.append("--requirement")
				args.append(requirements_file_path_str)

			ArchipelagoEnvBuilder._venv_pip_install(
				env_dir=env_dir,
				env_exec_cmd=env_exec_cmd,
				args=args,
			)

		print(
			("=" * shutil.get_terminal_size()[0]) + "\nSuccessfully installed the Archipelago requirements",
			file=sys.stderr,
		)

	@staticmethod
	def _venv_pip_install(env_dir: str, env_exec_cmd: str, args: Sequence[str]) -> None:
		# Taken from `venv.EnvBuilder` <https://github.com/python/cpython/blob/3.13/Lib/venv/__init__.py#L429-L442>

		env: dict[str, str] = os.environ.copy()
		env["VIRTUAL_ENV"] = env_dir
		env.pop("PYTHONHOME", None)
		env.pop("PYTHONPATH", None)

		process: CompletedProcess = subprocess.run(
			args=(env_exec_cmd, "-m", "pip", "install", *args),
			executable=env_exec_cmd,
			stdout=sys.stderr,
			stderr=sys.stderr,
			cwd=env_dir,
			env=env,
		)

		if process.returncode != 0:
			sys.exit(filter_subprocess_exit_status(process.returncode))


# endregion
# region target: SlotData class source file


# region slot data schema entry


class SlotDataSchemaEntryTypeData(ABC):

	@staticmethod
	@abstractmethod
	def get_python_type_name() -> str:
		raise NotImplementedError()


@final
class SlotDataSchemaEntryTypes:
	def __init__(self) -> None:
		raise NotImplementedError()

	@final
	@dataclass(frozen=True)
	class Bool(SlotDataSchemaEntryTypeData):

		@override
		@staticmethod
		def get_python_type_name() -> str:
			return "bool"

	@final
	@dataclass(frozen=True)
	class Int32(SlotDataSchemaEntryTypeData):
		min_value: int
		max_value: int

		@override
		@staticmethod
		def get_python_type_name() -> str:
			return "int"

	@final
	@dataclass(frozen=True)
	class String(SlotDataSchemaEntryTypeData):

		@override
		@staticmethod
		def get_python_type_name() -> str:
			return "str"


@final
@dataclass(frozen=True)
class SlotDataSchemaEntry:
	type_data: SlotDataSchemaEntryTypeData
	description: str | None

	def __post_init__(self):
		if self.description == "":
			raise ValueError("Slot data schema entry description must not be empty")


# endregion


@final
class SlotDataSchema:
	@final
	@enum.unique
	class _PropertyNames(StrEnum):
		MIN_VALUE = "min"
		MAX_VALUE = "max"
		FALLBACK_VALUE = "fallback"

	class _PartialEntry(ABC):
		_key: str
		_description: str | None = None

		def __init__(self, key: str) -> None:
			self._key = key

		@property
		def key(self) -> str:
			return self._key

		@property
		def description(self) -> str | None:
			return self._description

		@abstractmethod
		def init_property(self, name: str, value: str) -> bool:
			raise NotImplementedError()

		@abstractmethod
		def to_type_data(self) -> SlotDataSchemaEntryTypeData | None:
			raise NotImplementedError()

		def add_description_line(self, line: str) -> None:
			if self._description is None:
				self._description = ""
			else:
				self._description += "\n"

			self._description += line

	# region types

	@final
	class _PartialBoolEntry(_PartialEntry):
		# The APWorld code does not make use of the fallback value property, but we still validate.
		_is_fallback_initialized: bool = False

		@override
		def init_property(self, name: str, value: str) -> bool:
			if name != SlotDataSchema._PropertyNames.FALLBACK_VALUE.value:
				return False

			if self._is_fallback_initialized:
				return False

			if (value != "true") and (value != "false"):
				return False

			self._is_fallback_initialized = True
			return True

		@override
		def to_type_data(self) -> SlotDataSchemaEntryTypeData | None:
			if not self._is_fallback_initialized:
				return None

			return SlotDataSchemaEntryTypes.Bool()

	@final
	class _PartialInt32Entry(_PartialEntry):
		_min_value: int | None = None
		_max_value: int | None = None
		# The APWorld code does not make use of the fallback value property, but we still validate.
		_fallback_value: int | None = None

		@override
		def init_property(self, name: str, value: str) -> bool:
			match name:
				case SlotDataSchema._PropertyNames.MIN_VALUE.value:
					return self._init_min_value(value)
				case SlotDataSchema._PropertyNames.MAX_VALUE.value:
					return self._init_max_value(value)
				case SlotDataSchema._PropertyNames.FALLBACK_VALUE.value:
					return self._init_fallback_value(value)
				case _:
					return False

		@override
		def to_type_data(self) -> SlotDataSchemaEntryTypeData | None:
			if self._fallback_value is None:
				return None

			min_value: int = self._min_value if self._min_value is not None else -2 ** 31
			max_value: int = self._max_value if self._max_value is not None else (2 ** 31) - 1

			return SlotDataSchemaEntryTypes.Int32(min_value, max_value)

		def _init_min_value(self, min_value_str: str) -> bool:
			if self._min_value is not None:
				return False

			min_value: int | None = self._parse_string(min_value_str)
			if min_value is None:
				return False

			if (self._max_value is not None) and (min_value > self._max_value):
				return False
			if (self._fallback_value is not None) and (self._fallback_value < min_value):
				return False

			self._min_value = min_value
			return True

		def _init_max_value(self, max_value_str: str) -> bool:
			if self._max_value is not None:
				return False

			max_value: int | None = self._parse_string(max_value_str)
			if max_value is None:
				return False

			if (self._min_value is not None) and (max_value < self._min_value):
				return False
			if (self._fallback_value is not None) and (self._fallback_value > max_value):
				return False

			self._max_value = max_value
			return True

		def _init_fallback_value(self, fallback_value_str: str) -> bool:
			if self._fallback_value is not None:
				return False

			fallback_value: int | None = self._parse_string(fallback_value_str)
			if fallback_value is None:
				return False

			if (self._min_value is not None) and (fallback_value < self._min_value):
				return False
			if (self._max_value is not None) and (fallback_value > self._max_value):
				return False

			self._fallback_value = fallback_value
			return True

		@staticmethod
		def _parse_string(value_str: str) -> int | None:
			value_str = value_str.removeprefix("+").replace("+", " ")

			value: int
			try:
				value = int(value_str)
			except ValueError:
				return None

			if (value < (-2 ** 31)) or (value > ((2 ** 31) - 1)):
				return None

			return value

	@final
	class _PartialStringEntry(_PartialEntry):
		# The APWorld code does not make use of the fallback value property, but we still validate.
		_is_fallback_initialized: bool = False

		@override
		def init_property(self, name: str, value: str) -> bool:
			if name != SlotDataSchema._PropertyNames.FALLBACK_VALUE.value:
				return False

			if self._is_fallback_initialized:
				return False

			return (len(value) >= 2) and value.startswith("\"") and value.endswith("\"")

		@override
		def to_type_data(self) -> SlotDataSchemaEntryTypeData | None:
			return SlotDataSchemaEntryTypes.String()

	# endregion

	@final
	@dataclass(frozen=True)
	class _EntryStarted:
		new_entry: SlotDataSchema._PartialEntry

	@final
	@dataclass(frozen=True)
	class _EntryFinalized:
		key: str
		entry: SlotDataSchemaEntry

	@final
	@dataclass(frozen=True)
	class _InvalidSchema:
		pass

	_LineProcessingResult = _EntryStarted | _EntryFinalized | _InvalidSchema | None

	@staticmethod
	def parse_file(file_path: Path) -> Mapping[str, SlotDataSchemaEntry] | None:
		schema: dict[str, SlotDataSchemaEntry] = {}

		file: TextIOWrapper
		with open(file_path, mode="r", encoding="utf-8") as file:
			current_entry: SlotDataSchema._PartialEntry | None = None

			line: str
			for line in file:
				result: SlotDataSchema._LineProcessingResult = SlotDataSchema._process_line(line, current_entry)

				match result:
					case SlotDataSchema._EntryStarted(new_entry):
						current_entry = new_entry

					case SlotDataSchema._EntryFinalized(key, entry):
						schema[key] = entry
						current_entry = None

					case SlotDataSchema._InvalidSchema():
						return None

		return schema

	@staticmethod
	def _process_line(line: str, current_entry: _PartialEntry | None) -> _LineProcessingResult:
		comment_char_index: int = line.find("#")

		if comment_char_index >= 0:
			line = line[:comment_char_index]

		line = line.strip()
		if line == "":
			return None

		if current_entry is None:
			entry: SlotDataSchema._PartialEntry | None = SlotDataSchema._process_head_line(line)

			if entry is None:
				return SlotDataSchema._InvalidSchema()

			return SlotDataSchema._EntryStarted(entry)

		description_match: Match[str] | None = re.match(r"^\(i\)(.*)$", line)
		if description_match is not None:
			description_line: str = description_match.group(1).strip()

			if description_line == "":
				return SlotDataSchema._InvalidSchema()

			current_entry.add_description_line(description_line)
			return None

		property_match: Match[str] | None = re.match(r"^([a-z][a-z0-9_]*)\s*=\s*(.+)$", line)
		if property_match is not None:
			property_name: str = property_match.group(1)
			property_value: str = property_match.group(2).strip()

			success: bool = current_entry.init_property(property_name, property_value)
			if not success:
				return SlotDataSchema._InvalidSchema()

			return None

		if line == "}":
			type_data: SlotDataSchemaEntryTypeData | None = current_entry.to_type_data()
			if type_data is None:
				return SlotDataSchema._InvalidSchema()

			return SlotDataSchema._EntryFinalized(
				key=current_entry.key,
				entry=SlotDataSchemaEntry(type_data, current_entry.description),
			)

		return SlotDataSchema._InvalidSchema()

	@staticmethod
	def _process_head_line(line: str) -> _PartialEntry | None:
		head_match: Match[str] | None = re.match(r"^([a-z0-9_]+)\s*:\s*([a-z0-9_]+)\s*\{$", line)

		if head_match is None:
			return None

		key: str = head_match.group(1)
		type_name: str = head_match.group(2)

		match type_name:
			case "bool":
				return SlotDataSchema._PartialBoolEntry(key)
			case "int32":
				return SlotDataSchema._PartialInt32Entry(key)
			case "string":
				return SlotDataSchema._PartialStringEntry(key)
			case _:
				return None


class SlotDataClassSourceFileTarget(Target):
	def __init__(self) -> None:
		super().__init__(
			name="slot_data_class_source_file",
			dependencies=(),
		)

	@override
	def _is_up_to_date(self, environment: Environment) -> bool:
		slot_data_class_source_file_mtime: int
		try:
			slot_data_class_source_file_mtime = environment.slot_data_class_source_file_path.stat().st_mtime_ns
		except FileNotFoundError:
			return False

		slot_data_schema_file_mtime: int = environment.slot_data_schema_file_path.stat().st_mtime_ns

		return slot_data_class_source_file_mtime > slot_data_schema_file_mtime

	@override
	def _build(self, environment: Environment) -> None:
		schema: Mapping[str, SlotDataSchemaEntry] | None = \
			SlotDataSchema.parse_file(environment.slot_data_schema_file_path)

		if schema is None:
			print(f"{sys.argv[0]}: {environment.slot_data_schema_file_path}: invalid schema", file=sys.stderr)
			sys.exit(1)

		SlotDataClassSourceFileTarget._generate_file(schema, environment.slot_data_class_source_file_path)

	@staticmethod
	def _generate_file(schema: Mapping[str, SlotDataSchemaEntry], file_path: Path) -> None:
		slot_data_source_file: TextIOWrapper
		with (open(file_path, mode="w+", encoding="utf-8") as slot_data_source_file):
			slot_data_source_file.write(
				"# This file was automatically generated. DO NOT EDIT IT!\n"
				"\n"
				"from collections.abc import Mapping\n"
				"from dataclasses import dataclass\n"
				"from typing import Any, final\n"
				"\n"
				"\n"
				"@final\n"
				"@dataclass(frozen=True)\n"
				"class SlotData:\n",
			)

			key: str
			entry: SlotDataSchemaEntry

			for key, entry in schema.items():
				slot_data_source_file.write(f"\t{key}: {entry.type_data.get_python_type_name()}\n")

				if entry.description is not None:
					if "\n" in entry.description:
						slot_data_source_file.write(
							"\t\"\"\"\n" +
							("\t" + entry.description.replace("\n", "\n\t") + "\n") +
							"\t\"\"\"\n",
						)
					else:
						slot_data_source_file.write(f"\t\"\"\"{entry.description}\"\"\"\n")

				slot_data_source_file.write("\n")

			slot_data_source_file.write("\tdef __post_init__(self):\n")

			for key, entry in schema.items():
				slot_data_source_file.write(
					f"\t\tif not isinstance(self.{key}, {entry.type_data.get_python_type_name()}):\n"
					f"\t\t\traise TypeError(\"{key} must be of type {entry.type_data.get_python_type_name()}\")\n",
				)

				match entry.type_data:
					case SlotDataSchemaEntryTypes.Bool():
						pass

					case SlotDataSchemaEntryTypes.Int32(min_value, max_value):
						slot_data_source_file.write(
							f"\t\tif (self.{key} < {min_value}) or (self.{key} > {max_value}):\n"
							"\t\t\traise ValueError(\""
							f"{key} must be in the range [{min_value}, {max_value}]"
							"\")\n",
						)

					case SlotDataSchemaEntryTypes.String():
						slot_data_source_file.write(
							f"\t\tif self.{key} == \"\":\n"
							f"\t\t\traise ValueError(\"{key} must not be empty\")\n",
						)

				slot_data_source_file.write("\n")

			slot_data_source_file.write(
				"\tdef to_mapping(self) -> Mapping[str, Any]:\n"
				"\t\treturn {\n",
			)

			for key, entry in schema.items():
				slot_data_source_file.write(f"\t\t\t\"{key}\": self.{key},\n")

			slot_data_source_file.write("\t\t}\n")

	@override
	def clean(self, environment: Environment) -> None:
		try:
			os.remove(environment.slot_data_class_source_file_path)
		except FileNotFoundError:
			pass


slot_data_class_source_file_target = SlotDataClassSourceFileTarget()


# endregion
# region target: version python file


class VersionPythonFileTarget(Target):

	def __init__(self) -> None:
		super().__init__(
			name="version_python_file",
			dependencies=(),
		)

	@override
	def _is_up_to_date(self, environment: Environment) -> bool:
		version_python_file_mtime: int
		try:
			version_python_file_mtime = environment.version_python_file_path.stat().st_mtime_ns
		except FileNotFoundError:
			return False

		version_file_mtime: int = environment.version_file_path.stat().st_mtime_ns

		return version_python_file_mtime > version_file_mtime

	@override
	def _build(self, environment: Environment) -> None:
		version: str = environment.version_file_path.read_text(encoding="utf-8").strip()

		environment.version_python_file_path.write_text(
			data=f"# Generated. DO NOT EDIT!\n\nVERSION: str = \"{version}\"\n",
			encoding="utf-8",
		)

	@override
	def clean(self, environment: Environment) -> None:
		try:
			os.remove(environment.version_python_file_path)
		except FileNotFoundError:
			pass


version_python_file_target = VersionPythonFileTarget()


# endregion
# region target: manifest file


class ManifestFileTarget(Target):

	def __init__(self) -> None:
		super().__init__(
			name="manifest_file",
			dependencies=(),
		)

	@override
	def _is_up_to_date(self, environment: Environment) -> bool:
		manifest_file_mtime: int
		try:
			manifest_file_mtime = environment.manifest_file_path.stat().st_mtime_ns
		except FileNotFoundError:
			return False

		version_file_mtime: int = environment.version_file_path.stat().st_mtime_ns

		return manifest_file_mtime > version_file_mtime

	@override
	def _build(self, environment: Environment) -> None:
		version: str = environment.version_file_path.read_text(encoding="utf-8").strip()

		manifest: str = (environment.script_dir_path / "manifest.template.json") \
			.read_text(encoding="utf-8") \
			.replace("{{VERSION}}", version)

		environment.manifest_file_path.parent.mkdir(parents=True, exist_ok=True)
		environment.manifest_file_path.write_text(manifest, encoding="utf-8")

	@override
	def clean(self, environment: Environment) -> None:
		try:
			os.remove(environment.manifest_file_path)
		except FileNotFoundError:
			pass


manifest_file_target = ManifestFileTarget()


# endregion
# region target: apworld


class ApWorldTarget(Target):
	_relative_launcher_file_path: ClassVar[PurePath] = PurePath("Launcher.py")

	def __init__(self) -> None:
		super().__init__(
			name="apworld",
			dependencies=(
				archipelago_virtual_environment_target,
				slot_data_class_source_file_target,
				version_python_file_target,
				manifest_file_target,
			),
		)

	@override
	def _is_up_to_date(self, environment: Environment) -> bool:
		return False

	@override
	def _build(self, environment: Environment) -> None:
		venv_exec_cmd: str = environment.archipelago_venv_exec_cmd_file_path \
			.read_text(encoding="utf-8") \
			.removesuffix("\n")

		with TemporaryDirectory() as tmp_dir_path_str:
			tmp_dir_path = Path(tmp_dir_path_str)

			shutil.copytree(environment.archipelago_source_dir_path, tmp_dir_path, dirs_exist_ok=True)

			ApWorldTarget._make_open_folder_function_into_no_op_in_launcher_file(
				tmp_dir_path / ApWorldTarget._relative_launcher_file_path,
			)

			ApWorldTarget._remove_speedups_from_net_utils_file(tmp_dir_path / "NetUtils.py")

			def _ignore(dir_path_str: str, dir_entry_names: Sequence[str]) -> Sequence[str]:
				dir_path = Path(dir_path_str)

				ignored_names: list[str] = ["__pycache__"]

				if dir_path.samefile(environment.source_dir_path):
					ignored_names.append("test")

				return (
					# Don't know if this is necessary.
					*filter(
						lambda ignored_name: ignored_name in dir_entry_names,
						ignored_names,
					),
				)

			shutil.copytree(
				environment.source_dir_path,
				tmp_dir_path / "worlds" / APWORLD_NAME,
				ignore=_ignore,
			)

			shutil.copytree(
				environment.script_dir_path / "docs",
				tmp_dir_path / "worlds" / APWORLD_NAME / "docs",
			)

			shutil.copy(environment.manifest_file_path, tmp_dir_path / "worlds" / APWORLD_NAME / "archipelago.json")

			process: CompletedProcess = subprocess.run(
				args=(venv_exec_cmd, str(ApWorldTarget._relative_launcher_file_path), "Build APWorlds", "ULTRAKILL"),
				executable=venv_exec_cmd,
				stdout=sys.stderr,
				stderr=sys.stderr,
				cwd=tmp_dir_path,
			)

			if process.returncode != 0:
				sys.exit(filter_subprocess_exit_status(process.returncode))

			environment.apworld_output_file_path.parent.mkdir(parents=True, exist_ok=True)

			shutil.copy(
				tmp_dir_path / "build" / "apworlds" / f"{APWORLD_NAME}.apworld",
				environment.apworld_output_file_path,
			)

	@override
	def clean(self, environment: Environment) -> None:
		try:
			os.remove(environment.apworld_output_file_path)
		except FileNotFoundError:
			pass

		remove_empty_tree(environment.base_apworlds_output_dir_path)

	@staticmethod
	def _make_open_folder_function_into_no_op_in_launcher_file(file_path: Path) -> None:
		launcher_file: TextIOWrapper
		with open(file_path, mode="r+", encoding="utf-8") as launcher_file:
			tmp_file: SpooledTemporaryFile
			with SpooledTemporaryFile(
				max_size=io.DEFAULT_BUFFER_SIZE,
				mode="w+",
				encoding="utf-8",
			) as tmp_file:
				ApWorldTarget._make_open_folder_function_into_no_op(launcher_file, tmp_file)

				tmp_file.seek(0)
				launcher_file.seek(0)

				shutil.copyfileobj(tmp_file, launcher_file, length=io.DEFAULT_BUFFER_SIZE)

				launcher_file.truncate()

	@staticmethod
	def _make_open_folder_function_into_no_op(source: TextIOBase, destination: SpooledTemporaryFile) -> None:
		@final
		@enum.unique
		class State(Enum):
			NONE = enum.auto()
			AFTER_FUNC_HEAD = enum.auto()
			AFTER_FIRST_NON_BLANK_LINE = enum.auto()

		state: State = State.NONE

		line: str
		for line in source:
			match state:
				case State.NONE:
					destination.write(line)

					if re.match(r"^def\s+open_folder\s*\([^)]*\)\s*(->\s*[^:]+\s*)?:", line) is not None:
						state = State.AFTER_FUNC_HEAD

				case State.AFTER_FUNC_HEAD:
					if all(map(lambda ch: ch.isspace(), line)):
						destination.write(line)
						continue

					match: Match[str] | None = re.match(r"^(\s+).*?(\s*)$", line)

					if match is not None:
						eol: str = match.group(2)
						if eol == "":
							eol = "\n"

						destination.write(f"{match.group(1)}pass{eol}")
						state = State.AFTER_FIRST_NON_BLANK_LINE
					else:
						destination.write(line)
						state = State.NONE

				case State.AFTER_FIRST_NON_BLANK_LINE:
					if re.match(r"^\S+", line) is not None:
						destination.write(line)
						state = State.NONE

	@staticmethod
	def _remove_speedups_from_net_utils_file(file_path: Path) -> None:
		net_utils_file: TextIOWrapper
		with open(file_path, mode="r+", encoding="utf-8") as net_utils_file:
			tmp_file: SpooledTemporaryFile
			with SpooledTemporaryFile(
				max_size=io.DEFAULT_BUFFER_SIZE,
				mode="w+",
				encoding="utf-8",
			) as tmp_file:
				ApWorldTarget._remove_speedups(net_utils_file, tmp_file)

				tmp_file.seek(0)
				net_utils_file.seek(0)

				shutil.copyfileobj(tmp_file, net_utils_file, length=io.DEFAULT_BUFFER_SIZE)

				net_utils_file.truncate()

	@staticmethod
	def _remove_speedups(source: TextIOBase, destination: SpooledTemporaryFile) -> None:
		@final
		@dataclass(frozen=True)
		class AfterIfHead:
			saved_lines: str

		@final
		@dataclass(frozen=True)
		class AfterAssignment:
			indent: str

		state: None | AfterIfHead | AfterAssignment = None

		line: str
		for line in source:
			match state:
				case None:
					if re.match(r"^if\s+typing\s*.\s*TYPE_CHECKING\s*:", line) is not None:
						state = AfterIfHead(line)
					else:
						destination.write(line)

				case AfterIfHead(saved_lines):
					if all(map(lambda ch: ch.isspace(), line)):
						state = AfterIfHead(saved_lines=saved_lines + line)
						continue

					match: Match[str] | None = re.match(r"^(\s+)LocationStore\s*=\s*_LocationStore\b.*?(\s*)$", line)

					if match is not None:
						eol: str = match.group(2)
						if eol == "":
							eol = "\n"

						destination.write(f"LocationStore = _LocationStore{eol}")

						state = AfterAssignment(indent=match.group(1))
					else:
						destination.write(saved_lines)
						destination.write(line)

						state = None

				case AfterAssignment(indent):
					if re.match(rf"^({re.escape(indent)}|el(se|if)\s*:)", line) is None:
						destination.write(line)

						state = None


apworld_target = ApWorldTarget()


# endregion
# region target: test suite


class TestSuiteTarget(Target):

	def __init__(self) -> None:
		super().__init__(
			name="test",
			dependencies=(archipelago_virtual_environment_target, version_python_file_target),
		)

	@override
	def _is_up_to_date(self, environment: Environment) -> bool:
		return False

	@override
	def _build(self, environment: Environment) -> None:
		venv_exec_cmd: str = environment.archipelago_venv_exec_cmd_file_path \
			.read_text(encoding="utf-8") \
			.removesuffix("\n")

		tmp_dir_path_str: str
		with TemporaryDirectory() as tmp_dir_path_str:
			tmp_dir_path = Path(tmp_dir_path_str)

			shutil.copytree(environment.archipelago_source_dir_path, tmp_dir_path, dirs_exist_ok=True)

			shutil.copytree(environment.source_dir_path, tmp_dir_path / "worlds" / APWORLD_NAME)

			module_update_process: CompletedProcess = \
				subprocess.run(
					args=(venv_exec_cmd, "ModuleUpdate.py"),
					executable=venv_exec_cmd,
					stdout=sys.stderr,
					stderr=sys.stderr,
					cwd=tmp_dir_path,
				)
			if module_update_process.returncode != 0:
				sys.exit(filter_subprocess_exit_status(module_update_process.returncode))

			pytest_process: CompletedProcess = \
				subprocess.run(
					args=(venv_exec_cmd, "-m", "pytest"),
					executable=venv_exec_cmd,
					stdout=sys.stderr,
					stderr=sys.stderr,
					cwd=tmp_dir_path,
				)
			if pytest_process.returncode != 0:
				sys.exit(filter_subprocess_exit_status(pytest_process.returncode))

	@override
	def clean(self, environment: Environment) -> None:
		pass


test_suite_target = TestSuiteTarget()

# endregion

ALL_TARGETS: Sequence[Target] = (
	archipelago_source_archive_target,
	archipelago_source_directory_target,
	archipelago_virtual_environment_target,
	slot_data_class_source_file_target,
	version_python_file_target,
	manifest_file_target,
	apworld_target,
	test_suite_target,
)

DEFAULT_TARGETS: Sequence[Target] = (apworld_target, test_suite_target)


@final
@enum.unique
class ExecutionMode(Enum):
	BUILD = enum.auto()
	CLEAN = enum.auto()


@final
@dataclass(frozen=True)
class ParsedArguments:
	execution_mode: ExecutionMode
	targets: Sequence[Target]


def main() -> None:
	arguments: ParsedArguments = parse_arguments()

	environment = Environment()

	match arguments.execution_mode:
		case ExecutionMode.BUILD:
			for target in arguments.targets:
				target.build(environment)

		case ExecutionMode.CLEAN:
			if frozenset(arguments.targets) == frozenset(ALL_TARGETS):
				clean_all(environment)
			else:
				for target in arguments.targets:
					target.clean(environment)


def clean_all(environment: Environment) -> None:
	try:
		shutil.rmtree(environment.base_apworlds_output_dir_path)
	except FileNotFoundError:
		pass

	try:
		os.remove(environment.version_python_file_path)
	except FileNotFoundError:
		pass

	try:
		os.remove(environment.slot_data_class_source_file_path)
	except FileNotFoundError:
		pass

	try:
		shutil.rmtree(environment.base_build_dir_path)
	except FileNotFoundError:
		pass


def parse_arguments() -> ParsedArguments:
	processing_options: bool = True
	operands: list[str] = []
	first_invalid_option: str = ""

	for arg in sys.argv[1:]:
		if processing_options:
			if arg == "--":
				processing_options = False
				continue

			if arg.startswith("--"):
				opt_word: str = arg[2:]

				match opt_word:
					case "help":
						print_help_and_exit()

					case _:
						if first_invalid_option == "":
							first_invalid_option = arg
						continue

			if arg.startswith("-") and (len(arg) > 1):
				opt_chars: str = arg[1:]

				for opt_char in opt_chars:
					match opt_char:
						case "h":
							print_help_and_exit()

						case _:
							if first_invalid_option == "":
								first_invalid_option = arg
							continue

				continue

		operands.append(arg)

	if first_invalid_option != "":
		print(f"{sys.argv[0]} {first_invalid_option}: invalid option", file=sys.stderr)
		sys.exit(2)

	execution_mode: ExecutionMode
	target_names: list[str]
	if (len(operands) >= 1) and (operands[0] == "clean"):
		execution_mode = ExecutionMode.CLEAN
		target_names = operands[1:]
	else:
		execution_mode = ExecutionMode.BUILD
		target_names = operands

	targets: list[Target] = []

	for target_name in target_names:
		if target_name == "all":
			targets.extend(ALL_TARGETS)
			continue

		found_target: Target | None = None
		for target in ALL_TARGETS:
			if target.name != target_name:
				continue

			found_target = target
			break

		if found_target is None:
			print(f"{sys.argv[0]} {target_name}: no such target", file=sys.stderr)
			sys.exit(2)

		targets.append(found_target)

	if len(targets) == 0:
		targets.extend(DEFAULT_TARGETS)

	return ParsedArguments(execution_mode, targets)


def print_help_and_exit() -> Never:
	target_list_str: str = "\n".join(map(lambda target: f"* {target.name}", ALL_TARGETS))

	usage: str = f"usage: {sys.argv[0]} [clean] [(<target> | all)...]"

	print(
		f"{usage}\n"
		"    Build script for the ULTRAKILL APWorld.\n"
		"\n"
		"    <target> can be one of the following:\n"
		f"    {target_list_str.replace("\n", "\n    ")}\n"
		"\n"
		"    Specifying a target will always re-build it.\n"
		"    Dependant targets are only built if not cached.\n"
		"\n"
		f"    The default targets are {" and ".join(map(lambda target: f"\"{target.name}\"", DEFAULT_TARGETS))}.\n"
		"\n"
		"    The special target \"all\" is equivalent to specifying all targets at once.",
		file=sys.stderr,
	)

	sys.exit(0)


def remove_empty_tree(path: Path | str) -> bool:
	"""Returns whether the directory was removed."""

	try:
		directory_iterator: Iterator[DirEntry]
		with os.scandir(path) as directory_iterator:
			for entry in directory_iterator:
				if not entry.is_dir():
					return False

				removed: bool = remove_empty_tree(entry.path)
				if not removed:
					return False

		os.rmdir(path)
	except FileNotFoundError:
		pass

	return True


def is_dir_not_empty(path: Path) -> bool:
	try:
		directory_iterator: Iterator[DirEntry]
		with os.scandir(path) as directory_iterator:
			return any(directory_iterator)
	except FileNotFoundError:
		return False


def filter_subprocess_exit_status(status: int) -> int:
	return 1 if (status < 0) or (status == 2) or (status > 125) else status


if __name__ == "__main__":
	main()
