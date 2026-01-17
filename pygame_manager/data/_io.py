from pathlib import Path
from typing import Iterable, Optional
try:
    import easygui
except ImportError:
    raise RuntimeError("[InputOutput] requieres easygui to work normally\nTry to download it with : pip install easygui")


class InputOutputHandler:
    """Gestion des entrées/sorties utilisateur"""
    @staticmethod
    def select_file(
        title: str = "Select a file",
        default: Optional[Path] = None,
        filetypes: Optional[Iterable[str]] = None,
    ) -> Optional[Path]:
        """Sélection d'un fichier"""
        path = easygui.fileopenbox(
            title=title,
            default=str(default) if default else None,
            filetypes=list(filetypes) if filetypes else None,
        )
        return Path(path) if path else None

    @staticmethod
    def select_directory(
        title: str = "Select a directory",
        default: Optional[Path] = None,
    ) -> Optional[Path]:
        """Sélection d'un dossier"""
        path = easygui.diropenbox(
            title=title,
            default=str(default) if default else None,
        )
        return Path(path) if path else None

    @staticmethod
    def save_file(
        title: str = "Save file as",
        default: Optional[Path] = None,
        filetypes: Optional[Iterable[str]] = None,
    ) -> Optional[Path]:
        """Sauvegarde d'un fichier"""
        path = easygui.filesavebox(
            title=title,
            default=str(default) if default else None,
            filetypes=list(filetypes) if filetypes else None,
        )
        return Path(path) if path else None