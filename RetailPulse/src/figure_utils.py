"""
Figure Saving Utilities for RetailPulse
Centralizes figure saving to output/figures/ directory with consistent naming
"""

from pathlib import Path
import matplotlib.pyplot as plt
import logging

logger = logging.getLogger(__name__)

# Create output directories
OUTPUT_DIR = Path(__file__).parent.parent / "output"
FIGURES_DIR = OUTPUT_DIR / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# Also create legacy data directory if it doesn't exist
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

MODELS_DIR = Path(__file__).parent.parent / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)


def save_figure(fig, filename, dpi=300, formats=None):
    """
    Save matplotlib figure to multiple formats
    
    Parameters:
    -----------
    fig : matplotlib.figure.Figure
        The figure object to save
    filename : str
        Name of the file (without extension)
    dpi : int
        DPI resolution (default: 300 for high quality)
    formats : list
        List of formats to save (default: ['png', 'pdf'])
    
    Returns:
    --------
    dict : Paths to saved files
    """
    if formats is None:
        formats = ['png', 'pdf']
    
    saved_files = {}
    
    for fmt in formats:
        filepath = FIGURES_DIR / f"{filename}.{fmt}"
        try:
            fig.savefig(filepath, dpi=dpi, bbox_inches='tight')
            saved_files[fmt] = str(filepath)
            logger.info(f"✅ Saved figure: {filepath}")
        except Exception as e:
            logger.error(f"❌ Failed to save {filepath}: {str(e)}")
    
    return saved_files


def save_plotly_figure(fig, filename, formats=None):
    """
    Save Plotly figure to multiple formats
    
    Parameters:
    -----------
    fig : plotly.graph_objects.Figure
        The Plotly figure object to save
    filename : str
        Name of the file (without extension)
    formats : list
        List of formats to save (default: ['html', 'png'])
    
    Returns:
    --------
    dict : Paths to saved files
    """
    if formats is None:
        formats = ['html', 'png']
    
    saved_files = {}
    
    for fmt in formats:
        filepath = FIGURES_DIR / f"{filename}.{fmt}"
        try:
            if fmt == 'html':
                fig.write_html(str(filepath))
            else:
                fig.write_image(str(filepath), width=1200, height=600)
            saved_files[fmt] = str(filepath)
            logger.info(f"✅ Saved Plotly figure: {filepath}")
        except Exception as e:
            logger.warning(f"⚠️  Could not save {fmt}: {str(e)}")
    
    return saved_files


def get_figure_path(filename):
    """Get the full path for a figure file"""
    return FIGURES_DIR / filename


def list_saved_figures():
    """List all saved figures"""
    if FIGURES_DIR.exists():
        figures = list(FIGURES_DIR.glob("*"))
        return sorted(figures)
    return []


# Logging configuration
def setup_figure_logging():
    """Setup logging for figure saving"""
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)


setup_figure_logging()

print(f"[Figures] Figures will be saved to: {FIGURES_DIR}")
