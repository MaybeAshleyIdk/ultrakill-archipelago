#!/usr/bin/env python

# Copyright (c) 2025 MaybeAshleyIdk
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import hashlib
import http.client
import io
import platform
import shutil
import sys
import urllib.request
import xml.etree.ElementTree
from collections.abc import Generator, Iterable, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from io import BufferedRandom, BufferedReader, BufferedWriter
from pathlib import Path, PurePath
from tempfile import SpooledTemporaryFile
from typing import ClassVar, final
from xml.etree.ElementTree import Element
from zipfile import ZipFile

if sys.version_info < (3, 12, 0):
	print(f"{sys.argv[0]}: Python 3.12 required", file=sys.stderr)
	sys.exit(1)


@final
@dataclass(frozen=True)
class UltrakillAssemblyReference:
	TARGET_DIR_NAME: ClassVar[str] = "ultrakill"

	assembly_name: str
	assembly_file_name: str
	assembly_file_sha256_checksum: bytes
	base_target_dir_path: Path

	def get_target_assembly_file_path(self) -> Path:
		return self.base_target_dir_path / UltrakillAssemblyReference.TARGET_DIR_NAME / self.assembly_file_name


@final
@dataclass(frozen=True)
class PluginConfiguratorAssemblyReference:
	TARGET_DIR_NAME: ClassVar[str] = "com.eternalUnion.pluginConfigurator"

	assembly_name: str
	assembly_file_name: str
	assembly_file_sha256_checksum: bytes
	base_target_dir_path: Path
	version: str

	def get_target_assembly_file_path(self) -> Path:
		return self.base_target_dir_path / PluginConfiguratorAssemblyReference.TARGET_DIR_NAME / self.assembly_file_name


