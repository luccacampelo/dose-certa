# DoseCerta

Aplicação simples com interface GUI (web local) para ajudar no controle de horários de medicamentos,
reduzindo esquecimentos e atrasos de doses em rotinas de cuidado.

## Problema real
Muitas pessoas idosas e cuidadores familiares enfrentam dificuldade para manter uma rotina correta de
medicação. Esquecer uma dose ou tomar fora do horário pode prejudicar a saúde e aumentar riscos.

## Proposta da solução
O DoseCerta organiza os medicamentos cadastrados, mostra doses do dia com status e permite registrar
quando uma dose foi tomada. Assim, o usuário visualiza rapidamente o que está pendente, atrasado ou
concluído.

## Público-alvo
- Cuidadores familiares
- Pessoas idosas com rotina de medicação
- Pessoas com uso contínuo de remédios

## Funcionalidades principais
- Cadastro de medicamento (nome, dosagem, horários e observações)
- Listagem de medicamentos ativos
- Visualização diária de doses
- Status por dose: `Pendente`, `Atrasada`, `Tomada`
- Registro de dose tomada
- Armazenamento local em arquivo JSON

## Tecnologias utilizadas
- Python 3.12+
- Streamlit (GUI web local)
- Pytest (testes automatizados)
- Ruff (lint/análise estática)
- GitHub Actions (CI)

## Estrutura do projeto
```text
dose-certa/
├── .github/workflows/ci.yml
├── src/dose_certa/
│   ├── __init__.py
│   ├── app.py
│   ├── service.py
│   └── storage.py
├── tests/test_service.py
├── README.md
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── VERSION
├── CHANGELOG.md
├── CONTRIBUTING.md
└── LICENSE
```

## Instalação
### Windows (PowerShell)
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

## Execução da aplicação
```powershell
$env:PYTHONPATH = "src"
streamlit run src/dose_certa/app.py
```

Depois, abra no navegador o endereço exibido no terminal (normalmente `http://localhost:8501`).

## Rodar os testes
```powershell
$env:PYTHONPATH = "src"
pytest -q -p no:cacheprovider
```

## Rodar o lint
```powershell
ruff check --no-cache .
```

## Exemplo de uso (evidência)
```text
1) Cadastrar "Losartana 50mg" com horários 08:00, 20:00
2) Abrir painel diário
3) Marcar dose de 08:00 como tomada
4) Ver resumo: Tomadas: 1 | Pendentes: 1 | Atrasadas: 0
```

## Versionamento semântico
Versão atual: `1.0.0` (também registrada no arquivo `VERSION` e em `pyproject.toml`).

## Autor
LUCCA DOS SANTOS CAMPELO SERPA

## Link do repositório público
`https://github.com/lucca_campelo/dose-certa`
