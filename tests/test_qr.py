from qrcode.constants import ERROR_CORRECT_H, ERROR_CORRECT_L, ERROR_CORRECT_Q

from trmnl_liquid.qr import _select_rqrcode_matrix, render_qr_svg


def test_rqrcode_mask_selection_regressions() -> None:
    pattern, _ = _select_rqrcode_matrix("Test", ERROR_CORRECT_L)
    assert pattern == 4

    pattern, _ = _select_rqrcode_matrix("Hello world", ERROR_CORRECT_Q)
    assert pattern == 2

    pattern, _ = _select_rqrcode_matrix(
        "https://example.com/path?q=1", ERROR_CORRECT_H
    )
    assert pattern == 2


def test_qr_renderer_uses_rqrcode_svg_shape() -> None:
    svg = render_qr_svg("Test")

    assert svg.startswith('<?xml version="1.0" standalone="yes"?><svg ')
    assert 'viewBox="0 0 231 231"' in svg
    assert '<rect width="231" height="231" x="0" y="0" fill="#fff"/>' in svg
    assert '<path d="' in svg
    assert 'fill="#000" transform="translate(0,0) scale(11)"/>' in svg