@final
@dataclass(frozen=True)
class Csproj:
	@final
	@dataclass(frozen=True)
	class _UnresolvedReference:
		include: str
		hint_path: PurePath
		sha256_checksum: bytes

	ultrakill_assembly_references: Sequence[UltrakillAssemblyReference]
	plugin_configurator_assembly_reference: PluginConfiguratorAssemblyReference

	@staticmethod
	def read() -> Csproj:
		script_dir_path: Path = Path(__file__).parent

		try:
			script_dir_path = script_dir_path.relative_to(Path.cwd())
		except ValueError:
			pass

		return Csproj._read_from(parent_dir_path=script_dir_path)

	@staticmethod
	def _read_from(parent_dir_path: Path) -> Csproj:
		file_path: Path = parent_dir_path / "UltrakillArchipelago.csproj"

		project_element: Element = xml.etree.ElementTree.parse(file_path).getroot()

		if project_element.tag != "Project":
			print(
				f"{sys.argv[0]}: {pretty_path(file_path)}: "
				f"expected <Project> root element, but got <{project_element.tag}>",
				file=sys.stderr,
			)
			sys.exit(1)

		plugin_configurator_version: str = ""
		references: list[Csproj._UnresolvedReference] = []

		child: Element
		for child in project_element:
			if child.tag != "PropertyGroup":
				references.extend(Csproj._read_references_from_item_group_element(file_path, child))
				continue

			grandchild: Element
			for grandchild in child:
				if grandchild.tag != "PluginConfiguratorVersion":
					continue

				text: str | None = grandchild.text
				if (text is not None) and (text != ""):
					plugin_configurator_version = text

		return Csproj._resolve_references(
			source_file_path=file_path,
			plugin_configurator_version=plugin_configurator_version,
			references=references,
		)

	@staticmethod
	def _read_references_from_item_group_element(
		source_file_path: PurePath,
		item_group_element: Element,
	) -> Sequence[_UnresolvedReference]:
		if item_group_element.tag != "ItemGroup":
			return ()

		references: list[Csproj._UnresolvedReference] = []

		child: Element
		for child in item_group_element:
			reference: Csproj._UnresolvedReference | None = \
				Csproj._read_reference_from_reference_element(source_file_path, child)

			if reference is not None:
				references.append(reference)

		return references

	@staticmethod
	def _read_reference_from_reference_element(
		source_file_path: PurePath,
		reference_element: Element,
	) -> _UnresolvedReference | None:
		if reference_element.tag != "Reference":
			return None

		include: str = reference_element.attrib.get("Include", "")

		if include == "":
			print(
				f"{sys.argv[0]}: {pretty_path(source_file_path)}: "
				"a <Reference> element is missing the attribute `Include`",
				file=sys.stderr,
			)
			sys.exit(1)

		hint_path: PurePath | None = None
		sha256_checksum: bytes = b""

		child: Element
		for child in reference_element:
			match child.tag:
				case "HintPath":
					hint_path_str: str | None = child.text

					if (hint_path_str is not None) and (hint_path_str != ""):
						hint_path = PurePath(hint_path_str)

				case "Sha256Checksum":
					sha256_checksum_hex: str | None = child.text

					if (sha256_checksum_hex is not None) and (sha256_checksum_hex != ""):
						sha256_checksum = bytes.fromhex(sha256_checksum_hex)

		if (hint_path is None) or (len(sha256_checksum) == 0):
			print(
				f"{sys.argv[0]}: {pretty_path(source_file_path)}: "
				"a <Reference> element is missing <HintPath> and/or <Sha256Checksum> children",
				file=sys.stderr,
			)
			sys.exit(1)

		return Csproj._UnresolvedReference(include, hint_path, sha256_checksum)

	@staticmethod
	def _resolve_references(
		source_file_path: Path,
		plugin_configurator_version: str,
		references: Iterable[_UnresolvedReference],
	) -> Csproj:
		if plugin_configurator_version == "":
			print(
				f"{sys.argv[0]}: {pretty_path(source_file_path)}: PluginConfigurator version missing",
				file=sys.stderr,
			)
			sys.exit(1)

		ultrakill_assembly_references: list[UltrakillAssemblyReference] = []
		plugin_configurator_assembly_reference: PluginConfiguratorAssemblyReference | None = None

		reference: Csproj._UnresolvedReference
		for reference in references:
			hint_path_parent: PurePath = reference.hint_path.parent
			match hint_path_parent.name:
				case UltrakillAssemblyReference.TARGET_DIR_NAME:
					ultrakill_reference = UltrakillAssemblyReference(
						assembly_name=reference.include,
						assembly_file_name=reference.hint_path.name,
						assembly_file_sha256_checksum=reference.sha256_checksum,
						base_target_dir_path=source_file_path.parent / hint_path_parent.parent,
					)
					ultrakill_assembly_references.append(ultrakill_reference)

				case PluginConfiguratorAssemblyReference.TARGET_DIR_NAME:
					plugin_configurator_assembly_reference = PluginConfiguratorAssemblyReference(
						assembly_name=reference.include,
						assembly_file_name=reference.hint_path.name,
						assembly_file_sha256_checksum=reference.sha256_checksum,
						base_target_dir_path=source_file_path.parent / hint_path_parent.parent,
						version=plugin_configurator_version,
					)

				case _:
					print(
						f"{sys.argv[0]}: {pretty_path(source_file_path)}: unknown reference: "
						f"Include=\"{reference.include}\", "
						f"HintPath=\"{reference.hint_path}\", "
						f"Sha256Checksum={reference.sha256_checksum.hex()}",
						file=sys.stderr,
					)
					sys.exit(1)

		if plugin_configurator_assembly_reference is None:
			print(
				f"{sys.argv[0]}: {pretty_path(source_file_path)}: PluginConfigurator reference missing",
				file=sys.stderr,
			)
			sys.exit(1)

		return Csproj(ultrakill_assembly_references, plugin_configurator_assembly_reference)


@final
@dataclass(frozen=True)
class AssemblyFile:
	path: Path
	reader: BufferedReader
	sha256_checksum: bytes


