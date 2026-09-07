from PyQt6.QtWidgets import QMessageBox

from negpy.kernel.system.i18n import tr


def confirm_unload(parent, *, clear_all: bool = False, count: int = 1) -> bool:
    """Ask the user to confirm removing image(s) from the session.

    Unloading only drops the frames from the current list — saved edits stay in the
    database keyed by content hash — but re-adding a large roll is tedious, and an
    accidental Clear All is destructive to the working set, so we gate it behind a
    prompt. Enter confirms (default button); Esc cancels.
    """
    if clear_all:
        title = tr("Clear All")
        text = tr("Remove all loaded images from the session?")
    elif count > 1:
        title = tr("Unload Selected")
        text = tr("Unload the {count} selected images from the session?").format(count=count)
    else:
        title = tr("Unload")
        text = tr("Unload this image from the session?")

    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Icon.Question)
    box.setWindowTitle(title)
    box.setText(text)
    box.setInformativeText(tr("Your saved edits stay in the database — this only removes the frames from the list."))
    box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel)
    box.setDefaultButton(QMessageBox.StandardButton.Yes)
    return box.exec() == QMessageBox.StandardButton.Yes


def confirm_delete_named(parent, kind: str, name: str, *, informative: str = "") -> bool:
    """Ask before deleting a named, user-created item — a work print, a roll, a
    flat-field profile. None of them are undoable and none can be re-derived from the
    frame, so each one is gated like Clear All. Enter confirms; Esc cancels.
    """
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Icon.Question)
    box.setWindowTitle(tr("Delete {kind}").format(kind=kind))
    box.setText(tr("Delete the {kind} “{name}”?").format(kind=kind.lower(), name=name))
    if informative:
        box.setInformativeText(informative)
    box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel)
    box.setDefaultButton(QMessageBox.StandardButton.Yes)
    return box.exec() == QMessageBox.StandardButton.Yes


def confirm_delete_mask(parent) -> bool:
    """Ask before deleting a single dodge/burn mask. Enter confirms; Esc cancels."""
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Icon.Question)
    box.setWindowTitle(tr("Delete Mask"))
    box.setText(tr("Delete this dodge/burn mask?"))
    box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel)
    box.setDefaultButton(QMessageBox.StandardButton.Yes)
    return box.exec() == QMessageBox.StandardButton.Yes


def confirm_clear_heals(parent, count: int) -> bool:
    """Ask before wiping every manual heal/scratch on the frame.

    Unlike single-heal undo this is not step-recoverable, so gate it like the
    session Clear All. Enter confirms (default button); Esc cancels.
    """
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Icon.Question)
    box.setWindowTitle(tr("Clear All Heals"))
    heal_word = tr("heals") if count != 1 else tr("heal")
    box.setText(tr("Remove all {count} manual {heal_word} from this image?").format(count=count, heal_word=heal_word))
    box.setInformativeText(tr("Every heal and scratch repair placed on this frame will be removed."))
    box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel)
    box.setDefaultButton(QMessageBox.StandardButton.Yes)
    return box.exec() == QMessageBox.StandardButton.Yes
