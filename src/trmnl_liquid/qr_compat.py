"""RQRCode 3.2-compatible QR mask selection for qrcode 8.2."""

from __future__ import annotations

from collections.abc import Sequence

import qrcode

_QRModules = Sequence[Sequence[bool | None]]


def _rqrcode_lost_points(modules: _QRModules) -> float:
    """Score a QR matrix exactly as rqrcode_core 2.1.0 does."""
    module_count = len(modules)
    max_index = module_count - 1

    level1 = 0
    for row in range(module_count):
        modules_row = modules[row]
        for col in range(module_count):
            same_count = 0
            dark = modules_row[col]

            if row > 0:
                row_above = modules[row - 1]
                same_count += int(col > 0 and dark == row_above[col - 1])
                same_count += int(dark == row_above[col])
                same_count += int(col < max_index and dark == row_above[col + 1])

            same_count += int(col > 0 and dark == modules_row[col - 1])
            same_count += int(col < max_index and dark == modules_row[col + 1])

            if row < max_index:
                row_below = modules[row + 1]
                same_count += int(col > 0 and dark == row_below[col - 1])
                same_count += int(dark == row_below[col])
                same_count += int(col < max_index and dark == row_below[col + 1])

            if same_count > 5:
                level1 += 3 + same_count - 5

    level2 = 0
    for row in range(max_index):
        row_current = modules[row]
        row_next = modules[row + 1]
        for col in range(max_index):
            value = row_current[col]
            if (
                value == row_next[col]
                and value == row_current[col + 1]
                and value == row_next[col + 1]
            ):
                level2 += 3

    level3 = 0
    max_start = module_count - 7 + 1
    for row in modules:
        for col in range(max_start):
            if (
                row[col]
                and not row[col + 1]
                and row[col + 2]
                and row[col + 3]
                and row[col + 4]
                and not row[col + 5]
                and row[col + 6]
            ):
                level3 += 40

    for col in range(module_count):
        for row in range(max_start):
            if (
                modules[row][col]
                and not modules[row + 1][col]
                and modules[row + 2][col]
                and modules[row + 3][col]
                and modules[row + 4][col]
                and not modules[row + 5][col]
                and modules[row + 6][col]
            ):
                level3 += 40

    dark_count = sum(cell is True for row in modules for cell in row)
    ratio = dark_count / (module_count * module_count)
    level4 = abs(100 * ratio - 50) / 5 * 10

    return level1 + level2 + level3 + level4


class RQRCodeCompatibleQRCode(qrcode.QRCode):
    """QRCode that chooses masks using rqrcode_core 2.1.0 scoring."""

    def best_mask_pattern(self) -> int:
        min_lost_point: float | None = None
        pattern = 0

        for candidate in range(8):
            self.makeImpl(True, candidate)
            lost_point = _rqrcode_lost_points(self.modules)
            if min_lost_point is None or lost_point < min_lost_point:
                min_lost_point = lost_point
                pattern = candidate

        return pattern