@final
class UltrakillAssembliesService:
	_approved_game_directory_path: Path | None = None

	@contextmanager
	def open_assembly_file(self, file_name: str) -> Generator[AssemblyFile]:
		if self._approved_game_directory_path is not None:
			assembly_file: AssemblyFile
			with UltrakillAssembliesService._open_assembly_file_in_approved_game_directory(
				approved_game_directory_path=self._approved_game_directory_path,
				assembly_file_name=file_name,
			) as assembly_file:
				yield assembly_file

			return

		result: tuple[Path, AssemblyFile] | bool
		with UltrakillAssembliesService._try_open_assembly_file_in_possible_steam_libraries(
			assembly_file_name=file_name,
		) as result:
			if isinstance(result, tuple):
				self._approved_game_directory_path = result[0]
				yield result[1]
			else:
				self._approved_game_directory_path = \
					UltrakillAssembliesService._prompt_for_approved_game_directory(
						game_directory_automatically_detected=result,
					)

				assembly_file: AssemblyFile
				with UltrakillAssembliesService._open_assembly_file_in_approved_game_directory(
					self._approved_game_directory_path,
					assembly_file_name=file_name,
				) as assembly_file:
					yield assembly_file

	@staticmethod
	@contextmanager
	def _open_assembly_file_in_approved_game_directory(
		approved_game_directory_path: Path,
		assembly_file_name: str,
	) -> Generator[AssemblyFile]:
		result: tuple[Path, BufferedReader | None]
		with UltrakillAssembliesService._try_open_assembly_file(
			approved_game_directory_path,
			assembly_file_name,
		) as result:
			assembly_file_path: Path = result[0]
			assembly_file_reader: BufferedReader | None = result[1]

			if assembly_file_reader is not None:
				yield UltrakillAssembliesService._create_assembly_file(assembly_file_path, assembly_file_reader)
				return

			print(f"{sys.argv[0]}: {pretty_path(assembly_file_path)}: no such file", file=sys.stderr)
			sys.exit(1)

	@staticmethod
	@contextmanager
	def _try_open_assembly_file_in_possible_steam_libraries(
		assembly_file_name: str,
	) -> Generator[tuple[Path, AssemblyFile] | bool]:
		"""
		Yields a tuple with the game directory path and the open assembly file or yields whether a game directory was
		automatically detected.
		"""

		possible_steam_library_path: Path
		for possible_steam_library_path in UltrakillAssembliesService._get_possible_steam_library_paths():
			result: tuple[Path, AssemblyFile] | bool
			with UltrakillAssembliesService._try_open_assembly_file_in_possible_steam_library(
				possible_steam_library_path,
				assembly_file_name,
			) as result:
				if result == False:
					# Assembly file did not exist.
					continue

				if isinstance(result, tuple):
					yield result
					return

				# User rejected the game directory.
				assert result == True

				yield True
				return

		yield False

	@staticmethod
	def _get_possible_steam_library_paths() -> Sequence[Path]:
		match platform.system():
			case "Linux":
				user_home_dir_path: Path | None = home_path_or_none()

				if user_home_dir_path is not None:
					return (
						user_home_dir_path / ".local" / "share" / "Steam",
						user_home_dir_path / ".steam" / "steam",  # This is usually a symlink to `~/.local/share/Steam`.
					)

			case "Windows":
				return (
					# Default locations:
					Path("C:\\Program Files (x86)\\Steam"),  # 64-bit
					Path("C:\\Program Files\\Steam"),  # 32-bit
					# Other possible locations:
					Path("C:\\Games\\Steam"),
					Path("D:\\steam games"),
				)

			case "Darwin":
				user_home_dir_path: Path | None = home_path_or_none()

				if user_home_dir_path is not None:
					# <https://www.guidingtech.com/where-are-steam-games-stored/>
					# <https://www.easeus.com/data-recovery/where-are-steam-games-stored.html#2>
					return (user_home_dir_path / "Library" / "Application Support" / "Steam",)

		return ()

	@staticmethod
	@contextmanager
	def _try_open_assembly_file_in_possible_steam_library(
		possible_steam_library_path: Path,
		assembly_file_name: str,
	) -> Generator[tuple[Path, AssemblyFile] | bool]:
		"""
		If the assembly file did not exist, yields `False`.
		Other yield values indicate that the assembly file *did* exist.
		Yields a tuple with the game directory path and the open assembly file if the game directory in the given
		Steam library was approved by the user.
		"""

		game_directory_path: Path = possible_steam_library_path / "steam""apps" / "common" / "ULTRAKILL"

		result: tuple[Path, BufferedReader | None]
		with UltrakillAssembliesService._try_open_assembly_file(game_directory_path, assembly_file_name) as result:
			assembly_file_path: Path = result[0]
			assembly_file_reader: BufferedReader | None = result[1]

			if assembly_file_reader is None:
				yield False
				return

			print(
				f"Automatically detected the ULTRAKILL game directory as \"{pretty_path(game_directory_path)}\".\n"
				"Is this correct? [Y/n] ",
				end="",
				file=sys.stderr,
			)

			answer: str

			try:
				answer = input()
			except EOFError:
				answer = ""
			except KeyboardInterrupt:
				print("\nAborted.", file=sys.stderr)
				sys.exit(3)

			answer = answer.strip().lower()
			if (answer == "") or answer.startswith("y"):
				assembly_file: AssemblyFile = \
					UltrakillAssembliesService._create_assembly_file(
						assembly_file_path,
						assembly_file_reader,
					)
				yield game_directory_path, assembly_file
				return

			yield True

	@staticmethod
	def _prompt_for_approved_game_directory(game_directory_automatically_detected: bool) -> Path:
		prompt: str
		if game_directory_automatically_detected:
			prompt = "Enter the correct ULTRAKILL game directory path: "
		else:
			prompt = ("Could not automatically detect the ULTRAKILL game directory.\n"
			          "Please manually enter the path of it: ")

		print(prompt, end="", file=sys.stderr)

		approved_game_directory_path_str: str

		try:
			approved_game_directory_path_str = input()
		except EOFError:
			approved_game_directory_path_str = ""
		except KeyboardInterrupt:
			print("\nAborted.", file=sys.stderr)
			sys.exit(3)

		if approved_game_directory_path_str == "":
			print("Aborted.", file=sys.stderr)
			sys.exit(3)

		return Path(approved_game_directory_path_str).expanduser()

	@staticmethod
	def _create_assembly_file(path: Path, reader: BufferedReader) -> AssemblyFile:
		sha256_checksum: bytes = hashlib.file_digest(reader, "sha256").digest()
		reader.seek(0)

		return AssemblyFile(path, reader, sha256_checksum)

	@staticmethod
	@contextmanager
	def _try_open_assembly_file(
		game_directory_path: Path,
		assembly_file_name: str,
	) -> Generator[tuple[Path, BufferedReader | None]]:
		assembly_file_path: Path = game_directory_path / "ULTRAKILL_Data" / "Managed" / assembly_file_name

		assembly_file_reader: BufferedReader | None = None
		try:
			try:
				assembly_file_reader = open(assembly_file_path, "rb")
			except FileNotFoundError:
				pass

			yield assembly_file_path, assembly_file_reader
		finally:
			if assembly_file_reader is not None:
				assembly_file_reader.close()


