from qrcode.constants import ERROR_CORRECT_H, ERROR_CORRECT_L, ERROR_CORRECT_Q

from trmnl_liquid.qr_compat import RQRCodeCompatibleQRCode


def selected_mask(data: str, level: int) -> int:
    qr = RQRCodeCompatibleQRCode(
        version=None,
        error_correction=level,
        box_size=1,
        border=0,
    )
    qr.add_data(data)
    qr.best_fit()
    return qr.best_mask_pattern()


def test_rqrcode_mask_selection_regressions() -> None:
    assert selected_mask("Test", ERROR_CORRECT_L) == 4
    assert selected_mask("Hello world", ERROR_CORRECT_Q) == 2
    assert selected_mask("https://example.com/path?q=1", ERROR_CORRECT_H) == 2
