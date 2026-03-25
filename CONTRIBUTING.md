# Contribuindo

Obrigado por querer melhorar o DoseCerta.

## Fluxo sugerido
1. Faca um fork do repositorio.
2. Crie uma branch para sua alteracao (`feature/minha-melhoria`).
3. Rode lint e testes localmente.
4. Abra um Pull Request explicando o que mudou e por que mudou.

## Padrao minimo para aprovar PR
- `ruff check --no-cache .` sem erros
- `pytest -q -p no:cacheprovider` com todos os testes passando
- Documentacao atualizada quando houver mudanca de comportamento