def main() -> None:
	match sys.argv[1:]:
		case []:
			check_integrity_and_update_assemblies()

		case ["update-ultrakill"]:
			update_ultrakill_assembly_files()

		case ["update-plugin-configurator"]:
			update_plugin_configurator_assembly_file()

		case _:
			print(f"{sys.argv[0]}: usage error", file=sys.stderr)
			sys.exit(2)


# region get missing assemblies and check integrity


def check_integrity_and_update_assemblies() -> None:
	csproj: Csproj = Csproj.read()

	check_integrity_and_update_assemblies_internal_recursive(
		ultrakill_assemblies_service=UltrakillAssembliesService(),
		unopened_ultrakill_assembly_references=csproj.ultrakill_assembly_references,
		opened_ultrakill_assemblies=(),
		plugin_configurator_assembly_reference=csproj.plugin_configurator_assembly_reference,
	)


def check_integrity_and_update_assemblies_internal_recursive(
	ultrakill_assemblies_service: UltrakillAssembliesService,
	unopened_ultrakill_assembly_references: Sequence[UltrakillAssemblyReference],
	opened_ultrakill_assemblies: Sequence[tuple[UltrakillAssemblyReference, AssemblyFile]],
	plugin_configurator_assembly_reference: PluginConfiguratorAssemblyReference,
) -> None:
	if len(unopened_ultrakill_assembly_references) > 0:
		ultrakill_assembly_reference: UltrakillAssemblyReference = unopened_ultrakill_assembly_references[0]

		assembly_file: AssemblyFile
		# PyCharm false positive:
		# noinspection PyArgumentList
		with ultrakill_assemblies_service.open_assembly_file(
			ultrakill_assembly_reference.assembly_file_name,
		) as assembly_file:
			check_integrity_and_update_assemblies_internal_recursive(
				ultrakill_assemblies_service=ultrakill_assemblies_service,
				unopened_ultrakill_assembly_references=unopened_ultrakill_assembly_references[1:],
				opened_ultrakill_assemblies=(
					*opened_ultrakill_assemblies,
					(ultrakill_assembly_reference, assembly_file),
				),
				plugin_configurator_assembly_reference=plugin_configurator_assembly_reference,
			)

		return

	check_integrity_and_update_assemblies_internal_final(
		opened_ultrakill_assemblies,
		plugin_configurator_assembly_reference,
	)


