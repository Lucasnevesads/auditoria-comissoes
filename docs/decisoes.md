# Decisões do projeto

Registro do **porquê**, não do que foi feito. O código já mostra o que foi feito.

---

## A auditoria é proibida de ler o gabarito, e a proibição é código

**A escolha:** `config/fontes.yml` lista as tabelas permitidas, o gabarito não está nela, e `fontes.carregar()` levanta `PermissionError` para quem pedir. A pontuação vive em `src/medir.py`, arquivo separado que só roda depois.

**Por quê:** a base traz um arquivo dizendo exatamente onde estão os 24 erros. Se a auditoria puder abri-lo, ela não está auditando, está copiando.

**O que custa:** duas camadas a mais para uma coisa que um comentário "resolveria". Mas comentário não resolve: seis meses depois alguém faria o join sem perceber que estava colando. Regra que depende de lembrar não é regra.

---

## A ponte explica, não acusa

**A escolha:** decompor a diferença de R$ 630 mil em componentes com nome (apólices canceladas, parcelas não vencidas, negócio sem lastro) antes de apontar qualquer erro. Só o resíduo é tratado como problema.

**Por quê:** é o ponto do projeto inteiro. Um relatório que diz "faltam R$ 630 mil" está **errado**, cria pânico e queima a confiança de quem o escreveu. Um que diz "R$ 444 mil ainda não venceram, R$ 138 mil foram cancelados, e R$ 48 mil o financeiro nunca registrou" resolve o problema e aponta a única coisa que exige ação.

**O que custa:** a ponte precisa ser mantida. Toda regra de negócio nova (um status novo, um tipo novo de estorno) exige um componente novo, senão cai no resíduo e vira alarme falso. É manutenção que uma lista de erros não teria.

---

## A primeira versão da ponte contava o mesmo dinheiro duas vezes

**O que aconteceu:** a ponte fechava com resíduo de -R$ 1.672,06, valor muito próximo do total das parcelas canceladas marcadas como "Pendente". A leitura tentadora era que o resíduo apontava para o defeito.

**O que era:** dupla contagem. Essas parcelas entravam em **dois** componentes ao mesmo tempo, o de canceladas e o de pendentes, e a ponte subtraía o mesmo dinheiro duas vezes. Com o filtro correto o resíduo caiu para -R$ 0,65, que é a soma real das divergências de centavos.

**Por que fica registrado:** o erro quase virou uma conclusão bonita construída em cima de uma conta errada. **Resíduo que "coincidentemente" bate com um achado quase sempre é dupla contagem, não descoberta.** É a armadilha mais comum de reconciliação e merece estar escrita.

---

## Casar as bases pelo par (apólice, parcela), não por id

**A escolha:** juntar planilha e sistema por `numero_apolice` + `numero_parcela`.

**Por quê:** planilha de produção é digitada a partir do documento e não guarda id de sistema. Foi ao escrever esta auditoria que ficou claro que a base estava exportando o id na planilha, e o projeto da base foi corrigido por causa disso: com o id, a conferência seria um join de uma linha, o que não existe na vida real.

**O que custa:** o join fica sujeito a erro de digitação no número da apólice, e uma linha mal digitada some da conferência em silêncio. É exatamente o risco que existe na prática, então o custo é o realismo funcionando. A conferência `numero_de_apolice_repetido` cobre o outro lado desse mesmo risco.

---

## Uma conferência que sempre passa

**A escolha:** manter `numero_de_apolice_repetido`, que acha zero e vai continuar achando zero.

**Por quê:** se dois contratos tiverem o mesmo número, **todas** as outras conferências passam a errar em silêncio, porque o casamento entre as bases depende desse número. O valor dela não é o que ela acha, é o que ela garante.

**O que custa:** o relatório mostra uma linha com zero, o que parece desperdício para quem lê rápido. Preferível a descobrir seis meses depois que a auditoria inteira estava errada e ninguém tinha como saber.
