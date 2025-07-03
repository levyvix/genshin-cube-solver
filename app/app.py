from fastapi import FastAPI, Request, Form, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import json
from dataclasses import dataclass, asdict
from genshin_cube_solver.solver import CubeSolver
from genshin_cube_solver.utils import get_logger

logger = get_logger()

app = FastAPI(
    title="Genshin Cube Solver",
    description="Interface web para resolver cubos do Genshin Impact",
)

here = Path(__file__).parent

# Configuração de templates e arquivos estáticos
templates = Jinja2Templates(directory=here / "templates")
app.mount("/static", StaticFiles(directory=here / "static"), name="static")


@dataclass
class SolverConfig:
    """Configuração do solver com estado inicial e mapa de ataques."""

    initial: str
    attack_map: Dict[int, List[int]]
    max_steps: int = 10

    def to_dict(self) -> Dict:
        """Converte a configuração para dicionário."""
        return asdict(self)


class CubeSolverManager:
    """Gerenciador de instâncias do CubeSolver."""

    def __init__(self):
        self.configs: Dict[str, SolverConfig] = {}
        self.solutions: Dict[str, Tuple[List[int], List[int]]] = {}

    def create_config(
        self,
        config_id: str,
        initial: str,
        attack_map: Dict[int, List[int]],
        max_steps: int = 10,
    ) -> SolverConfig:
        """
        Cria uma nova configuração do solver.

        Args:
            config_id: Identificador único da configuração
            initial: Estado inicial dos cubos (ex: "2 1 1 3")
            attack_map: Mapa de ataques {posição: [cubos_afetados]}
            max_steps: Número máximo de passos para a solução

        Returns:
            SolverConfig: Configuração criada

        Example:
            >>> manager = CubeSolverManager()
            >>> config = manager.create_config("test", "2 1 1 3", {1: [1,2], 2: [2,3,1]})
        """
        config = SolverConfig(initial, attack_map, max_steps)
        self.configs[config_id] = config
        return config

    def solve(self, config_id: str) -> Optional[Tuple[List[int], List[int]]]:
        """
        Resolve o puzzle usando a configuração especificada.

        Args:
            config_id: ID da configuração a ser usada

        Returns:
            Tuple[List[int], List[int]]: Sequência de ataques e estado final, ou None se não encontrar solução

        Example:
            >>> solution = manager.solve("test")
            >>> if solution:
            ...     sequence, final_state = solution
        """
        if config_id not in self.configs:
            return None

        config = self.configs[config_id]
        solver = CubeSolver(config.initial, config.attack_map, config.max_steps)

        try:
            seq, final = solver.find_solution()
            seq = list(map(int, seq))
            final = list(map(int, final))
            print(seq, final)
            return (seq, final)
        except Exception as e:
            logger.error(f"Erro ao resolver configuração {config_id}: {e}")
            return None


solver_manager = CubeSolverManager()

# Configuração padrão
DEFAULT_CONFIG = {
    "initial": "2 1 1 3",
    "attack_map": {
        1: [1, 2],
        2: [2, 3, 1],
        3: [3, 2, 4],
        4: [4, 3],
    },
    "max_steps": 10,
}


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Página inicial com formulário de configuração.

    Args:
        request: Objeto de requisição FastAPI

    Returns:
        HTMLResponse: Página HTML renderizada
    """
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "default_config": DEFAULT_CONFIG,
            "configs": list(solver_manager.configs.keys()),
        },
    )


@app.post("/solve")
async def solve_cube(
    request: Request,
    initial: str = Form(...),
    attack_map_json: str = Form(...),
    max_steps: int = Form(10),
    config_name: str = Form("default"),
):
    """
    Endpoint para resolver o puzzle dos cubos.

    Args:
        request: Objeto de requisição
        initial: Estado inicial dos cubos
        attack_map_json: Mapa de ataques em formato JSON
        max_steps: Número máximo de passos
        config_name: Nome da configuração

    Returns:
        HTMLResponse: Página com resultado da solução
    """
    try:
        attack_map = json.loads(attack_map_json)
        attack_map = {int(k): v for k, v in attack_map.items()}

        config = solver_manager.create_config(
            config_name, initial, attack_map, max_steps
        )
        solution = solver_manager.solve(config_name)

        if solution:
            print(solution)
            sequence, final_state = solution
            success = True
            message = f"Solução encontrada em {len(sequence)} passos!"
        else:
            sequence, final_state = [], "Sem solução"
            success = False
            message = "Nenhuma solução encontrada dentro do limite de passos."
        print("--------------------------------")
        return templates.TemplateResponse(
            "result.html",
            {
                "request": request,
                "success": success,
                "message": message,
                "sequence": sequence,
                "initial_state": initial,
                "final_state": final_state,
                "config": config.to_dict(),
            },
        )

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400, detail="Formato JSON inválido no mapa de ataques"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@app.get("/api/configs")
async def get_configs():
    """
    API para obter todas as configurações salvas.

    Returns:
        Dict: Dicionário com todas as configurações
    """
    return {
        "configs": {k: v.to_dict() for k, v in solver_manager.configs.items()},
        "solutions": dict(solver_manager.solutions),
    }


@app.post("/api/config/{config_id}")
async def save_config(
    config_id: str,
    initial: str = Form(...),
    attack_map_json: str = Form(...),
    max_steps: int = Form(10),
):
    """
    API para salvar uma configuração específica.

    Args:
        config_id: ID da configuração
        initial: Estado inicial
        attack_map_json: Mapa de ataques em JSON
        max_steps: Número máximo de passos

    Returns:
        Dict: Configuração salva
    """
    try:
        attack_map = json.loads(attack_map_json)
        attack_map = {int(k): v for k, v in attack_map.items()}

        config = solver_manager.create_config(config_id, initial, attack_map, max_steps)
        return {"success": True, "config": config.to_dict()}

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Formato JSON inválido")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/config/{config_id}")
async def delete_config(config_id: str):
    """
    API para deletar uma configuração.

    Args:
        config_id: ID da configuração a ser deletada

    Returns:
        Dict: Status da operação
    """
    if config_id in solver_manager.configs:
        del solver_manager.configs[config_id]
        if config_id in solver_manager.solutions:
            del solver_manager.solutions[config_id]
        return {"success": True, "message": f"Configuração {config_id} removida"}
    else:
        raise HTTPException(status_code=404, detail="Configuração não encontrada")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