def check_integrity_and_update_assemblies_internal_final(
	ultrakill_assemblies: Sequence[tuple[UltrakillAssemblyReference, AssemblyFile]],
	plugin_configurator_assembly_reference: PluginConfiguratorAssemblyReference,
) -> None:
	check_ultrakill_assemblies_integrity(ultrakill_assemblies)

	plugin_configurator_assembly: PluginConfiguratorAssembly
	with open_plugin_configurator_assembly(
		plugin_configurator_assembly_reference.version,
	) as plugin_configurator_assembly:
		check_plugin_configurator_assembly_integrity(
			plugin_configurator_assembly_reference,
			plugin_configurator_assembly,
		)

		update_assemblies(ultrakill_assemblies, plugin_configurator_assembly_reference, plugin_configurator_assembly)


def check_ultrakill_assemblies_integrity(assemblies: Sequence[tuple[UltrakillAssemblyReference, AssemblyFile]]) -> None:
	invalid_assemblies: Sequence[tuple[UltrakillAssemblyReference, AssemblyFile]] = (
		*filter(
			lambda ultrakill_assembly: \
				ultrakill_assembly[1].sha256_checksum != ultrakill_assembly[0].assembly_file_sha256_checksum,
			assemblies,
		),
	)

	if len(invalid_assemblies) == 0:
		return

	invalid_assemblies_str: str = "\n".join(
		map(
			lambda invalid_assembly: " * " + pretty_path(invalid_assembly[1].path),
			invalid_assemblies,
		),
	)

	print(
		"\nThe following ULTRAKILL assembly files have unexpected SHA-256 checksums:\n" +
		invalid_assemblies_str +
		"\nThis most likely means that the game directory contains an unexpected version of ULTRAKILL.\n"
		"Refer to the readme file how to update the ULTRAKILL target version.",
		file=sys.stderr,
	)

	sys.exit(1)


def check_plugin_configurator_assembly_integrity(
	assembly_reference: PluginConfiguratorAssemblyReference,
	assembly: PluginConfiguratorAssembly,
) -> None:
	if assembly.file_sha256_checksum == assembly_reference.assembly_file_sha256_checksum:
		return

	terminal_width: int = shutil.get_terminal_size()[0]

	separator_exclamation_marks_count: int = max(0, terminal_width - 9)
	separator_exclamation_marks_count_half: int = separator_exclamation_marks_count // 2

	separator: str = (("!" * separator_exclamation_marks_count_half) +
	                  " WARNING " +
	                  ("!" * (separator_exclamation_marks_count - separator_exclamation_marks_count_half)))
	print(
		f"\n{separator}\n\n"
		"The downloaded UKPluginConfigurator assembly file's SHA-256 checksum is not what is expected!\n"
		f"Actual:   {assembly.file_sha256_checksum.hex()}\n"
		f"Expected: {assembly_reference.assembly_file_sha256_checksum.hex()}\n"
		"\n"
		"This may be due to various reasons:\n"
		"\n"
		"* The UKPluginConfigurator version was changed, but the expected SHA-256 checksum was not updated "
		"(most likely)\n"
		"\n"
		"* The UKPluginConfigurator ZIP archive failed to properly download and got corrupted, "
		"possibly due to a spotty internet connection.\n"
		"  Please make sure that there is a stable internet connection and then try again\n"
		"\n"
		f"* The UKPluginConfigurator author intentionally re-released version {assembly_reference.version} or "
		"the UKPluginConfigurator GitHub repository was hijacked by bad actors that try to share malware. "
		"(both unlikely)\n"
		"  In either cases, please get in contact with the UKPluginConfigurator author to get clarifications as to "
		"what happened\n"
		f"\n{separator}",
		file=sys.stderr,
	)

	sys.exit(1)


