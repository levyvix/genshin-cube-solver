from loguru import logger
import sys
from pathlib import Path
import datetime


def get_logger():
    """
    Configura o logger do sistema com formato seguro para nomes de arquivo.

    Cria logs na pasta 'logs' com rotação diária e formatação adequada.
    Remove caracteres problemáticos do timestamp para compatibilidade com Windows.

    Example:
        >>> setup_logger()
        >>> logger.info("Sistema iniciado")
    """
    logs_dir = Path(__file__).parent / "logs"
    logs_dir.mkdir(exist_ok=True)

    # Formato seguro para nome de arquivo (substitui : por -)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = logs_dir / f"cube_solver_{timestamp}.log"

    # Remove handler padrão se existir
    logger.remove()

    # Adiciona handler para console
    logger.add(
        sink=lambda msg: print(msg, end=""),
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO",
    )

    # Adiciona handler para arquivo com rotação diária
    logger.add(
        sink=str(log_file),
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="1 day",
        retention="7 days",
        compression="zip",
        level="INFO",
        enqueue=True,
        backtrace=True,
        diagnose=True,
    )

    logger.info("Logger configurado com sucesso")
    logger.info(f"Logs sendo salvos em: {log_file}")

    return logger
