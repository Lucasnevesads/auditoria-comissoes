# Auditoria de comissões · Norte Garantia

791 apólices · 1570 parcelas · 1568 linhas na planilha do financeiro

1. Integridade das fontes
=========================

O que precisa fechar ao centavo. Se falhar aqui, nada abaixo vale.

  [OK] Créditos de seguradora no extrato x demonstrativos
         R$ 3.498.097,63 x R$ 3.498.097,63  diferença R$ 0,00
  [OK] Parcelas recebidas x demonstrativos
         R$ 3.498.097,63 x R$ 3.498.097,63  diferença R$ 0,00

As duas fecham. Banco e seguradora são sistemas e não erram conta:
qualquer divergência daqui pra frente vem do controle manual.

2. A diferença entre as duas réguas
===================================

  Registrado no CRM (comissão cheia, data da venda)     R$ 4.080.660,80
  Recebido no banco (parcela, data do pagamento)        R$ 3.450.030,87
  --------------------------------------------------------------------
  Diferença                                               R$ 630.629,93

Decompondo a diferença:

  Apólices canceladas (venda que nunca virou apólice)   -R$ 138.150,95
  Parcelas ainda não recebidas (calendário, não atraso)  -R$ 444.412,22
  Negócios sem lastro na planilha do financeiro          -R$ 48.066,11
  Resíduo sem explicação                                      -R$ 0,65

A diferença está inteiramente explicada. Não é dinheiro faltando:
é venda cancelada, parcela que ainda não venceu e negócio que o
financeiro não recebeu. Nenhum real sem destino.

3. Achados
==========

  gravidade   tipo                          qtd           impacto
  ---------------------------------------------------------------
  alta        negocio_so_no_crm               2      R$ 48.066,11
  alta        competencia_trocada             6      R$ 24.748,59
  alta        cancelada_como_pendente         3       R$ 1.672,71
  baixa       divergencia_de_centavos         8           R$ 3,13
  media       consultor_com_espaco            5         R$ 735,31
  ---------------------------------------------------------------
  TOTAL                                      24      R$ 75.225,85

Detalhe linha a linha em saida/achados.csv