def update_assemblies(
	ultrakill_assemblies: Sequence[tuple[UltrakillAssemblyReference, AssemblyFile]],
	plugin_configurator_assembly_reference: PluginConfiguratorAssemblyReference,
	plugin_configurator_assembly: PluginConfiguratorAssembly,
) -> None:
	for ultrakill_assembly in ultrakill_assemblies:
		ultrakill_target_assembly_file_path: Path = ultrakill_assembly[0].get_target_assembly_file_path()
		ultrakill_target_assembly_file_path.parent.mkdir(parents=True, exist_ok=True)

		ultrakill_target_assembly_file: BufferedWriter
		with open(ultrakill_target_assembly_file_path, mode="wb") as ultrakill_target_assembly_file:
			# <https://youtrack.jetbrains.com/issue/PY-81830>
			# noinspection PyTypeChecker
			shutil.copyfileobj(ultrakill_assembly[1].reader, ultrakill_target_assembly_file)

	plugin_configurator_target_assembly_file_path: Path = \
		plugin_configurator_assembly_reference.get_target_assembly_file_path()
	plugin_configurator_target_assembly_file_path.parent.mkdir(parents=True, exist_ok=True)

	plugin_configurator_target_assembly_file: BufferedWriter
	with open(plugin_configurator_target_assembly_file_path, mode="wb") as plugin_configurator_target_assembly_file:
		# <https://youtrack.jetbrains.com/issue/PY-81830>
		# noinspection PyTypeChecker
		shutil.copyfileobj(plugin_configurator_assembly.file, plugin_configurator_target_assembly_file)

	print("\nDone.", file=sys.stderr)


# endregion
# region Updating ULTRAKILL assembly files


@final
@dataclass(frozen=True)
class UpdatedUltrakillAssemblyFileInfo:
	source_file_path: Path
	target_file_path: Path
	file_sha256_checksum: bytes


def update_ultrakill_assembly_files() -> None:
	csproj: Csproj = Csproj.read()

	assemblies_service = UltrakillAssembliesService()

	updated_assembly_file_info_list: list[UpdatedUltrakillAssemblyFileInfo] = []

	assembly_reference: UltrakillAssemblyReference
	for assembly_reference in csproj.ultrakill_assembly_references:
		info: UpdatedUltrakillAssemblyFileInfo = update_ultrakill_assembly_file(assemblies_service, assembly_reference)
		updated_assembly_file_info_list.append(info)

	print_ultrakill_assembly_file_info_list(updated_assembly_file_info_list)


def update_ultrakill_assembly_file(
	assemblies_service: UltrakillAssembliesService,
	assembly_reference: UltrakillAssemblyReference,
) -> UpdatedUltrakillAssemblyFileInfo:
	source_assembly_file: AssemblyFile
	# PyCharm false positive:
	# noinspection PyArgumentList
	with assemblies_service.open_assembly_file(assembly_reference.assembly_file_name) as source_assembly_file:
		target_assembly_file_path: Path = assembly_reference.get_target_assembly_file_path()
		target_assembly_file_path.parent.mkdir(parents=True, exist_ok=True)

		target_assembly_file: BufferedWriter
		with open(target_assembly_file_path, mode="wb") as target_assembly_file:
			# <https://youtrack.jetbrains.com/issue/PY-81830>
			# noinspection PyTypeChecker
			shutil.copyfileobj(source_assembly_file.reader, target_assembly_file)

		return UpdatedUltrakillAssemblyFileInfo(
			source_assembly_file.path,
			target_assembly_file_path,
			source_assembly_file.sha256_checksum,
		)


