# DoseCerta

[![CI](https://github.com/luccacampelo/dose-certa/actions/workflows/ci.yml/badge.svg)](https://github.com/luccacampelo/dose-certa/actions/workflows/ci.yml)


AplicaÃ§Ã£o simples com interface GUI (web local) para ajudar no controle de horÃ¡rios de medicamentos,
reduzindo esquecimentos e atrasos de doses em rotinas de cuidado.

## Problema real
Muitas pessoas idosas e cuidadores familiares enfrentam dificuldade para manter uma rotina correta de
medicaÃ§Ã£o. Esquecer uma dose ou tomar fora do horÃ¡rio pode prejudicar a saÃºde e aumentar riscos.

## Proposta da soluÃ§Ã£o
O DoseCerta organiza os medicamentos cadastrados, mostra doses do dia com status e permite registrar
quando uma dose foi tomada. Assim, o usuÃ¡rio visualiza rapidamente o que estÃ¡ pendente, atrasado ou
concluÃ­do.

## PÃºblico-alvo
- Cuidadores familiares
- Pessoas idosas com rotina de medicaÃ§Ã£o
- Pessoas com uso contÃ­nuo de remÃ©dios

## Funcionalidades principais
- Cadastro de medicamento (nome, dosagem, horÃ¡rios e observaÃ§Ãµes)
- Listagem de medicamentos ativos
- VisualizaÃ§Ã£o diÃ¡ria de doses
- Status por dose: `Pendente`, `Atrasada`, `Tomada`
- Registro de dose tomada
- Armazenamento local em arquivo JSON

## Tecnologias utilizadas
- Python 3.12+
- Streamlit (GUI web local)
- Pytest (testes automatizados)
- Ruff (lint/anÃ¡lise estÃ¡tica)
- GitHub Actions (CI)

## Estrutura do projeto
```text
dose-certa/
â”œâ”€â”€ .github/workflows/ci.yml
â”œâ”€â”€ src/dose_certa/
â”‚   â”œâ”€â”€ __init__.py
â”‚   â”œâ”€â”€ app.py
â”‚   â”œâ”€â”€ service.py
â”‚   â””â”€â”€ storage.py
â”œâ”€â”€ tests/test_service.py
â”œâ”€â”€ README.md
â”œâ”€â”€ pyproject.toml
â”œâ”€â”€ requirements.txt
â”œâ”€â”€ requirements-dev.txt
â”œâ”€â”€ VERSION
â”œâ”€â”€ CHANGELOG.md
â”œâ”€â”€ CONTRIBUTING.md
â””â”€â”€ LICENSE
```

## InstalaÃ§Ã£o
### Windows (PowerShell)
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

## ExecuÃ§Ã£o da aplicaÃ§Ã£o
```powershell
$env:PYTHONPATH = "src"
streamlit run src/dose_certa/app.py
```

Depois, abra no navegador o endereÃ§o exibido no terminal (normalmente `http://localhost:8501`).

## Rodar os testes
```powershell
$env:PYTHONPATH = "src"
pytest -q -p no:cacheprovider
```

## Rodar o lint
```powershell
ruff check --no-cache .
```

## Exemplo de uso (evidÃªncia)
```text
1) Cadastrar "Losartana 50mg" com horÃ¡rios 08:00, 20:00
2) Abrir painel diÃ¡rio
3) Marcar dose de 08:00 como tomada
4) Ver resumo: Tomadas: 1 | Pendentes: 1 | Atrasadas: 0
```

## Versionamento semÃ¢ntico
VersÃ£o atual: `1.0.0` (tambÃ©m registrada no arquivo `VERSION` e em `pyproject.toml`).

## Autor
LUCCA DOS SANTOS CAMPELO SERPA

## Link do repositÃ³rio pÃºblico
`https://github.com/luccacampelo/dose-certa`

