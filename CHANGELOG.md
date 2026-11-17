# Changelog

Formato: versão, data, o que mudou e o que quebra.

## 0.1.1 — 17/11/2026

Correção de nomenclatura. Ver `docs/ERRATA.md`, entrada E-001.

### Corrigido
- `ISTH` é a abreviação de Isthmus; `STH` passa a ser sublinguagem derivada, com
  semântica própria, em vez de apelido da mesma CLI
- `sth decide` recusa com `ISTH-STH-NOT-ALLOWED` em vez de decidir silenciosamente

### Adicionado
- `isthmus/sth.py` com `seal`, `verify`, `chain` e `derive`
- `isthmus/sth_cli.py` e entry point `sth` separado
- 10 testes novos, 42 no total

### Quebra
- quem chamava `sth decide` passa a receber recusa. É intencional

## 0.1.0 — 17/11/2026

Primeira publicação: 14 algoritmos em três camadas, recibo com fase grossa e fase
fina, verificação de cadeia, 17 códigos de recusa, zero dependência externa.