def print_ultrakill_assembly_file_info_list(info_list: Sequence[UpdatedUltrakillAssemblyFileInfo]) -> None:
	did_print: bool = \
		print_table_if_fits_on_terminal(
			head_row=("Source Assembly File", "Target Assembly File", "SHA-256 Checksum"),
			body_rows=(
				*(
					(
						pretty_path(info.source_file_path),
						pretty_path(info.target_file_path),
						info.file_sha256_checksum.hex(),
					)
					for info
					in info_list
				),
			),
		)
	if did_print:
		return

	s = ("\n\n" + ("=" * shutil.get_terminal_size()[0]) + "\n\n").join(
		map(
			lambda info: \
				f"{pretty_path(info.source_file_path)}\n"
				"\t=>\n"
				f"{pretty_path(info.target_file_path)}\n"
				"---\n"
				f"SHA-256 Checksum:\n{info.file_sha256_checksum.hex()}",
			info_list,
		),
	)

	print(file=sys.stderr)  # Separator between game directory prompt and output
	print(s)


# endregion
# region Updating PluginConfigurator assembly file


@final
@dataclass(frozen=True)
class UpdatedPluginConfiguratorAssemblyFileInfo:
	source_zip_url: str
	target_file_path: Path
	assembly_file_sha256_checksum: bytes


def update_plugin_configurator_assembly_file() -> None:
	info: UpdatedPluginConfiguratorAssemblyFileInfo = download_plugin_configurator_and_replace_assembly_file()
	print_plugin_configurator_update_info(info)


def download_plugin_configurator_and_replace_assembly_file() -> UpdatedPluginConfiguratorAssemblyFileInfo:
	csproj: Csproj = Csproj.read()

	target_assembly_file_path: Path = csproj.plugin_configurator_assembly_reference.get_target_assembly_file_path()

	assembly: PluginConfiguratorAssembly
	with open_plugin_configurator_assembly(version=csproj.plugin_configurator_assembly_reference.version) as assembly:
		target_assembly_file_path.parent.mkdir(parents=True, exist_ok=True)

		target_assembly_file: BufferedRandom
		with open(target_assembly_file_path, mode="w+b") as target_assembly_file:
			# <https://youtrack.jetbrains.com/issue/PY-81830>
			# noinspection PyTypeChecker
			shutil.copyfileobj(
				assembly.file,
				target_assembly_file,
				length=io.DEFAULT_BUFFER_SIZE,
			)

			return UpdatedPluginConfiguratorAssemblyFileInfo(
				assembly.source_zip_url,
				target_assembly_file_path,
				assembly.file_sha256_checksum,
			)


def print_plugin_configurator_update_info(info: UpdatedPluginConfiguratorAssemblyFileInfo) -> None:
	source_zip_url: str = info.source_zip_url
	pretty_target_assembly_file_path: str = pretty_path(info.target_file_path)
	sha256_checksum_hex: str = info.assembly_file_sha256_checksum.hex()

	did_print: bool

	did_print = \
		print_table_if_fits_on_terminal(
			head_row=("Source URL", "Target Assembly File", "SHA-256 Checksum"),
			body_rows=((source_zip_url, pretty_target_assembly_file_path, sha256_checksum_hex),),
		)
	if did_print:
		return

	did_print = \
		print_if_all_lines_fit_on_terminal(
			f"          Source URL:  {source_zip_url}\n"
			f"Target Assembly File:  {pretty_target_assembly_file_path}\n"
			f"    SHA-256 Checksum:  {sha256_checksum_hex}",
		)
	if did_print:
		return

	print(
		f"Source URL:\n{source_zip_url}\n---\n"
		f"Target Assembly File:\n{pretty_target_assembly_file_path}\n---\n"
		f"SHA-256 Checksum:\n{sha256_checksum_hex}",
	)


# endregion


@final
@dataclass(frozen=True)
class PluginConfiguratorAssembly:
	source_zip_url: str
	file: SpooledTemporaryFile
	file_sha256_checksum: bytes


