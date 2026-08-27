"""QR rendering compatible with RQRCode 3.2 / rqrcode_core 2.1.

Compatibility references:
- TRMNL 0.8.2 ``qr_code`` filter:
  https://github.com/usetrmnl/trmnl-liquid/blob/0.8.2/lib/trmnl/liquid/filters.rb
- rqrcode_core 2.1.0 mask scoring:
  https://github.com/whomwah/rqrcode_core/blob/v2.1.0/lib/rqrcode_core/qrcode/qr_util.rb
- RQRCode 3.2.0 SVG/path serializer:
  https://github.com/whomwah/rqrcode/blob/v3.2.0/lib/rqrcode/export/svg.rb
- python-qrcode 8.2 public ``mask_pattern`` API:
  https://github.com/lincolnloop/python-qrcode/blob/v8.2/qrcode/main.py
"""

from __future__ import annotations

from collections.abc import Sequence

import qrcode
from qrcode.constants import ERROR_CORRECT_H, ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q

_QRMatrix = Sequence[Sequence[bool]]
_Edge = tuple[int, int, int]
_ERROR_CORRECTION = {
    "l": ERROR_CORRECT_L,
    "m": ERROR_CORRECT_M,
    "q": ERROR_CORRECT_Q,
    "h": ERROR_CORRECT_H,
}


def _rqrcode_lost_points(modules: _QRMatrix) -> float:
    """Score a candidate mask using rqrcode_core 2.1.0 rules.

    Reference:
    https://github.com/whomwah/rqrcode_core/blob/v2.1.0/lib/rqrcode_core/qrcode/qr_util.rb
    """
    module_count = len(modules)
    max_index = module_count - 1

    level1 = 0
    for row_index in range(module_count):
        modules_row = modules[row_index]
        for col in range(module_count):
            same_count = 0
            dark = modules_row[col]

            if row_index > 0:
                row_above = modules[row_index - 1]
                same_count += int(col > 0 and dark == row_above[col - 1])
                same_count += int(dark == row_above[col])
                same_count += int(col < max_index and dark == row_above[col + 1])

            same_count += int(col > 0 and dark == modules_row[col - 1])
            same_count += int(col < max_index and dark == modules_row[col + 1])

            if row_index < max_index:
                row_below = modules[row_index + 1]
                same_count += int(col > 0 and dark == row_below[col - 1])
                same_count += int(dark == row_below[col])
                same_count += int(col < max_index and dark == row_below[col + 1])

            if same_count > 5:
                level1 += 3 + same_count - 5

    level2 = 0
    for row_index in range(max_index):
        row_current = modules[row_index]
        row_next = modules[row_index + 1]
        for col in range(max_index):
            value = row_current[col]
            if (
                value == row_next[col]
                and value == row_current[col + 1]
                and value == row_next[col + 1]
            ):
                level2 += 3

    level3 = 0
    max_start = module_count - 6
    for modules_row in modules:
        for col in range(max_start):
            if (
                modules_row[col]
                and not modules_row[col + 1]
                and modules_row[col + 2]
                and modules_row[col + 3]
                and modules_row[col + 4]
                and not modules_row[col + 5]
                and modules_row[col + 6]
            ):
                level3 += 40

    for col in range(module_count):
        for row_index in range(max_start):
            if (
                modules[row_index][col]
                and not modules[row_index + 1][col]
                and modules[row_index + 2][col]
                and modules[row_index + 3][col]
                and modules[row_index + 4][col]
                and not modules[row_index + 5][col]
                and modules[row_index + 6][col]
            ):
                level3 += 40

    dark_count = sum(cell for modules_row in modules for cell in modules_row)
    ratio = dark_count / (module_count * module_count)
    level4 = abs(100 * ratio - 50) / 5 * 10

    return level1 + level2 + level3 + level4


