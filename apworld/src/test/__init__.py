# Copyright (c) 2023-2025 Trevor L
# SPDX-License-Identifier: MIT

from test.bases import WorldTestBase
from .. import UltrakillWorld


class UltrakillTestBase(WorldTestBase):
    game = "ULTRAKILL"
    world: UltrakillWorld