@contextmanager
def open_plugin_configurator_assembly(version: str) -> Generator[PluginConfiguratorAssembly]:
	source_zip_url: str = ("https://github.com/eternalUnion/UKPluginConfigurator/releases/download/"
	                       f"{version}/EternalsTeam-PluginConfigurator-{version}.zip")

	source_zip_file_raw: SpooledTemporaryFile
	with SpooledTemporaryFile(max_size=io.DEFAULT_BUFFER_SIZE, mode="r+b") as source_zip_file_raw:
		source_zip: http.client.HTTPResponse
		with urllib.request.urlopen(source_zip_url) as source_zip:
			# <https://youtrack.jetbrains.com/issue/PY-81830>
			# noinspection PyTypeChecker
			shutil.copyfileobj(source_zip, source_zip_file_raw, length=io.DEFAULT_BUFFER_SIZE)
		source_zip_file_raw.seek(0)

		source_zip_file: ZipFile
		with ZipFile(source_zip_file_raw) as source_zip_file:
			with source_zip_file.open("plugins/PluginConfigurator/PluginConfigurator.dll") as assembly_source:
				assembly_file: SpooledTemporaryFile
				with SpooledTemporaryFile(max_size=io.DEFAULT_BUFFER_SIZE, mode="r+b") as assembly_file:
					# <https://youtrack.jetbrains.com/issue/PY-81830>
					# noinspection PyTypeChecker
					shutil.copyfileobj(assembly_source, assembly_file, length=io.DEFAULT_BUFFER_SIZE)
					assembly_file.seek(0)

					assembly_file_sha256_checksum: bytes = hashlib.file_digest(assembly_file, "sha256").digest()
					assembly_file.seek(0)

					yield PluginConfiguratorAssembly(source_zip_url, assembly_file, assembly_file_sha256_checksum)


def print_table_if_fits_on_terminal(head_row: Sequence[str], body_rows: Sequence[Sequence[str]]) -> bool:
	columns_count: int = len(head_row)

	body_row: Sequence[str]
	for body_row in body_rows:
		if len(body_row) != columns_count:
			raise ValueError("Each body row must have the same length as the head row")

	max_cell_lengths: Sequence[int] = (
		*map(
			lambda column_index: max(
				map(
					lambda row: len(row[column_index]),
					(head_row, *body_rows),
				),
			),
			range(columns_count),
		),
	)

	def create_horizontal_line(begin: str, middle: str, end: str) -> str:
		line: str = begin

		line += middle.join(
			map(
				lambda max_cell_length: "─" * (max_cell_length + 2),
				max_cell_lengths,
			),
		)

		line += end

		return line

	def create_row_str(row: Sequence[str]) -> str:
		row_str: str = "│ "

		row_str += " │ ".join(
			map(
				lambda pair: pair[1] + (" " * (max_cell_lengths[pair[0]] - len(pair[1]))),
				enumerate(row),
			),
		)

		row_str += " │"
		return row_str

	table_str: str = ""

	table_str += create_horizontal_line("┌", "┬", "┐") + "\n"
	table_str += create_row_str(head_row) + "\n"
	table_str += create_horizontal_line("├", "┼", "┤") + "\n"

	body_row: Sequence[str]
	for body_row in body_rows:
		table_str += create_row_str(body_row) + "\n"

	table_str += create_horizontal_line("└", "┴", "┘")

	return print_if_all_lines_fit_on_terminal(table_str)


def print_if_all_lines_fit_on_terminal(string: str) -> bool:
	max_line_length: int = max(map(len, string.splitlines()))

	terminal_width: int = shutil.get_terminal_size()[0]

	if max_line_length > terminal_width:
		return False

	print(string)
	return True


def pretty_path(path: PurePath) -> str:
	relative_path: PurePath | None
	try:
		relative_path = path.relative_to(Path.cwd())
	except ValueError:
		relative_path = None
	if relative_path is not None:
		return str(relative_path)

	home_path: Path | None = home_path_or_none()

	if (home_path is not None) and home_path.is_absolute():
		try:
			relative_path = path.relative_to(home_path)
		except ValueError:
			relative_path = None

		if relative_path is not None:
			path = PurePath("~") / relative_path

	return str(path)


def home_path_or_none() -> Path | None:
	path: Path | None
	try:
		path = Path.home()
	except RuntimeError:
		path = None
	return path


if __name__ == "__main__":
	main()