def _mask_evaluation_matrix(modules: _QRMatrix, version: int) -> list[list[bool]]:
    """Return the matrix RQRCode scores while selecting a mask.

    Both RQRCode and python-qrcode temporarily suppress format/version bits when
    evaluating masks. python-qrcode exposes fixed-mask generation publicly through
    ``mask_pattern`` but not its internal test matrix, so derive the test matrix from
    the generated candidate by clearing only those reserved fields.

    Ruby reference:
    https://github.com/whomwah/rqrcode_core/blob/v2.1.0/lib/rqrcode_core/qrcode/qr_code.rb
    Python reference:
    https://github.com/lincolnloop/python-qrcode/blob/v8.2/qrcode/main.py
    """
    candidate = [list(row) for row in modules]
    module_count = len(candidate)

    for index in range(15):
        if index < 6:
            row = index
        elif index < 8:
            row = index + 1
        else:
            row = module_count - 15 + index
        candidate[row][8] = False

    for index in range(15):
        if index < 8:
            col = module_count - index - 1
        elif index < 9:
            col = 15 - index
        else:
            col = 14 - index
        candidate[8][col] = False

    candidate[module_count - 8][8] = False

    if version >= 7:
        for index in range(18):
            candidate[index // 3][index % 3 + module_count - 11] = False
            candidate[index % 3 + module_count - 11][index // 3] = False

    return candidate


def _make_candidate(
    data: str, error_correction: int, mask_pattern: int
) -> tuple[list[list[bool]], int]:
    """Build a fixed-mask QR using python-qrcode's public constructor API.

    Reference:
    https://github.com/lincolnloop/python-qrcode/blob/v8.2/qrcode/main.py
    """
    qr = qrcode.QRCode(
        version=None,
        error_correction=error_correction,
        box_size=1,
        border=0,
        mask_pattern=mask_pattern,
    )
    qr.add_data(data)
    qr.make(fit=True)
    return [[bool(cell) for cell in row] for row in qr.get_matrix()], qr.version


def _select_rqrcode_matrix(data: str, error_correction: int) -> tuple[int, list[list[bool]]]:
    """Generate the matrix chosen by rqrcode_core's mask-selection algorithm.

    Reference:
    https://github.com/whomwah/rqrcode_core/blob/v2.1.0/lib/rqrcode_core/qrcode/qr_code.rb
    """
    best_pattern = 0
    best_score: float | None = None
    best_matrix: list[list[bool]] | None = None

    for mask_pattern in range(8):
        matrix, version = _make_candidate(data, error_correction, mask_pattern)
        score = _rqrcode_lost_points(_mask_evaluation_matrix(matrix, version))
        if best_score is None or score < best_score:
            best_pattern = mask_pattern
            best_score = score
            best_matrix = matrix

    assert best_matrix is not None
    return best_pattern, best_matrix


def _qr_path(modules: list[list[bool]]) -> str:
    """Serialize modules using RQRCode 3.2's SVG path algorithm.

    Reference:
    https://github.com/whomwah/rqrcode/blob/v3.2.0/lib/rqrcode/export/svg.rb
    """
    dir_up, dir_down, dir_left, dir_right = range(4)
    deltas = ((0, -1), (0, 1), (-1, 0), (1, 0))
    commands = ("v-", "v", "h-", "h")

    module_count = len(modules)
    matrix_size = module_count + 1
    edge_matrix: list[list[list[_Edge] | None]] = [
        [None for _ in range(matrix_size)] for _ in range(matrix_size)
    ]
    edge_count = 0

    def add_edge(x: int, y: int, direction: int) -> None:
        nonlocal edge_count
        cell = edge_matrix[y][x]
        if cell is None:
            cell = []
            edge_matrix[y][x] = cell
        cell.append((x, y, direction))
        edge_count += 1

    for row_index in range(module_count + 1):
        for col_index in range(module_count):
            above = row_index > 0 and modules[row_index - 1][col_index]
            below = row_index < module_count and modules[row_index][col_index]
            if above and not below:
                add_edge(col_index + 1, row_index, dir_left)
            elif not above and below:
                add_edge(col_index, row_index, dir_right)

    for row_index in range(module_count):
        for col_index in range(module_count + 1):
            left = col_index > 0 and modules[row_index][col_index - 1]
            right = col_index < module_count and modules[row_index][col_index]
            if left and not right:
                add_edge(col_index, row_index, dir_down)
            elif not left and right:
                add_edge(col_index, row_index + 1, dir_up)

    path_parts: list[str] = []
    search_y = 0
    search_x = 0

    while edge_count > 0:
        start_edge: _Edge | None = None
        found_y = search_y
        found_x = search_x
        for y in range(search_y, matrix_size):
            start_col = search_x if y == search_y else 0
            for x in range(start_col, matrix_size):
                cell = edge_matrix[y][x]
                if cell:
                    start_edge = cell[0]
                    found_y = y
                    found_x = x
                    break
            if start_edge is not None:
                break

        if start_edge is None:
            break

        search_y = found_y
        search_x = found_x
        path = f"M{start_edge[0]} {start_edge[1]}"
        current_edge: _Edge | None = start_edge
        current_dir: int | None = None
        current_count = 0

        while current_edge is not None:
            x, y, direction = current_edge
            cell = edge_matrix[y][x]
            assert cell is not None
            cell.remove(current_edge)
            if not cell:
                edge_matrix[y][x] = None
            edge_count -= 1

            if direction == current_dir:
                current_count += 1
            else:
                if current_dir is not None:
                    path += commands[current_dir] + str(current_count)
                current_dir = direction
                current_count = 1

            dx, dy = deltas[direction]
            next_cell = edge_matrix[y + dy][x + dx]
            current_edge = next_cell[0] if next_cell else None

        path_parts.append(path + "z")

    return "".join(path_parts)


def render_qr_svg(
    data: object,
    size: int = 11,
    level: object = "",
    view: object = "responsive",
) -> str:
    """Render the SVG produced by TRMNL Liquid 0.8.2's ``qr_code`` filter.

    TRMNL reference:
    https://github.com/usetrmnl/trmnl-liquid/blob/0.8.2/lib/trmnl/liquid/filters.rb
    RQRCode SVG reference:
    https://github.com/whomwah/rqrcode/blob/v3.2.0/lib/rqrcode/export/svg.rb
    """
    level_name = str(level).lower()
    error_correction = _ERROR_CORRECTION.get(level_name, ERROR_CORRECT_H)
    _, modules = _select_rqrcode_matrix(str(data), error_correction)

    module_size = int(size)
    width = len(modules) * module_size
    height = width
    if str(view) == "responsive":
        dimensions = f'viewBox="0 0 {width} {height}"'
    else:
        dimensions = f'width="{width}" height="{height}"'

    attributes = " ".join(
        (
            'version="1.1"',
            'xmlns="http://www.w3.org/2000/svg"',
            'xmlns:xlink="http://www.w3.org/1999/xlink"',
            'xmlns:ev="http://www.w3.org/2001/xml-events"',
            dimensions,
            'shape-rendering="crispEdges"',
            'class="qr-code"',
        )
    )
    dimension = max(width, height)
    background = (
        f'<rect width="{dimension}" height="{dimension}" x="0" y="0" fill="#fff"/>'
    )
    path = (
        f'<path d="{_qr_path(modules)}" fill="#000" '
        f'transform="translate(0,0) scale({module_size})"/>'
    )
    return (
        '<?xml version="1.0" standalone="yes"?>'
        f"<svg {attributes}>{background}{path}</svg>"
    )
